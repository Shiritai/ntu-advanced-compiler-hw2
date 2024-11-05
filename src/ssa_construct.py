from typing import Dict, List, Set
from bril import Const, Function, Instruction, ValueOperation
from cfg import CFG, BasicBlock
from logger.logger import logger
from dominance import DominatorTree

def construct_ssa(function: Function):
    """
    Transforms the function into SSA form.
    """
    cfg = CFG(function)
    dom_tree = DominatorTree(cfg)

    logger.debug(str(function.instrs))
    logger.debug(str(cfg.blocks))

    # Step 1: Variable Definition Analysis
    def_blocks = collect_definitions(cfg)

    # Step 2: Insert φ-Functions
    insert_phi_functions(cfg, dom_tree, def_blocks)

    # Step 3: Rename Variables
    rename_variables(cfg, dom_tree)

    # After transformation, update the function's instructions
    function.instrs = reconstruct_instructions(cfg)

def collect_definitions(cfg: CFG):
    """
    Collects (global_names, defs, val_kill)
    
    Args:
        global_names (dict[str, set[BasicBlock]]):
            variables that are of interest in multiple defs
        defs (dict[str, set[str]]):
            the set of basic blocks in which each variable is defined
        val_kill (set[str]):
            variables that is defined in each block
    """
    # TODO: Implement variable definition collection
    defs: dict[str, set[BasicBlock]] = {}
    val_kill: dict[str, set[str]] = {}
    global_names = set()
    for label, bb in cfg.blocks.items():
        for inst in bb.insts:
            if isinstance(inst, (Const, ValueOperation)):
                if (isinstance(inst, ValueOperation)
                    and inst.args is not None):
                    for arg in inst.args:
                        if arg not in val_kill.setdefault(label, set()):
                            global_names.add(arg)
                val_kill.setdefault(label, set()).add(inst.dest)
                defs.setdefault(inst.dest, set()).add(label)
    return global_names, defs, val_kill

def insert_phi_functions(cfg: CFG, dom_tree: DominatorTree, def_blocks: Dict[str, Set[BasicBlock]]):
    """
    Inserts φ-functions into the basic blocks.
    """
    # TODO: Implement φ-function insertion using dominance frontiers
    pass

def rename_variables(cfg: CFG, dom_tree: DominatorTree):
    """
    Renames variables to ensure each assignment is unique.
    """
    # TODO: Implement variable renaming
    pass

def reconstruct_instructions(cfg: CFG) -> List[Instruction]:
    """
    Reconstructs the instruction list from the CFG after SSA transformation.
    """
    # TODO: Implement instruction reconstruction
    pass