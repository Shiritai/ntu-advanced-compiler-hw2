import json
from typing import Any, Dict, Literal, Optional

from logger.logger import logger
from instruction.common import OpType

class Instruction:
    """Abstract class of an instruction
    """
    
    def __init__(self, instr: Dict[str, Any]):
        self.op: Optional[OpType] = OpType.find(instr.get('op'))
        self.instr = instr

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.op is not None:
            result['op'] = self.op.value
        return result

    def __repr__(self):
        return json.dumps(self.to_dict())

ConstInstKeys = Literal["op", "type", "dest", "value"]
ConstInst = dict[ConstInstKeys, Any]

ValueOperationInstKeys = Literal["op", "type", "dest", "args", "funcs", "labels"]
ValueOperationInst = dict[ValueOperationInstKeys, Any]

EffectOperationInstKeys = Literal["op", "args", "funcs", "labels"]
EffectOperationInst = dict[EffectOperationInstKeys, Any]

LabelInstKeys = Literal["op", "label"]
LabelInst = dict[LabelInstKeys, Any]
