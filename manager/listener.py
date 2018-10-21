#!/usr/bin/python3
import boto3
import json
import threading
from threading import Thread
import sys
import time
import logging

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
        self._poll_interval = kwargs["interval"] if 'interval' in kwargs else 30
        self._queue_visibility_timeout = kwargs['visibility_timeout'] if 'visibility_timeout' in kwargs else 600
        self._error_queue_name = kwargs['error_queue'] if 'error_queue' in kwargs else None
        self._error_queue_url = kwargs['error_queue_url'] if 'error_queue_url' in kwargs else None
        self._error_queue_visibility_timeout = kwargs[
            'error_visibility_timeout'] if 'error_visibility_timeout' in kwargs else '600'
        self._message_attribute_names = kwargs['message_attribute_names'] if 'message_attribute_names' in kwargs else []
        self._attribute_names = kwargs['attribute_names'] if 'attribute_names' in kwargs else []
        self._region_name = kwargs['region_name'] if 'region_name' in kwargs else None
        self._wait_time = kwargs['wait_time'] if 'wait_time' in kwargs else 20
        self._max_number_of_messages = kwargs['max_number_of_messages'] if 'max_number_of_messages' in kwargs else 1

        self._sqs = self._initialize_sqs()

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
                VisibilityTimeout=self._queue_visibility_timeout,
                WaitTimeSeconds=self._wait_time
            )

            if 'Messages' in messages:
                sqs_logger.info(str(len(messages['Messages'])) + " messages received")

                for message in messages['Messages']:
                    receipt_handle = message['ReceiptHandle']
                    m_body = message['Body']
                    message_attribs = None
                    attribs = None
                    message_id = None

                    try:
                        body_dict = json.loads(m_body)
                    except:
                        sqs_logger.warning("Unable to parse message from SQS queue '%s': data '%s'"
                                           % (self._queue_name, m_body))
                        continue
                    if 'MessageAttributes' in message:
                        message_attribs = message['MessageAttributes']
                    if 'Attributes' in message:
                        attribs = message['Attributes']
                    if 'MessageId' in message:
                        message_id = message['MessageId']

                    self.process_message(body_dict, message_id, message_attribs, attribs)
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

    def process_message(self, body, message_id, attributes, messages_attributes):
        sqs_logger.info("Processing message ")
        """
        Implement this method to do something with the SQS message contents
        :param body: dict
        :param attributes: dict
        :param messages_attributes: dict
        :return:
        """
        return

    # # is this a fifo queue?
    # if self._queue_name.endswith(".fifo"):
    #     fifoQueue = "true"
    #     q = sqs.create_queue(
    #         QueueName=self._queue_name,
    #         Attributes={
    #             'VisibilityTimeout': self._queue_visibility_timeout,  # 10 minutes
    #             'FifoQueue': fifoQueue
    #         }
    #     )
    # else:
    #     # need to avoid FifoQueue property for normal non-fifo queues
    #     q = sqs.create_queue(
    #         QueueName=self._queue_name,
    #         Attributes={
    #             'VisibilityTimeout': self._queue_visibility_timeout,  # 10 minutes
    #         }
    #     )