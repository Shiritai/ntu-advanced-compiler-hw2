from enum import Enum

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

class CompOpType(OpType):
    """Core comparision operator
    """

    EQ = "eq"
    LT = "lt"
    GT = "gt"
    LE = "le"
    GE = "ge"
    
class LogicOpType(OpType):
    """Core logic operator
    """

    NOT = "not"
    AND = "and"
    OR = "or"

class CtrlOpType(OpType):
    """Control operator
    """

    JMP = "jmp"
    BR = "br"
    CALL = "call"
    RET = "ret"

class TrivialOpType(OpType):
    """Miscellaneous operator
    """

    ID = "id"
    PRINT = "print"
    NOP = "nop"
    

def register_type():
    ValType.register(CoreValType)
    for tp in (ConstOpType, ArithOpType, CompOpType, LogicOpType, CtrlOpType, TrivialOpType):
        OpType.register(tp)

if __name__ == '__main__':
    register_type()  # register types in any cases
    
    print(ValType.cases())
    print(OpType.cases())
