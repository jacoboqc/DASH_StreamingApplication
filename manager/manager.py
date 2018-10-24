#!/usr/bin/python3
import boto3
from listener import Listener
import sys
import logging
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)

formatstr = '[%(asctime)s - %(name)s - %(levelname)s]  %(message)s'
formatter = logging.Formatter(formatstr)

sh.setFormatter(formatter)
logger.addHandler(sh)


class Manager(object):

    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.region_name = "eu-west-1"


if __name__ == "__main__":
    manager = Manager()
    logger.info("Manager iniliazed ")
    queue_name = "test_queue"
    listener = Listener(queue_name, region_name="eu-west-1", max_number_of_messages=5)
    listener.start()






    # queue_url = manager.sqs.get_queue_url(QueueName=queue_name)
    # queue_url = queue_url['QueueUrl']
    #
    # for i in range(0, 5):
    #     manager.sqs.send_message(
    #         QueueUrl=queue_url,
    #         MessageBody="Message %s in queue '%s''" % (i, queue_name),
    #         DelaySeconds=0,
    #     )
    #     logger.info("Message sent")
    #     time.sleep(10)
    #
    # logger.info("Finiseh sending messages")
    # time.sleep(20)
    #manager.sqs.delete_queue(QueueUrl=queue_url)
    #logger.info("Queue deleted")
