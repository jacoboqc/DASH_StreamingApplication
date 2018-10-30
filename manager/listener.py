#!/usr/bin/python3
import boto3
import json
import threading
from threading import Thread
import time
import logging
import requests
import datetime

sqs_logger = logging.getLogger(__name__)
sqs_logger.setLevel(logging.INFO)

sh = logging.FileHandler('listener.log')
sh.setLevel(logging.INFO)

formatstr = '[%(asctime)s - %(name)s - %(levelname)s]  %(message)s'
formatter = logging.Formatter(formatstr)

sh.setFormatter(formatter)
sqs_logger.addHandler(sh)


class Listener(Thread):

    def __init__(self, queue=None, queue_url=None, **kwargs):
        threading.Thread.__init__(self)
        if not queue and not queue_url:
            raise ValueError('Either `queue` or `queue_url` should be provided.')
        self._queue_name = queue
        self._queue_url = queue_url
        self._poll_interval = kwargs["interval"] if 'interval' in kwargs else 20
        self._queue_visibility_timeout = kwargs['visibility_timeout'] if 'visibility_timeout' in kwargs else '600'
        self._message_attribute_names = kwargs['message_attribute_names'] if 'message_attribute_names' in kwargs else []
        self._attribute_names = kwargs['attribute_names'] if 'attribute_names' in kwargs else []
        self._region_name = kwargs['region_name'] if 'region_name' in kwargs else None
        self._wait_time = kwargs['wait_time'] if 'wait_time' in kwargs else 20
        self._max_number_of_messages = kwargs['max_number_of_messages'] if 'max_number_of_messages' in kwargs else 1

        self._sqs = self._initialize_sqs()
        self._ec2 = boto3.resource('ec2')
        self._ec2_client = boto3.client('ec2')
        self._cwatch = boto3.client('cloudwatch')
        self._launch_template_name = 'ffmpeg_instance'
        self._instance_api_endpoint = '/time_remaining'

    def _initialize_sqs(self):
        # create SQS client
        sqs = boto3.client('sqs')
        if not self._queue_url:
            try:
                queue_url = sqs.get_queue_url(QueueName=self._queue_name)
                self._queue_url = queue_url['QueueUrl']
            except:
                sqs_logger.info("The specified queue does not exist")

        if self._queue_url is None:
            # create queue if not found
            sqs_logger.warning("main queue not found, creating now")
            if self._queue_name.endswith(".fifo"):
                fifo_queue = "true"
                q = sqs.create_queue(
                    QueueName=self._queue_name,
                    Attributes={
                        'VisibilityTimeout': self._queue_visibility_timeout,
                        'FifoQueue': fifo_queue
                    }
                )
            else:
                q = sqs.create_queue(
                    QueueName=self._queue_name,
                    Attributes={
                        'VisibilityTimeout': self._queue_visibility_timeout,
                    }
                )
            self._queue_url = q['QueueUrl']
        return sqs

    def _start_listening(self):
        while True:
            sqs_logger.info('Waiting for message in queue...')
            messages = self._sqs.receive_message(
                QueueUrl=self._queue_url,
                AttributeNames=self._attribute_names,
                MessageAttributeNames=self._message_attribute_names,
                MaxNumberOfMessages=self._max_number_of_messages,
                WaitTimeSeconds=self._wait_time
            )

            if 'Messages' in messages:
                sqs_logger.info(str(len(messages['Messages'])) + " messages received")

                for message in messages['Messages']:
                    sqs_logger.info('Getting message...')
                    receipt_handle = message['ReceiptHandle']
                    data = message['Body']
                    message_id = None
                    m_body = None
                    success = False
                    try:
                        m_body = json.loads(data)
                    except:
                        sqs_logger.warning("Unable to parse message from SQS queue '%s': data '%s'"
                                           % (self._queue_name, data))
                    if m_body is not None:
                        success = self._process_message(m_body)
                    if message['MessageId'] is not None:
                        message_id = message['MessageId']
                    # Delete received message from queue
                    if success:
                        self._sqs.delete_message(
                            QueueUrl=self._queue_url,
                            ReceiptHandle=receipt_handle
                        )
                        sqs_logger.info("Message with ID: %s deleted." % message_id)
            else:
                time.sleep(self._poll_interval)

    def run(self):
        sqs_logger.info("Listening to queue '%s' - URL %s" % (self._queue_name, self._queue_url))

        self._start_listening()

    def _process_message(self, body):
        sqs_logger.info("Processing message %s" % body)
        video_s3_location = body['fileUrl']

        for instance in self._ec2.instances.all():
            if instance.state.get('Code') == 16:
                ip = instance.public_ip_address
                ins_id = instance.id
                if (ip != '52.17.18.108' and ip != '52.16.139.42' and ip != '34.247.193.119' and
                        ins_id != 'i-0499fe00dbf35e2ae' and ins_id != 'i-0832e3e1c8cea1435'):
                    response = self._cwatch.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        StartTime=(datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat(),
                        EndTime=datetime.datetime.now().isoformat(),
                        Statistics=['Average'],
                        Period=1,
                        Dimensions=[
                            {
                                'Name': 'InstanceId',
                                'Value': instance.id
                            }
                        ]
                    )
                    i = 0
                    date = response['Datapoints'][i]['Timestamp']
                    cpu_load = response['Datapoints'][i]['Average']
                    for d in response['Datapoints']:
                        if i != 0:
                            if date < d['Timestamp']:
                                cpu_load = d['Average']
                        i += 1
                    if cpu_load <= 50.0:
                        sqs_logger.info('Instance running with low load. Assigning job to it. ID: ' + instance.id)
                        self.assign_job(video_s3_location, instance.public_dns_name, instance.id)
                        return

                    r = requests.get('http://' + instance.public_dns_name + self._instance_api_endpoint)
                    time_remaining = 0
                    if r.status_code == 200:
                        j = json.loads(r.json())
                        time_remaining = j['time']

                    if time_remaining < 15:
                        sqs_logger.info('Job almost finished in instance with id: ' + str(instance.id) + '. Waiting '
                                        + str(time_remaining) + ' seconds to assign job to it.')
                        time.sleep(time_remaining)
                        success = self.assign_job(video_s3_location, instance.public_dns_name, instance.id)
                        return success

        sqs_logger.info('No instances with low load. Launching or creating new instances')
        new_instance = self.launch_or_create()
        success = self.assign_job(video_s3_location, new_instance.public_dns_name, new_instance.id)
        return success

    def assign_job(self, video_s3_location, dns_name, instance_id):
        response = self._ec2_client.describe_instance_status(InstanceIds=[instance_id])
        instance_status = response['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status']
        system_status = response['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']
        while instance_status != 'passed' and system_status != 'passed':
            time.sleep(10)
            response = self._ec2_client.describe_instance_status(InstanceIds=[instance_id])
            instance_status = response['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status']
            system_status = response['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']

        sqs_logger.info('Assigning job to instance with id: ' + str(instance_id))
        post_job_endpoint = '/accept_job'

        try:
            response = requests.post('http://' + dns_name + post_job_endpoint,
                                     json={"video": video_s3_location})
            return response.status_code == 200
        except requests.exceptions.RequestException:
            sqs_logger.error('Error trying to connect to FFMPEG instance while trying to assing job. InstanceID: '
                             + str(instance_id))
            return False

    def launch_or_create(self):
        for instance in self._ec2.instances.all():
            ip = instance.public_ip_address
            ins_id = instance.id
            if (ip != '52.17.18.108' and ip != '52.16.139.42' and ip != '34.247.193.119' and
                    ins_id != 'i-0499fe00dbf35e2ae' and ins_id != 'i-0832e3e1c8cea1435'):
                if instance.state.get('Code') == 80:
                    sqs_logger.info('Starting instance with id: ' + str(instance.id))
                    instance.start(DryRun=False)
                    # wait until instance running
                    sqs_logger.info('Status of the instance (id: ' + str(instance.id) + ') - '
                                    + str(instance.state.get('Name')))
                    while instance.state.get('Code') != 16:
                        time.sleep(10)
                        instance.load()
                    return instance

        instances = self._ec2.create_instances(
            LaunchTemplate={
                'LaunchTemplateName': self._launch_template_name,
                'Version': '$Default'
            },
            MaxCount=1,
            MinCount=1
        )
        sqs_logger.info('No instances stopped. Creating new instance... ID: ' + str(instances[0].id))
        # wait until instance running
        sqs_logger.info('Status of the instance (id: ' + str(instances[0].id) + ' - '
                        + str(instances[0].state.get('Name')))
        while instances[0].state.get('Code') != 16:
            instances[0].load()
            time.sleep(10)
        return instances[0]
