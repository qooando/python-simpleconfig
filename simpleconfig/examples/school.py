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

print(schoolConfig)