#!/usr/bin/env python

import yagmail
import logging

logger = logging.getLogger(__name__)


def send(password, username, sender_alias, recipients, subject, content,
         is_production):
    if is_production:
        logger.info('Will send e-mail to %s', str(recipients))
        yag = yagmail.SMTP({username: sender_alias}, password)
        send_result = yag.send(recipients, subject, content)

        # False means it did not send, everything else is OK
        if send_result is False:
            logger.info('Was unable to send email, not sure why')
        else:
            logger.info('Email successfully sent')
    else:
        logger.info('[noop] Will send e-mail to %s', str(recipients))
