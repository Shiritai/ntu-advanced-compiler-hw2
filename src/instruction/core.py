from typing import Dict, Union
from instruction.common import OpType, ValType


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
        mapping: Dict[CoreValType, Union[bool, int]] = { CoreValType.BOOL: bool, CoreValType.INT: int }
        return mapping[self]
        

class ConstOpType(OpType):
    """Core arithmetic operator
    """
    CONST = "const"

class ArithOpType(OpType):
    """Core arithmetic operator
    """

    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"

    @property
    def nargs(self) -> int:
        """Get the number of the arguments of `op`

        Args:
            op (OpType): operator

        Returns:
            int: the number of the arguments
        """
        return 2

class CompOpType(OpType):
    """Core comparision operator
    """

    EQ = "eq"
    LT = "lt"
    GT = "gt"
    LE = "le"
    GE = "ge"
    
    @property
    def nargs(self) -> int:
        """Get the number of the arguments of `op`

        Args:
            op (OpType): operator

        Returns:
            int: the number of the arguments
        """
        return 2
    
class LogicOpType(OpType):
    """Core logic operator
    """

    NOT = "not"
    AND = "and"
    OR = "or"
    
    @property
    def nargs(self) -> int:
        """Get the number of the arguments of `op`

        Args:
            op (OpType): operator

        Returns:
            int: the number of the arguments
        """
        return 2 if self != self.NOT else 1

class CtrlOpType(OpType):
    """Control operator
    """

    JMP = "jmp"
    BR = "br"
    CALL = "call"
    RET = "ret"
    
    @property
    def is_block_terminator(self) -> bool:
        return True if self in (CtrlOpType.JMP, CtrlOpType.BR, CtrlOpType.RET) else False
    
    @property
    def has_side_effect(self) -> bool:
        return True

class TrivialOpType(OpType):
    """Miscellaneous operator
    """

    ID = "id"
    PRINT = "print"
    NOP = "nop"
    
    @property
    def has_side_effect(self) -> bool:
        return True if self == TrivialOpType.PRINT else False

def register_type():
    ValType.register(CoreValType)
    OpType.register_all(ConstOpType, 
                        ArithOpType,
                        CompOpType,
                        LogicOpType,
                        CtrlOpType,
                        TrivialOpType)
