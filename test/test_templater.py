#!/usr/bin/env python

import unittest

from src import templater


class TestCases(unittest.TestCase):
    def test_build_subject(self):
        assert templater._build_subject() is not None and \
               len(templater._build_subject()) > 1

    def test_build_row_product_unavailable(self):
        event = {'type': 'PRODUCT_UNAVAILABLE', 'url': 'arbitrary-url'}

        actual_row = templater._build_row(event)

        expected_row = '<p><a href="arbitrary-url">En bevakad produkt</a> ' \
                       'har tagits bort ur sortimentet eller flyttats och ' \
                       'lanken fungerar inte</p>'

        assert actual_row == expected_row

    def test_build_row_product_price_lower(self):
        event = {'type': 'PRICE_LOWER', 'url': 'arbitrary-url',
                 'new_price': '50', 'old_price': '100'}

        actual_row = templater._build_row(event)

        expected_row = '<p>Priset pa <a href="arbitrary-url">en bevakad ' \
                       'produkt</a> har <strong>sankts</strong> fran 100kr ' \
                       'till 50kr (med 50kr skillnad)</p>'

        assert actual_row == expected_row

    def test_build_row_product_price_higher(self):
        event = {'type': 'PRICE_HIGHER', 'url': 'arbitrary-url',
                 'new_price': '450', 'old_price': '100'}

        expected_row = templater._build_row(event)

        actual_row = '<p>Priset pa <a href="arbitrary-url">en bevakad ' \
                     'produkt</a> har <strong>hojts</strong> fran 100kr ' \
                     'till 450kr (med 350kr skillnad)</p>'

        assert expected_row == actual_row

    def test_build_row_product_unknown_event_type(self):
        event = {'type': 'NON_EXISTING_TYPE'}

        self.assertRaises(ValueError, templater._build_row, event)

    def test_build_with_single_event(self):
        events = [{'type': 'PRICE_HIGHER', 'url': 'arbitrary-url',
                   'new_price': '450', 'old_price': '100'}]

        actual_template = templater.build(events)

        expected_template = {'subject': 'En eller flera av dina bevakade '
                                        'produkter har uppdaterats',
                             'body': '<p>Priset pa <a href="arbitrary-url">'
                                     'en bevakad produkt</a> har <strong>'
                                     'hojts</strong> fran 100kr till 450kr '
                                     '(med 350kr skillnad)</p>'}

        assert actual_template == expected_template

    def test_build_with_multiple_event(self):
        events = [{'type': 'PRICE_HIGHER', 'url': 'arbitrary-url',
                   'new_price': '450', 'old_price': '100'},
                  {'type': 'PRICE_LOWER', 'url': 'arbitrary-url',
                   'new_price': '50', 'old_price': '100'}]

        actual_template = templater.build(events)

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

        assert actual_template == expected_template
