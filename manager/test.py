#from listener import Listener
import boto3
import sys
import time

response = {'InstanceStatuses': [{'AvailabilityZone': 'eu-west-1c', 'InstanceId': 'i-0351d1c087d6b1c05', 'InstanceState': {'Code': 16, 'Name': 'running'}, 'InstanceStatus': {'Details': [{'Name': 'reachability', 'Status': 'passed'}], 'Status': 'ok'}, 'SystemStatus': {'Details': [{'Name': 'reachability', 'Status': 'passed'}], 'Status': 'ok'}}], 'ResponseMetadata': {'RequestId': '91785132-fb7f-4a10-8582-5d9620aadeda', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'text/xml;charset=UTF-8', 'content-length': '1139', 'date': 'Sun, 28 Oct 2018 17:38:07 GMT', 'server': 'AmazonEC2'}, 'RetryAttempts': 0}}

instance_status = response['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status']
system_status = response['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']
print(instance_status)
print(system_status)
#
# sqs = boto3.client('sqs')
# region_name = 'eu-west-1'
# queue_name = 'task_queue'
# listener = Listener(queue_name, region_name=region_name, max_number_of_messages=5)
# listener.start()
#
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