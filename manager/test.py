from listener2 import Listener
import boto3
import json
import requests
import datetime
import asyncio
import concurrent.futures


sqs = boto3.client('sqs')
region_name = 'eu-west-1'
queue_name = 'task_queue'
listener = Listener(queue_name, region_name=region_name, max_number_of_messages=5)
listener.start()

# queue_url = sqs.get_queue_url(QueueName=queue_name)
# queue_url = queue_url['QueueUrl']
# for i in range(0, 5):
#     sqs.send_message(
#         QueueUrl=queue_url,
#         MessageBody="Message %s in queue '%s''" % (i, queue_name),
#         DelaySeconds=0,
#         MessageGroupId=''
#     )
#     print("Message sent")
#     time.sleep(10)
# print("Finiseh sending messages")
# time.sleep(20)