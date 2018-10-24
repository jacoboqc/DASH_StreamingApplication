import boto3
import datetime
import requests
import json
import time
from threading import Thread

cwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')

launch_template_name = 'ffmpeg_instance'
instance_api_endpoint = '/time_remaining'


class Balancer(Thread):
    def run(self):
        while True:
            for instance in ec2.instances.all():
                response = cwatch.get_metric_statistics(
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
                cpu_load = response['Datapoints'][1]['Timestamp']
                if cpu_load <= 5:
                    ec2.stop_instances(InstanceIds=[instance.id], DryRun=False)

                time.sleep(5)
