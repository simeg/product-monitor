#!/usr/bin/env python

import ast
import os
import logging

from src import \
    requester, \
    config_handler as cfgh, \
    db as dbh, \
    emailer, \
    templater

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run():
    logger.info('Started Product Monitor')

    products = cfgh.products()
    db_conn = dbh.connect(
        os.environ.get('REDIS_URL') if cfgh.is_production
        else _get_local_db_conn())

    price_changes = map(lambda product: _handle_product(product, db_conn),
                        products)

    price_changes = filter(lambda x: x is not None, price_changes)

    if not len(price_changes):
        logger.info('No price changes found, doing nothing')
        return

    logger.info('Found %s price changes', len(price_changes))
    logger.info(price_changes)

    # email_template = templater.format_for_email(price_changes)

    # _send_email(cfgh, email_template)


def _handle_product(_product, db_conn):
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

    db_product = dbh.query_url(db_conn, url)

    if db_product is None:
        logger.info('Product is new, storing it in DB')
        # If product does not exist in database it's new and shall be stored
        dbh.insert_product(db_conn, url, price)
        return None

    else:
        logger.info('Found product in DB=[%s]', db_product)
        # We have already stored this product before, it's not the first
        # time we're dealing with this product
        db_product = _str_to_dict(db_product)
        db_product_price = db_product.get('price')
        db_product_status_code = db_product.get('status_code')

        if int(price) < int(db_product_price):
            # MEW price is LOWER, return something indicating this
            return {
                'todo': 'todo'
            }

        if int(db_product_price) < int(price):
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


def _send_email(cfgh, email_template):
    password = cfgh.get('PASSWORD')
    username = cfgh.get('USERNAME')
    raw_recipients = cfgh.get('RECIPIENTS')
    recipients = raw_recipients.split(',')
    email_config = cfgh.default().get('email')

    emailer.send(
        password,
        username,
        email_config.get('sender_alias'),
        recipients,
        email_config.get('subject'),
        email_template)


def _get_local_db_conn():
    config = cfgh.default().get('redis')
    return 'redis://%s:%s' % (config.get('host'), config.get('port'))


def _str_to_dict(input_str):
    return ast.literal_eval(input_str)


if __name__ == '__main__':
    run()
