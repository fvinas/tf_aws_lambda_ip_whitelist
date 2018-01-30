# tf_aws_lambda_ip_whitelist 

## Module to provide a lambda-based mechanism to temporarily whitelist IP addresses in security groups ingress rules

This module will provision two lambda functions:
- `lambda_add_rule`, whose role is to add entries in a given security group
- `lambda_clean_rules`, whose role is to periodically clean expired entries in the security group

A common use case this two-fold lambda mechanism allows you to run is a "deny by default" SSH-access policy, where you temporarily register your origin IP address in the SG via a lambda function.

The end product allows you to set up a self-managed, temporary, IP whitelisting security policy via security groups and provide users with high-level commands to run from where (home, hotel, …) to grant a temporary network access to the infrastructure (can be SSH, HTTP or whatever port).

```shell
# Behind the scene, will retrieve my public IP address and authorize it for 1 day
./allow_ip bob
IP address now authorized! 😀
```

## Inputs

  * `region` - AWS region code (required)
  * `security_group_id` - The id of the security group the lambdas will add rules to or remove rules from (required)
  * `name` - Name to be used as a basename on all the resources identifiers (optional, defaults to `'TF_AWS_LAMBDA_IP_WHITELIST'`)
  * `expiry_duration` - The duration after which a rule will be considered expired (in minutes, optional, defaults to `'1440'`, 1 day)
  * `cleaning_rate` - The rate at which `lambda_clean_rules` will be launched. This is an AWS CloudWatch Events rate expression. (optional, defaults to `'cron(0 0/2 * * ? *)'` - every 2 hours)

## Outputs

  * `lambda_add_rule.arn`: ARN of the entry-point Lambda, so that you provide the rights accordingly to the users allowed to run it.

## Usage

### Shell script, client side

This is an example of script that you may set up and provide to your users for them to have a way to whitelist their current IP address.

It can be called, for instance, via:

```shell
./example.py Bob $(curl -s http://checkip.amazonaws.com/) 22 22
```

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# System
import sys
import json
import base64

# Third party
import boto3


# Customize to fit your needs
FUNCTION_NAME = '-ip-whitelisting-lambda-add-rule'
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

```

### Terraform code, infrastructure definition side

TODO: example code to add lambda invoke permissions

```hcl

resource "aws_security_group" "my_sg" {
    ...
}

module "ssh_whitelisting_mechanism" {
    security_group_id = '${aws_security_group.my_sg.id}'
    region         = 'us-east-1'
}
```

## Next steps

- displays a success message with the expiry timestamp when adding a rule
- remove error in case of duplicate entry (update)
- support for ipv6 rules
- support for egress rules
- support for ports and IPs ranges

## Authors

Originally created and maintained by [Fabien Vinas](https://github.com/fvinas)

## License

Apache 2 Licensed. See LICENSE for full details.
