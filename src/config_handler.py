#!/usr/bin/env python

import os
import yaml

is_production = bool(os.environ.get('IS_PRODUCTION', failobj=False))


def get(key):
    return os.environ.get(key) if is_production \
        else _private_config().get(key)


def default():
    return _get('config')


def products():
    return _get('products')


def _get(file):
    return _get_file('src/config/%s.yaml' % file) if is_production \
        else _get_file('config/%s.yaml' % file)


def _private_config():
    return _get('private_config')


def _get_file(path):
    with open(path, 'r') as _file:
        return yaml.load(_file)
