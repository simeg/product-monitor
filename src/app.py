#!/usr/bin/env python

import ast
import yaml
import os
import logging
import redis
import config_handler as cfgh

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RESPONSE_404 = '<html><head></head><body></body></html>'


def run():
    logger.info('Started Product Monitor')

    products_obj = cfgh.products()
    products = products_obj.get('products')

    price_changes = map(lambda product: _handle_product(product), products)
    logger.info('Got all price changes')

    if len(price_changes):
        # We should notify user about changes
        pass

    # Fetch the products from the config - DONE
    # For each product do:
    #   Fetch URL DONE FOR COUNT=1
    #   Parse HTML for price DONE FOR COUNT=1
    #   Get price of product from DB DONE FOR COUNT=1
    #   Compare if price has lowered
    #   If so, store that in memory
    # If lowered prices found, send email
    pass


def _handle_product(product):
    try:
        # TODO: URL encode this url to make debugging easier
        url = product.get('url', None)
        css_selector = product.get('price_selector', None)
        parse_type = product.get('parse_type', None)

        if url is None or css_selector is None or parse_type is None:
            logger.error(
                "Product configuration is broken, URL=[%s] selector=[%s] "
                "parse type=[%s]",
                url, css_selector, parse_type)
            return None

        browser = webdriver.PhantomJS()
        # Wait for 30 seconds before throwing Exception
        browser.implicitly_wait(30)

        logger.info('Requesting [%s]', url)
        browser.get(url)
        logger.info('Request done')

        if browser.page_source == RESPONSE_404:
            return {
                'todo': 'todo'
            }

        logger.info('Querying response with selector=[%s]', css_selector)
        result = browser.find_element_by_css_selector(css_selector)

        raw_price = result.text
        # raw_price = '1 295,00 SEK'
        price = _format_price(parse_type, raw_price)

        # Does not work locally at the moment
        db_handler = redis.from_url(os.environ.get("REDIS_URL"))
        db_product = db_handler.get(url)

        if db_product is None:
            try:
                logger.info(
                    "Inserting new value for url=[%s]",
                    url)
                query_result = db_handler.set(url, {
                    'price': price,
                    'status_code': 200,
                })

                if query_result is True:
                    logger.info(
                        "Successfully inserted record for URL=[%s]",
                        url)
                    # As this is the first time this URL is being used it
                    # should not report of any changes, hence returning None
                    return None
                else:
                    logger.error(
                        "Failed inserted record for URL=[%s]",
                        url)
                    return None

            except Exception as e:
                logger.exception(
                    'Got unexpected exception of type=[%s]',
                    str(type(e)))
                return None

        else:
            # We have already stored this product before, it's not the first
            # time we're dealing with this product
            product = _str_to_dict(db_product)
            product_price = product.get('price')
            product_status_code = product.get('status_code')

            if int(price) < int(product_price):
                # MEW price is LOWER, return something indicating this
                return {
                    'todo': 'todo'
                }

            if int(product_price) < int(price):
                # NEW price is HIGHER, return something indicating this
                return {
                    'todo': 'todo'
                }

            # Not sure if we need to store status_code, can't think of a valid
            # use-case where you'd want to know if status went from 200 -> 404
            # or the other way around. Not sure what I was thinking.
            #
            # If response is not 200 it should be handled on line 53
            return None

    except NoSuchElementException:
        # If the CSS selector returned nothing
        logger.warn('The CSS selector did not find anything on the URL, '
                    'selector=[%s] URL=[%s]',
                    css_selector, url)
        return None
    except Exception as e:
        logger.exception('Got unexpected exception of type=[%s]',
                         str(type(e)))


def _str_to_dict(input_str):
    return ast.literal_eval(input_str)


def _format_price(parse_type, raw_price):
    parse_options = {
        'zara': _zara_format,
    }

    return parse_options[parse_type](raw_price)


def _zara_format(unformatted_price):
    break_index = unformatted_price.index(',')
    unformatted_price = unformatted_price[0:break_index]
    return unformatted_price.strip().replace(' ', '')


def _get_file(path):
    with open(path, 'r') as _file:
        return yaml.load(_file)


if __name__ == '__main__':
    run()
