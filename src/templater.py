#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# TODO: Clean up this .format() and %s mess and figure out
# why åäö are causing exceptions to be thrown


def build(events):
    subject = _build_subject()
    body = map(lambda event: _build_row(event), events)

    # Make list into string and separate elements with '\n'
    body = '\n'.join(body)

    return {
        'subject': subject,
        'body': body,
    }


def _build_subject():
    # TODO: Pass in events and decide on singular/plural
    return 'En eller flera av dina bevakade produkter har ' \
           'uppdaterats'.encode('utf-8')


def _build_row(event):
    event_type = event.get('type')

    if event_type == 'PRODUCT_UNAVAILABLE':
        row = _format_unavailable_product_row(event)

    elif event_type == 'PRICE_LOWER' or event_type == 'PRICE_HIGHER':
        row = _format_price_row(event)

    elif event_type == 'STOCK_CHANGE':
        row = _format_stock_change_row(event)

    else:
        raise ValueError('Unknown event type=[%s]' % event_type)

    return ('<p>%s</p>' % row).encode('utf-8')


def _format_unavailable_product_row(event):
    return ('<a href="%s">En bevakad produkt</a> har tagits bort ur '
            'sortimentet eller flyttats och lanken fungerar inte' %
            event.get('url')).encode('utf-8')


def _format_price_row(event):
    event_type = event.get('type')

    price_is_higher = event_type == 'PRICE_HIGHER'
    diff_type = 'hojts' if price_is_higher else 'sankts'
    price_diff = abs(int(event.get('old_price')) - int(event.get('new_price')))

    return (('Priset pa <a href="{}">en bevakad produkt</a> har '
             '<strong>{}</strong> fran {}kr till {}kr '
             '(med {}kr skillnad)').encode('utf-8').format(
        event.get('url'),
        diff_type,
        event.get('old_price'),
        event.get('new_price'),
        price_diff)
    ).encode('utf-8')


def _format_stock_change_row(event):
    return (('<a href="{}">En bevakad produkt</a> har andrat lagerstatus '
             'fran <strong>{}</strong> till '
             '<strong>{}</strong>').encode('utf-8').format(
        event.get('url'),
        event.get('old_price'),
        event.get('new_price'))
    ).encode('utf-8')
