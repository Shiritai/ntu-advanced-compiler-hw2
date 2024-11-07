from typing import Dict, Union
from instruction.common import ValType


class CoreValType(ValType):
    """Core value type
    """
    
    INT = "int"
    """64-bit, two's complement, signed integers.
    """
    BOOL = "bool"
    """True or false.
    """
    
    @property
    def py_type(self):
        mapping: Dict[CoreValType, Union[bool, int]] = {
            CoreValType.BOOL: bool,
            CoreValType.INT: int
        }
        return mapping[self]

class NullityType(ValType):
    """Unknown, undefined types
    """
    UNKNOWN = "unknown"
    UNDEFINED = "undefined"
    
def register_type():
    ValType.register(CoreValType)
    ValType.register(NullityType)
