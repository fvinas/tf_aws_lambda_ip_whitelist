# -*- coding: utf-8 -*-

"""A very simple file to centralize all methods related to SG rules descriptions."""

# System
import re
import copy
from datetime import datetime, timedelta


RULE_PREFIX = 'TEMPORARY_WHITELIST'
TIMESTAMP_FORMAT = '%Y-%m-%d-%H.%M.%S'


def build_rule_description(user, expiry_duration):
    """Creates a rule description from a user and an expiry duration."""

    expires = datetime.now() + timedelta(minutes=expiry_duration)
    return '{prefix}/{user}/{expires}'.format(
        prefix=RULE_PREFIX,
        user=user.replace('/', ''),
        expires=expires.strftime(TIMESTAMP_FORMAT)
    )


def match_rule_description(rule_description):
    """Returns True if the rule description matches the expected format, False otherwise."""

    return rule_description.startswith('{prefix}/'.format(prefix=RULE_PREFIX))


def parse_rule_description(rule_description):
    """Extracts user and timestamp from a rule description."""

    parts = rule_description.split('/')
    user = parts[1]
    timestamp = datetime.strptime(parts[2], TIMESTAMP_FORMAT)
    return user, timestamp


def is_rule_expired(rule_timestamp):
    """Returns True if the rule timestamp is expired."""

    return rule_timestamp < datetime.now()


def generate_ip_permissions(ip_permission_template, port_rule):
    """Helper to generate AWS SG IP permissions based on the port rule."""
    port_rule = port_rule.strip()

    if re.match(r'^(\d+)$', port_rule):
        # If port_rule is only a number
        ip_permission_templates = copy.deepcopy(ip_permission_template)
        ip_permission_templates['FromPort'] = int(port_rule)
        ip_permission_templates['ToPort'] = int(port_rule)
        return [ip_permission_templates]

    elif ';' in port_rule:
        # Sequence of ports
        parts = port_rule.split(';')
        permissions = []
        for p in parts:
            permissions.append(generate_ip_permissions(ip_permission_template, p)[0])
        return permissions

    elif '-' in port_rule:
        # Port range
        parts = port_rule.split('-')
        ip_permission_templates = copy.deepcopy(ip_permission_template)
        ip_permission_templates['FromPort'] = int(parts[0])
        ip_permission_templates['ToPort'] = int(parts[1])
        return ip_permission_templates
