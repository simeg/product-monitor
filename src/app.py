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

    events = map(lambda product: _handle_product(product, db_conn),
                 products)

    events = filter(lambda x: x is not None, events)

    if not len(events):
        logger.info('No events found, doing nothing')
        return

    logger.info('Found [%s] events', len(events))
    logger.info(str(events))

    logger.info('Start building e-mail template')
    email_template = templater.build(events)
    logger.info('Finished building e-mail template')
    _send_email(cfgh, email_template)

    logger.info('Product Monitor execution finished')


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

        new_value = \
            requester.get_element_value(url, css_selector, parse_type)

        stored_product = db_handler.query_product(db_conn, url)

        if stored_product is None:
            logger.info('Product is new, storing it in DB')
            db_handler.insert_product(db_conn, url, new_value)
            return None

        else:
            logger.info('Will examine if product value has changed')

            stored_product = _str_to_dict(stored_product)
            product_type = _product.get('type')

            # TODO: Extract to function
            if product_type == 'price_change':
                old_price = stored_product.get('value')

                new_value = int(new_value)
                old_price = int(old_price)

                if new_value == old_price:
                    logger.info('Nothing has changed, value is the same')
                    return None

                if new_value < old_price:
                    return {
                        'type': 'PRICE_LOWER',
                        'url': url,
                        'old_price': old_price,
                        'new_price': new_value,
                    }

                if new_value > old_price:
                    return {
                        'type': 'PRICE_HIGHER',
                        'url': url,
                        'old_price': old_price,
                        'new_price': new_value,
                    }

            elif product_type == 'stock_change':
                old_stock_status = stored_product.get('value')

                if new_value == old_stock_status:
                    logger.info('Nothing has changed, value is the same')
                    return None

                return {
                    'type': 'STOCK_CHANGE',
                    'url': url,
                    'old_price': old_stock_status,  # TODO: Use term value
                    'new_price': new_value,         # instead of price in key
                }

            raise KeyError('Invalid type for product=[%s]' % product_type)

    except NoSuchElementException or BadResponseException:
        logger.error('Product or value is not available')
        # TODO: Store occurrence in DB, if it happens n times in a row an
        # e-mail should be sent notifying the user
        return None


def _send_email(config, email_template):
    username = config.get('EMAIL_USERNAME')
    password = config.get('EMAIL_PASSWORD')
    raw_recipients = config.get('EMAIL_RECIPIENTS')
    recipients = raw_recipients.split(',')

    emailer.send(
        password,
        username,
        config.default().get('email').get('sender_alias'),
        recipients,
        email_template.get('subject'),
        email_template.get('body'),
        cfgh.is_production)


def _get_local_db_conn():
    config = cfgh.default().get('redis')
    return 'redis://%s:%s' % (config.get('host'), config.get('port'))


def _str_to_dict(input_str):
    return ast.literal_eval(input_str)


if __name__ == '__main__':
    run()
