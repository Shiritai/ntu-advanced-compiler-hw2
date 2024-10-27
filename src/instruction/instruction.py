import json
from typing import Any, Dict, Optional

from logger.logger import logger
from instruction.common import OpType

class Instruction:
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