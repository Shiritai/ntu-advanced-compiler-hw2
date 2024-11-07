from logger.logger import LoggedTestCase
from instruction.common import ValType, OpType
from instruction.compute import LogicOpType
from instruction.control import CtrlOpType

class InstTest(LoggedTestCase):
    def test_keys(self):
        self.assertSetEqual(set(ValType.cases().keys()),
                            { 'int', 'bool', 'unknown', 'undefined' })
        self.assertSetEqual(set(OpType.cases().keys()),
                            { 'const', 'add', 'sub',
                              'mul',   'div', 'eq',
                              'lt',    'gt',  'le',
                              'ge',    'not', 'and',
                              'or',    'jmp', 'br',
                              'call',  'ret', 'id',
                              'print', 'nop', 'phi'})
  
    def test_property(self):
        self.assertEqual(LogicOpType.NOT.nargs, 1)
        self.assertEqual(LogicOpType.AND.nargs, 2)

        self.assertFalse(CtrlOpType.CALL.is_block_terminator)
        self.assertTrue(CtrlOpType.RET.is_block_terminator)
        self.assertTrue(CtrlOpType.BR.is_block_terminator)
        self.assertTrue(CtrlOpType.JMP.is_block_terminator)
        
  
    def test_classmethod(self):
        self.assertEqual(set(ValType.all_py_types()), set((bool, int, None)))
