import unittest
import elise
from elise.Compiler import Compiler


class CompilerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        env = elise.ELISE_ENV
        env['lib'] = '../Lib'
        self.compiler = Compiler(env)

    def test_seven(self):
        self.compiler.compile('Seven')
        with open('../build/Seven/Seven.asm') as asm_file:
            asm_code = asm_file.read()
        self.assertIn('Output.printInt:', asm_code)
        self.assertIn('Sys.return:', asm_code)
        self.assertNotIn('Memory.alloc:', asm_code)
        self.assertNotIn('Screen.locate:', asm_code)

    def test_seven_cartridge(self):
        env = elise.ELISE_ENV_CARTRIDGE
        env['lib'] = '../Lib'
        self.compiler = Compiler(env)
        self.compiler.compile('Seven')

    def test_func_arguments(self):
        self.compiler.compile('Func_Arguments')

    def test_while_if_local(self):
        self.compiler.compile('While_If_Local')

    def test_memory(self):
        self.compiler.compile('Memory')

    def test_array(self):
        self.compiler.compile('Array')

    def test_string(self):
        self.compiler.compile('String')

    def test_trigger(self):
        self.compiler.compile('Trigger')

    def test_average(self):
        self.compiler.compile("Average")

    def test_easy_class(self):
        self.compiler.compile('Easy_Class')

    def test_else_if(self):
        self.compiler.compile('ELSE_IF')

    def test_x2(self):
        self.compiler.compile('x2')

    def test_shift(self):
        self.compiler.compile('Shift')
        with open('../build/Shift/Main.vm') as vm_file:
            vm_code = vm_file.read()
        self.assertIn('shl_const 3', vm_code)
        self.assertIn('shl_const 4', vm_code)
        self.assertIn('shr_const 4', vm_code)
        self.assertIn('\nshr\n', '\n' + vm_code + '\n')
        self.assertEqual(vm_code.count('call MSXMath.multiply 2'), 1)

    def test_memory_leak(self):
        env = elise.ELISE_ENV
        env['heap_start'] = 0xC000
        self.compiler = Compiler(env)
        self.compiler.compile('Memory_Leak')

    def test_memory_leak_2(self):
        env = elise.ELISE_ENV
        env['heap_start'] = 0xC000
        self.compiler = Compiler(env)
        self.compiler.compile('Memory_Leak_2')

    def test_square(self):
        self.compiler.compile('Square')

    def test_sound3(self):
        self.compiler.compile('Sound3')
        with open('../build/Sound3/Sound3.asm') as asm_file:
            asm_code = asm_file.read()
        self.assertIn('Sound.play3:', asm_code)
        self.assertIn('ld a, 0xb8', asm_code)
        self.assertIn('ld a, 0xbf', asm_code)
        self.assertIn('sound_remaining_a:', asm_code)
        self.assertIn('sound_remaining_b:', asm_code)
        self.assertIn('sound_remaining_c:', asm_code)
        self.assertIn('Timer.waitFrames.next:', asm_code)
        self.assertIn('Timer.waitFrames.delay:', asm_code)
        self.assertNotIn('Timer.waitFrames.poll:', asm_code)
        self.assertNotIn('\n\t\t\thalt\n', asm_code)

    def test_breakout2_example(self):
        env = dict(elise.ELISE_ENV_CARTRIDGE)
        env['lib'] = '../Lib'
        self.compiler = Compiler(env)
        self.compiler.compile('../examples/Breakout2')
        with open('../build/Breakout2/Breakout2.asm') as asm_file:
            asm_code = asm_file.read()
        self.assertIn('Sound.playB:', asm_code)
        self.assertIn('Sound.playAC:', asm_code)
        self.assertIn('jp Sound.playB', asm_code)
        self.assertIn('jp Sound.playAC', asm_code)
        self.assertNotIn('jp Sound.playC', asm_code)
        self.assertIn('Breakout2.updateMusic:', asm_code)
        self.assertIn('Sound._enableB:', asm_code)
        self.assertIn('and 0xfd', asm_code)
        self.assertIn('and 0xfa', asm_code)


if __name__ == '__main__':
    unittest.main()
