import boto3
import datetime
import requests
import json
import time
from threading import Thread

cwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')

LaunchTemplateName = 'ffmpeg_instance''
instanceApiEndpoint = '/time_remaining'

class Balancer(Thread):
    def run(self):
        while True:
            for instance in ec2.instances.all():
                response = cwatch.get_metric_statistics(
                    Namespace = 'AWS/EC2',
                    MetricName = 'CPUUtilization',
                    StartTime = (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat(),
                    EndTime = datetime.datetime.now().isoformat(),
                    Statistics = ['Average'],
                    Period = 1,
                    Dimensions = [
                        {
                            'Name' : 'InstanceId',
                            'Value' : instance.id
                        }
                    ]
                )
                cpuLoad = response['Datapoints'[1].'Timestamp']
                if cpuLoad <= 5:
                    ec2.stop_instances(InstanceIds=[instance.id], DryRun=False)
            time.sleep(5)

    def select_instance_to_run(videoS3Location):
        for instance in ec2.instances.all():
            response = cwatch.get_metric_statistics(
                Namespace = 'AWS/EC2',
                MetricName = 'CPUUtilization',
                StartTime = (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat(),
                EndTime = datetime.datetime.now().isoformat(),
                Statistics = ['Average'],
                Period = 1,
                Dimensions = [
                    {
                        'Name' : 'InstanceId',
                        'Value' : instance.id
                    }
                ]
            )
            cpuLoad = response['Datapoints'[1].'Timestamp']
            if cpuLoad <= 50:
                assign_job(videoS3Location, instance.public_dns_name)
                continue

            r = requests.get('http://' + instance.public_dns_name + instanceApiEndpoint)
            if r.status_code == 200:
                j = json.loads(r.json())
                timeRemaining = j['time']

            if timeRemaining < 60:
                time.sleep(timeRemaining)
                assign_job(videoS3Location, instance.public_dns_name)
                continue

            dns_name_new_instance = launch_or_create()
            assign_job(videoS3Location, dns_name_new_instance)


    def assign_job(videoS3Location, dnsName):
        postJobEndpoint = '/accept_job'

        requests.post('http://' + dnsName + postJobEndpoint,
            params = {'video': videoS3Location}
            )

    def launch_or_create():
        for instance in ec2.instances.all():
            if instance.state['Code'] == 80:
                instance.start(DryRun=False)
                return instance.public_dns_name
        instance = ec2.create_instances(
            LaunchTemplate = {
                'LaunchTemplateName' : LaunchTemplateName,
                'Version' : '$Default'
                },
            MaxCount=1,
            MinCount=1
        )
        return instance[0].public_dns_name
