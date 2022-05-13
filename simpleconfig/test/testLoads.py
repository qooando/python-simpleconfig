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


class TestLoads(unittest.TestCase):

    def test_invalid(self):
        self.assertRaises(LoaderNotFoundError, lambda: loads(MyConfig(), srcFormat="non_existent"))

    def test_json(self):
        src = """{"a":"world","b": 15,"c": {"d":"test","f":["abra","cadabra"]}}"""
        config = loads(src, srcFormat="json", Config=MyConfig)
        print(dumps(config, destFormat="json", indent=2))
        self.assertEqual("world", config.a)
        self.assertEqual(15, config.b)
        self.assertEqual("test", config.c.d)
        self.assertEqual("abra", config.c.f[0])

    def test_yaml(self):
        src = """
a: world
b: 15
c:
  d: test
  f:
    - abra
    - cadabra
"""
        config = loads(src, srcFormat="yaml", Config=MyConfig)
        print(dumps(config, destFormat="yaml"))
        self.assertEqual("world", config.a)
        self.assertEqual(15, config.b)
        self.assertEqual("test", config.c.d)
        self.assertEqual("abra", config.c.f[0])


if __name__ == '__main__':
    unittest.main()
