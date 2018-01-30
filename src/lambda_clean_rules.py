# -*- coding: utf-8 -*-

"""Lambda function that periodically cleans a security group from its expired entries.

AWS permissions required:
    ec2:DescribeSecurityGroups
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
REGION = os.environ['REGION']

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    ec2 = boto3.resource('ec2', region_name=REGION)
    ec2_client = boto3.client('ec2', region_name=REGION)

    # Describe security group & ingress permissions
    security_group = ec2.SecurityGroup(SECURITY_GROUP_ID)
    ingress_permissions = security_group.ip_permissions

    # Iterating through all the rules, only keeping those with a matching description
    nb_rules = 0
    nb_expired = 0
    for p in ingress_permissions:
        from_port = p['FromPort']
        to_port = p['ToPort']
        protocol = p['IpProtocol']

        for r in p['IpRanges']:
            # Only rules with a description
            if 'Description' in r:
                description = r['Description']
                ip_range = r['CidrIp']
                # Preferably a description labeled by the module
                if rule.match_rule_description(description):
                    nb_rules += 1
                    rule_user, rule_timestamp = rule.parse_rule_description(description)
                    logger.info('Examining rule {}'.format(description))
                    if rule.is_rule_expired(rule_timestamp):
                        logger.info('Rule is expired: removing it.')
                        # Rule is expired, remove it
                        ec2_client.revoke_security_group_ingress(
                            GroupId=SECURITY_GROUP_ID,
                            FromPort=from_port,
                            CidrIp=ip_range,
                            IpProtocol=protocol,
                            ToPort=to_port
                        )
                        nb_expired += 1
                        logger.info('Rule was removed')
                    else:
                        # Rule is not expired, keep it
                        logger.info('Rule is not expired, keeping it.')
                        pass

    logger.info('{nb} rules were examined, thereof {nb_expired} were expired and removed'.format(
        nb=nb_rules,
        nb_expired=nb_expired
    ))
