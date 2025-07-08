from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class AttrSpec:
    name      : str
    type_name : str
    exists    : Callable[[Any], bool]
    getter    : Callable[[Any], Any]
    setter    : Callable[[Any, Any], None]

    @property
    def tag(self) -> str:
        return self.name.lower().replace(" ", "_")

__all__ = ["AttrSpec"]

from .defs import *
__all__ += defs.__all__
from .log import *
__all__ += log.__all__
from .args import *
__all__ += args.__all__
from .utils import *
__all__ += utils.__all__
from .nv import *
__all__ += nv.__all__
from .xml import *
__all__ += xml.__all__
from .db import *
__all__ += db.__all__
from .icon import *
__all__ += icon.__all__
