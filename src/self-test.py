import os
import random
import subprocess
import sys
from typing import Optional
from unittest import TextTestRunner, TestSuite, defaultTestLoader
from cfg import CFG, BasicBlock
from bril import Const, ValueOperation, parse_bril, serialize_bril
from is_ssa import is_ssa
from instruction.instruction import Instruction
from instruction.value import CoreValType
from instruction.ssa import SsaOpType
from logger.logger import logger
from ssa_construct import collect_definitions, construct_ssa, def2global_d2b, insert_phi_functions, reconstruct_instructions, rename_variables
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

script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
example_path = os.path.realpath(f"{script_dir}/../tests/example.bril")

def load_program(bril_file: Optional[str] = None):
    bril_file = bril_file if bril_file is not None else example_path
    with open(bril_file, "r") as f:
        res = subprocess.run(["bril2json"], stdin=f, stdout=subprocess.PIPE)
        return parse_bril(res.stdout)

def load_args(bril_file: Optional[str] = None):
    bril_file = bril_file if bril_file is not None else example_path
    with open(bril_file, "r") as f:
        line = f.readline()
        if line.startswith("# ARGS: "):
            return line.strip("# ARGS: ").split()
    return None

def load_golden_program(bril_file: Optional[str]):
    bril_file = bril_file if bril_file is not None else example_path
    with open(bril_file, "r") as f:
        res = subprocess.run(["bril2json"], stdin=f, stdout=subprocess.PIPE)
        p = subprocess.Popen(["python3", f"{script_dir}/../bril/examples/to_ssa.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        res, _ = p.communicate(input=res.stdout)
        return parse_bril(res.decode())

def find_all_bril(entry: str):
    res = []
    def _traverse(entry: str):
        if entry.endswith('.bril'):
            res.append(entry)
        elif os.path.isdir(entry):
            for e in os.listdir(entry):
                _traverse(f"{entry}/{e}")
    _traverse(entry)
    return res
            
def bb2labels(s: set[BasicBlock]):
    return set(bb.label for bb in s)

class CfgTest(LoggedTestCase):

    def test_make_cfg(self):
        program = load_program()
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
        program = load_program()
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
        program = load_program()
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
        program = load_program()
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
        program = load_program()
        cfg = CFG(program.functions[0])
        defs, global_names, _ = collect_definitions(cfg)
        asq = self.assertSetEqual
        # check def blocks
        asq(bb2labels(defs['i'][0]), set(('b0', 'b3')))
        asq(bb2labels(defs['a'][0]), set(('b1', 'b5')))
        asq(bb2labels(defs['b'][0]), set(('b2', 'b7')))
        asq(bb2labels(defs['c'][0]), set(('b1', 'b2', 'b8')))
        asq(bb2labels(defs['d'][0]), set(('b2', 'b5', 'b6')))
        asq(bb2labels(defs['y'][0]), set(('b3',)))
        asq(bb2labels(defs['z'][0]), set(('b3',)))
        asq(bb2labels(defs['hundred'][0]), set(('b3',)))
        asq(bb2labels(defs['cond'][0]), set(('b1',)))
        asq(bb2labels(defs['cond2'][0]), set(('b3',)))
        asq(bb2labels(defs['cond3'][0]), set(('b5',)))
        # check def type
        self.assertEqual(defs['i'][1], CoreValType.INT)
        self.assertEqual(defs['a'][1], CoreValType.INT)
        self.assertEqual(defs['b'][1], CoreValType.INT)
        self.assertEqual(defs['c'][1], CoreValType.INT)
        self.assertEqual(defs['d'][1], CoreValType.INT)
        self.assertEqual(defs['y'][1], CoreValType.INT)
        self.assertEqual(defs['z'][1], CoreValType.INT)
        self.assertEqual(defs['hundred'][1], CoreValType.INT)
        self.assertEqual(defs['cond'][1], CoreValType.BOOL)
        self.assertEqual(defs['cond2'][1], CoreValType.BOOL)
        self.assertEqual(defs['cond3'][1], CoreValType.BOOL)
        asq(global_names, set(('i', 'a', 'b', 'c', 'd')))

        global_d2b = def2global_d2b(defs, global_names)
        asq(bb2labels(global_d2b['i'][0]), set(('b0', 'b3')))
        asq(bb2labels(global_d2b['a'][0]), set(('b1', 'b5')))
        asq(bb2labels(global_d2b['b'][0]), set(('b2', 'b7')))
        asq(bb2labels(global_d2b['c'][0]), set(('b1', 'b2', 'b8')))
        asq(bb2labels(global_d2b['d'][0]), set(('b2', 'b5', 'b6')))

    def test_insert_phi(self):
        program = load_program()
        cfg = CFG(program.functions[0])
        defs, global_names, _ = collect_definitions(cfg)
        global_d2b = def2global_d2b(defs, global_names)
        dom_tree = DominatorTree(cfg)
        insert_phi_functions(dom_tree, global_d2b)

        def check_phi_for_var(var: str, golden: set[str]):
            bbs = set()
            for bb in cfg.blocks.values():
                for i in bb.insts:
                    if isinstance(i, ValueOperation) and i.op == SsaOpType.PHI and i.dest == var:
                        bbs.add(bb.label)
            self.assertSetEqual(bbs, golden)
        
        check_phi_for_var('a', { 'b1', 'b3' })
        check_phi_for_var('b', { 'b1', 'b3' })
        check_phi_for_var('c', { 'b1', 'b3', 'b7' })
        check_phi_for_var('d', { 'b1', 'b3', 'b7' })
        check_phi_for_var('i', { 'b1' })

    def test_dom_tree_links(self):
        program = load_program()
        cfg = CFG(program.functions[0])
        dom_tree = DominatorTree(cfg)
        bb2label_ls = lambda ls: list(bb.label for bb in ls)
        dc = dom_tree.children
        self.assertEqual(bb2label_ls(dc['b0']), ['b1'])
        self.assertEqual(bb2label_ls(dc['b1']), ['b2', 'b3', 'b5'])
        self.assertEqual(dc.get('b2'), None)
        self.assertEqual(bb2label_ls(dc['b3']), ['b4'])
        self.assertEqual(dc.get('b4'), None)
        self.assertEqual(bb2label_ls(dc['b5']), ['b6', 'b7', 'b8'])
        self.assertEqual(dc.get('b6'), None)
        self.assertEqual(dc.get('b7'), None)
        self.assertEqual(dc.get('b8'), None)

    def test_rename_runnable(self):
        program = load_program()
        cfg = CFG(program.functions[0])
        defs, global_names, _ = collect_definitions(cfg)
        global_d2b = def2global_d2b(defs, global_names)
        dom_tree = DominatorTree(cfg)
        insert_phi_functions(dom_tree, global_d2b)
        rename_variables(cfg, dom_tree, defs, global_names)

def ssa_checker(cfg1: CFG, cfg2: CFG):
    name_map: dict[str, str] = {}
    for bb1, bb2 in zip(cfg1.blocks.values(), cfg2.blocks.values()):
        for i1, i2 in zip(sorted(bb1.get_by_op(SsaOpType.PHI), key=lambda i: i.dest),
                          sorted(bb2.get_by_op(SsaOpType.PHI), key=lambda i: i.dest)):
            if isinstance(i1, (ValueOperation, Const)):
                if (not isinstance(i2, (ValueOperation, Const)) or
                    i1.op != i2.op):
                    err = ValueError(f"Unequal CFGs (inst type not match): {i1} can't map to {i2}")
                    logger.error(err)
                    raise err
                if i1.dest in name_map:
                    err = ValueError(f"CFG1 is not in SSA form: duplicated {i1.dest}")
                    logger.error(err)
                    raise err
                if i2.dest in name_map.values() is not None:
                    err = ValueError(f"CFG2 is not in SSA form: duplicated {i2.dest}")
                    logger.error(err)
                    raise err
                name_map[i1.dest] = i2.dest
                    
    for bb1, bb2 in zip(cfg1.blocks.values(), cfg2.blocks.values()):
        for i1, i2 in zip(list(i for i in bb1.insts if i.op != SsaOpType.PHI),
                          list(i for i in bb2.insts if i.op != SsaOpType.PHI)):
            if isinstance(i1, (ValueOperation, Const)) and isinstance(i2, (ValueOperation, Const)):
                name_map[i1.dest] = i2.dest
                    
    for bb1, bb2 in zip(cfg1.blocks.values(), cfg2.blocks.values()):
        for i1, i2 in zip(list(i for i in bb1.insts if i.op != SsaOpType.PHI),
                          list(i for i in bb2.insts if i.op != SsaOpType.PHI)):
            if i1.op != i2.op:
                err = ValueError(f"Can't map [op] {i1} to {i2}")
                logger.error(err)
                cfg1.view_blocks()
                cfg2.view_blocks()
                raise err
            if hasattr(i1, 'type'):
                if not hasattr(i2, 'type') or i1.type != i2.type:
                    err = ValueError(f"Can't map [type] {i1} to {i2}")
                    logger.error(err)
                    raise err
            if hasattr(i1, 'value'):
                if not hasattr(i2, 'value') or i1.value != i2.value:
                    err = ValueError(f"Can't map [value] {i1} to {i2}")
                    logger.error(err)
                    raise err
            if hasattr(i1, 'dest'):
                if not hasattr(i2, 'dest') or i1.dest not in name_map or name_map[i1.dest] != i2.dest:
                    cfg1.view_blocks()
                    cfg2.view_blocks()
                    err = ValueError(f"Can't map [dest] {i1} to {i2}")
                    logger.error(err)
                    raise err
            if hasattr(i1, 'args') and i1.args is not None:
                if not hasattr(i2, 'args') or i2.args is None:
                    err = ValueError(f"Can't map [args] {i1} to {i2}")
                    logger.error(err)
                    raise err
                else:
                    for arg1, arg2 in zip(i1.args, i2.args):
                        if name_map[arg1] != arg2:
                            err = ValueError(f"Can't map [args] {i1} to {i2}")
                            logger.error(err)
                            raise err
            if hasattr(i1, 'funcs'):
                if not hasattr(i2, 'funcs'):
                    err = ValueError(f"Can't map [funcs] {i1} to {i2}")
                    logger.error(err)
                    raise err
                else:
                    if i1.funcs != i2.funcs:
                        err = ValueError(f"Can't map [funcs] {i1} to {i2}")
                        logger.error(err)
                        raise err

class SsaCheckerTest(LoggedTestCase):
    def test_example(self):
        program = load_program()
        cfg1 = CFG(program.functions[0])
        defs, global_names, _ = collect_definitions(cfg1)
        global_d2b = def2global_d2b(defs, global_names)
        dom_tree = DominatorTree(cfg1)
        insert_phi_functions(dom_tree, global_d2b)
        rename_variables(cfg1, dom_tree, defs, global_names)
        
        if not is_ssa(program):
            err = ValueError(f"Program is not in ssa form")
            logger.error(err)
            raise err
        
        program = load_program()
        cfg2 = CFG(program.functions[0])
        defs, global_names, _ = collect_definitions(cfg2)
        global_d2b = def2global_d2b(defs, global_names)
        dom_tree = DominatorTree(cfg2)
        insert_phi_functions(dom_tree, global_d2b)
        rename_variables(cfg2, dom_tree, defs, global_names)
        
        ssa_checker(cfg1, cfg2)

        def rename_var(i: Instruction, a: str, b: str):
            if hasattr(i, 'dest') and i.dest == a:
                i.dest = b
            if hasattr(i, 'args') and i.args is not None:
                for arg_idx in range(len(i.args)):
                    if i.args[arg_idx] == a:
                        i.args[arg_idx] = b
            
        # rename some variables in cfg2
        for bb in cfg2.blocks.values():
            for i in bb.insts:
                rename_var(i, 'a.2', 'a.meow')
        
        ssa_checker(cfg1, cfg2)
    
    def test_execute(self):
        program = load_program()
        json_input = serialize_bril(program)
        p = subprocess.Popen(["brili"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        golden = p.communicate(input=json_input.encode())
        
        for func in program.functions:
            cfg = CFG(func)
            defs, global_names, _ = collect_definitions(cfg)
            dom_tree = DominatorTree(cfg)
            insert_phi_functions(dom_tree, defs)
            rename_variables(cfg, dom_tree, defs, global_names)
            func.instrs = reconstruct_instructions(cfg)
        
        json_output = serialize_bril(program)
        p = subprocess.Popen(["brili"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        _ = p.communicate(input=json_output.encode())

def test_brils(path: str):
    brils = find_all_bril(path)
    failed = []
    for bril_file in brils:
        logger.debug(f"Test {bril_file}")
        program = load_program(bril_file)
        cmd = ["brili"]
        args = load_args(bril_file)
        if args is not None:
            cmd.extend(args)

        json_input = serialize_bril(program)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        golden = p.communicate(input=json_input.encode())
        for func1 in program.functions:
            logger.debug(f"Test function {func1.name}")
            logger.flush()
            construct_ssa(func1)
        if not is_ssa(program):
            err = ValueError(f"Program is not in ssa form")
            logger.error(err)
            raise err
        json_output = serialize_bril(program)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        attempt = p.communicate(input=json_output.encode())
        if golden != attempt:
            err = ValueError(f"Computation comparison does not match\n\tGolden: <{                golden[0].decode().strip()}>\n\tAttempt: <{                attempt[0].decode().strip()}>")
            failed.append(err)
    if len(failed) > 0:
        for err in failed:
            logger.error(err)
        raise ValueError(f"Errors: {failed}")

class IntegrationTest(LoggedTestCase):
    def test_advanced_integration(self):
        advanced_tests = os.path.realpath(f"{script_dir}/../bril/examples/test")
        test_brils(advanced_tests)

    def test_basic_integration(self):
        basic_tests = os.path.realpath(f"{script_dir}/../tests")
        test_brils(basic_tests)
                
class GradeTest(LoggedTestCase):
    def test_grade(self):
        basic_tests = os.path.realpath(f"{script_dir}/../tests")
        brils = find_all_bril(basic_tests)
        for bril in brils:
            res = subprocess.run([f"{script_dir}/../run_test_case.sh", bril], stdout=subprocess.PIPE)
            out = res.stdout.decode()
            if 'Not SSA' in out or 'passed' not in out:
                logger.warn(res.stdout.decode())
            
if __name__ == '__main__':
    cases = (LoggerTest, BasicBlockTest, InstTest,
             CfgTest, DomTest, SsaTest,
             SsaCheckerTest,
             IntegrationTest,
             GradeTest)
    suites = TestSuite(defaultTestLoader.loadTestsFromTestCase(t)
                       for t in cases)
    res = TextTestRunner().run(suites)
