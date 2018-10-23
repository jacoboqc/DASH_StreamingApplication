import boto3
import datetime
import requests
import json
import time

cwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')

LaunchTemplateName = 'ffmpeg_instance''
instanceApiEndpoint = '/time_remaining'

videoS3Location = '...'

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
        assignJob(videoS3Location, instance.public_dns_name)
        continue

    r = requests.get('http://' + instance.public_dns_name + instanceApiEndpoint)
    if r.status_code == 200:
        j = json.loads(r.json())
        timeRemaining = j['time']

    if timeRemaining < 60:
        time.sleep(timeRemaining, instance.public_dns_name)
        assignJob(videoS3Location)

ec2.create_instance(
    LaunchTemplate = {
        'LaunchTemplateName' = LaunchTemplateName,
        'Version' = 'Default'
    }
)

def assignJob(videoS3Location, dnsName):
    postJobEndpoint = '/accept_job'

    requests.post('http://' + dnsName + postJobEndpoint,
        params = {'video': videoS3Location}
        )
