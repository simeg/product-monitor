#!/usr/bin/env python

import os
import yaml

is_production = bool(os.environ.get('IS_PRODUCTION', failobj=False))


def products():
    return _get_file('src/products.yaml') if is_production \
        else _get_file('products.yaml')


def _get_file(path):
    with open(path, 'r') as _file:
        return yaml.load(_file)
