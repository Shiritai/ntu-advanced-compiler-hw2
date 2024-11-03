from instruction.common import OpType


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
    OpType.register(TrivialOpType)
