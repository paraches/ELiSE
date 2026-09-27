from .Tokenizer import Tokenizer
from .Parser import Parser


class Analyzer:
    def __init__(self, env=None):
        self.tokens_list = []
        self.env = env
        self.parser = Parser(env)

    def analyze(self, file, symbol_table):
        tokens = Tokenizer().tokenize(file)
        writer = self.load_vm_writer(self.env)
        result = self.parser.parse(tokens, symbol_table, writer)
        return result

    def load_vm_writer(self, env):
        from . import VMWriter
        vm_writer_vars = vars(VMWriter)
        writer = {key[3:]: vm_writer_vars[key] for key in vm_writer_vars if key.startswith('vm_') }
        if env['verbose'] > 0:
            print('Read following functions:\n%s\n' % [x for x in writer.keys()])
        return writer
