#!/usr/bin/python3
import boto3
import json
import threading
from threading import Thread
import sys
import time
import logging
import requests
import datetime

sqs_logger = logging.getLogger(__name__)
sqs_logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
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
                    receipt_handle = message['ReceiptHandle']
                    data = message['Body']
                    message_id = None

                    try:
                        m_body = json.loads(data)
                    except:
                        sqs_logger.warning("Unable to parse message from SQS queue '%s': data '%s'"
                                           % (self._queue_name, data))
                        continue
                    if 'MessageId' in message:
                        message_id = message['MessageId']

                    self._process_message(m_body, message_id)
                    # Delete received message from queue
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

    def _process_message(self, body, message_id):
        sqs_logger.info("Processing message %s" % body)
        video_s3_location = body.fileUrl

        for instance in self._ec2.instances.all():
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
            cpu_load = response['Datapoints'][0]['Timestamp']
            if cpu_load <= 50:
                self.assign_job(video_s3_location, instance.public_dns_name)
                continue

            r = requests.get('http://' + instance.public_dns_name + self._instance_api_endpoint)
            time_remaining = 0
            if r.status_code == 200:
                j = json.loads(r.json())
                time_remaining = j['time']

            if time_remaining < 20:
                time.sleep(time_remaining)
                self.assign_job(video_s3_location, instance.public_dns_name)
                continue

            dns_name_new_instance = self.launch_or_create()
            self.assign_job(video_s3_location, dns_name_new_instance)

        return

    def assign_job(self, video_s3_location, dns_name):
        post_job_endpoint = '/accept_job'

        requests.post('http://' + dns_name + post_job_endpoint,
                      data={'video': video_s3_location})


    def launch_or_create(self):
        for instance in self._ec2.instances.all():
            if instance.state.get('Code') == 80:
                instance.start(DryRun=False)
                return instance.public_dns_name
        instance = self._ec2.create_instances(
            LaunchTemplate={
                'LaunchTemplateName': self._launch_template_name,
                'Version': '$Default'
                },
            MaxCount=1,
            MinCount=1
        )
        return instance[0].public_dns_name
