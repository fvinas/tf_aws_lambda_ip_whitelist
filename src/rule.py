# -*- coding: utf-8 -*-

"""A very simple file to centralize all methods related to SG rules descriptions."""

# System
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
