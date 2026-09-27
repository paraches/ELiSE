def vm_push(dic):
    codes = ['push %s %s' % (dic['kind'], dic['number'])]
    return codes


def vm_pop(dic):
    codes = ['pop %s %s' % (dic['kind'], dic['number'])]
    return codes


def vm_arithmetic(dic):
    codes = ['%s' % dic['opcode']]
    return codes


def vm_shift_const(dic):
    codes = ['%s_const %s' % (dic['opcode'], dic['count'])]
    return codes


def vm_function(dic):
    codes = ['function %s %s' % (dic['label'], dic['count'])]
    return codes


def vm_label(dic):
    codes = ['label %s' % dic['label']]
    return codes


def vm_goto(dic):
    codes = ['goto %s' % dic['label']]
    return codes


def vm_if(dic):
    codes = ['if-goto %s' % dic['label']]
    return codes


def vm_call(dic):
    codes = ['call %s %s' % (dic['label'], dic['count'])]
    return codes


def vm_lib_call(dic):
    codes = ['lib_call %s' % dic['label']]
    return codes


def vm_lib_ret_address(dic):
    codes = ['lib_ret_address %s' % dic['label']]
    return codes


def vm_return(dic):
    codes = ['return %s' % dic['void']]
    return codes


def vm_data(dic):
    codes = ['data %s %s' % (dic['label'], dic['value'])]
    return codes


def vm_x2(dic):
    codes = ['x2']
    return codes
