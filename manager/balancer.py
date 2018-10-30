from __future__ import division
import boto3
import datetime
import sys
import logging
import time
import csv
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
        with open('monitor.csv', 'a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            metrics = ['InstanceID', 'CPUUtilization', 'NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskWriteBytes']
            writer.writerow(metrics)
            csv_file.flush()
            while True:
                # Code status 16 = running / 0 = pending
                size = sum(1 for ins in ec2.instances.all() if ins.state.get('Code') == 16)
                logger.info('Running %s instances.' % str(size))
                instances_running = 0
                for instance in ec2.instances.all():
                    if instance.state.get('Code') == 16:
                        ip = instance.public_ip_address
                        if (ip != '52.17.18.108' and ip != '52.16.139.42' and ip != '34.247.193.119'
                                and instance.id != 'i-0499fe00dbf35e2ae' and instance.id != 'i-0832e3e1c8cea1435'):
                            instances_running += 1

                            cpu_load = self.cpu_metric(instance)
                            network_in = self.network_in(instance)
                            network_out = self.network_out(instance)
                            read_bytes = self.read_bytes(instance)
                            write_bytes = self.write_bytes(instance)

                            metrics = [instance.id, cpu_load, network_in, network_out, read_bytes, write_bytes]
                            writer.writerow(metrics)
                            csv_file.flush()

                            launch_time = instance.launch_time
                            now = datetime.datetime.now(timezone.utc)
                            difference = (now - launch_time).total_seconds()
                            logger.info('Total Time instance running (id: ' + str(instance.id) + ') - ' + str(difference))
                            if float(cpu_load) < 5.0 and int(instances_running) > 1 and int(difference) > 10*600:
                                ec2_client.stop_instances(InstanceIds=[instance.id], DryRun=False)
                                logger.info('Stopping instance %s for low load' % instance.id)

                time.sleep(5)

    def cpu_metric(self, instance):
        response = cwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            StartTime=(datetime.datetime.now() - datetime.timedelta(seconds=120)).isoformat(),
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
        if len(response['Datapoints']) != 0:
            i = 0
            date = response['Datapoints'][i]['Timestamp']
            metric = response['Datapoints'][i]['Average']
            metric_unit = response['Datapoints'][i]['Unit']
            for d in response['Datapoints']:
                if i != 0:
                    if date < d['Timestamp']:
                        metric = d['Average']
                        metric_unit = d['Unit']
                i += 1
            logger.info('CPU metric for instance %s: %s %s' % (instance.id, metric, metric_unit))
            return metric
        return 0

    def network_in(self, instance):
        response = cwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            StartTime=(datetime.datetime.now() - datetime.timedelta(seconds=120)).isoformat(),
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
        if len(response['Datapoints']) != 0:
            i = 0
            date = response['Datapoints'][i]['Timestamp']
            metric = response['Datapoints'][i]['Average']
            metric_unit = response['Datapoints'][i]['Unit']
            for d in response['Datapoints']:
                if i != 0:
                    if date < d['Timestamp']:
                        metric = d['Average']
                        metric_unit = d['Unit']
                i += 1
            logger.info('Networkin metric for instance %s: %s %s/second' % (instance.id, metric, metric_unit))
            return metric
        return 0

    def network_out(self, instance):
        response = cwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkOut',
            StartTime=(datetime.datetime.now() - datetime.timedelta(seconds=120)).isoformat(),
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
        if len(response['Datapoints']) != 0:
            i = 0
            date = response['Datapoints'][i]['Timestamp']
            metric = response['Datapoints'][i]['Average']
            metric_unit = response['Datapoints'][i]['Unit']
            for d in response['Datapoints']:
                if i != 0:
                    if date < d['Timestamp']:
                        metric = d['Average']
                        metric_unit = d['Unit']
                i += 1
            logger.info('NetworkOut metric for instance %s: %s %s/second' % (instance.id, metric, metric_unit))
            return metric
        return 0

    def write_bytes(self, instance):
        response = cwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='DiskWriteBytes',
            StartTime=(datetime.datetime.now() - datetime.timedelta(seconds=120)).isoformat(),
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
        if len(response['Datapoints']) != 0:
            i = 0
            date = response['Datapoints'][i]['Timestamp']
            metric = response['Datapoints'][i]['Average']
            metric_unit = response['Datapoints'][i]['Unit']
            for d in response['Datapoints']:
                if i != 0:
                    if date < d['Timestamp']:
                        metric = d['Average']
                        metric_unit = d['Unit']
                i += 1
            logger.info('DiskWriteBytes metric for instance %s: %s %s/second' % (instance.id, metric, metric_unit))
            return metric
        return 0

    def read_bytes(self, instance):
        response = cwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='DiskReadBytes',
            StartTime=(datetime.datetime.now() - datetime.timedelta(seconds=120)).isoformat(),
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
        if len(response['Datapoints']) != 0:
            i = 0
            date = response['Datapoints'][i]['Timestamp']
            metric = response['Datapoints'][i]['Average']
            metric_unit = response['Datapoints'][i]['Unit']
            for d in response['Datapoints']:
                if i != 0:
                    if date < d['Timestamp']:
                        metric = d['Average']
                        metric_unit = d['Unit']
                i += 1
            logger.info('DiskReadBytes metric for instance %s: %s %s/second' % (instance.id, metric, metric_unit))
            return metric
        return 0
