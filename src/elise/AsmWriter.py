import inspect
import os
from .MSXMathLibrary import call_address_dic as math_lib_dic

WORK_BASE_ADDRESS = 0xC000
SP_ADDRESS = 0xF000
SP = 'SP'
LOCAL = 'LOCAL'
ARGUMENT = 'ARGUMENT'
THIS = 'THIS'
THAT = 'THAT'
STATIC = 'STATIC'
POINTER = 'POINTER'
CONSTANT = 'CONSTANT'
TEMP = 'TEMP'
STRING = 'STRING'
ADD = 'add'
SUB = 'sub'
AND = 'and'
OR = 'or'
NEG = 'neg'
NOT = 'not'
INC = 'inc'
DEC = 'dec'
SHL = 'shl'
SHR = 'shr'
EQ = 'eq'
GT = 'gt'
LT = 'lt'
arithmetic_add_sub_code = {
    'add': ['ADD HL, DE'],
    'sub': ['OR A', 'SBC HL, DE'],
}
arithmetic_not_code = [
    '',
    '; arithmetic not',
    'LD A, H',
    'CPL',
    'LD H, A',
    'LD A, L',
    'CPL',
    'LD L, A'
]
arithmetic_lt_gt_code = [
    '',
    '; arithmetic lt_gt',
    'OR A',
    'SBC HL, DE',
    'LD A, 0',
    'SBC A, 0',
    'LD H, A',
    'LD L, A'
]


