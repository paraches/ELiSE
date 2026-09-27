from .ASMTranslator import ASMTranslator
from .SystemLibrary import work_area, end_code
from .BootLibrary import lib_code as boot_lib
from .Util.file_lib import files_in_dir

import os
import re


class AsmComposer:
    implicit_library_dependencies = {
        'Array': {'Memory'},
        'Debug': {'Output', 'System'},
        'Keyboard': {'Output', 'String'},
        'Memory': {'MSX'},
        'Output': {'MSX'},
        'Screen': {'MSX'},
        'Sprite': {'MSX'},
        'String': {'Memory'},
    }

    def __init__(self, env):
        self.env = env
        self.translator = ASMTranslator(env)
        self.asm_codes = []
        self.static_list = []
        self.string_dic = {}
        self.data_dic = {}

    def compose(self, asm_file_name, vm_files, env=None):
        if env is not None:
            self.env = env

        # translate all .vm file to assembler code
        for vm_file in vm_files:
            self.asm_translate(vm_file)

        # compose assembler code with boot, system, library and work
        self.asm_link(asm_file_name)

    #
    # translate .vm file to assembler code
    #   asm_code:       assembler code
    #   static_list:    static var list
    #   string_dic:     string label and value dictionary
    #   data_dic:       data label and value dictionary
    #
    def asm_translate(self, vm_file):
        asm_code, statics, strings, data = self.translator.translate(vm_file)
        self.asm_codes.extend(asm_code)
        self.static_list.extend(statics)
        self.string_dic.update(strings)
        self.data_dic.update(data)

    #
    #   write everything with asm_file_bame
    def asm_link(self, asm_file_name):
        if self.env['verbose'] > 0:
            print('\n----------------------------------------------')
            print('AsmComposer.asm_link: %s' % asm_file_name)
            print('----------------------------------------------\n')
        with open(asm_file_name, 'w') as sf:
            self.boot_write(sf)
            self.code_write(sf)
            self.lib_write(sf)
            self.work_write(sf, self.static_list, self.string_dic, self.data_dic)
            self.end_write(sf)

    #
    #   write boot code and header
    def boot_write(self, sf):
        if self.env['verbose'] > 0:
            print('boot code')
        boot_code = boot_lib(self.env)
        self.write_list(sf, boot_code)

    #
    #   write assembler code in list
    def code_write(self, sf):
        if self.env['verbose'] > 0:
            print('code')
        self.asm_codes.append('\n\n')
        self.write_list(sf, self.asm_codes)

    #
    #   write libraries
    def lib_write(self, sf):
        libraries = files_in_dir(self.env['lib'], 'asm')
        link_libs = self.env.get('link_libs')
        if link_libs is not None:
            libraries = [
                library for library in libraries
                if os.path.basename(library) in link_libs
            ]
        elif self.env.get('auto_link_libs', False):
            libraries = self.auto_link_libraries(libraries)
        if self.env['verbose'] > 0:
            print('libraries:')
            for lib in libraries:
                print(lib)
        for lib_name in libraries:
            if not self.env['db'] and os.path.basename(lib_name) == 'Debug.asm':
                continue
            with open(lib_name, 'r') as readfile:
                sf.write(readfile.read() + '\n\n')

    def auto_link_libraries(self, libraries):
        """Keep only libraries referenced by VM code or library dependencies."""
        library_by_class = {
            os.path.splitext(os.path.basename(path))[0]: path
            for path in libraries
        }
        required = set()
        pending = ['System']

        for line in self.asm_codes:
            match = re.match(
                r'^\s*(?:call|jp)\s+([A-Za-z_][A-Za-z0-9_]*)\.',
                line,
            )
            if match and match.group(1) in library_by_class:
                pending.append(match.group(1))

        while pending:
            class_name = pending.pop()
            if class_name in required:
                continue
            if class_name not in library_by_class:
                continue
            required.add(class_name)
            for dependency in self.implicit_library_dependencies.get(class_name, set()):
                pending.append(dependency)
            with open(library_by_class[class_name], 'r') as library_file:
                for line in library_file:
                    match = re.match(
                        r'^\s*(?:call|jp)\s+([A-Za-z_][A-Za-z0-9_]*)\.',
                        line,
                    )
                    if match and match.group(1) in library_by_class:
                        pending.append(match.group(1))

        return [
            library
            for library in libraries
            if os.path.splitext(os.path.basename(library))[0] in required
        ]

    #
    #   work area write
    def work_write(self, sf, static_list, string_dic, data_dic):
        if self.env['verbose'] > 0:
            print('work area')
            print('\tstatic: %d' % len(static_list))
            print('\tstring: %d' % len(string_dic))
            print('\tdata: %d' % len(data_dic))
        work_area_code = work_area(self.env, static_list, string_dic, data_dic)
        self.write_list(sf, work_area_code)

    #
    #   end code
    def end_write(self, sf):
        if self.env['verbose'] > 0:
            print('end code')
        self.write_list(sf, end_code(self.env))

    def write_list(self, file, asm_code):
        for line in asm_code:
            if len(line) > 0 and ':' not in line:  # need to care comment which contain `:`
                line = '\t\t\t' + line
            file.write(line + '\n')
