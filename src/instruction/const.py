from instruction.common import OpType


class ConstOpType(OpType):
    """Core arithmetic operator
    """
    CONST = "const"

def register_type():
    OpType.register(ConstOpType)
