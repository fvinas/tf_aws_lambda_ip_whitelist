#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System
import sys
import json
import base64

# Third party
import boto3


FUNCTION_NAME = 'TF_AWS_LAMBDA_IP_WHITELIST-ip-whitelisting-lambda-add-rule'
REGION = 'us-east-1'


def main():
    client = boto3.client('lambda', region_name=REGION)

    # Checks
    user = sys.argv[1]
    ip_address = sys.argv[2]
    from_port = sys.argv[3]
    to_port = sys.argv[4]

    # Lambda invocation
    response = client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType='RequestResponse',
        LogType='Tail',
        Payload=json.dumps({
            'user': user,
            'ip': ip_address,
            'from_port': from_port,
            'to_port': to_port
        })
    )
    if 'FunctionError' in response:
        print('Error while authorizing the IP address 🙁')
        print(base64.b64decode(response['LogResult']))
    else:
        print('IP address now authorized! 😀')


if __name__ == '__main__':
    main()
