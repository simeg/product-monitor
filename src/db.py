#!/usr/bin/env python

import logging
import redis

logger = logging.getLogger(__name__)


def connect(url):
    logger.info('Connecting to DB')
    db = redis.from_url(url)
    logger.info('DB connection established')
    return db


def query_product(db, url):
    logger.info('Querying DB for key=[%s]', url)
    result = db.get(url)

    if result is None:
        logger.info('Product was not found in DB')
    else:
        logger.info('Found product in DB=[%s]', str(result))

    return result


def insert_product(db, url, value):
    logger.info('Will try to insert value=[%s] with key=[%s]', value, url)
    query_result = db.set(url, {
        'value': value,
    })

    if query_result is True:
        logger.info('Successfully inserted value')
        # As this is the first time this URL is being used it
        # should not report of any changes, hence returning None
        return None

    else:
        logger.error('Failed inserting record')
        return None
