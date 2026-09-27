import os
from .SymbolTableCreator import SymbolTableCreator
from .Analyzer import Analyzer
from .AsmComposer import AsmComposer
from .DebugMetadata import DebugMetadataWriter
from .Util.file_lib import files_in_dir


def save_codes(file, codes, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    vm_file = os.path.join(output_dir, os.path.splitext(os.path.basename(file))[0] + '.vm')
    with open(vm_file, 'w') as sf:
        for line in codes:
            sf.write(line + '\n')


class Compiler:
    def __init__(self, env):
        self.env = env
        self.analyzer = None
        self.symbol_table = None
        self.symbols_file = None
        lib_names = self.find_lib()
        lib_names.append('MSXMath')
        self.env['libNames'] = lib_names

    def compile(self, directory=None):
        # set directory to compile
        if directory is None:
            directory = self.env['directory']
        else:
            self.env['directory'] = directory

        # create .els file list in directory
        if os.path.isdir(directory):
            files = files_in_dir(directory, 'els')
        else:
            files = [directory]
        output_dir = self.output_directory(directory)
        os.makedirs(output_dir, exist_ok=True)

        # create symbol table
        self.symbol_table = self.create_symbol_table(files)
        if self.env['verbose'] > 1:
            print(self.symbol_table)

        # parse
        error = False
        for file in files:
            error = self.start(file, output_dir)
            if error:
                return

        # asm
        asm_name = self.env.get('asm_name')
        if not asm_name:
            asm_name = os.path.basename(self.output_directory(directory)) + '.asm'
        asm_file_name = os.path.join(output_dir, asm_name)
        vm_files = files_in_dir(output_dir, 'vm')
        composer = AsmComposer(self.env)
        composer.compose(asm_file_name, vm_files)
        symbols_file_name = os.path.splitext(asm_file_name)[0] + '.symbols.json'
        self.symbols_file = symbols_file_name
        DebugMetadataWriter().write(
            asm_file_name,
            files,
            vm_files,
            symbols_file_name,
        )
        return asm_file_name

    def output_directory(self, directory):
        output_root = self.env.get('output')
        if output_root is None:
            output_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', 'build')
            )
        if os.path.isfile(directory):
            program_name = os.path.splitext(os.path.basename(directory))[0]
        else:
            program_name = os.path.basename(os.path.normpath(directory))
        return os.path.join(output_root, program_name)

    def assemble(self, asm_file):
        from .AssemblerAdapter import ZasmAssembler

        assembler = ZasmAssembler(self.env.get('assembler', 'zasm'))
        result = assembler.assemble(asm_file)
        if result.success and self.symbols_file and os.path.isfile(result.list_file):
            DebugMetadataWriter().attach_listing(self.symbols_file, result.list_file)
        return result

    def run(self, media_file):
        from .EmulatorAdapter import OpenMSXEmulator

        emulator = OpenMSXEmulator(
            self.env.get('openmsx', 'openmsx'),
            self.env.get('machine'),
        )
        return emulator.run(media_file, os.path.dirname(media_file), self.env.get('script'))

    def debug_script(self, breakpoints):
        from .OpenMSXDebugScript import OpenMSXDebugScript

        if not self.symbols_file:
            raise ValueError('Compile the program before creating a debug script')
        output_file = self.symbols_file.replace('.symbols.json', '.tcl')
        return OpenMSXDebugScript().generate(
            self.symbols_file,
            breakpoints,
            output_file,
        )

    def control(self, media_file):
        from .OpenMSXControl import OpenMSXControlSession

        return OpenMSXControlSession.launch(
            media_file,
            executable=self.env.get('openmsx', 'openmsx'),
            machine=self.env.get('machine'),
            script_file=self.env.get('script'),
            output_dir=os.path.dirname(media_file),
        )

    def create_symbol_table(self, files):
        creator = SymbolTableCreator()
        creator.add_library(self.env['lib'])
        for file in files:
            creator.create(file)
        return creator.table

    def start(self, file, output_dir):
        print('\n----------------------------------------------')
        print('compile: %s' % file)
        print('----------------------------------------------\n')
        self.analyzer = Analyzer(self.env)
        codes, error = self.analyzer.analyze(file, self.symbol_table)
        if error:
            print('\033[31mError occurred\033[0m')
        else:
            save_codes(file, codes, output_dir)
        return error

    def find_lib(self):
        current_directory = os.getcwd()
        lib_directory = os.path.join(current_directory, self.env['lib'])

        lib_files = files_in_dir(lib_directory, 'asm')
        if lib_files is None:
            print('No Library found...')
            return None
        lib_names = [os.path.basename(lib_file).split('.')[0] for lib_file in lib_files]
        print(lib_names)
        return lib_names
