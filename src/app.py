#!/usr/bin/env python

import ast
import os
import logging
from selenium.common.exceptions import NoSuchElementException

from src.requester import BadResponseException
from src import \
    requester, \
    config_handler as cfgh, \
    db as db_handler, \
    emailer, \
    templater

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run():
    logger.info('Started Product Monitor')

    products = cfgh.products()
    db_conn = db_handler.connect(
        os.environ.get('REDIS_URL') if cfgh.is_production
        else _get_local_db_conn())

    price_changes = map(lambda product: _handle_product(product, db_conn),
                        products)

    price_changes = filter(lambda x: x is not None, price_changes)

    if not len(price_changes):
        logger.info('No price changes found, doing nothing')
        return

    logger.info('Found [%s] price changes', len(price_changes))
    logger.info(price_changes)  # TODO: Remove when done

    email_template = templater.format_for_email(price_changes)

    _send_email(cfgh, email_template)


def _handle_product(_product, db_conn):
    try:
        # TODO: URL encode this url to make debugging easier
        url = _product.get('url', None)
        css_selector = _product.get('price_selector', None)
        parse_type = _product.get('parse_type', None)

        if None in [url, css_selector, parse_type]:
            logger.error(
                'Product configuration is broken, URL=[%s] selector=[%s] '
                'parse type=[%s]',
                url, css_selector, parse_type)
            return None

        price = requester.get_price(url, css_selector, parse_type)

        stored_product = db_handler.query_url(db_conn, url)

        if stored_product is None:
            logger.info('Product is new, storing it in DB')
            db_handler.insert_product(db_conn, url, price)
            return None

        else:
            logger.info('Found product in DB=[%s]', stored_product)
            stored_product = _str_to_dict(stored_product)
            stored_price = stored_product.get('price')

            price = int(price)
            stored_price = int(stored_price)

            if price == stored_price:
                return None

            if price < stored_price:
                return {
                    'type': 'PRICE_LOWER',
                    'url': url,
                    'old_price': stored_price,
                    'new_price': price,
                }

            if price > stored_price:
                return {
                    'type': 'PRICE_HIGHER',
                    'url': url,
                    'old_price': stored_price,
                    'new_price': price,
                }

    except NoSuchElementException or BadResponseException:
        return {
            'type': 'PRODUCT_UNAVAILABLE',
            'url': url,
        }


def _send_email(config, email_template):
    password = config.get('PASSWORD')
    username = config.get('USERNAME')
    raw_recipients = config.get('RECIPIENTS')
    recipients = raw_recipients.split(',')

    emailer.send(
        password,
        username,
        config.default().get('email').get('sender_alias'),
        recipients,
        email_template.subject,
        email_template.body,
        cfgh.is_production)


def _get_local_db_conn():
    config = cfgh.default().get('redis')
    return 'redis://%s:%s' % (config.get('host'), config.get('port'))


def _str_to_dict(input_str):
    return ast.literal_eval(input_str)


if __name__ == '__main__':
    run()
