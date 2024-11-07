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

    Returns:
        `(defs, global_names, val_kill)`

        defs (dict[str, tuple[set[BasicBlock], ValType]]):
            the set of basic blocks in which each variable is defined
        global_names (dict[str, set[str]]):
            variables that are of interest in multiple defs
        val_kill (set[str]):
            variables that is defined in each block
    """
    # TODO: Implement variable definition collection
    defs: dict[str, tuple[set[BasicBlock], ValType]] = {}
    val_kill: dict[str, set[str]] = {}
    global_names: set[str] = set()
    
    for label, bb in cfg.blocks.items():
        for inst in bb.insts:
            if isinstance(inst, (Const, ValueOperation)):
                if (isinstance(inst, ValueOperation)
                    and inst.args is not None):
                    for arg in inst.args:
                        if arg not in val_kill.setdefault(label, set()):
                            global_names.add(arg)
                val_kill.setdefault(label, set()).add(inst.dest)
                defs.setdefault(inst.dest, (set(), inst.type))[0].add(bb)
                
    return defs, global_names, val_kill

def def2global_d2b(defs: dict[str, tuple[set[BasicBlock], ValType]],
                   global_names: set[str]):
    """Get global definition-block map

    Args:
        defs (dict[str, set[BasicBlock]]): all possible definitions
        global_names (set[str]): variables used cross `BasicBlock`s in such cfg

    Returns:
        dict[str, tuple[set[BasicBlock], ValType]]: global definition-(blocks, type) map
    """
    return { k: v for k, v in defs.items() if k in global_names }

def insert_phi_functions(dom_tree: DominatorTree,
                         global_d2b: dict[str, tuple[set[BasicBlock], ValType]]):
    """
    Inserts φ-functions into the basic defs.
    """
    # TODO: Implement φ-function insertion using dominance frontiers
    for var, (def_blocks, def_type) in global_d2b.items():
        q = deque(def_blocks)
        while len(q) > 0:
            b = q.popleft()
            for df in dom_tree.dom_frontiers[b]:
                if df.insert_phi_if_not_exist_for(var, def_type):
                    q.append(df)

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