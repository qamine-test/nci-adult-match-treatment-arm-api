#!/usr/bin/env python3

import unittest
from ddt import ddt, data, unpack
from mock import patch


@ddt
class MyTestCase(unittest.TestCase):
    @data(

    )
    @unpack
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
