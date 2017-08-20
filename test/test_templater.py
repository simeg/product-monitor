#!/usr/bin/env python

import unittest

from src import templater


class TestCases(unittest.TestCase):
    def test_build_subject(self):
        assert templater._build_subject() is not None and \
               len(templater._build_subject()) > 1

    def test_build_event_row_product_unavailable(self):
        event = {'type': 'PRODUCT_UNAVAILABLE', 'url': 'arbitrary-url'}

        row = templater._build_event_row(event)

        assert row == '<p><a href="arbitrary-url">En bevakad produkt</a> ' \
                      'har tagits bort ur sortimentet eller flyttats och ' \
                      'lanken fungerar inte</p>'

    def test_build_event_row_product_price_lower(self):
        event = {'type': 'PRICE_LOWER', 'url': 'arbitrary-url',
                 'new_price': '50', 'old_price': '100'}

        row = templater._build_event_row(event)

        assert row == '<p>Priset pa <a href="arbitrary-url">en bevakad ' \
                      'produkt</a> har <strong>sankts</strong> fran 100kr ' \
                      'till 50kr (med 50kr skillnad)</p>'

    def test_build_event_row_product_price_higher(self):
        event = {'type': 'PRICE_HIGHER', 'url': 'arbitrary-url',
                 'new_price': '450', 'old_price': '100'}

        row = templater._build_event_row(event)

        assert row == '<p>Priset pa <a href="arbitrary-url">en bevakad ' \
                      'produkt</a> har <strong>hojts</strong> fran 100kr ' \
                      'till 450kr (med 350kr skillnad)</p>'

    def test_build_event_row_product_unknown_event_type(self):
        event = {'type': 'NON_EXISTING_TYPE'}

        self.assertRaises(ValueError, templater._build_event_row, event)

    def test_build_with_single_event(self):
        events = [{'type': 'PRICE_HIGHER', 'url': 'arbitrary-url',
                   'new_price': '450', 'old_price': '100'}]

        template = templater.build(events)

        expected_template = {'subject': 'En eller flera av dina bevakade '
                                        'produkter har uppdaterats',
                             'body': '<p>Priset pa <a href="arbitrary-url">'
                                     'en bevakad produkt</a> har <strong>'
                                     'hojts</strong> fran 100kr till 450kr '
                                     '(med 350kr skillnad)</p>'}

        assert template == expected_template

    def test_build_with_multiple_event(self):
        events = [{'type': 'PRICE_HIGHER', 'url': 'arbitrary-url',
                   'new_price': '450', 'old_price': '100'},
                  {'type': 'PRICE_LOWER', 'url': 'arbitrary-url',
                   'new_price': '50', 'old_price': '100'}]

        template = templater.build(events)

        expected_template = {'subject': 'En eller flera av dina bevakade '
                                        'produkter har uppdaterats',
                             'body': '<p>Priset pa <a href="arbitrary-url">'
                                     'en bevakad produkt</a> har <strong>'
                                     'hojts</strong> fran 100kr till 450kr '
                                     '(med 350kr skillnad)</p>\n'
                                     '<p>Priset pa <a href="arbitrary-url">'
                                     'en bevakad produkt</a> har <strong>'
                                     'sankts</strong> fran 100kr '
                                     'till 50kr (med 50kr skillnad)</p>'}

        assert template == expected_template
