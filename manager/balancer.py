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
            logger.info('Running %s instances.' % str(len(ec2.instances.all())))
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

                logger.info('CPU metric for instance %s: %s' % (instance.id, cpu_load))
                if cpu_load <= 5:
                    ec2.stop_instances(InstanceIds=[instance.id], DryRun=False)
                    logger.info('Stopping instance %s for low load' % instance.id)
                time.sleep(5)
