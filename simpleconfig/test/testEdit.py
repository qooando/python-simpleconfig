import dataclasses
import logging
import unittest
from simpleconfig import *
from dataclasses import dataclass
from typing import *

logging.basicConfig(level=logging.DEBUG)


class TestLoads(unittest.TestCase):

    def test_unexpected_error(self):
        @dataclass
        class MyConfig(Config):
            pass

        result = MyConfig()
        def setfun():
            result.foo = 5
        self.assertRaises(AttributeError, setfun)
        self.assertFalse(hasattr(result, "foo"))

    def test_unexpected_set(self):
        @allow_unknown_fields
        @dataclass
        class MyConfig(Config):
            pass

        result = MyConfig()
        result.foo = 5
        self.assertTrue(hasattr(result, "foo"))


if __name__ == '__main__':
    unittest.main()
