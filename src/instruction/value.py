import random
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
            CoreValType.INT: int}
        return mapping[self]
    
    @property
    def random_val(self):
        rnd = random.randint(0, 1024)
        mapping: Dict[CoreValType, Union[bool, int]] = {
            CoreValType.BOOL: rnd & 1 == 0,
            CoreValType.INT: rnd}
        return mapping[self]
    
    @property
    def random_bril_val(self):
        return f"{self.random_val}".lower()
        
class NullityType(ValType):
    """Unknown, undefined types
    """
    UNKNOWN = "unknown"
    UNDEFINED = "undefined"
    
def register_type():
    ValType.register(CoreValType)
    ValType.register(NullityType)
