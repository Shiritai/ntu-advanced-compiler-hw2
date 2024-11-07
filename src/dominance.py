from collections import deque
from functools import reduce
from typing import Optional
from cfg import CFG, BasicBlock
from logger.logger import logger
from util import Convertor

class Cfg2Dom(Convertor):
    @classmethod
    def convert(cls, cfg: CFG) -> dict[BasicBlock, set[BasicBlock]]:
        """Convert cfg to Dominance: dict in format `BasicBlock : set of BasicBlock` pair

        Computes the dominators for each basic block.
        """
        # TODO: Implement the iterative algorithm to compute dominators.
        full_set = lambda: set(cfg.blocks.values())
        dom = { bb: full_set() for bb in cfg.blocks.values() }
        while True:
            changed = False
            for bb in cfg.blocks.values():
                nxt_dom = { bb }
                if len(bb.preds) > 0:
                    nxt_dom.update(reduce(lambda s1, s2: s1.intersection(s2),
                                          list(dom.get(pred) for pred in bb.preds)))

                if dom[bb] != nxt_dom:
                    dom[bb] = nxt_dom
                    changed = True
                
            if not changed:
                break
        return dom

class Dom2Idom(Convertor):
    @classmethod
    def convert(cls,
                dom: dict[BasicBlock, set[BasicBlock]]) -> dict[BasicBlock, Optional[BasicBlock]]:
        """
        Computes the immediate dominator for each basic block.
        """
        # TODO: Compute immediate dominators based on the dominator sets.
        idom: dict[BasicBlock, Optional[BasicBlock]] = {}
        for bb, bb_dom in dom.items():
            candidates = { d: len(dom[d]) for d in bb_dom if d != bb }
            if len(candidates) == 0:  # first block
                idom[bb] = None
            else:
                idom[bb] = max(candidates.items(), key=lambda e: e[1])[0]
        return idom

class Idom2Df(Convertor):
    @classmethod
    def convert(cls, idom: dict[BasicBlock, Optional[BasicBlock]]):
        """
        Computes the dominance frontiers for each basic block.
        """
        # TODO: Implement dominance frontier computation.
        df: dict[BasicBlock, set[BasicBlock]] = {
            bb: set() for bb in idom.keys() }
        for bb in idom.keys():
            if len(bb.preds) > 1:
                for pred in bb.preds:
                    cur = pred
                    while cur != idom[bb]:
                        df[cur].add(bb)
                        cur = idom[cur]
        return df

class Idom2DomTree(Convertor):
    @classmethod
    def convert(cls, idom: dict[BasicBlock, Optional[BasicBlock]]):
        dom_links: dict[str, list[BasicBlock]] = {}
        for bb, _idom in idom.items():
            if _idom is not None:
                dom_links.setdefault(_idom.label, []).append(bb)
        return { k: sorted(v, key=lambda bb: bb.label) for k, v in dom_links.items() }

class DominatorTree:
    def __init__(self, cfg: CFG):
        self.cfg = cfg
        self.dom = Cfg2Dom.convert(self.cfg)
        self.idom = Dom2Idom.convert(self.dom)
        self.dom_frontiers = Idom2Df.convert(self.idom)
        self.children = Idom2DomTree.convert(self.idom)
        """blocks under block `(subscripting bb)` in this Dominator tree
        """
