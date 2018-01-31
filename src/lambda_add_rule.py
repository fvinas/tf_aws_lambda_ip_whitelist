# -*- coding: utf-8 -*-

"""Lambda function that periodically cleans a security group from its expired entries.

AWS permissions required:
    ec2:DescribeSecurityGroups
    ec2:AuthorizeSecurityGroupIngress
    ec2:RevokeSecurityGroupIngress
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
    """Entry point for the lambda function."""
    # pylint: disable=locally-disabled, unused-argument, too-many-locals

    ec2 = boto3.resource('ec2', region_name=REGION)
    ec2_client = boto3.client('ec2', region_name=REGION)

    logger.debug('Event: {}'.format(event))

    user = event['user']
    ip_address = event['ip']

    logger.info('Received parameters:')
    logger.info(' - user = {}'.format(user))
    logger.info(' - ip_address = {}'.format(ip_address))

    # Prepare new rule
    rule_description = rule.build_rule_description(user, EXPIRY_DURATION)
    requested_cidr_range = '{ip}/32'.format(ip=ip_address)
    logger.info('Rule description is {}'.format(rule_description))

    ip_permission_template = {
        'IpProtocol': 'tcp',
        'IpRanges': [{
            'CidrIp': requested_cidr_range,
            'Description': rule_description
        }]
    }
    ip_permissions = rule.generate_ip_permissions(ip_permission_template, PORT)

    # Describe security group & ingress permissions
    security_group = ec2.SecurityGroup(SECURITY_GROUP_ID)
    ingress_permissions = security_group.ip_permissions

    # Search if the rule already exists
    # pylint: disable=locally-disabled, too-many-nested-blocks
    for ingress_permission in ingress_permissions:
        from_port = ingress_permission['FromPort']
        to_port = ingress_permission['ToPort']
        protocol = ingress_permission['IpProtocol']
        for ip_range in ingress_permission['IpRanges']:
            # Only rules with a description
            if 'Description' in ip_range:
                description = ip_range['Description']
                cidr_range = ip_range['CidrIp']
                # Preferably a description labeled by the module
                if rule.match_rule_description(description):
                    if cidr_range == requested_cidr_range:
                        # It's a rule with the same IP as the one requested, let's check ports
                        # Iterate through the prepared ip_permissions
                        for permission in ip_permissions:
                            if permission['FromPort'] == from_port and permission['ToPort'] == to_port:
                                # Same rule, delete it so that it's recreated
                                logger.info("Whitelisting rule already in place, removing it so that it's updated")
                                ec2_client.revoke_security_group_ingress(
                                    GroupId=SECURITY_GROUP_ID,
                                    FromPort=from_port,
                                    CidrIp=cidr_range,
                                    IpProtocol=protocol,
                                    ToPort=to_port
                                )

    logger.info('Authorizing SG ingress…')
    response = ec2_client.authorize_security_group_ingress(
        GroupId=SECURITY_GROUP_ID,
        IpPermissions=ip_permissions
    )

    assert 'ResponseMetadata' in response
    assert 'HTTPStatusCode' in response['ResponseMetadata']
    if response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        logger.info('Success! IP {ip} is now authorized on port {port} until {expiration} 😀'.format(
            ip=requested_cidr_range,
            port=PORT,
            expiration=rule_description.split('/')[2]
        ))
    else:
        logger.error('Did not receive a successful response from AWS EC2 API 🙁')
        logger.error(response)
