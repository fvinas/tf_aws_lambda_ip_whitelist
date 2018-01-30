#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System
import sys
import json
import base64

# Third party
import boto3


FUNCTION_NAME = 'PROD-UAT-DataProduction-ip-whitelisting-lambda-add-rule'
REGION = 'eu-central-1'


def main():
    client = boto3.client('lambda', region_name=REGION)

    # Checks
    user = sys.argv[1]
    ip_address = sys.argv[2]

    # Lambda invocation
    response = client.invoke(
        FunctionName=FUNCTION_NAME,
        InvocationType='RequestResponse',
        LogType='Tail',
        Payload=json.dumps({
            'user': user,
            'ip': ip_address
        })
    )
    if 'FunctionError' in response:
        print('Error while authorizing the IP address 🙁')
        print(base64.b64decode(response['LogResult']))
    else:
        print('IP address now authorized! 😀')


if __name__ == '__main__':
    main()
