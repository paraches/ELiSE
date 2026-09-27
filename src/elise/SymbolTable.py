

class SymbolTable:
    def __init__(self):
        self.class_tables = {}

    def __str__(self):
        for c in self.class_tables.keys():
            print('class: %s' % c)
            print('%s' % self.class_tables[c])
        return ''

    def add_class(self, class_name, class_type='normal'):
        self.class_tables[class_name] = self.ClassTable(class_type)

    def add_class_parent(self, class_name, parent_name):
        class_table = self.class_tables[class_name]
        class_table.add_parent(parent_name)

    def add_class_var(self, class_name, var_kind, var_type, var_name):
        class_table = self.class_tables[class_name]
        class_table.add_class_var(var_kind, var_type, var_name)

    def add_function(self, class_name, f_kind, f_type, f_name):
        class_table = self.class_tables[class_name]
        class_table.add_function(f_kind, f_type, f_name)

    def add_function_var(self, class_name, function_name, v_kind, v_type, v_name):
        class_table = self.class_tables[class_name]
        function_table = class_table.functions[function_name]
        function_table.add_var(v_kind, v_type, v_name)

    def class_type(self, class_name):
        if class_name in self.class_tables:
            return self.class_tables[class_name].class_type
        return None

    def function_kind(self, class_name, f_name):
        return self.class_tables[class_name].function_kind(f_name)

    def function_type(self, class_name, f_name):
        return self.class_tables[class_name].function_type(f_name)

    def var_kind_count(self, class_name, f_name, v_kind):
        return self.class_tables[class_name].var_kind_count(f_name, v_kind)

    def var_info(self, class_name, f_name, v_name):
        return self.class_tables[class_name].var_info(f_name, v_name)

    def var_kind(self, class_name, f_name, v_name):
        return self.class_tables[class_name].var_kind(f_name, v_name)

    def var_type(self, class_name, f_name, v_name):
        return self.class_tables[class_name].var_type(f_name, v_name)

    def var_number(self, class_name, f_name, v_name):
        return self.class_tables[class_name].var_number(f_name, v_name)

    class ClassTable:
        def __init__(self, class_type='normal'):
            self.class_vars = {'static': {}, 'field': {}}
            self.functions = {}
            self.parent = None
            self.class_type = class_type  # normal, library, quick(Math)

        def __str__(self):
            print('\tparent: %s' % self.parent)
            print('\ttype: %s' % self.class_type)
            print('\tstatic: %s' % self.class_vars['static'])
            print('\tfield: %s' % self.class_vars['field'])
            print('\tfunctions:')
            for f in self.functions.keys():
                print('\t\t%s' % f)
                print('\t\t%s' % self.functions[f])
            return ''

        def add_class_parent(self, parent_name):
            self.parent = parent_name

        def add_class_var(self, var_kind, var_type, var_name):
            if var_name in self.class_vars['static'] or var_name in self.class_vars['field']:
                print('Error: %s is already declared.' % var_name)
                return
            count = self.var_kind_count(None, var_kind)
            self.class_vars[var_kind][var_name] = {'type': var_type, 'number': count}

        def add_function(self, f_kind, f_type, f_name):
            self.functions[f_name] = SymbolTable.FunctionTable(f_kind, f_type)

        def function_kind(self, f_name):
            return self.functions[f_name].function_kind

        def function_type(self, f_name):
            if f_name in self.functions:
                return self.functions[f_name].function_type
            else:
                return None

        def var_kind_count(self, f_name, v_kind):
            if v_kind in ['static', 'field']:
                return len(self.class_vars[v_kind])
            else:
                return self.functions[f_name].var_kind_count(v_kind)

        def var_info(self, f_name, v_name):
            info = self.functions[f_name].var_info(v_name)
            if info is None:
                if v_name in self.class_vars['static']:
                    info = self.class_vars['static'][v_name]
                    info.update({'kind': 'static'})
                elif v_name in self.class_vars['field']:
                    info = self.class_vars['field'][v_name]
                    info.update({'kind': 'field'})
            return info

        def var_kind(self, f_name, v_name):
            return self.functions[f_name].var_kind(v_name)

        def var_type(self, f_name, v_name):
            return self.functions[f_name].var_type(v_name)

        def var_number(self, f_name, v_name):
            return self.functions[f_name].var_number(v_name)

    class FunctionTable:
        def __init__(self, f_kind, f_type):
            self.function_kind = f_kind
            self.function_type = f_type
            self.vars = {'argument': {}, 'local': {}}

        def __str__(self):
            print('\t\t\tkind: %s' % self.function_kind)
            print('\t\t\ttype: %s' % self.function_type)
            print('\t\t\targument: %s' % self.vars['argument'])
            print('\t\t\tlocal: %s' % self.vars['local'])
            return ''

        def var_kind_count(self, v_kind):
            return len(self.vars[v_kind])

        def add_var(self, v_kind, v_type, v_name):
            if v_name in self.vars['argument'] or v_name in self.vars['local']:
                print('Error: %s is already declared.' % v_name)
                return
            count = self.var_kind_count(v_kind)
            self.vars[v_kind][v_name] = {'type': v_type, 'number': count}

        def var_info(self, v_name):
            info = None
            if v_name in self.vars['argument']:
                info = self.vars['argument'][v_name]
                info.update({'kind': 'argument'})
            elif v_name in self.vars['local']:
                info = self.vars['local'][v_name]
                info.update({'kind': 'local'})
            return info

        def var_kind(self, v_name):
            if v_name in self.vars['argument']:
                return 'argument'
            elif v_name in self.vars['local']:
                return 'local'
            else:
                return None

        def var_type(self, v_name):
            kind = self.var_kind(v_name)
            if kind is None:
                return kind
            return self.vars[kind][v_name]['type']

        def var_number(self, v_name):
            kind = self.var_kind(v_name)
            if kind is None:
                return kind
            return self.vars[kind][v_name]['number']
