from instruction.common import OpType
        

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

def register_type():
    OpType.register_all(ArithOpType,
                        CompOpType,
                        LogicOpType)
