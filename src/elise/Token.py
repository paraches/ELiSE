
remark_list = ['remark', 'remark0', 'remark1', 'remark2', 'remark3']

class_var_kind = ['static', 'field']
subroutine_kind = ['constructor', 'function', 'method']
var_type = ['int', 'boolean', 'char', 'Array', 'String']
statements = ['if', 'while', 'return', 'dat', 'let', 'do']
keyword_constant = ['true', 'false', 'null', 'this']
p_instruction = ['db', 'dw', 'ds']
unary_op = ['-', '~', '_INC_', '_DEC_']
comparison_operator = ['<', '>', '_EQUAL_', '_LE_', '_GE_', '_NE_']
high_operator = ['*', '/', '%']
add_operator = ['+', '-']
shift_operator = ['_LSHIFT_', '_RSHIFT_']
and_operator = ['&']
or_operator = ['|']

operator = unary_op + comparison_operator + high_operator + add_operator + shift_operator + and_operator + or_operator
keyword = class_var_kind + subroutine_kind + var_type + statements + keyword_constant + p_instruction + operator

unary_op_code = {'-': 'neg', '~': 'not', '_INC_': 'inc', '_DEC_': 'dec'}
operator_code = {'+': ['add'], '-': ['sub'], '*': ['call MSXMath.multiply 2'], '/': ['call MSXMath.divide 2'],
                 '%': ['call MSXMath.modulo 2'],
                 '&': ['and'], '|': ['or'], '<': ['lt'], '>': ['gt'], '_EQUAL_': ['eq'],
                 '_LE_': ['gt', 'not'], '_GE_': ['lt', 'not'], '_NE_': ['eq', 'not'],
                 '_LSHIFT_': ['shl'], '_RSHIFT_': ['shr']}
keyword_constant_dic = {
    'true': [('push', {'kind': 'constant', 'number': 1, 'type': 'int'}), ('arithmetic', {'opcode': 'neg',})],
    'false': [('push', {'kind': 'constant', 'number': 0, 'type': 'int'})],
    'null': [('push', {'kind': 'constant', 'number': 0, 'type': 'int'})],
    'this': [('push', {'kind': 'pointer', 'number': 0, 'type': 'int16'})]
}


class Token:
    def __init__(self, kind, value, line_number):
        self.kind = kind
        self.value = value
        self.line_number = line_number

    def __str__(self):
        return '%04d: %15s,   %s' % (self.line_number, self.kind, self.value)

    def short_print(self):
        return '%s: %s' % (self.kind, self.value)

    def is_remark(self):
        return self.kind in remark_list

    def is_class(self):
        return self.value == 'class'

    def is_identifier(self):
        return self.kind == 'identifier'

    def is_class_var_kind(self):
        return self.value in class_var_kind

    def is_subroutine_kind(self):
        return self.value in subroutine_kind

    def is_subroutine_type(self):
        return self.is_var_type() or self.value == 'void'

    def is_var_type(self):
        return self.value in var_type or self.kind == 'identifier'

    def is_var_name(self):
        return self.is_identifier()

    def is_subroutine_name(self):
        return self.is_identifier()

    def is_class_name(self):
        return self.is_identifier()

    def is_statement(self):
        return self.value in statements or self.is_identifier()

    def is_keyword_constant(self):
        return self.value in keyword_constant

    def is_pseudo_instruction(self):
        return self.value in p_instruction

    def is_unary_op(self):
        return self.value in unary_op

    def is_constant(self):
        return self.is_keyword_constant() or self.kind == 'integerConstant' or self.kind == 'stringConstant'

    def is_term(self):
        return self.is_constant() or self.is_var_name() or self.is_left_par() or self.is_right_par() or self.is_unary_op()

    def is_operator(self):
        return self.value in operator

    def is_high_operator(self):
        return self.value in high_operator

    def is_low_operator(self):
        return self.value in add_operator or self.value in and_operator or self.value in or_operator

    def is_add_operator(self):
        return self.value in add_operator

    def is_shift_operator(self):
        return self.value in shift_operator

    def is_and_operator(self):
        return self.value in and_operator

    def is_or_operator(self):
        return self.value in or_operator

    def is_comparison_operator(self):
        return self.value in comparison_operator

    def is_left_par(self):
        return self.kind == 'symbol' and self.value == '('

    def is_right_par(self):
        return self.kind == 'symbol' and self.value == ')'

    def is_left_br_par(self):
        return self.kind == 'symbol' and self.value == '['

    def is_right_br_par(self):
        return self.kind == 'symbol' and self.value == ']'

    def is_left_wv_par(self):
        return self.kind == 'symbol' and self.value == '{'

    def is_right_wv_par(self):
        return self.kind == 'symbol' and self.value == '}'

    def is_comma(self):
        return self.kind == 'symbol' and self.value == ','

    def is_dot(self):
        return self.kind == 'symbol' and self.value == '.'

    def is_semi_colon(self):
        return self.kind == 'symbol' and self.value == ';'

    def is_colon(self):
        return self.kind == 'symbol' and self.value == ':'

    def is_equal(self):
        return self.kind == 'symbol' and self.value == '='

    def is_comp_equal(self):
        return self.kind == 'symbol' and self.value == '_EQUAL_'

    def keyword_constant_value(self):
        if self.value in keyword_constant:
            return keyword_constant_dic[self.value]
        return None

    def operator_code(self):
        if self.is_operator():
            return operator_code[self.value]
        return None

    def unary_code(self):
        if self.is_unary_op():
            return unary_op_code[self.value]
        return None
