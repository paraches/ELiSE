import os
import re
from .Util.file_lib import change_file_ext
from .AsmWriter import AsmWriter

#command_list = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not', 'pop', 'push', 'label', 'goto',
#                'if-goto', 'function', 'return', 'call', 'lib_call', 'lib_ret_address', 'data']


class ASMTranslator:
    def __init__(self, env=None):
        self.writer = None
        self.vm_files = []
        self.env = env

    def translate(self, file):
        if self.env['verbose'] > 0:
            print('\n----------------------------------------------')
            print('AsmTranslator: %s' % file)
            print('----------------------------------------------\n')
        file_body, ext = os.path.splitext(os.path.basename(file))
        if ext != '.vm':
            return
        with open(file, 'r') as f:
            asm_file = change_file_ext(file, 'asm')
            self.writer = AsmWriter(asm_file, self.env)
            write_dic = self.writer.code_dic()
            parser = AsmParser(f, write_dic.keys())
            while parser.has_more_command():
                command, args = parser.get_command()
                if self.env['verbose'] > 0:
                    print('%s, %s' % (command, args))
                self.writer.set_source_location(parser.current_source_location)
                write_dic[command](args)
        return self.writer.codes, self.writer.static_list, self.writer.string_dic, self.writer.data_dic


class AsmParser:
    def __init__(self, file, command_list):
        self.current_line_index = 0
        self.lines = []
        self.command_list = command_list
        self.source_locations = []
        self.current_source_location = None
        pending_source = None
        for vm_line_number, line in enumerate(file, start=1):
            source_match = re.match(
                r'^\s*//\s*source\s+(\d+)\s+(\S+)',
                line,
            )
            if source_match:
                pending_source = {
                    'source_line': int(source_match.group(1)),
                    'function': source_match.group(2),
                    'vm_line': vm_line_number + 1,
                }
                continue
            if '"' in line:
                line, quotes = self.do_quote(line)
                print(quotes)
            else:
                quotes = None
            items = [item.strip() for item in line.strip().split() if len(item.strip()) > 0]
            if len(items) > 0 and (items[0] != '//'):
                if quotes is not None:
                    for item_num in range(0, len(items)):
                        if items[item_num] in quotes:
                            items[item_num] = quotes[items[item_num]]
                self.lines.append(items)
                self.source_locations.append(pending_source)
                pending_source = None

    def has_more_command(self):
        return len(self.lines) > self.current_line_index

    def get_command(self):
        line = self.lines[self.current_line_index]
        self.current_source_location = self.source_locations[self.current_line_index]
        self.advance()
        return self.parse(line)

    def parse(self, line):
        if len(line) < 1:
            print('line have no item.')
            return
        command = line[0]
        if command not in self.command_list:
            print('%s is not command' % command)
        return command, line[1:]

    def advance(self):
        self.current_line_index = self.current_line_index + 1

    def do_quote(self, line):
        string_table = {}
        string_number = 0
        string_range = [pos for pos, char in enumerate(line) if char == '"']
        while len(string_range) > 1:
            left = string_range[0]
            right = string_range[1]
            string_value = line[left + 1: right]
            string_constant = 'STRING_CONSTANT_%d' % string_number
            line = line.replace(string_value, string_constant)
            string_table['"' + string_constant + '"'] = string_value
            string_number = string_number + 1
            string_range.remove(left)
            string_range.remove(right)
        return line, string_table
