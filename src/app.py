#!/usr/bin/env python

import yaml
import redis
import os

from selenium import webdriver


def run():
    products_obj = _get_file('src/products.yaml')
    products = products_obj.get('products')

    price_changes = map(lambda product: _handle_product(product), products)
    # Fetch the products from the config
    # For each product do:
    #   Fetch URL
    #   Parse HTML for price
    #   Get price of product from DB
    #   Compare if price has lowered
    #   If so, store that in memory
    # If lowered prices found, send email
    pass


def _handle_product(product):
    try:
        url = product.get('url')
        css_selector = product.get('price_selector')

        browser = webdriver.PhantomJS()
        # Wait for 30 seconds before throwing Exception
        browser.implicitly_wait(30)

        browser.get(url)

        result = browser.find_element_by_css_selector(css_selector)
        raw_price = result.text

        # raw_price = '1 295,00 SEK'

        # price = _format_price(product, raw_price)
        #
        # print "Raw price: " + str(raw_price)
        # print "Formatted price: " + str(price)
        #
        # r = redis.from_url(os.environ.get("REDIS_URL"))
        #
        # product_in_db = r.get('test')
        # product_in_db = r.get(url)
        #
        # if product_in_db is None:
        #     # set_result = r.set(url, {'price': price})
        #     set_result = r.set('test', {'price': price})
        #     print "Set set_result: " + str(set_result)

    except Exception as e:
        print "GOT EXCEPTION:"
        print e


def _format_price(product, raw_price):
    parse_options = {
        'zara': _zara_format,
    }

    return parse_options[product.get('parse_type')](raw_price)


def _clean_price(price):
    return price.strip().replace(' ', '').replace(',', '').replace('.', '')


def _strip_letters(input_str):
    # https://stackoverflow.com/questions/1450897/python-removing-characters-except-digits-from-string
    return input_str
    # from string import maketrans
    # from string import digits
    # table = maketrans('', '')
    # no_digits_table = table.translate(table, digits)
    # return input_str.translate(table, no_digits_table)


def _zara_format(unformatted_price):
    break_index = unformatted_price.index(',')
    unformatted_price = unformatted_price[0:break_index]
    return _strip_letters(_clean_price(unformatted_price))


def _get_file(path):
    with open(path, 'r') as _file:
        return yaml.load(_file)


if __name__ == '__main__':
    run()
