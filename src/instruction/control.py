from instruction.common import OpType


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
    
def register_type():
    OpType.register(CtrlOpType)
