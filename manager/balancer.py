import boto3
import datetime
import sys
import logging
import time
from threading import Thread

cwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')

launch_template_name = 'ffmpeg_instance'
instance_api_endpoint = '/time_remaining'

logger = logging.getLogger('monitor')
logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)

formatstr = '[%(asctime)s - %(name)s - %(levelname)s]  %(message)s'
formatter = logging.Formatter(formatstr)

sh.setFormatter(formatter)
logger.addHandler(sh)


class Balancer(Thread):
    def run(self):
        while True:
            size = sum(1 for _ in ec2.instances.all() if _.state == 16)
            logger.info('Running %s instances.' % str(size))
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
                if instance.state == 16:
                    ip = instance.public_ip_address
                    if ip != '52.17.18.108' and ip != '52.16.139.42' and ip != '34.247.193.119':
                        cpu_load = response['Datapoints'][0]['Average']
                        load_unit = response['Datapoint'][0]['Unit']

                        logger.info('CPU metric for instance %s: %s %s' % (instance.id, cpu_load, load_unit))
                        if cpu_load <= 5:
                            ec2.stop_instances(InstanceIds=[instance.id], DryRun=False)
                            logger.info('Stopping instance %s for low load' % instance.id)
            time.sleep(5)
