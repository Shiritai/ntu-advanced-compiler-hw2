from enum import Enum, unique
from typing import Dict, Optional

val_types: Dict[str, 'ValType'] = {}

@unique
class ValType(Enum):
    @classmethod
    def register(cls, tp: type['ValType']):
        val_types.update({t.value: t for t in tp})
    
    @classmethod
    def cases(cls):
        return val_types
    
    @classmethod
    def find(cls, tp: Optional[str]):
        return val_types.get(tp)

op_types: Dict[str, 'OpType'] = {}

@unique
class OpType(Enum):
    @classmethod
    def register(cls, tp: type['OpType']):
        op_types.update({t.value: t for t in tp})
    
    @classmethod
    def cases(cls):
        return op_types
    
    @classmethod
    def find(cls, op: Optional[str]):
        return op_types.get(op)
