# python-simpleconfig
Another really simple python library to import configuration files to python dataclasses

## How-to

The library provides classic `load`, `loads`, `dump`, `dumps` functions.

The class `Config` can be extended to custom configuration classes
with typed fields, it also permits json serialization out of the box
thanks to a simple monkey patch of default serializer that looks up for
`__as_dict__` special method.

## Example

```python3
import simpleconfig as sc
from dataclasses import dataclass, field
from typing import List, Mapping

data = '''---
school:
  classes:
    - className: 1A
      teachers:
        - J. Smith
        - M. Sue
    - className: 1B
      teachers:
        - L. Watson
        - A. Buffy
'''


@dataclass
class SchoolClass(sc.Config):
    className: str = ""
    teachers: List[str] = field(default_factory=list)

@dataclass
class School(sc.Config):
    classes: List[SchoolClass] = field(default_factory=list)

@dataclass
class MyConfig(sc.Config):
    school: School = None

schoolConfig = sc.loads(data, srcFormat="yaml", Config=MyConfig)

print(schoolConfig.school.classes[1].teachers[0]) # L. Watson
```

You can also register your loads and dumps function using `@ConfigLoader("myFormat")` and `@ConfigDumper("myFormat")`
decorators above the selected functions.

Note that the loader performs also the type check. To disable the typecheck use the `@allow_type_mismatch_fields`
decorator above the config class.

`Config` class prevents to set unknown fields, to restore classic python behavior prepend the `@allow_unknown_fields`
decorator to the config class.

