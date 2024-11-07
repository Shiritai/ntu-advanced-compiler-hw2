from enum import Enum, unique
from typing import Collection, Dict, Optional

val_types: Dict[str, 'ValType'] = {}

@unique
class ValType(Enum):
    """General value type
    """
    
    @classmethod
    def register(cls, tp: type['ValType']):
        val_types.update({t.value: t for t in tp})
    
    @classmethod
    def cases(cls):
        return val_types
    
    @classmethod
    def find(cls, tp: Optional[str] | 'ValType'):
        if isinstance(tp, ValType):
            return tp
        return val_types.get(tp)
    
    @classmethod
    def all_py_types(cls):
        return tuple(map(lambda x: x.py_type, cls.cases().values()))
    
    @property
    def py_type(self) -> object:
        """Return the corresponding type in Python, default to `None`
        """
        return None
    
    @property
    def random_val(self):
        """Generate a random value of this type in python data structure
        """
        return None
    
    @property
    def random_bril_val(self):
        """Generate a random value of this type in bril format
        """
        raise NotImplementedError

op_types: Dict[str, 'OpType'] = {}

@unique
class OpType(Enum):
    """General operator type
    """
    
    @classmethod
    def register(cls, tp: type['OpType']):
        op_types.update({t.value: t for t in tp})

    @classmethod
    def register_all(cls, *tps: Collection[type['OpType']]):
        for tp in tps: cls.register(tp)
    
    @classmethod
    def cases(cls):
        return op_types
    
    @classmethod
    def find(cls, op: Optional[str] | 'OpType'):
        """Find the operator named op
        """
        if isinstance(op, OpType):
            return op
        return op_types.get(op)
    
    @property
    def is_block_terminator(self) -> bool:
        """Determin whether a operator is a terminator of a block
        
        Default to `False`.
        """
        return False
    
    @property
    def has_side_effect(self) -> bool:
        """Check whether this operation has side effect (not value related)

        e.g. call function, change control flow, default to `False`
        """
        return False
    
    @property
    def nargs(self) -> int:
        """Get the number of the arguments of `op`

        Args:
            op (OpType): operator

        Returns:
            int: the number of the arguments
        """
        return 0
