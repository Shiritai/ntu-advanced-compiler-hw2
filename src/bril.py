import json
from typing import Any, Optional

from instruction.const import ConstOpType
from logger.logger import logger
from instruction.common import ValType
from instruction.instruction import Instruction, ConstInst, ValueOperationInst, EffectOperationInst, LabelInst

class Const(Instruction):
    """Constant assignment instruction
    """
    
    def __init__(self, instr: ConstInst):
        super().__init__(instr)
        # guardian, check validity
        if self.op != ConstOpType.CONST:
            err = ValueError(f"Invalid {type(self)} construction: op: {self.op} is not {ConstOpType.CONST}")
            logger.error(err)
            raise err

        tp = ValType.find(instr.get('type'))
        if tp is None:
            err = ValueError(f"Invalid {type(self)} construction: type: {tp} is not in {ValType.cases()}")
            logger.error(err)
            raise err

        dest = instr.get('dest')
        if not isinstance(dest, str):
            err = ValueError(f"Invalid {type(self)} construction: dest: {dest} is not of type str")
            logger.error(err)
            raise err

        value = instr.get('value')
        if not isinstance(value, ValType.all_py_types()):
            err = ValueError(f"Invalid {type(self)} construction: value: {value} is not in {possible_types}")
            logger.error(err)
            raise err
            
        self.dest = dest
        self.type = tp
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result['dest'] = self.dest
        result['type'] = self.type.value
        result['value'] = self.value
        return result

class ValueOperation(Instruction):
    """Instruction that definitely has destination (value assignment)
    e.g.
    * x = y + z (binary operation)
    * x = a (copy)
    * x = func(...) (function call)
    * x = phi(...) (phi function)
    """
    
    def __init__(self, instr: ValueOperationInst):
        super().__init__(instr)

        tp = ValType.find(instr.get('type'))
        if tp is None:
            err = ValueError(f"Invalid {type(self)} construction: type: {tp} is not in {ValType.cases()}")
            logger.error(err)
            raise err
        
        dest = instr.get('dest')
        if not isinstance(dest, str):
            err = ValueError(f"Invalid {type(self)} construction: dest: {dest} is not of type str")
            logger.error(err)
            raise err
        
        args: Optional[list[str]]  = instr.get('args')
        if args is not None and not isinstance(args, list):
            err = ValueError(f"Invalid {type(self)} construction: args: {args} is not of type list")
            logger.error(err)
            raise err
        
        funcs: Optional[list[str]]  = instr.get('funcs')
        if funcs is not None and not isinstance(funcs, list):
            err = ValueError(f"Invalid {type(self)} construction: funcs: {funcs} is not of type list")
            logger.error(err)
            raise err
        
        labels: Optional[list[str]]  = instr.get('labels')
        if labels is not None and not isinstance(labels, list):
            err = ValueError(f"Invalid {type(self)} construction: labels: {labels} is not of type list")
            logger.error(err)
            raise err
        
        self.dest = dest
        self.type = tp
        self.args = args
        self.funcs = funcs
        self.labels = labels

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        result['dest'] = self.dest
        result['type'] = self.type.value
        if self.args:
            result['args'] = self.args
        if self.funcs:
            result['funcs'] = self.funcs
        if self.labels:
            result['labels'] = self.labels
        return result

class EffectOperation(Instruction):
    """Instruction that has side effect without value assignment
    """
    
    def __init__(self, instr: EffectOperationInst):
        super().__init__(instr)
        # guardian, check validity
        if not self.op.has_side_effect:
            err = ValueError(f"Invalid {type(self)} construction: op: {self.op} has no side effect")
            logger.error(err)
            raise err
        
        args: Optional[list[str]]  = instr.get('args')
        if args is not None and not isinstance(args, list):
            err = ValueError(f"Invalid {type(self)} construction: args: {args} is not of type list")
            logger.error(err)
            raise err
        
        funcs: Optional[list[str]]  = instr.get('funcs')
        if funcs is not None and not isinstance(funcs, list):
            err = ValueError(f"Invalid {type(self)} construction: funcs: {funcs} is not of type list")
            logger.error(err)
            raise err
        
        labels: Optional[list[str]] = instr.get('labels')
        if labels is not None and not isinstance(labels, list):
            err = ValueError(f"Invalid {type(self)} construction: labels: {labels} is not of type list")
            logger.error(err)
            raise err
        
        self.args = args
        self.funcs = funcs
        self.labels = labels

    def to_dict(self) -> dict[str, Any]:
        result = super().to_dict()
        if self.args:
            result['args'] = self.args
        if self.funcs:
            result['funcs'] = self.funcs
        if self.labels:
            result['labels'] = self.labels
        return result

class Label(Instruction):
    """Pure label, not a real instruction
    """
    
    def __init__(self, instr: LabelInst):
        super().__init__(instr)
        label = instr.get('label')
        if not isinstance(label, str):
            err = ValueError(f"Invalid {type(self)} construction: label {label} should be str")
            logger.error(err)
            raise err
        
        self.label = label

    def to_dict(self) -> dict[str, Any]:
        return { 'label': self.label }

class Function:
    def __init__(self, func: dict[str, Any]):
        self.name = func.get('name')
        args: Optional[list[dict[str, str]]] = func.get('args', [])
        if not isinstance(args, list):
            err = ValueError(f"Invalid args {args} in function {func}")
            logger.error(err)
            raise err
        self.args = args
        self.type = func.get('type')
        self.instrs = [self._parse_instr(instr) for instr in func.get('instrs', [])]

    def _parse_instr(self, instr: dict[str, Any]) -> Instruction:
        if 'label' in instr:
            return Label(instr)
        else:
            op = instr.get('op')
            if op == 'const':
                return Const(instr)
            elif 'dest' in instr:
                return ValueOperation(instr)
            else:
                return EffectOperation(instr)

    def to_dict(self) -> dict[str, Any]:
        result = {'name': self.name}
        if self.args:
            result['args'] = self.args
        if self.type is not None:
            result['type'] = self.type
        if self.instrs is None:
            logger.error(self.name)
            logger.flush()
        result['instrs'] = [instr.to_dict() for instr in self.instrs]
        return result

class Program:
    def __init__(self, prog: dict[str, Any]):
        self.functions = [Function(func) for func in prog.get('functions', [])]

    def to_dict(self) -> dict[str, Any]:
        return {'functions': [func.to_dict() for func in self.functions]}

def parse_bril(json_str: str) -> Program:
    prog = json.loads(json_str)
    return Program(prog)

def serialize_bril(prog: Program) -> str:
    return json.dumps(prog.to_dict(), indent=2)