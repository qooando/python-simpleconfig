import dataclasses
import logging
import unittest
from simpleconfig import *
from dataclasses import dataclass
from typing import *

logging.basicConfig(level=logging.DEBUG)

@dataclass
class MyConfig(Config):
    @dataclass
    class MyInnerConfig(Config):
        d: str
        e: str = "world"
        f: List[str] = ("n", "m")
    a: str = "hello"
    b: int = 10
    c: MyInnerConfig = dataclasses.field(default_factory=lambda: MyConfig.MyInnerConfig("hello"))


class TestDumps(unittest.TestCase):

    def test_invalid(self):
        self.assertRaises(DumperNotFoundError, lambda: dumps(MyConfig(), destFormat="non_existent"))

    def test_json(self):
        result = dumps(MyConfig(), destFormat="json")
        print(dumps(MyConfig(), destFormat="json"))
        # print(dumps(MyConfig(), destFormat="json", indent=2))
        self.assertEqual('{"a": "hello", "b": 10, "c": {"d": "hello", "e": "world", "f": ["n", "m"]}}', result)

    def test_yaml(self):
        result = dumps(MyConfig(), destFormat="yaml")
        expected = """a: hello
b: 10
c:
  d: hello
  e: world
  f:
  - n
  - m
"""
        self.assertEqual(expected, result)
        print(result)

if __name__ == '__main__':
    unittest.main()
