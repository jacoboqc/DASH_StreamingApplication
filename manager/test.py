from listener2 import Listener
import boto3
import json
import requests
import datetime
import asyncio
import concurrent.futures

instance_api_endpoint = '/time_remaining'

r = requests.get('http://' + '34.246.202.12' + instance_api_endpoint)
if r.status_code == 200:
    time_remaining = r.json()
    print(time_remaining)

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