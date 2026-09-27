class Parser:
    def __init__(self, env=None):
        self.env = env
        self.symbol_table = None
        self.tokens = []
        self.token_index = 0
        self.lib_call_counter = 0
        self.if_label_counter = 0
        self.while_label_counter = 0
        self.writer = None
        self.codes = []
        self.error = False
        self.current_line_number = 1
        self.current_function = None

    def lib_call_index(self):
        index = self.lib_call_counter
        self.lib_call_counter += 1
        return index

    def if_label_index(self):
        index = self.if_label_counter
        self.if_label_counter = self.if_label_counter + 1
        return index

    def while_label_index(self):
        index = self.while_label_counter
        self.while_label_counter = self.while_label_counter + 1
        return index

    def get_token(self):
        if self.token_index < len(self.tokens):
            token = self.tokens[self.token_index]
            self.token_index += 1
            while token.is_remark():
                token = self.tokens[self.token_index]
                self.token_index += 1
            self.current_line_number = token.line_number
            return token
        else:
            print('token_index(%d) is over the size of tokens(%d).' % (self.token_index, len(self.tokens)))

    def next_token(self):
        temp_index = self.token_index
        if temp_index < len(self.tokens):
            token = self.tokens[temp_index]
            while token.is_remark():
                temp_index += 1
                token = self.tokens[temp_index]
            return token
        else:
            print('token_index(%d) is over the size of tokens(%d).' % (self.token_index, len(self.tokens)))

    def parse(self, tokens, symbol_table, writer):
        self.tokens = tokens
        self.symbol_table = symbol_table
        self.token_index = 0
        self.writer = writer

        token = self.get_token()
        while not token.is_class():
            token = self.get_token()
        self.do_class()
        return self.codes, self.error

    def do_class(self):
        # className
        token = self.get_token()
        if not token.is_class_name():
            self.error_message('class', 'identifier', token)
            return
        class_name = token.value

        # {
        token = self.get_token()
        if not token.is_left_wv_par():
            self.error_message('class', '{', token)
            return

        # class var dec
        # static | field
        # it is already in symbol table
        token = self.get_token()
        while token.is_class_var_kind():
            while not token.is_semi_colon():
                token = self.get_token()
            token = self.get_token()

        # subroutine dec
        # constructor | function | method
        while token.is_subroutine_kind():
            self.do_subroutine_dec(class_name, token)
            token = self.get_token()

        # }
        if not token.is_right_wv_par():
            self.error_message('class', '}', token)
            return

    def do_subroutine_dec(self, class_name, token):
        subroutine_kind = token.value

        # 'void' | type | identifier
        token = self.get_token()
        if not token.is_subroutine_type():
            self.error_message('subroutine_dec', 'subroutine_type', token)
            return
        subroutine_type = token.value

        # subroutineName
        token = self.get_token()
        if not token.is_subroutine_name():
            self.error_message('subroutine_dec', 'identifier', token)
            return
        subroutine_name = token.value

        # write function
        function_label = class_name + '.' + subroutine_name
        self.current_function = function_label
        local_count = self.symbol_table.var_kind_count(class_name, subroutine_name, 'local')
        self.code_write('function', {'label': function_label, 'count': local_count})

        if subroutine_kind == 'constructor':
            lib_call_label = 'lib_call.%s.%d' % (function_label, self.lib_call_index())
            field_count = self.symbol_table.var_kind_count(class_name, None, 'field')
            self.code_write('lib_call', {'label': lib_call_label})
            self.code_write('push', {'kind': 'constant', 'number': field_count, 'type': 'int'})
            self.code_write('call', {'label': 'Memory.alloc', 'count': 1})
            self.code_write('lib_ret_address', {'label': lib_call_label})
            self.code_write('pop', {'kind': 'pointer', 'number': 0, 'type': 'int16'})
        elif subroutine_kind == 'method':
            self.code_write('push', {'kind': 'argument', 'number': 0, 'type': 'int16'})
            self.code_write('pop', {'kind': 'pointer', 'number': 0, 'type': 'int16'})

        while not token.is_left_wv_par():
            token = self.get_token()

        token = self.get_token()
        while token.value == 'var':
            while not token.is_semi_colon():
                token = self.get_token()
            token = self.get_token()

        self.do_statements(class_name, subroutine_name, token)

    def do_statements(self, class_name, f_name, token):
        while token.is_statement():
            # switch statement
            statement = token.value
            if statement == 'let':
                self.do_let(class_name, f_name)
            elif statement == 'if':
                self.do_if(class_name, f_name)
            elif statement == 'while':
                self.do_while(class_name, f_name)
            elif statement == 'do':
                self.do_do(class_name, f_name)
            elif statement == 'return':
                self.do_return(class_name, f_name)
            elif statement == 'dat':
                self.do_data(class_name, f_name)
            elif token.is_identifier():
                self.do_statement_identifier(class_name, f_name, token)
            else:
                self.error_message('Statements', 'any statement', token)
                return
            token = self.get_token()
        return token

    def do_statement_identifier(self, class_name, f_name, token):
        var_info = self.symbol_table.var_info(class_name, f_name, token.value)
        #
        # subroutine call   Class.func() or func()
        #
        if var_info is None:
            token, is_void = self.do_subroutine_call(class_name, f_name, token)
            if not is_void:
                print('Not void function called in statement.')
                self.code_write('pop', {'kind': 'temp', 'number': 0, 'type': 'int'})
            return

        var_name = token.value
        next_token = self.next_token()
        #
        # subroutine call  varName.func()
        #
        if next_token.is_dot():
            token, is_void = self.do_subroutine_call(class_name, f_name, token)
            return

        token = self.get_token()
        is_array = False

        #
        # Array
        #
        if token.is_left_br_par():
            is_array = True
            token = self.do_array(class_name, f_name, var_name)

        #
        # =
        #
        if not token.is_equal():
            self.error_message('statement_identifier', '=', token)
            return

        # expression
        token = self.get_token()
        token = self.do_expression(class_name, f_name, token)

        if is_array:
            self.code_write('pop', {'kind': 'temp', 'number': 0, 'type': 'int'})
            self.code_write('pop', {'kind': 'pointer', 'number': 1, 'type': 'int16'})
            self.code_write('push', {'kind': 'temp', 'number': 0, 'type': 'int'})
            self.code_write('pop', {'kind': 'that', 'number': 0, 'type': 'int16'})
        else:
            if var_info['kind'] == 'field':
                var_info['kind'] = 'this'
            self.code_write('pop', var_info)

        # ;
        if not token.is_semi_colon():
            self.error_message('let', ';', token)
            return

        return

    def do_let(self, class_name, f_name):
        is_array = False

        token = self.get_token()
        if not token.is_var_name():
            self.error_message('let', 'var_name', token)
            return
        left_var_name = token.value

        token = self.get_token()
        if token.is_left_br_par():
            is_array = True
            token = self.do_array(class_name, f_name, left_var_name)

        # =
        if not token.is_equal():
            self.error_message('let', '=', token)
            return

        # expression
        token = self.get_token()
        token = self.do_expression(class_name, f_name, token)

        if is_array:
            self.code_write('pop', {'kind': 'temp', 'number': 0, 'type': 'int'})
            self.code_write('pop', {'kind': 'pointer', 'number': 1, 'type': 'int16'})
            self.code_write('push', {'kind': 'temp', 'number': 0, 'type': 'int'})
            self.code_write('pop', {'kind': 'that', 'number': 0, 'type': 'int16'})
        else:
            var_info = self.symbol_table.var_info(class_name, f_name, left_var_name)
            if var_info is None:
                self.error_message('let', 'can not find', token)
                return
            if var_info['kind'] == 'field':
                var_info['kind'] = 'this'
            self.code_write('pop', var_info)

        # ;
        if not token.is_semi_colon():
            self.error_message('let', ';', token)
            return

        return

    def do_array(self, class_name, f_name, var_name):
        var_info = self.symbol_table.var_info(class_name, f_name, var_name)
        if var_info['kind'] == 'field':
            var_info['kind'] = 'this'
        self.code_write('push', var_info)

        token = self.get_token()
        token = self.do_expression(class_name, f_name, token)
        if not token.is_right_br_par():
            self.error_message('array', ']', token)
            return

        # calc array index is originally for 16bit
        # if use 8bit, need to x2 for index
