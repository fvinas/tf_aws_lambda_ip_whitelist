# tf_aws_lambda_ip_whitelist 

## Lambda-based mechanism to temporarily whitelist IP addresses in security groups ingress rules

This Terraform module for AWS allows you to set up a self-managed, temporary, IP whitelisting security policy via security groups and to provide end users with high-level commands to run from where they are (home, hotel, …) to grant a temporary network access to the infrastructure (can be SSH, HTTPS or whatever port), meanwhile keeping the infrastructure secure (access through a whitelist the rest of the time) and automated (rules expiration and cleaning is automated).

```shell
# Behind the scene, retrieves my public IP address and authorize it for 1 day
./allow_ip bob
IP address now authorized! 😀
```

This module will provision two lambda functions:
- `lambda_add_rule`, whose role is to add entries in a given security group
- `lambda_clean_rules`, whose role is to periodically clean expired entries in the security group

A common use case this two-fold lambda mechanism allows you to run is a "deny by default" SSH or HTTPS access policy, where you temporarily register your origin IP address in the SG via a lambda function.

Feel free to fork and file a PR to fit it with your needs (UDP…)

## Inputs

  * `region` - AWS region code (required)
  * `security_group_id` - The id of the security group the lambdas will add rules to or remove rules from (required)
  * `port` - The TCP port(s) on which ingress traffic will be authorized (optional, defaults to `22`, SSH). Can be provided as a single port (e.g. `'22'`), as a list of ports (e.g. `'22;80;443'`) or as a port range (e.g. `'3000-4000'`).
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

```

### Terraform code, infrastructure definition side

TODO: example code to add lambda invoke permissions

```hcl

resource "aws_security_group" "my_sg" {
    ...
}

module "ssh_whitelisting_mechanism" {
    source            = "github.com/fvinas/tf_aws_lambda_ip_whitelist"
    security_group_id = "${aws_security_group.my_sg.id}"
    region            = "us-east-1"
}
```

## Next steps

- displays a success message with the expiry timestamp when adding a rule
- support for non IAM users
- integrate Lambda behind an API Gateway
- remove error in case of duplicate entry (update)
- support for ipv6 rules
- support for egress rules
- support for ranges of IPs
- support for UDP

## Authors

Originally created and maintained by [Fabien Vinas](https://github.com/fvinas)

## License

Apache 2 Licensed. See LICENSE for full details.
