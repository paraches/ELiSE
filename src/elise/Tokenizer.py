from .Token import Token


ptl1_tokens = {
    'class': 'keyword',
    'constructor': 'keyword',
    'function': 'keyword',
    'method': 'keyword',
    'field': 'keyword',
    'static': 'keyword',
    'var': 'keyword',
    'int': 'keyword',
    'char': 'keyword',
    'boolean': 'keyword',
    'void': 'keyword',
    'true': 'keyword',
    'false': 'keyword',
    'null': 'keyword',
    'this': 'keyword',
    # 'let': 'keyword',
    # 'do': 'keyword',
    'if': 'keyword',
    'elif': 'keyword',
    'else': 'keyword',
    'while': 'keyword',
    'return': 'keyword',
    'dat': 'keyword',
    'db': 'keyword',
    'dw': 'keyword',
    'ds': 'keyword',
    '{': 'symbol',
    '}': 'symbol',
    '(': 'symbol',
    ')': 'symbol',
    '[': 'symbol',
    ']': 'symbol',
    '.': 'symbol',
    ',': 'symbol',
    ';': 'symbol',
    '+': 'symbol',
    '-': 'symbol',
    '*': 'symbol',
    '/': 'symbol',
    '&': 'symbol',
    '|': 'symbol',
    '<': 'symbol',
    '>': 'symbol',
    '=': 'symbol',
    '~': 'symbol',
    '%': 'symbol',
    '_GE_': 'symbol',
    '_LE_': 'symbol',
    '_NE_': 'symbol',
    '_DEC_': 'symbol',
    '_INC_': 'symbol',
    '_LSHIFT_': 'symbol',
    '_RSHIFT_': 'symbol',
    '_EQUAL_': 'symbol',
    '"': 'quote',
}
space_tokens = ['(', ')', '[', ']', '{', '}', ';', '"', ',', '.', '~', '+', '-', '*', '/', '<', '>', '=',
                '_LE_', '_GE_', '_NE_', '_DEC_', '_INC_', '_LSHIFT_', '_RSHIFT_']
change_operators = {'==': '_EQUAL_', '<=': '_LE_', '>=': '_GE_', '!=': '_NE_', '--': '_DEC_', '++': '_INC_',
                    '<<': '_LSHIFT_', '>>': '_RSHIFT_'}
int_prefix = {'0x': 16, '0o': 8, '0b': 2}


class Tokenizer:
    def __init__(self):
        self.tokens = []
        self.in_remark = False
        self.string_table = {}
        self.line_number = 1

    def tokenize(self, file):
        self.line_number = 1
        with open(file) as f:
            for line in f:
                tokens = self.line2tokens(line)
                self.tokens.extend(tokens)
                self.line_number +=  1
        return self.tokens

    def line2tokens(self, line):
        remark_token = []
        tokens = []
        #
        # remark
        #
        if '/*' in line or '//' in line or '*/' in line:
            line, remark_token = self.do_remark(line)
            if len(line) == 0:
                tokens.extend(remark_token)
                return tokens
        elif self.in_remark:
            token = Token('remark3', line.strip(), self.line_number)
            return [token]
        #
        # String
        #
        if '"' in line:
            line = self.do_quote(line)
        #
        # <=, >=
        #
        for op in change_operators:
            line = line.replace(op, change_operators[op])
        #
        # add space around operators
        #
        for token in space_tokens:
            line = line.replace(token, ' ' + token + ' ')
        #
        # split line into tokens
        #
        divided_line = line.strip().split()
        #
        # work with token
        #
        for item in divided_line:
            if item in ptl1_tokens:
                # special token
                token_kind = ptl1_tokens[item]
            else:
                if item[:15] == 'STRING_CONSTANT':
                    # string constant
                    token_kind = 'stringConstant'
                    item = self.string_table.pop(item)
                elif item.isdigit():
                    # integer constant
                    token_kind = 'integerConstant'
                elif item[:2].lower() in int_prefix:
                    # hex or bin value
                    token_kind = 'integerConstant'
                    item = int(item, int_prefix[item[:2].lower()])
                else:
                    token_kind = 'identifier'
            if not token_kind == 'quote':
                token = Token(token_kind, item, self.line_number)
                tokens.append(token)
        tokens.extend(remark_token)
        return tokens

    def do_quote(self, line):
        string_number = 0
        string_range = [pos for pos, char in enumerate(line) if char == '"']
        while len(string_range) > 1:
            left = string_range[0]
            right = string_range[1]
            string_value = line[left + 1: right]
            string_constant = 'STRING_CONSTANT_%d' % string_number
            line = line.replace(string_value, string_constant)
            self.string_table[string_constant] = string_value
            string_number = string_number + 1
            string_range.remove(left)
            string_range.remove(right)
        return line

    def do_remark(self, line):
        if '/*' in line:
            left_position = line.find('/*')
            if '*/' in line:
                right_position = line.find('*/')
                remark_body = line[left_position: right_position + 2]
                token = Token('remark', remark_body, self.line_number)
                line = line[:left_position] + line[right_position + 2:]
                return line, [token]
            else:
                self.in_remark = True
                token = Token('remark1', line[left_position:].strip(), self.line_number)
                line = line[:left_position]
                return line, [token]
        elif '*/' in line:
            if self.in_remark:
                self.in_remark = False
                right_position = line.find('*/')
                remark_body = line[:right_position + 2]
                token = Token('remark2', remark_body, self.line_number)
                line = line[right_position + 2:]
                return line, [token]
            else:
                print('error:')
        elif '//' in line:
            left_position = line.find('//')
            remark_body = line[left_position:]
            token = Token('remark0', remark_body.strip(), self.line_number)
            line = line[:left_position]
            return line, [token]
        else:
            return line, None
