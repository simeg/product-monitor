#!/usr/bin/env python

import unittest

from src import db


class TestCases(unittest.TestCase):
    def test_hash_cache(self):
        assert len(db.hash_cache.keys()) == 0

        db._hash('arbitrary-same-value')
        assert len(db.hash_cache.keys()) == 1

        db._hash('arbitrary-same-value')
        assert len(db.hash_cache.keys()) == 1

        db._hash('new-value')
        assert len(db.hash_cache.keys()) == 2
