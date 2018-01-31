#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System
import sys
import json
import base64
import requests

# Third party
import boto3

FUNCTION_NAME = 'TF_AWS_LAMBDA_IP_WHITELIST-ip-whitelisting-lambda-add-rule'
REGION = 'us-east-1'


def get_public_ip():
    """Helper to retrieve current public IP address."""
    AMAZON_CHECKIP_URL = 'http://checkip.amazonaws.com/'

    response = requests.get(AMAZON_CHECKIP_URL)
    response.raise_for_status()
    return response.content.strip()


def main():
    client = boto3.client('lambda', region_name=REGION)

    user = sys.argv[1]

    # Lambda invocation
    response = client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType='RequestResponse',
        LogType='Tail',
        Payload=json.dumps({
            'user': user,
            'ip': get_public_ip()
        })
    )
    if 'FunctionError' in response:
        print('Error while authorizing the IP address 🙁')
        print(base64.b64decode(response['LogResult']))
    else:
        print('IP address now authorized! 😀')
        print(base64.b64decode(response['LogResult']))


if __name__ == '__main__':
    main()
