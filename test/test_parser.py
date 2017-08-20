#!/usr/bin/env python

import unittest

from src import parser


class TestCases(unittest.TestCase):
    def test_parsing(self):
        raw_price = '1 295,00 SEK'
        parse_type = 'zara'

        parsed_price = parser.parse(parse_type, raw_price)

        assert parsed_price == '1295'
