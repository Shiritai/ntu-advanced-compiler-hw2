from instruction.common import OpType

class SsaOpType(OpType):
    """Operators for SSA representation
    """
    PHI = "phi"

def register_type():
    OpType.register(SsaOpType)
