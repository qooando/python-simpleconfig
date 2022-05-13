import dataclasses
import logging
import unittest
from simpleconfig import *
from dataclasses import dataclass
from typing import *

logging.basicConfig(level=logging.DEBUG)


class TestSimpleConfig(unittest.TestCase):

    def test_unexpected_ignore(self):
        @dataclass
        class MyConfig:
            pass

        source = {
            "foo": 10
        }
        result = loads(source, Config=MyConfig)
        self.assertFalse(hasattr(result, "foo"))

    def test_unexpected_set(self):
        @allow_unknown_fields
        @dataclass
        class MyConfig:
            pass

        source = {
            "foo": 10
        }
        result = loads(source, Config=MyConfig)
        self.assertTrue(hasattr(result, "foo"))

    def test_type_mismatch_error(self):
        @dataclass
        class MyConfig:
            foo: str = None

        source = {
            "foo": 10
        }

        self.assertRaises(TypeError, lambda: loads(source, Config=MyConfig))

    def test_type_mismatch_ignore(self):
        @allow_type_mismatch_fields
        @dataclass
        class MyConfig:
            foo: str = None

        source = {
            "foo": 10
        }

        result = loads(source, Config=MyConfig)
        self.assertTrue(hasattr(result, "foo"))
        self.assertEqual(10, result.foo)

    def test_loads(self):
        @dataclass
        class MyConfig:
            a: str = None
            b: int = None

        source = {
            "a": "hello",
            "b": 10
        }

        result = loads(source, Config=MyConfig)
        self.assertEqual("hello", result.a)
        self.assertEqual(10, result.b)

    def test_loads_list(self):
        @dataclass
        class MyConfig:
            foo: List[str] = None

        source = {
            "foo": ["a", "b", "c"]
        }

        result = loads(source, Config=MyConfig)
        self.assertEqual(source["foo"], result.foo)

    def test_type_mismatch_list(self):
        @dataclass
        class MyConfig:
            foo: List[str] = None

        source = {
            "foo": [1, 2, 3, 4]
        }

        self.assertRaises(TypeError, lambda: loads(source, Config=MyConfig))

    def test_loads_dict(self):
        @dataclass
        class MyConfig:
            foo: Dict[str, int] = None

        source = {
            "foo": {
                "a": 1,
                "b": 2
            }
        }

        result = loads(source, Config=MyConfig)
        self.assertEqual(source["foo"], result.foo)

    def test_type_mismatch_dict(self):
        @dataclass
        class MyConfig:
            foo: Dict[str, str] = None

        source = {
            "foo": {
                "a": 1,
                "b": 2
            }
        }

        self.assertRaises(TypeError, lambda: loads(source, Config=MyConfig))

    def test_load_subclasses(self):
        @dataclass
        class MyConfig:
            @dataclass
            class MyInnerConfig:
                d: str
                e: str = None
            a: str = None
            b: int = None
            c: MyInnerConfig = dataclasses.field(default_factory=lambda: MyConfig.MyInnerConfig("hello"))

        source = {
            "a": "hello",
            "b": 10,
            "c": {
                "e": "world"
            }
        }

        result = loads(source, Config=MyConfig)
        self.assertEqual("hello", result.a)
        self.assertEqual(10, result.b)
        self.assertEqual("hello", result.c.d)
        self.assertEqual("world", result.c.e)


if __name__ == '__main__':
    unittest.main()