#        self.code_write('push', {'kind': 'constant', 'number': 2, 'type': 'int16'})
#        self.code_write('call', {'label': 'MSXMath.multiply', 'count': 2})
        self.code_write('x2', {})

        self.code_write('arithmetic', {'opcode': 'add', })

        token = self.get_token()

        return token

    def do_if(self, class_name, f_name):
        if_index_num = self.if_label_index()
        label_if_else = '%s.%s.if.else.%d' % (class_name, f_name, if_index_num)
        label_if_end = '%s.%s.if.end.%d' % (class_name, f_name, if_index_num)

        # ( expression )
        self.do_par_expression('if', class_name, f_name)

        self.code_write('arithmetic', {'opcode': 'not', })
        self.code_write('if', {'label': label_if_else, })

        # { statements }
        self.do_wv_par_statements('if', class_name, f_name)

        next_token = self.next_token()

        has_elif = next_token.value == 'elif'
        if has_elif:
            self.code_write('goto', {'label': label_if_end, })
            self.code_write('label', {'label': label_if_else, })

        while next_token.value == 'elif':
            # elif
            self.get_token()

            # ( expression )
            self.do_par_expression('elif', class_name, f_name)

            self.code_write('arithmetic', {'opcode': 'not', })
            label_if_else = '%s.%s.if.elif.%d' % (class_name, f_name, self.if_label_index())
            self.code_write('if', {'label': label_if_else, })

            # { statements }
            self.do_wv_par_statements('elif', class_name, f_name)
            self.code_write('goto', {'label': label_if_end, })
            self.code_write('label', {'label': label_if_else, })
            next_token = self.next_token()

        has_else = self.next_token().value == 'else'

        if has_else and not has_elif:
            self.code_write('goto', {'label': label_if_end, })

        if not has_elif:
            self.code_write('label', {'label': label_if_else, })

        if has_elif and not has_else:
            self.code_write('label', {'label': label_if_end, })

        if has_else:
            # else
            self.get_token()

            # { statements }
            self.do_wv_par_statements('if', class_name, f_name)

            self.code_write('label', {'label': label_if_end, })

    def do_while(self, class_name, f_name):
        while_index_num = self.while_label_index()
        label_while_start = '%s.%s.while.start.%d' % (class_name, f_name, while_index_num)
        label_while_end = '%s.%s.while.end.%d' % (class_name, f_name, while_index_num)

        self.code_write('label', {'label': label_while_start, })

        # ( expression)
        self.do_par_expression('while', class_name, f_name)

        self.code_write('arithmetic', {'opcode': 'not', })
        self.code_write('if', {'label': label_while_end, })

        # { statements }
        self.do_wv_par_statements('while', class_name, f_name)

        self.code_write('goto', {'label': label_while_start, })
        self.code_write('label', {'label': label_while_end, })

    def do_do(self, class_name, f_name):
        token = self.get_token()
        if not token.is_subroutine_name():
            self.error_message('do', 'subroutineName', token)
            return

        token, is_void = self.do_subroutine_call(class_name, f_name, token)

        #
        #   for don't needed returned value
        #
        if not is_void:
            self.code_write('pop', {'kind': 'temp', 'number': 0, 'type': 'int'})

    def do_return(self, class_name, f_name):
        is_void = True
        token = self.get_token()
        if not token.is_semi_colon():
            token = self.do_expression(class_name, f_name, token)
            if not token.is_semi_colon():
                self.error_message('return', ';', token)
                return
            is_void = False
        self.code_write('return', {'void': is_void})
        return

    def do_data(self, class_name, f_name):
        token = self.get_token()
        if not token.is_identifier():
            self.error_message('dat', 'identifier', token)
            return
        var_info = self.symbol_table.var_info(class_name, f_name, token.value)
        label_name = token.value

        # =
        token = self.get_token()
        if not token.is_equal():
            self.error_message('dat', '=', token)
            return

        token = self.get_token()
        if token.is_identifier():
            # <label>
            label_name = token.value
            token = self.get_token()

        # db, dw, ds
        if not token.is_pseudo_instruction():
            self.error_message('dat', 'pseudo instruction', token)
            return
        data_type = token.value

        token = self.get_token()
        value_string = ''
        while not token.is_semi_colon():
            value_string += ('00'+hex(token.value)[2:])[-2:]
            token = self.get_token()
            if token.is_comma():
                token = self.get_token()

        if self.env['verbose'] > 1:
            print('data')
            print('\tlabel: %s' % label_name)
            print('\tvalues: %s' % value_string)
            print('\tvarInfo: %s' % var_info)
        self.code_write('data', {'label': label_name, 'value': value_string})
        self.code_write('pop', var_info)

        return

    def do_expression(self, class_name, f_name, token):
        if not token.is_term():
            self.error_message('expression', 'term', token)
            return

        token = self.do_bitwise_or_fact(class_name, f_name, token)

        while token.is_comparison_operator():
            opcodes = token.operator_code()

            token = self.get_token()
            if not token.is_term():
                self.error_message('expression', 'term', token)
                return
            token = self.do_bitwise_or_fact(class_name, f_name, token)

            for opcode in opcodes:
                self.code_write('arithmetic', {'opcode': opcode,})

        return token

    def do_bitwise_or_fact(self, class_name, f_name, token):
        if not token.is_term():
            self.error_message('bitwise_or_fact', 'term', token)
            return

        token = self.do_bitwise_and_fact(class_name, f_name, token)

        while token.is_or_operator():
            opcodes = token.operator_code()

            token = self.get_token()
            if not token.is_term():
                self.error_message('bitwise_or_fact', 'term', token)
                return
            token = self.do_bitwise_and_fact(class_name, f_name, token)

            for opcode in opcodes:
                self.code_write('arithmetic', {'opcode': opcode,})

        return token

    def do_bitwise_and_fact(self, class_name, f_name, token):
        if not token.is_term():
            self.error_message('bitwise_and_fact', 'term', token)
            return

        token = self.do_shift_fact(class_name, f_name, token)

        while token.is_and_operator():
            opcodes = token.operator_code()

            token = self.get_token()
            if not token.is_term():
                self.error_message('bitwise_and_fact', 'term', token)
                return
            token = self.do_shift_fact(class_name, f_name, token)

            for opcode in opcodes:
                self.code_write('arithmetic', {'opcode': opcode,})

        return token

    def do_shift_fact(self, class_name, f_name, token):
        if not token.is_term():
            self.error_message('shift_fact', 'term', token)
            return

        token = self.do_add_fact(class_name, f_name, token)

        while token.is_shift_operator():
            operator = token.value
            opcode = 'shl' if operator == '_LSHIFT_' else 'shr'

            token = self.get_token()
            if not token.is_term():
                self.error_message('shift_fact', 'term', token)
                return

            if token.kind == 'integerConstant':
                shift_count = int(token.value)
                token = self.get_token()
                self.code_write('shift_const', {
                    'opcode': opcode,
                    'count': shift_count,
                })
            else:
                token = self.do_add_fact(class_name, f_name, token)
                self.code_write('arithmetic', {'opcode': opcode,})

        return token

    def do_add_fact(self, class_name, f_name, token):
        if not token.is_term():
            self.error_message('add_fact', 'term', token)
            return

        token = self.do_high_fact(class_name, f_name, token)

        while token.is_add_operator():
            opcodes = token.operator_code()

            token = self.get_token()
            if not token.is_term():
                self.error_message('add_fact', 'term', token)
                return
            token = self.do_high_fact(class_name, f_name, token)

            for opcode in opcodes:
                self.code_write('arithmetic', {'opcode': opcode,})

        return token

    def do_high_fact(self, class_name, f_name, token):
        if not token.is_term():
            self.error_message('high_fact', 'term', token)
            return

        token = self.do_term(class_name, f_name, token)

        while token.is_high_operator():
            operator = token.value
            opcodes = token.operator_code()

            token = self.get_token()
            if not token.is_term():
                self.error_message('high_fact', 'term', token)
                return

            if operator == '*' and token.kind == 'integerConstant':
                multiplier = int(token.value)
                if multiplier > 0 and multiplier <= 0x8000 and multiplier & (multiplier - 1) == 0:
                    shift_count = multiplier.bit_length() - 1
                    token = self.get_token()
                    self.code_write('shift_const', {
                        'opcode': 'shl',
                        'count': shift_count,
                    })
                    continue

            token = self.do_term(class_name, f_name, token)
            for opcode in opcodes:
                self.code_write('arithmetic', {'opcode': opcode,})

        return token

    def do_term(self, class_name, f_name, token):
        #
        #   integer constant
        #
        if token.kind == 'integerConstant':
            term_value = token.value
            self.code_write('push', {'kind': 'constant', 'number': term_value, 'type': 'int'})
            token = self.get_token()
        #
        #   string constant
        #
        elif token.kind == 'stringConstant':
            term_value = token.value
            self.code_write('push', {'kind': 'string', 'number': '"' + term_value + '"', 'type': 'str'})
            token = self.get_token()
        #
        #   keyword constant
        #   true, false, null, this
        #
        elif token.is_keyword_constant():
            codes = token.keyword_constant_value()
            for command, args in codes:
                self.code_write(command, args)
            token = self.get_token()
        #
        #   ( expression )
        #
        elif token.is_left_par():
            token = self.get_token()
            token = self.do_expression(class_name, f_name, token)
            if not token.is_right_par():
                self.error_message('term left_par', ')', token)
                return token
            token = self.get_token()
        #
        #   unary operator
        #   ~, -
        #
        elif token.is_unary_op():
            op = token

            token = self.get_token()
            if not token.is_term():
                self.error_message('term unaryOp', 'term', token)
                return token
            token = self.do_term(class_name, f_name, token)

            self.code_write('arithmetic', {'opcode': op.unary_code(),})

            return token
        #
        #   var name
        #   varName, varName[expression],
        #   subName(expressionList), (className|varName).subName(expressionList)
        else:
            token = self.do_var_name(class_name, f_name, token)

        return token

    def do_var_name(self, class_name, f_name, token):
        if not token.is_var_name():
            self.error_message('term.var_name', 'var_name', token)
            return
        right_name = token.value

        next_token = self.next_token()
        #
        # varName[expression]
        #
        if next_token.is_left_br_par():
            token = self.array_expression(class_name, f_name, token)
            return token

        #
        # varName
        #
        elif not (next_token.is_dot() or next_token.is_left_par()):
            var_name = right_name
            var_info = self.symbol_table.var_info(class_name, f_name, var_name)
            if var_info is None:
                self.error_message('var_name', 'var_info', var_name)
                return
            var_kind = var_info['kind']
            if var_kind == 'field':
                var_kind = 'this'
            var_number = var_info['number']
            self.code_write('push', {'kind': var_kind, 'number': var_number, 'type': var_info['type']})
            token = self.get_token()
            return token

        #
        # subroutineName(expressionList), (className|varName).subroutineName(expressionList)
        #
        else:
            token, is_void = self.do_subroutine_call(class_name, f_name, token)
            return token

    def array_expression(self, class_name, f_name, token):
        self.get_token()

        var_info = self.symbol_table.var_info(class_name, f_name, token.value)
        if var_info['kind'] == 'field':
            var_info['kind'] = 'this'
        self.code_write('push', var_info)

        token = self.get_token()

        token = self.do_expression(class_name, f_name, token)

