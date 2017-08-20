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
        # Wait for response for 30 seconds before timing out
        browser.implicitly_wait(30)

        logger.info('Requesting [%s]', url)
        browser.get(url)

        if browser.page_source == RESPONSE_404:
            msg = 'Request came back with status code 404'
            logger.error(msg)
            raise BadResponseException(msg)

        logger.info('Request came back with status code 200, all is good')

        logger.info('Querying response with selector=[%s]', css_selector)
        html_value_ele = browser.find_element_by_css_selector(css_selector)

        raw_value = html_value_ele.text
        logger.info('Found value=[%s]', raw_value)

        # raw_value = '1 295,00 SEK'  # Testing Zara

        parsed_value = parser.parse(parse_type, raw_value)
        logger.info('Parsed value to=[%s]', parsed_value)

        return parsed_value

    except NoSuchElementException as e:
        logger.error(
            'The CSS selector did not find anything on the URL, '
            'selector=[%s] URL=[%s]',
            css_selector, url)
        raise e


class BadResponseException(Exception):
    pass
