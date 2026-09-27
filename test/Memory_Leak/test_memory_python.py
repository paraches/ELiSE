import unittest
from memory_python import Memory


class MemoryPythonTestCase(unittest.TestCase):
    def test_memory_python(self):
        # setup
        memory = Memory()
        memory.dump_em()
        result = memory.ld16(memory.mem_free_list)
        expect = 0xC000
        self.assertEqual(expect, result)

        # i = Memory.alloc(3);
        i = memory.mem_alloc(3)
        memory.dump_em()

        result = i
        expect = 0xC004
        self.assertEqual(expect, result)

        result = memory.ld16(memory.mem_free_list)
        expect = 0xC00A
        self.assertEqual(expect, result)

        # j = Memory.alloc(5)
        j = memory.mem_alloc(5)
        memory.dump_em()

        result = j
        expect = 0xC00E
        self.assertEqual(expect, result)

        result = memory.ld16(memory.mem_free_list)
        expect = 0xC018
        self.assertEqual(expect, result)

        # Memory.deAlloc(j);
        memory.mem_dealloc(j)
        memory.dump_em()

        result = memory.ld16(memory.mem_free_list)
        expect = 0xC00A
        self.assertEqual(expect, result)

        # k = Memory.alloc(3);
        k = memory.mem_alloc(3)
        memory.dump_em()

        result = k
        expect = 0xC00E
        self.assertEqual(expect, result)

        result = memory.ld16(memory.mem_free_list)
        expect = 0xC018
        self.assertEqual(expect, result)

    def test_memory_python2(self):
        # setup
        memory = Memory()
        memory.dump_em()
        result = memory.ld16(memory.mem_free_list)
        expect = 0xC000
        self.assertEqual(expect, result)

        # i = Memory.alloc(2)
        # j = Memory.alloc(4)
        # Memory.deAlloc(i)
        # Memory.deAlloc(j)
        # k = Memory.alloc(4)
        i = memory.mem_alloc(2)
        j = memory.mem_alloc(4)
        memory.dump_em()
        memory.mem_dealloc(i)
        memory.mem_dealloc(j)
        memory.dump_em()    # Ok until this line
        k = memory.mem_alloc(4)
        memory.dump_em()
        result = k
        expect = 0xC00C
        self.assertEqual(expect, result)


if __name__ == '__main__':
    unittest.main()
