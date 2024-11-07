from collections import OrderedDict
from bril import Const, EffectOperation, Function, Instruction, Label, ValueOperation
from instruction.value import NullityType
from instruction.common import OpType, ValType
from instruction.ssa import SsaOpType
from instruction.control import CtrlOpType
from instruction.instruction import Instruction
from logger.logger import logger
from util import Convertor, new_name

class BasicBlock:
    def __init__(self, label: str, insts: list[Instruction] = None):
        self.label = label
        self.insts = insts if insts is not None else []
        self.preds: set['BasicBlock'] = set()
        """predecessor blocks
        """
        self.succs: set['BasicBlock'] = set()
        """successor blocks
        """

    def __repr__(self):
        return f'BasicBlock({self.label})'
    
    def get_by_op(self, op: OpType) -> list[Instruction]:
        """Query all instructions by op: `OpType` in instruction order

        Args:
            op (OpType): operation type to search
        """
        return [ i for i in self.insts if i.op == op ]

    def insert_phi_if_not_exist_for(self, var: str, tp: ValType = NullityType.UNKNOWN):
        pos = 0
        for i in self.insts:
            if hasattr(i, 'dest') and isinstance(i.dest, str) and i.dest == var:
                if i.op == SsaOpType.PHI:
                    return False
                else:
                    possible_types = (ValueOperation, Const)
                    if not isinstance(i, possible_types):
                        err = ValueError(f"Invalid instruction {i} has dest but not in {possible_types}")
                        logger.error(err)
                        raise err
            if i.op == SsaOpType.PHI and i.dest < var:
                pos += 1
                
        # phi for var DNE, insert one
        self.insts.insert(pos, ValueOperation({
            "op": SsaOpType.PHI, "args": [], "labels": [],
            "dest": var, "type": tp }))
        return True
                

class Inst2BasicBlockDict(Convertor):
    @classmethod
    def _name_basic_block(cls,
                          insts: list[Instruction],
                          named_bb: OrderedDict[str, BasicBlock]):
        """Construct a BasicBlock, named it to its label.
        if it doesn't have label, give it a new name,
        and store it into `named_bb`

        Args:
            insts (list[Instruction]): instructions to form a basic block
            named_bb (dict[str, BasicBlock]): named list (OrderedDict) of `label:BasicBlock` pair 
        """
        name: str
        first_inst = insts[0]
        if isinstance(first_inst, Label):
            name = first_inst.label
            insts = insts[1:]
        else:
            name = new_name('b', named_bb)
        named_bb[name] = BasicBlock(name, insts)
    
    @classmethod
    def convert(cls, insts: list[Instruction]) -> OrderedDict[str, BasicBlock]:
        """Convert a list of instructions to a named list (OrderedDict) of `label:BasicBlock` pair
        """
        named_bb: OrderedDict[str, BasicBlock] = OrderedDict()
        collector = []
        for i in insts:
            if isinstance(i, Label):
                if len(collector) != 0:
                    cls._name_basic_block(collector, named_bb)
                collector = [i]
            else:
                collector.append(i)
                # If end of BasicBlock detected
                if i.op.is_block_terminator:
                    cls._name_basic_block(collector, named_bb)
                    collector = []
        if len(collector) != 0:
            cls._name_basic_block(collector, named_bb)
        return named_bb

class BasicBlockDict2Cfg(Convertor):
    @classmethod
    def _add_first_block_if_need(cls, named_bb: OrderedDict[str, BasicBlock]):
        first_bb = next(iter(named_bb.keys()))
        for bb in named_bb.values():
            if any(isinstance(i, (ValueOperation, EffectOperation))
                and i.labels is not None
                and first_bb in i.labels  # first_bb is referenced
                for i in bb.insts):
                # there is at least one reference to the first bb
                # -> create a pure entry without in-edge
                leading = BasicBlock(new_name('fresh', named_bb))
                # Add a psudo leading BB and move it to the front of OrderedDict
                named_bb[leading.label] = leading
                named_bb.move_to_end(leading.label, last=False)
                break
    
    @classmethod
    def _patch_and_link(cls, named_bb: OrderedDict[str, BasicBlock]):
        """make all block has terminator and link them (successors)
        """
        labels = list(named_bb.keys())
        for n, bb in enumerate(named_bb.values()):
            if (len(bb.insts) == 0  # pure label block
                or not bb.insts[-1].op.is_block_terminator):  # doesn't have ret/jump at the end of bb
                if n == len(named_bb) - 1:  # last BB in CFG, add return inst
                    bb.insts.append(EffectOperation({ 'op': CtrlOpType.RET }))
                else:  # not last BB, add jump inst to the next bb
                    bb.insts.append(EffectOperation({
                        'op': CtrlOpType.JMP,
                        'labels': [labels[n + 1]] }))
                    bb.succs.add(named_bb[labels[n + 1]])
            else:  # has ret/br/jmp inst
                last = bb.insts[-1]
                if not isinstance(last, EffectOperation):
                    err = ValueError(f"Invalid last instruction {last} in {bb}")
                    logger.error(err)
                    raise err
                if last.op == CtrlOpType.JMP or last.op == CtrlOpType.BR:
                    if last.labels is None or len(last.labels) == 0:
                        err = ValueError(f"Invalid last instruction {last} in {bb} with labels {last.labels}")
                        logger.error(err)
                        raise err
                    bb.succs.update(named_bb[label] for label in last.labels)

    @classmethod
    def _link_back_pred(cls, named_bb: OrderedDict[str, BasicBlock]):
        """link predecessors based on successors
        """
        for bb in named_bb.values():
            if len(bb.insts) == 0:
                err = ValueError(f"Invalid bb with no instructions")
                logger.error(err)
                raise err
            last = bb.insts[-1]
            if (not isinstance(last, EffectOperation)
                or not last.op.is_block_terminator):
                err = ValueError(f"Invalid last instruction {last} in {bb}")
                logger.error(err)
                raise err
            if last.labels is not None:
                for label in last.labels:
                    named_bb[label].preds.add(bb)
    
    @classmethod
    def convert(cls, named_bb: OrderedDict[str, BasicBlock]) -> BasicBlock:
        """Use `named_bb` to construct a CFG

        Args:
            named_bb (OrderedDict[str, BasicBlock]):
                named list (OrderedDict) of `name:BasicBlock`

        Returns:
            BasicBlock: leading `BasicBlock` in CFG
        """
        cls._add_first_block_if_need(named_bb)
        cls._patch_and_link(named_bb)
        cls._link_back_pred(named_bb)
        # return the first BB
        return next(iter(named_bb.values()))
        

class CFG:
    def __init__(self, function: Function):
        self.function = function
        # TODO: Implement CFG construction logic
        # 1. Divide instructions into basic blocks.
        self.blocks = Inst2BasicBlockDict.convert(self.function.instrs)
        """`label:BasicBlock` map
        """
        # 2. Establish successor and predecessor relationships.
        # 3. Handle labels and control flow instructions.
        self.entry_block = BasicBlockDict2Cfg.convert(self.blocks)
        """The first block of this `CFG`
        """
        
    def view_blocks(self):
        for bb in self.blocks.values():
            logger.info(f"[ {bb} ]")
            for i in bb.insts:
                logger.info(f"\t{i}")

    def get_blocks(self) -> list[BasicBlock]:
        return list(self.blocks.values())
    
    
