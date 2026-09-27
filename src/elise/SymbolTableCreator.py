import os
from .SymbolTable import SymbolTable
from .Tokenizer import Tokenizer
from .Util.file_lib import files_in_dir


def error(place, expect, actual):
    print('%s expect: %s, but actually appear %s' % (place, expect, actual.value))
    return


class SymbolTableCreator:
    def __init__(self):
        self.table = SymbolTable()
        self.tokens = []
        self.token_index = 0

    #
    # Create SymbolTable from Library
    #   read library comment
    #       ; func f_kind f_type f_name ( v_type v_name , ... )
    #
    def add_library(self, directory):
        current_directory = os.getcwd()
        lib_directory = os.path.join(current_directory, directory)

        lib_files = files_in_dir(lib_directory, 'asm')
        if lib_files is None:
            print('No Library found...')
            return
        for lib_file in lib_files:
            self.add_lib_functions(lib_file)
        return

    def add_lib_functions(self, file):
        class_name = os.path.basename(file).split('.')[0]
        self.table.add_class(class_name, 'library')
        with open(file, 'r') as f:
            for line in f:
                line = line.replace('(', ' ( ')
                line = line.replace(')', ' ) ')
                line = line.replace('.', ' . ')
                tokens = line.strip().split()
                if 'func' in tokens:
                    f_kind = tokens[2]
                    f_type = tokens[3]
                    f_name = tokens[4]
                    self.table.add_function(class_name, f_kind, f_type, f_name)
                    index = 6
                    v_kind = 'argument'
                    while tokens[index] != ')':
                        v_type = tokens[index]
                        v_name = tokens[index+1]
                        self.table.add_function_var(class_name, f_name, v_kind, v_type, v_name)
                        index += 2
                        if tokens[index] != ',':
                            break
                        index += 1

    def get_token(self):
        if self.token_index < len(self.tokens):
            token = self.tokens[self.token_index]
            self.token_index = self.token_index + 1
            while token.is_remark():
                token = self.tokens[self.token_index]
                self.token_index = self.token_index + 1
            return token
        else:
            print('token_index(%d) is over the size of tokens(%d).' % (self.token_index, len(self.tokens)))

    #
    # Create SymbolTable from tokens
    #
    def create(self, file):
        tokenizer = Tokenizer()
        self.token_index = 0
        self.tokens = tokenizer.tokenize(file)
        self.start()

    def start(self):
        token = self.get_token()
        while token is not None:
            if token.is_class():
                self.do_class()
                return
            else:
                token = self.get_token()

    def do_class(self):
        # class name
        token = self.get_token()
        if not token.is_identifier():
            error('class', 'identifier', token)
            return None
        class_name = token.value
        self.table.add_class(class_name)

        # {
        token = self.get_token()
        if not token.is_left_wv_par():
            error('class', '{', token)
            return None

        # class var
        token = self.get_token()
        token = self.do_class_var_dec(class_name, token)

        # subroutine dec
        # subroutine kind
        while token.is_subroutine_kind():
            token = self.do_subroutine(class_name, token)

        return None

    def do_class_var_dec(self, class_name, token):
        while token.is_class_var_kind():
            var_kind = token.value
            # var type
            token = self.get_token()
            if not token.is_var_type():
                error('class_var', 'var_type', token)
                return None
            var_type = token.value

            # var name
            token = self.get_token()
            while token.is_var_name():
                var_name = token.value

                # add class var
                self.table.add_class_var(class_name, var_kind, var_type, var_name)

                # ,
                token = self.get_token()
                if not token.is_comma():
                    break

                token = self.get_token()

            # ;
            if not token.is_semi_colon():
                error('class_var', ';', token)
                return None

            token = self.get_token()

        return token

    def do_subroutine(self, class_name, token):
        subroutine_kind = token.value

        # subroutine type
        token = self.get_token()
        if not token.is_subroutine_type():
            error('subroutine', 'subroutine_type', token)
            return None
        subroutine_type = token.value

        # subroutine name
        token = self.get_token()
        if not token.is_identifier():
            error('subroutine', 'identifier', token)
            return None
        subroutine_name = token.value

        # add subroutine
        self.table.add_function(class_name, subroutine_kind, subroutine_type, subroutine_name)

        # this for method
        if subroutine_kind == 'method':
            self.table.add_function_var(class_name, subroutine_name, 'argument', class_name, 'this')

        # arguments
        token = self.get_token()
        token = self.do_argument_list(class_name, subroutine_name, token)

        # {
        if not token.is_left_wv_par():
            error('subroutine', '{', token)
            return None

        # var
        token = self.get_token()
        token = self.do_var_dec(class_name, subroutine_name, token)

        # }
        left_wv_par = 1
        while left_wv_par != 0:
            token = self.get_token()
            if token.is_right_wv_par():
                left_wv_par -= 1
            elif token.is_left_wv_par():
                left_wv_par += 1

        token = self.get_token()
        return token

    def do_argument_list(self, class_name, subroutine_name, token):
        var_kind = 'argument'
        # (
        if not token.is_left_par():
            error('subroutine', '(', token)
            return None

        # var_type var_name (, var_name)
        token = self.get_token()
        while token.is_var_type():
            # var_type
            var_type = token.value
            token = self.get_token()

            # var_name
            if not token.is_var_name():
                error('argument_list', 'var_name', token)
                return None
            var_name = token.value

            # add var
            self.table.add_function_var(class_name, subroutine_name, var_kind, var_type, var_name)

            # ,
            token = self.get_token()
            if not token.is_comma():
                break
            token = self.get_token()

        # )
        if not token.is_right_par():
            error('argument_list', ')', token)
            return None

        token = self.get_token()
        return token

    def do_var_dec(self, class_name, subroutine_name, token):
        while token.value == 'var':
            # var type
            token = self.get_token()
            if not token.is_var_type():
                error('varDec', 'varType', token)
                return None
            var_type = token.value

            # var name
            token = self.get_token()
            while token.is_var_name():
                var_name = token.value

                # add var
                self.table.add_function_var(class_name, subroutine_name, 'local', var_type, var_name)

                # ,
                token = self.get_token()
                if not token.is_comma():
                    break
                token = self.get_token()

            # ;
            if not token.is_semi_colon():
                error('varDec', ';', token)
                return None

            token = self.get_token()
        return token
