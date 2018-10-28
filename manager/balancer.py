import boto3
import datetime
import sys
import logging
import time
from datetime import timezone
from threading import Thread

cwatch = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

launch_template_name = 'ffmpeg_instance'
instance_api_endpoint = '/time_remaining'

logger = logging.getLogger('monitor')
logger.setLevel(logging.INFO)

sh = logging.FileHandler('balancer.log')
sh.setLevel(logging.INFO)

formatstr = '[%(asctime)s - %(name)s - %(levelname)s]  %(message)s'
formatter = logging.Formatter(formatstr)

sh.setFormatter(formatter)
logger.addHandler(sh)


class Balancer(Thread):
    def run(self):
        while True:
            # Code status 16 = running / 0 = pending
            size = sum(1 for ins in ec2.instances.all() if ins.state.get('Code') == 16)
            logger.info('Running %s instances.' % str(size))
            instances_running = 0
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
                if instance.state.get('Code') == 16:
                    ip = instance.public_ip_address
                    if ip != '52.17.18.108' and ip != '52.16.139.42' and ip != '34.247.193.119':
                        instances_running += 1
                        if len(response['Datapoints']) != 0:
                            cpu_load = response['Datapoints'][0]['Average']
                            load_unit = response['Datapoints'][0]['Unit']

                            logger.info('CPU metric for instance %s: %s %s' % (instance.id, cpu_load, load_unit))
                            launch_time = instance.launch_time
                            now = datetime.datetime.now(timezone.utc)
                            difference = (now - launch_time).total_seconds()
                            if cpu_load <= 5 and instances_running > 1 and difference > 10*3600:
                                ec2_client.stop_instances(InstanceIds=[instance.id], DryRun=False)
                                logger.info('Stopping instance %s for low load' % instance.id)
            time.sleep(5)
