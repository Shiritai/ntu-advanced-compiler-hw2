import os
import subprocess
import sys
from unittest import TextTestRunner, TestSuite, defaultTestLoader
from cfg import CFG, BasicBlock
from bril import parse_bril
from ssa_construct import collect_definitions
from dominance import Cfg2Dom, Dom2Idom, DominatorTree, Idom2Df
from logger.logger import LoggedTestCase
from logger.test import LoggerTest
from instruction.test import InstTest

class BasicBlockTest(LoggedTestCase):
    def test_eq(self):
        b1 = BasicBlock('b1')
        b2 = b1
        self.assertEqual(b1, b2)
        b3 = BasicBlock('b1')
        self.assertNotEqual(b1, b3)

    def test_hash(self):
        b1 = BasicBlock('b1')
        bb_set = { b1 }
        bb_set2 = { b1 }
        self.assertSetEqual(bb_set, bb_set2)

def load_example_program():
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    test_bril = os.path.realpath(f"{script_dir}/../tests/example.bril")
    
    with open(test_bril, "r") as f:
        res = subprocess.run(["bril2json"], stdin=f, stdout=subprocess.PIPE)
        return parse_bril(res.stdout)

def bb2labels(s: set[BasicBlock]):
    return set(bb.label for bb in s)

class CfgTest(LoggedTestCase):

    def test_make_cfg(self):
        program = load_example_program()
        self.assertEqual(len(program.functions), 1)
        cfg = CFG(program.functions[0])
        self.assertEqual(cfg.entry_block.label, 'b0')
        
        asq = self.assertSetEqual  # alias
        asq(bb2labels(cfg.blocks.values()),
                      set(('b0', 'b1', 'b2', 'b3', 'b4',
                           'b5', 'b6', 'b7', 'b8')))
        asq(bb2labels(cfg.blocks['b0'].preds), set())
        asq(bb2labels(cfg.blocks['b0'].succs), set(('b1',)))
        asq(bb2labels(cfg.blocks['b1'].preds), set(('b0', 'b3')))
        asq(bb2labels(cfg.blocks['b1'].succs), set(('b2', 'b5')))
        asq(bb2labels(cfg.blocks['b2'].preds), set(('b1',)))
        asq(bb2labels(cfg.blocks['b2'].succs), set(('b3',)))
        asq(bb2labels(cfg.blocks['b3'].preds), set(('b2', 'b7')))
        asq(bb2labels(cfg.blocks['b3'].succs), set(('b4', 'b1')))
        asq(bb2labels(cfg.blocks['b4'].preds), set(('b3',)))
        asq(bb2labels(cfg.blocks['b4'].succs), set())
        asq(bb2labels(cfg.blocks['b5'].preds), set(('b1',)))
        asq(bb2labels(cfg.blocks['b5'].succs), set(('b6', 'b8')))
        asq(bb2labels(cfg.blocks['b6'].preds), set(('b5',)))
        asq(bb2labels(cfg.blocks['b6'].succs), set(('b7',)))
        asq(bb2labels(cfg.blocks['b7'].preds), set(('b6', 'b8')))
        asq(bb2labels(cfg.blocks['b7'].succs), set(('b3',)))
        asq(bb2labels(cfg.blocks['b8'].preds), set(('b5',)))
        asq(bb2labels(cfg.blocks['b8'].succs), set(('b7',)))

class DomTest(LoggedTestCase):
    def test_make_dom(self):
        program = load_example_program()
        self.assertEqual(len(program.functions), 1)
        cfg = CFG(program.functions[0])
        dom = Cfg2Dom.convert(cfg)
        label_dom = dict(map(lambda kv: (kv[0].label, kv[1]), dom.items()))
        asq = self.assertSetEqual
        asq(bb2labels(label_dom['b0']), set(('b0',)))
        asq(bb2labels(label_dom['b1']), set(('b0', 'b1')))
        asq(bb2labels(label_dom['b2']), set(('b0', 'b1', 'b2')))
        asq(bb2labels(label_dom['b3']), set(('b0', 'b1', 'b3')))
        asq(bb2labels(label_dom['b4']), set(('b0', 'b1', 'b3', 'b4')))
        asq(bb2labels(label_dom['b5']), set(('b0', 'b1', 'b5')))
        asq(bb2labels(label_dom['b6']), set(('b0', 'b1', 'b5', 'b6')))
        asq(bb2labels(label_dom['b7']), set(('b0', 'b1', 'b5', 'b7')))
        asq(bb2labels(label_dom['b8']), set(('b0', 'b1', 'b5', 'b8')))

    def test_make_idom(self):
        program = load_example_program()
        cfg = CFG(program.functions[0])
        dom = Cfg2Dom.convert(cfg)
        idom = Dom2Idom.convert(dom)
        label_dom = dict(map(lambda kv: (kv[0].label, kv[1]), idom.items()))
        self.assertEqual(label_dom['b0'], None)
        self.assertEqual(label_dom['b1'].label, 'b0')
        self.assertEqual(label_dom['b2'].label, 'b1')
        self.assertEqual(label_dom['b3'].label, 'b1')
        self.assertEqual(label_dom['b4'].label, 'b3')
        self.assertEqual(label_dom['b5'].label, 'b1')
        self.assertEqual(label_dom['b6'].label, 'b5')
        self.assertEqual(label_dom['b7'].label, 'b5')
        self.assertEqual(label_dom['b8'].label, 'b5')

    def test_make_df(self):
        program = load_example_program()
        cfg = CFG(program.functions[0])
        dom = Cfg2Dom.convert(cfg)
        idom = Dom2Idom.convert(dom)
        df = Idom2Df.convert(idom)
        label_dom = dict(map(lambda kv: (kv[0].label, kv[1]), df.items()))
        asq = self.assertSetEqual
        asq(bb2labels(label_dom['b0']), set())
        asq(bb2labels(label_dom['b1']), set(('b1',)))
        asq(bb2labels(label_dom['b2']), set(('b3',)))
        asq(bb2labels(label_dom['b3']), set(('b1',)))
        asq(bb2labels(label_dom['b4']), set())
        asq(bb2labels(label_dom['b5']), set(('b3',)))
        asq(bb2labels(label_dom['b6']), set(('b7',)))
        asq(bb2labels(label_dom['b7']), set(('b3',)))
        asq(bb2labels(label_dom['b8']), set(('b7',)))

class SsaTest(LoggedTestCase):
    def test_collect_definitions(self):
        program = load_example_program()
        cfg = CFG(program.functions[0])
        global_names, defs, _ = collect_definitions(cfg)
        asq = self.assertSetEqual
        asq(defs['i'], set(('b0', 'b3')))
        asq(defs['a'], set(('b1', 'b5')))
        asq(defs['b'], set(('b2', 'b7')))
        asq(defs['c'], set(('b1', 'b2', 'b8')))
        asq(defs['d'], set(('b2', 'b5', 'b6')))
        asq(defs['y'], set(('b3',)))
        asq(defs['z'], set(('b3',)))
        asq(defs['hundred'], set(('b3',)))
        asq(defs['cond'], set(('b1',)))
        asq(defs['cond2'], set(('b3',)))
        asq(defs['cond3'], set(('b5',)))
        asq(global_names, set(('i', 'a', 'b', 'c', 'd')))

if __name__ == '__main__':
    cases = (LoggerTest, BasicBlockTest, InstTest, CfgTest, DomTest, SsaTest)
    suites = TestSuite(defaultTestLoader.loadTestsFromTestCase(t)
                       for t in cases)
    res = TextTestRunner().run(suites)