#        self.code_write('push', {'kind': 'constant', 'number': 2, 'type': 'int16'})
#        self.code_write('call', {'label': 'MSXMath.multiply', 'count': 2})
        self.code_write('x2', {})
        self.code_write('arithmetic', {'opcode': 'add',})
        self.code_write('pop', {'kind': 'pointer', 'number': 1, 'type': 'int16'})
        self.code_write('push', {'kind': 'that', 'number': 0, 'type': 'int16'})

        if not token.is_right_br_par():
            self.error_message('array', ']', token)
            return

        token = self.get_token()
        return token

    def do_subroutine_call(self, class_name, f_name, token):
        method = False
        method_push_info = {'kind': 'pointer', 'number': 0, 'type': 'int16'}

        next_token = self.next_token()
        right_name = token.value

        #
        # (className|varName).subName(expressionList)
        #
        if next_token.is_dot():
            self.get_token()
            token = self.get_token()

            if not token.is_var_name():
                self.error_message('term.varName.', 'varName', token)
                return token

            left_name = right_name
            right_name = token.value

            #
            # confirm whether left_name is ClassName or varName
            #
            var_info = self.symbol_table.var_info(class_name, f_name, left_name)
            if var_info is not None:
                #
                # left_name is found in subroutine or class var
                # left_name is varName, so get className from varName's type
                # this is method call, but don't push pointer 0, push leftName var
                #
                method = True
                left_name = var_info['type']
                var_kind = var_info['kind']
                if var_kind == 'field':
                    var_kind = 'this'
                var_index = var_info['number']
                method_push_info = {'kind': var_kind, 'number': var_index, 'type': 'int16'}  # push this
            #
            # ClassName.subroutine don't need to do extra work
            #

            #
            # function name is fixed
            #
            func_name = '%s.%s' % (left_name, right_name)

            token = self.get_token()
        #
        # subName(expressionList)
        #
        else:
            var_info = self.symbol_table.var_info(class_name, f_name, right_name)
            if var_info is None:
                # subroutine will be define below of code
                # subroutineName() must be `method`.
                # `function` must be called as Class.functionName()
                method = True
            else:
                if var_info['kind'] == 'method':
                    method = True
            left_name = class_name
            func_name = '%s.%s' % (left_name, right_name)
            token = self.get_token()

        f_type = self.symbol_table.function_type(left_name, right_name)
        if f_type is None:
            self.error_message('subroutineCall', 'functionName', token)
            return token, None

        #   add push return address for lib here
        lib_call = False
        lib_call_label = None
        class_type = self.symbol_table.class_type(left_name)
        if class_type == 'library':
            lib_call = True
            lib_call_index = self.lib_call_index()
            lib_call_label = "lib_call.%s.%s.%s.%d" % (func_name, class_name, f_name, lib_call_index)
            self.code_write('lib_call', {'label': lib_call_label,})

        if method:
            self.code_write('push', method_push_info)     # push this

        count = 0

        if not token.is_left_par():
            self.error_message('term', '(', token)
            return token

        token = self.get_token()
        if not token.is_right_par():
            token, count = self.do_expression_list(class_name, f_name, token)

        if not token.is_right_par():
            self.error_message('term', ')', token)
            return token

        if method:
            count = count + 1

        self.code_write('call', {'label': func_name, 'count': count})

        if lib_call:
            self.code_write('lib_ret_address', {'label': lib_call_label,})

        token = self.get_token()

        return token, f_type == 'void'

    def do_expression_list(self, class_name, f_name, token):
        count = 0
        while True:
            token = self.do_expression(class_name, f_name, token)
            count = count + 1
            if not token.is_comma():
                break
            token = self.get_token()
        return token, count

    def do_par_expression(self, owner, class_name, f_name):
        # (
        token = self.get_token()
        if not token.is_left_par():
            self.error_message(owner, '(', token)
            return

        # expression
        token = self.get_token()
        token = self.do_expression(class_name, f_name, token)

        # )
        if not token.is_right_par():
            self.error_message(owner, ')', token)
            return

    def do_wv_par_statements(self, owner, class_name, f_name):
        # {
        token = self.get_token()
        if not token.is_left_wv_par():
            self.error_message(owner, '{', token)
            return

        # statements
        token = self.get_token()
        token = self.do_statements(class_name, f_name, token)

        # }
        if not token.is_right_wv_par():
            self.error_message(owner, '}', token)
            return

    def code_write(self, func, args):
        if self.env['verbose'] > 0:
            print('%s, %s' % (func, args))
        code = self.writer[func](args)
        source_marker = '// source %d %s' % (
            self.current_line_number,
            self.current_function or '-',
        )
        self.codes.append(source_marker)
        self.codes.extend(code)

    def error_message(self, who, expect, actual):
        print('\033[31m%s expect: %s, but actually appear %s\033[0m' % (who, expect, actual))
        print('\033[31mline: %d\033[0m' % actual.line_number)
        self.error = True
        return
