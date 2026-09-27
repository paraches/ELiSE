def init_code(env):
    code_0 = [
        ';',
        '; %s' % env['directory'],
        ';',
        '; compiled by',
        ';',
        '; ELiSE Cross compiler for MSX',
        ';',
        '',
        ';',
        'org %s' % hex(env['org']),
        ';',
        '',
    ]
    code_cartridge = [
        ';',
        '; ROM Header',
        ';',
        'db "AB"',
        'dw start',
        'dw 0,0,0,0,0,0',
    ]
    end_code = 'jp Sys.return'
    if env['media'] == 'cartridge':
        end_code = 'jp Boot.main.0'
    code_2 = [
        ';',
        '; boot code',
        ';',
        'start:',
        '; save environment SP and set new SP to below HiMem (0xDE79 on MSXPen)',
        'ld (sys_return), sp',  # save environment SP
        'ld sp, sys_init_sp',  # set SP to top of stack area
        'ld (sys_LOCAL), sp',  # set LCL to SP (function Main.main have 0 local var)
        '',
        '; call Main.main 0 in compiler way',
        'ld hl, Boot.main.0',
        'push hl',
        '',
        '; dummy push for Local, argument, this that',
        'ld hl, 0x0000',
        'push hl',
        'push hl',
        'push hl',
        'push hl',
        'add hl, sp',
        'dec hl',
        'dec hl',
        'ld (sys_LOCAL), hl',
        'ld de, 10',
        'add hl, de',
        'ld (sys_ARGUMENT), hl',
        'jp Main.main',
        'Boot.main.0:',
        '%s' % end_code,
        '',
        ';',
        '; boot code end',
        ';',
    ]
    if env['media'] == 'cartridge':
        init_ram = [
            '',
            '; initialize cartridge RAM work area',
            'ld hl, heap',
            'ld (mem_free_list), hl',
            'xor a',
            'ld (hl), a',
            'inc hl',
            'ld (hl), a',
            'inc hl',
            'ld de, %s' % hex(env['heap_size']),
            'ld (hl), e',
            'inc hl',
            'ld (hl), d',
            '',
        ]
        insert_at = code_2.index('') + 1
        code_2[insert_at:insert_at] = init_ram

    return_code = code_0
    if env['media'] == 'cartridge':
        return_code.extend(code_cartridge)
    return_code.extend(code_2)
    return return_code


def lib_code(env):
    code = init_code(env)
    return code
