#!/usr/bin/env python


def parse(parse_type, raw_price):
    parse_options = {
        'zara': _zara_format,
    }

    if parse_type not in parse_options:
        raise KeyError('Missing parse option=[{}]'.format(parse_type))

    return parse_options[parse_type](raw_price)


def _zara_format(price):
    break_index = price.index(',')  # Remove tailing 'SEK'
    price = price[0:break_index]
    return price.strip().replace(' ', '')
