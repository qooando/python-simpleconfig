#
# This is simpleconfig, a simple way to load your configuration files (yaml, json, ...)
# As long ass you can return a dictionary, you can load any type of configuration you want
# to dataclass objects
#

__author__ = "Lorenzo Cenceschi (l.cenceschi@gmail.com)"
__version__ = "1.0.0"

import copy
import dataclasses
import json
import logging
import sys
import typing
from dataclasses import _MISSING_TYPE
from typing import Any

import yaml
from yaml import SafeLoader

_is_dataclass = dataclasses.is_dataclass

_logger = logging.getLogger(__name__)
_this = sys.modules[__name__]
_loaders = {}
_dumpers = {}

__all__ = [
    "Config",
    "load",
    "loads",
    "dump",
    "dumps",
    "allow_unknown_fields",
    "allow_type_mismatch_fields",
    "simplify",
    "LoaderNotFoundError",
    "DumperNotFoundError",
    "ConfigLoader",
    "ConfigDumper"
]


# =============================================================
# Exception
# =============================================================

class LoaderNotFoundError(Exception):
    pass


class DumperNotFoundError(Exception):
    pass


# =============================================================
# Default config
# =============================================================

@dataclasses.dataclass()
class Config:
    __initialized = False
    def __post_init__(self):
        self.__initialized = True
    def __as_dict__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
    def __reduce__(self):
        return (self.__class__, (), self.__as_dict__())
    def __setattr__(self, key, value):
        if self.__initialized:
            if not _allows_unknown_fields(self) and not hasattr(self, key):
                raise AttributeError(f"Invalid field '{key}' in object '{self.__class__.__name__}'")
        super().__setattr__(key, value)


# =============================================================
# Annotations()
# =============================================================

def ConfigLoader(format: str):
    """
    Function decorator that registers the function as a loader for the specified format
    """
    def inner(target):
        _loaders[format] = target
        return target
    return inner


def ConfigDumper(format: str):
    """
    Function decorator that registers the function as a dumper for the specified format
    """
    def inner(target):
        _dumpers[format] = target
        return target
    return inner


def allow_unknown_fields(target):
    """
    Decorator that allows the load function to set unknown fields
    not previously initialized in the target object
    """
    target.ALLOW_UNKNOWN_FIELDS = True
    return target


def allow_type_mismatch_fields(target):
    """
    Decorator that allows to assign mismatching types to fields
    """
    target.ALLOW_TYPE_MISMATCH_FIELDS = True
    return target


def _allows_unknown_fields(target):
    """
    Test if an object allows unknown fields
    """
    if hasattr(target, "ALLOW_UNKNOWN_FIELDS"):
        return getattr(target, "ALLOW_UNKNOWN_FIELDS")
    else:
        return False


def _allows_type_mismatch_fields(target):
    """
    Test if an object allows unknown fields
    """
    if hasattr(target, "ALLOW_TYPE_MISMATCH_FIELDS"):
        return getattr(target, "ALLOW_TYPE_MISMATCH_FIELDS")
    else:
        return False

# =============================================================
# Public functions and helpers
# =============================================================

def simplify(config) -> Any:
    """
    Transform configuration to dicts and lists

    :param config: config
    :return: dict
    """
    allow = False if not hasattr(config, "ALLOW_UNKNOWN_FIELDS") else getattr(config, "ALLOW_UNKNOWN_FIELDS")
    if _is_dataclass(config) and not allow:
        result = dataclasses.asdict(config)
    elif hasattr(config, "__as_dict__"):
        result = dict(config.__as_dict__())
    elif hasattr(config, "__dict__"):
        result = dict(config.__dict__)
    else:
        result = config

    if hasattr(result, "items"):
        result = {k: simplify(v) for k, v in result.items()}

    elif hasattr(result, "__getitem__") and not hasattr(result, "lower"):
        result = [simplify(v) for v in result]

    return result

def load(src, srcFormat: str = None, Config=Config, **k) -> Any:
    """
    Load a configuration from a file

    :param src: a path or an object with read() like an open file
    :param srcFormat: format of the file, default is the file extension itself
    :param Config: a dataclass class
    :return: a Config object
    """
    assert src is not None
    assert Config is not None
    assert _is_dataclass(Config)

    if hasattr(src, "read"):
        assert srcFormat is not None
        return loads(src.read(), srcFormat=srcFormat, Config=Config)
    else:
        with open(src, 'r') as f:
            return load(src=f, srcFormat=srcFormat or src.split(".")[-1], Config=Config)


def loads(src: str or dict, srcFormat: str or None = None, Config=Config, **k) -> Any:
    """
    Load a configuration from a string

    :param src: configuration string or dictionary
    :param srcFormat: configuration format (e.g. json)
    :param Config: config class
    :return: a Config object
    """
    assert src is not None
    assert Config is not None
    if hasattr(src, "__getitem__") and hasattr(src, "items"):
        return _load(Config(), src)
    else:
        assert srcFormat is not None
        if srcFormat not in _loaders:
            raise LoaderNotFoundError(f"Loader not found for format '{srcFormat}'")
        return loads(_loaders[srcFormat](src), srcFormat=None, Config=Config, **k)


