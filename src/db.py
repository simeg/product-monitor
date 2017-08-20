#!/usr/bin/env python

import logging
import redis

logger = logging.getLogger(__name__)
hash_cache = {}


def connect(url):
    logger.info('Connecting to DB')
    db = redis.from_url(url)
    logger.info('DB connection established')
    return db


def query_product(db, url):
    key = _hash(url)
    logger.info('Querying DB for key=[%s]', key)
    result = db.get(key)

    if result is None:
        logger.info('Product was not found in DB')
    else:
        logger.info('Found product in DB=[%s]', str(result))

    return result


def insert_product(db, url, value):
    key = _hash(url)
    logger.info('Will try to insert value=[%s] with key=[%s]', value, key)
    query_result = db.set(key, {
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


def _hash(value):
    if value in hash_cache:
        return hash_cache.get(value)
    else:
        hashed_value = hash(value)
        hash_cache[value] = hashed_value
        return hashed_value