class AsmWriter:
    def __init__(self, file=None, env=None):
        self.codes = []
        self.call_func_count = {}
        self.eq_count = 0
        self.shift_count = 0
        self.asm_file = file
        self.file_name = os.path.splitext(os.path.basename(file))[0]
        self.static_list = []
        self.string_dic = {}
        self.string_count = 0
        self.data_dic = {}
        self.data_count = 0
        self.env = env
        self.source_location = None

    def set_source_location(self, source_location):
        self.source_location = source_location

    def code_dic(self):
        func_dic = {}
        items = inspect.getmembers(self)
        for item_name, item in items:
            if item_name.startswith('write_'):
                func_name = item_name.replace('write_', '')
                if func_name == 'if_goto':
                    func_name = 'if-goto'
                func_dic[func_name] = item
        return func_dic

    def add_code(self, code):
        if self.source_location is not None:
            code = [
                '; source %d %s %d' % (
                    self.source_location['source_line'],
                    self.source_location['function'],
                    self.source_location['vm_line'],
                )
            ] + code
            self.source_location = None
        self.codes.extend(code)
        if self.env['verbose'] > 1:
            for item in code:
                print(item)

    def segment_address(self, segment):
        return 'sys_' + segment.upper()

    #
    #   create arithmetic `EQ` code
    #
    def arithmetic_eq_code(self):
        count = self.eq_count
        self.eq_count += 1

        asm_name = 'sample_asm'
        if self.asm_file is not None:
            asm_name = os.path.basename(self.asm_file)
        jr_1 = '%s_eq_1_%d' % (asm_name, count)
        jr_2 = '%s_eq_2_%d' % (asm_name, count)
        code = [
            '',
            '; arithmetic eq',
            'OR A',
            'SBC HL, DE',
            'JR Z, %s' % jr_1,
            'LD HL, 0x0000',
            'JR %s' % jr_2,
            '%s:' % jr_1,
            'LD HL, 0xFFFF',
            '%s:' % jr_2,
        ]

        return code

    #
    #   LD DE, segment's index address
    #
    def ld_hl_segment_index_address(self, segment: str, index: int):
        code = [
            'LD HL, (%s)' % self.segment_address(segment),
        ]
        index = int(index)
        if index > 0:
            index_value = index * 2
            if segment == THIS:
                code.extend([
                    'LD DE, %d' % index_value,
                    'ADD HL, DE',
                ])
            else:
                code.extend([
                    'LD DE, %d' % index_value,
                    'OR A',
                    'SBC HL, DE',
                ])
        return code

    #
    #   function func_name local_variable_count
    #
    #   make LABEL with function name
    #   save local 0 (SP) to LCL
    #   then push '0' count of local variable
    #
    def write_function(self, args):
        func_name, l_count = args
        code = [
            '',
            '; function %s %s' % (func_name, l_count),
            '%s:' % func_name
        ]
        l_count = int(l_count)
        if l_count > 0:
            code.append(
                'LD HL, 0x0000',
            )
            for i in range(0, l_count):
                code.append(
                    'PUSH HL'
                )
        self.add_code(code)

    #
    #   push segment index bit_width
    #
    def write_push(self, args):
        segment, index = args
        segment = segment.upper()
        if segment == CONSTANT:
            code = [
                '',
                '; push %s %s' % (segment, index),
                'LD HL, %s' % hex(int(index)),
                'PUSH HL'
            ]
        elif segment == TEMP or segment == POINTER:
            code = [
                '',
                '; push %s %s' % (segment, index),
                'LD HL, (%s + %d)' % (self.segment_address(segment), int(index) * 2),
                'PUSH HL'
            ]
        elif segment == STATIC:
            static_name = self.file_name + '.' + str(index)
            code = [
                '',
                '; push %s %s' % (segment, index),
                'LD HL, (%s)' % static_name,
                'PUSH HL'
            ]
            if static_name not in self.static_list:
                self.static_list.append(static_name)
        elif segment == STRING:
            string_data_label = self.file_name + '.string.' + str(self.string_count)
            self.string_count += 1
            self.string_dic[string_data_label] = index
            code = [
                '',
                '; push %s %s' % (segment, index),
                'ld hl, %s' % string_data_label,
                'push hl',
            ]
        else:
            code = [
                '',
                '; push %s %s' % (segment, index)
            ]
            code.extend(self.ld_hl_segment_index_address(segment, index))
            code.extend([
                'LD E, (HL)',
                'INC HL',
                'LD D, (HL)',
                'PUSH DE'
            ])
        self.add_code(code)

    #
    #   pop segment index bit_width
    #
    def write_pop(self, args):
        segment, index = args
        segment = segment.upper()
        if segment == TEMP or segment == POINTER:
            code = [
                '',
                '; pop %s %s' % (segment, index),
                'POP HL',
                'LD (%s + %d), HL' % (self.segment_address(segment), int(index) * 2),
            ]
        elif segment == STATIC:
            static_name = self.file_name + '.' + str(index)
            code = [
                '',
                '; pop %s %s' % (segment, index),
                'POP HL',
                'LD (%s), HL' % static_name,
            ]
            if static_name not in self.static_list:
                self.static_list.append(static_name)
        else:
            code = [
                '',
                '; pop %s %s' % (segment, index)
            ]
            code.extend(self.ld_hl_segment_index_address(segment, index))
            code.extend([
                'POP DE',
                'LD (HL), E',
                'INC HL',
                'LD (HL), D'
            ])
        self.add_code(code)

    #
    #   for arithmetic operator jump point
    #
    def write_add(self, args):
        self.arithmetic('add')

    def write_sub(self, args):
        self.arithmetic('sub')

    def write_and(self, args):
        self.arithmetic('and')

    def write_or(self, args):
        self.arithmetic('or')

    def write_not(self, args):
        self.arithmetic('not')

    def write_neg(self, args):
        self.arithmetic('neg')

    def write_lt(self, args):
        self.arithmetic('lt')

    def write_gt(self, args):
        self.arithmetic('gt')

    def write_eq(self, args):
        self.arithmetic('eq')

    def write_inc(self, args):
        self.arithmetic('inc')

    def write_shl(self, args):
        self.shift('shl')

    def write_shr(self, args):
        self.shift('shr')

    def write_shl_const(self, args):
        self.shift_const('shl', args)

    def write_shr_const(self, args):
        self.shift_const('shr', args)

    #
    #   arithmetic code
    #   add, sub, and, or, not, neg, lt, gt, eq, inc, dec, shl, shr
    #
    and_or_operator = [AND, OR]
    lt_gt_operator = [LT, GT]
    single_operator = [NOT, NEG, INC, DEC]

    def arithmetic(self, operator):
        if operator == GT:
            arithmetic_code = [
                '',
                '; arithmetic %s' % operator,
                'POP HL',
                'POP DE',
            ]
        elif operator in self.single_operator:
            arithmetic_code = [
                '',
                '; arithmetic %s' % operator,
                'POP HL'
            ]
        else:
            arithmetic_code = [
                '',
                '; arithmetic %s' % operator,
                'POP DE',
                'POP HL'
            ]

        if operator in self.and_or_operator:
            arithmetic_code.extend([
                'LD A,L',
                '%s E' % operator.upper(),
                'LD L, A',
                'LD A, H',
                '%s D' % operator.upper(),
                'LD H, A'
            ])
        elif operator == NEG:
            arithmetic_code.append('DEC HL')
            arithmetic_code.extend(arithmetic_not_code)
        elif operator == NOT:
            arithmetic_code.extend(arithmetic_not_code)
        elif operator in self.lt_gt_operator:
            arithmetic_code.extend(arithmetic_lt_gt_code)
        elif operator == EQ:
            code = self.arithmetic_eq_code()
            arithmetic_code.extend(code)
        elif operator == INC or operator == DEC:
            arithmetic_code.append('%s HL' % operator)
        else:
            arithmetic_code.extend(arithmetic_add_sub_code[operator])

        arithmetic_code.append('PUSH HL')

        self.add_code(arithmetic_code)

    def shift(self, operator):
        count = self.shift_count
        self.shift_count += 1

        asm_name = 'sample_asm'
        if self.asm_file is not None:
            asm_name = os.path.basename(self.asm_file)

        loop_label = '%s_%s_loop_%d' % (asm_name, operator, count)
        zero_label = '%s_%s_zero_%d' % (asm_name, operator, count)
        end_label = '%s_%s_end_%d' % (asm_name, operator, count)

        code = [
            '',
            '; arithmetic %s' % operator,
            'POP DE',
            'POP HL',
            'LD A, D',
            'OR A',
            'JR NZ, %s' % zero_label,
            'LD A, E',
            'CP 16',
            'JR NC, %s' % zero_label,
            'OR A',
            'JR Z, %s' % end_label,
            '%s:' % loop_label,
        ]

        if operator == SHL:
            code.append('ADD HL, HL')
        else:
            code.extend([
                'SRL H',
                'RR L',
            ])

        code.extend([
            'DEC E',
            'JR NZ, %s' % loop_label,
            'JR %s' % end_label,
            '%s:' % zero_label,
            'LD HL, 0x0000',
            '%s:' % end_label,
            'PUSH HL',
        ])

        self.add_code(code)

    def shift_const(self, operator, args):
        shift_count = int(args[0])
        code = [
            '',
            '; arithmetic %s_const %d' % (operator, shift_count),
            'POP HL',
        ]

        if shift_count >= 16:
            code.append('LD HL, 0x0000')
        else:
            for _ in range(shift_count):
                if operator == SHL:
                    code.append('ADD HL, HL')
                else:
                    code.extend([
                        'SRL H',
                        'RR L',
                    ])

        code.append('PUSH HL')
        self.add_code(code)

    def write_label(self, args):
        label_name, = args
        code = [
            '',
            '; label %s' % label_name,
        ]
        code.extend(['%s:' % label_name])
        self.add_code(code)

    def write_if_goto(self, args):
        label_name, = args
        code = [
            '',
            '; if-goto %s' % label_name,
            'pop hl',
            'ld a, h',
            'or l',
            'jp nz, %s' % label_name,
        ]
        self.add_code(code)

    def write_goto(self, args):
        label_name, = args
        code = [
            '',
            '; goto %s' % label_name,
            'jp %s' % label_name
        ]
        self.add_code(code)

    def write_call(self, args):
        func_name, arg_count = args
        func_class = func_name.split('.')[0]
        if func_class in self.env['libNames']:
            self.call_library(func_class, func_name, arg_count)
            return
        if func_name in self.call_func_count:
            index = self.call_func_count[func_name]
        else:
            index = 0
            self.call_func_count[func_name] = index
        self.call_func_count[func_name] = self.call_func_count[func_name] + 1
        ret_func_name = self.file_name + '.' + func_name
        return_address_label = 'call.%s.%d' % (ret_func_name, index)

        code = [
            '',
            '; call %s %s' % (func_name, arg_count),
            # push return address
            # nArgs + 1 is return address's save location
            'ld hl, %s' % return_address_label,
            'push hl',
            # push LOCAL
            'ld hl, (%s)' % self.segment_address(LOCAL),
            'push hl',
            # push ARGUMENT
            'ld hl, (%s)' % self.segment_address(ARGUMENT),
            'push hl',
            # push THIS
            'ld hl, (%s)' % self.segment_address(THIS),
            'push hl',
            # push THAT
            'ld hl, (%s)' % self.segment_address(THAT),
            'push hl',
            # set ARGUMENT to SP + (5 + argument count) * 2
            'ld hl, 0',
            'add hl, sp',   # this hl is called function's LCL
            'dec hl',
            'dec hl',
            'ld (%s), hl' % self.segment_address(LOCAL),
            'ld de, %d' % ((5 + int(arg_count)) * 2),
            'add hl, de',
            'ld (%s), hl' % self.segment_address(ARGUMENT),
            # LCL = SP
            # LCL = SP is already done in above
            'jp %s' % func_name,
            # return address label
            '%s:' % return_address_label
        ]

        self.add_code(code)

    def call_library(self, func_class, func_name, arg_count):
        code = [
            '',
            '; call library (%s %s)' % (func_name, arg_count),
        ]
        if func_class == 'MSXMath':
            math_code = [
                'pop hl',
                'pop de',
                'call %s' % math_lib_dic[func_name],
                'push hl',
            ]
            code.extend(math_code)
        else:
            code.append('jp %s' % func_name)
        self.add_code(code)

    def write_lib_call(self, args):
        func_name_label, = args
        code = [
            '',
            '; lib_call prepare',
            'ld hl, %s' % func_name_label,
            'push hl'
        ]
        self.add_code(code)

    def write_lib_ret_address(self, args):
        label, = args
        code = [
            '',
            '; lib_ret_address',
            '%s:' % label
        ]
        self.add_code(code)

    def write_return(self, args):
        is_void, = args
        code = [
            '',
            '; return void: %s' % is_void,

            'ld hl, (%s)' % self.segment_address(ARGUMENT),
            'ld (%s), hl' % self.segment_address(TEMP),
        ]

        if is_void == 'False':
            code2 = [
                'pop hl',
                'ld (sys_TEMP + 2), hl',
            ]
            code.extend(code2)

        code3 = [
            'ld sp, (%s)' % self.segment_address(LOCAL),
            'pop hl',

            'pop hl',   # sp move `that` and HL is that value
            'ld (%s), hl' % self.segment_address(THAT),
            'pop hl',   # sp move `this` and HL is this value
            'ld (%s), hl' % self.segment_address(THIS),
            'pop hl',   # sp move `argument` and...
            'ld (%s), hl' % self.segment_address(ARGUMENT),
            'pop hl',   # sp move `local` and...
            'ld (%s), hl' % self.segment_address(LOCAL),

            'pop de',   # return address

            'ld sp, (%s)' % self.segment_address(TEMP),
            'inc sp',
            'inc sp',
        ]
        code.extend(code3)

        if is_void == 'False':
            code4 = [
                'ld hl, (sys_TEMP + 2)',
                'push hl',
            ]
            code.extend(code4)

        code5 = [
            'push de',
            'ret'
        ]
        code.extend(code5)
        self.add_code(code)

    def write_data(self, args):
        label_name, values_string = args
        print('write_data: %s, %s' % (label_name, values_string))
        data_label = self.file_name + '.data.' + label_name
        self.data_dic[data_label] = values_string
        code = [
            '',
            '; data %s %s' % (label_name, values_string),
            'ld hl, %s' % data_label,
            'push hl',
        ]
        self.add_code(code)

    def write_x2(self, args):
        print('x2')
        code = [
            '',
            '; x2',
            'pop hl',
            'add hl, hl',
            'push hl',
        ]
        self.add_code(code)
