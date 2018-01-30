# -*- coding: utf-8 -*-

"""Lambda function that periodically cleans a security group from its expired entries.

AWS permissions required:
    ec2:AuthorizeSecurityGroupIngress
"""

# System
import os
import logging

# Third party
import boto3

# Module
import rule


SECURITY_GROUP_ID = os.environ['SECURITY_GROUP_ID']
EXPIRY_DURATION = int(os.environ['EXPIRY_DURATION'])
REGION = os.environ['REGION']
PORT = os.environ['PORT']

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    ec2_client = boto3.client('ec2', region_name=REGION)

    logger.debug('Event: {}'.format(event))

    user = event['user']
    ip_address = event['ip']

    logger.info('Received parameters:')
    logger.info(' - user = {}'.format(user))
    logger.info(' - ip_address = {}'.format(ip_address))

    rule_description = rule.build_rule_description(user, EXPIRY_DURATION)

    logger.info('Rule description is {}'.format(rule_description))

    cidr_ip = '{ip}/32'.format(ip=ip_address)

    logger.info('Authorizing SG ingress…')

    ip_permission_template = {
        'IpProtocol': 'tcp',
        'IpRanges': [{
            'CidrIp': cidr_ip,
            'Description': rule_description
        }]
    }
    ip_permissions = rule.generate_ip_permissions(ip_permission_template, PORT)

    response = ec2_client.authorize_security_group_ingress(
        GroupId=SECURITY_GROUP_ID,
        IpPermissions=ip_permissions
    )

    assert('ResponseMetadata' in response)
    assert('HTTPStatusCode' in response['ResponseMetadata'])
    if response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info('Successul response from AWS EC2 API 😀')
    else:
        logger.error('Did not receive a successful response from AWS EC2 API 🙁')
        logger.error(response)
