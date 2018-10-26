#!/usr/bin/python3
from botocore.exceptions import ClientError

from listener import Listener
from balancer import Balancer
import sys
import os
import time
import logging
import boto3
ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
launch_template_name = 'ffmpeg_instance'

logger = logging.getLogger('manager')
logger.setLevel(logging.INFO)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.INFO)

formatstr = '[%(asctime)s - %(name)s - %(levelname)s]  %(message)s'
formatter = logging.Formatter(formatstr)

sh.setFormatter(formatter)
logger.addHandler(sh)


def launch_proxy():
    # launch proxy
    response = ec2.create_instances(
        LaunchTemplate={
            'LaunchTemplateName': launch_template_name,
            'Version': '$Default',
        },
        MaxCount=1,
        MinCount=1
    )
    instance = response[0]
    instance_id = instance.id
    try:
        while instance.state != 16:
            time.sleep(5)
            instance.load()
            logger.info('---------> status proxy ' + str(instance.state))

        response = ec2_client.associate_address(AllocationId='eipalloc-04c4e9298333c289e',
                                                InstanceId=instance_id)
        logger.info('Elastic IP associated with proxy instance. Response: ' + str(response))
    except ClientError as e:
        logger.error('An error occurred while associating Elastic IP to Proxy instance. Error: ' + str(e.response))


def ping_manager():
    # check if main manager still up
    response = os.system('ping -c 1 ' + ip_manager)
    if response == 0:
        logger.info('Main manager is still active.')
    else:
        logger.error('Main manager does not responde to PING.')
        logger.info('Waking up second manager.')
        global main_manager
        main_manager = True


def ping_proxy():
    # check if proxy still up
    response = os.system('ping -c 1 ' + ip_proxy)
    if response == 0:
        logger.info('Proxy server is still active.')
    else:
        logger.error('Proxy server does not responde to PING.')
        logger.info('Waking up proxy.')
        global proxy_up
        proxy_up = False


# main code execution
main_manager = (sys.argv[1] == 'True')
region_name = 'eu-west-1'
proxy_up = not main_manager
ip_manager = sys.argv[2]
ip_proxy = '52.17.18.108'

while True:
    if main_manager:
        logger.info("MAIN manager iniliazed. Creating Listener/Task Scheduler and Balancer.")
        queue_name = 'task_queue.fifo'
        listener = Listener(queue_name, region_name=region_name, max_number_of_messages=5)
        listener.start()
        balancer = Balancer()
        balancer.start()
        while True:
            if not proxy_up:
                launch_proxy()
            time.sleep(10)
            ping_proxy()
    else:
        ping_manager()
        time.sleep(10)
