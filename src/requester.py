#!/usr/bin/env python

import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from src import parser

logger = logging.getLogger(__name__)
RESPONSE_404 = '<html><head></head><body></body></html>'


def get_element_value(url, css_selector, parse_type):
    try:
        browser = webdriver.PhantomJS()
        # Wait for response for 30 seconds before throwing Exception
        browser.implicitly_wait(30)

        logger.info('Requesting [%s]', url)
        browser.get(url)
        logger.info('Request finished')

        if browser.page_source == RESPONSE_404:
            msg = 'The request returned 404'
            logger.error(msg)
            raise BadResponseException(msg)

        logger.info('Querying response with selector=[%s]', css_selector)
        html_price_ele = browser.find_element_by_css_selector(css_selector)

        raw_price = html_price_ele.text
        logger.info('Found price=[%s]', raw_price)

        # raw_price = '1 295,00 SEK'  # Testing Zara

        price = parser.parse(parse_type, raw_price)
        logger.info('Formatted price to=[%s]', price)

        return price

    except NoSuchElementException as e:
        logger.error(
            'The CSS selector did not find anything on the URL, '
            'selector=[%s] URL=[%s]',
            css_selector, url)
        raise e


class BadResponseException(Exception):
    pass