def dump(config, dest, destFormat: str="json", **k):
    """
    Write a string representation in the chosen format for the config object to a file

    :param config: input Config
    :param dest: file or stream
    :param destFormat: file format
    """
    assert dest is not None

    if hasattr(dest, "write"):
        return dest.write(dumps(config, destFormat, **k))
    else:
        with open(dest, 'w') as f:
            return dump(config, f, destFormat, **k)

def dumps(config: Config, destFormat: str = "json", **k) -> str:
    """
    Convert config to string representation in the chosen format

    :param config: the input configuration
    :param destFormat: the output format
    :return: a string
    """
    assert config is not None
    assert destFormat is not None

    if destFormat not in _dumpers:
        raise DumperNotFoundError(f"Dumper not found for format '{destFormat}'")
    return _dumpers[destFormat](config, **k)

# =============================================================
# Dumper and loaders
# =============================================================

@ConfigDumper("json")
def _to_json(config, **k):
    return json.dumps(config, **k)

@ConfigLoader("json")
def _from_json(src: str, **k) -> dict:
    return json.loads(src)

@ConfigDumper("yaml")
def _to_yaml(config, **k):
    return yaml.dump(simplify(config), **k)

@ConfigLoader("yaml")
def _from_yaml(src: str, **k) -> dict:
    return yaml.load(src, Loader=SafeLoader, **k)

# =============================================================
# Monkey Patch
# =============================================================

from json import JSONEncoder
_logger.debug(f"Monkey patch {JSONEncoder.default.__name__} to support class method __as_dict__")

def _default(self, obj):
    return getattr(obj.__class__, "__as_dict__", _default.default)(obj)

_default.default = JSONEncoder.default  # Save unmodified default.
JSONEncoder.default = _default # Replace it.

# =============================================================
# Helper functions for loading from dict
# =============================================================

def _load(target, source, targetType=None):
    if source is None:
        return target
    if not target and targetType:
        target = (typing.get_origin(targetType) or targetType)()
    if _is_dataclass(target):
        return _load_dataclass(target, source)
    if hasattr(target, "keys"): # target is a dict
        return _load_dict(target, source, targetType=targetType)
    if hasattr(source, "pop"): # list
        return _load_list(target, source, targetType=targetType)
    return source


def _load_dataclass(target, source: dict):
    assert _is_dataclass(target)
    assert hasattr(source, "keys")
    source = copy.deepcopy(source)

    for field in dataclasses.fields(target):
        fieldName = field.name
        fieldType = field.type
        fieldFactory = field.default_factory if field.default_factory == _MISSING_TYPE else typing.get_origin(fieldType) or fieldType
        fieldValue = getattr(target, fieldName)

        if fieldName in source:
            newValue = source[fieldName]
            del source[fieldName]

            if not _is_correct_type(newValue, fieldType):
                if _allows_type_mismatch_fields(target):
                    _logger.warning(f"Ignore type mismatch for field '{fieldName}'")
                else:
                    raise TypeError(f"type mismatch for field '{fieldName}', type is '{newValue}' instead of '{fieldType}")

            # create if not present
            if not fieldValue:
                fieldValue = fieldFactory()
                setattr(target, fieldName, fieldValue)

            # populate
            setattr(target, fieldName, _load(fieldValue, newValue, targetType=fieldType))

    if _allows_unknown_fields(target):
        for newName, newValue in source.items():
            _logger.warning(f"Set unexpected key '{newName}'")
            setattr(target, newName, newValue)
    else:
        for newName in source.keys():
            _logger.warning(f"Ignore unexpected key '{newName}'")

    return target


def _load_list(target, source: list, targetType=None):
    assert hasattr(source, "pop")
    assert hasattr(source, "__iter__")

    if targetType:
        assert typing.get_origin(targetType) is list
        innerType = typing.get_args(targetType)[0]
        return [_load(None, x, innerType) for x in source]
    else:
        return copy.deepcopy(source)


def _load_dict(target, source: dict, targetType=None):
    assert hasattr(source, "keys")
    assert hasattr(source, "items")

    if targetType:
        assert typing.get_origin(targetType) is dict
        innerType = typing.get_args(targetType)[1]
        return {k: _load(None, v, innerType) for k,v in source.items()}
    else:
        source = copy.deepcopy(source)
        target.update(**source)
        return target


def _is_correct_type(obj, objType):
    if _is_dataclass(objType) and hasattr(obj, "items"):
        # dict + dataclass is ok
        return True

    if issubclass(type(obj), typing.get_origin(objType) or objType):
        subTypes = typing.get_args(objType)
        if len(subTypes) == 0:
            return True
        elif len(subTypes) == 1:
            assert hasattr(obj, "__iter__")
            return all(_is_correct_type(x, subTypes[0]) for x in obj)
        elif len(subTypes) == 2:
            assert hasattr(obj, "items")
            return all(_is_correct_type(k, subTypes[0]) and _is_correct_type(v, subTypes[1]) for k, v in obj.items())
        else:
            raise NotImplementedError()

    return False

