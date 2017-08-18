#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# TODO: Clean up this .format() and %s mess and figure out
# why åäö are causing exceptions to be thrown


def build(events):
    subject = _build_subject()
    body = map(lambda event: _build_event_row(event), events)

    return {
        'subject': subject,
        'body': body,
    }


def _build_subject():
    return 'En eller flera av dina bevakade produkter har ' \
           'uppdaterats'.encode('utf-8')


def _build_event_row(event):
    event_type = event.get('type')

    if event_type is 'PRODUCT_UNAVAILABLE':
        row = ('<a href="%s">En bevakad produkt</a> har tagits bort ur '
               'sortimentet eller flyttats och lanken fungerar inte' %
               event.get('url')).encode('utf-8')

    elif event_type is 'PRICE_LOWER' or event_type is 'PRICE_HIGHER':
        row = _format_monitored_product(event)

    else:
        raise ValueError('Unknown event type=[%s]', event_type)

    return ('<p>%s</p>' % row).encode('utf-8')


def _format_monitored_product(event):
    event_type = event.get('type')
    price_is_higher = event_type is 'PRICE_HIGHER'
    diff_type = 'hojts' if price_is_higher else 'sankts'

    return (('Priset pa <a href="{}">en bevakad produkt</a> har '
             '<strong>{}</strong> fran {}kr till {}kr (med {}kr skillnad)')
        .encode('utf-8')
        .format(
        event.get('url'),
        diff_type,
        event.get('new_price') if price_is_higher else event.get('old_price'),
        event.get('old_price') if price_is_higher else event.get('new_price'),
        abs(int(event.get('old_price')) - int(event.get('new_price'))))
    ).encode('utf-8')
