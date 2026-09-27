def end_code(env):
    code = [
        '',
        ';',
        '; end code',
        ';',
        # 'end start',
    ]
    if env['media'] == 'msxpen':
        code.append('end start')
    else:
        code.append('End:')
    return code


def work_area(env, static_list, string_dic, data_dic):
    if env['media'] == 'cartridge':
        return cartridge_work_area(env, static_list, string_dic, data_dic)

    work_org = ('ORG %s' % hex(env['org']+env['size'])) if env['media'] == 'cartridge' else ''
    work = [
        '',
        ';              system const',
        'sys_init_sp:   equ %s' % hex(env['stack']),
        '',
        ';              work area',
        '',
        '               %s' % work_org,
        '',
        'sys_SP:        dw 0x0000',
        'sys_LOCAL:     dw 0x0000',
        'sys_ARGUMENT:  dw 0x0000',
        'sys_POINTER:',
        'sys_THIS:      dw 0x0000',
        'sys_THAT:      dw 0x0000',
        'sys_TEMP:      dw 0x0000, 0x0000, 0x0000, 0x0000',
        '   dw 0x0000, 0x0000, 0x0000, 0x0000',
        'sys_R10:       dw 0x0000',
        'sys_R11:       dw 0x0000',
        'sys_R12:       dw 0x0000',
        'sys_return:    dw 0x0000',
        '',

        # Memory.asm
        'mem_free_list:     dw heap             ; 1st free block',
        'prev_block_link:   dw mem_free_list    ; previous free block',
        'block_p:           dw 0x0000           ; current block',
        'next_block_p:      dw 0x0000           ; next block',
        'new_block_p:       dw 0x0000           ; created block',
        'size:              dw 0x0000           ; current block size',
        'req_size_2:        dw 0x0000           ; requested size x 2',
        '',

        # Sprite.asm
        'Sprite.off.original:   Db 0x00',
        '',

        # Timer.asm
        'timer_ticks:       dw 0x0000',
        'timer_installed:   dw 0x0000',
        'timer_old_hook:    dw 0x0000, 0x0000, 0x0000',
        '',

        # Sound.asm
        'sound_mixer:       dw 0x0000',
        'sound_remaining_a: dw 0x0000',
        'sound_remaining_b: dw 0x0000',
        'sound_remaining_c: dw 0x0000',
    ]
    debug_work = [
        '; work area of DebugLib',
        'Debug.af: dw 0x0000',
        'Debug.bc: dw 0x0000',
        'Debug.de: dw 0x0000',
        'Debug.hl: dw 0x0000',
        'Debug.ix: dw 0x0000',
        'Debug.iy: dw 0x0000',
        'Debug.af.string: db " A"',
        'Debug.bc.string: db "BC"',
        'Debug.de.string: db "DE"',
        'Debug.hl.string: db "HL"',
        'Debug.sp.string: db "SP"',
        'Debug.ix.string: db "IX"',
        'Debug.iy.string: db "IY"',
    ]
    heap_value = ('ORG %s' % hex(env['heap_start'])) if env['heap_start'] != 0 else ''
    heap = [
        '',
        '; heap',
        'heap:          %s' % heap_value,
        '   dw 0x0000   ; first link',  # 1st free area link is 0
        '   dw %s   ; block size' % hex(env['heap_size']),
        ''
    ]
    code = []
    code.extend(work)
    if env['db']:
        code.extend(debug_work)
    code.extend(create_static_labels(static_list))
    code.extend(create_string_labels(string_dic))
    code.extend(create_data_labels(data_dic))
    code.extend(heap)
    return code


def create_static_labels(static_list):
    code = [
        '',
        '; statics'
    ]
    for static in static_list:
        static_label = static + ':' + '         dw 0x0000'
        code.append(static_label)
    return code


def cartridge_work_area(env, static_list, string_dic, data_dic):
    """Place immutable data in ROM and reserve runtime state in RAM."""
    ram_base = env['org'] + env['size']
    code = [
        '',
        '; cartridge ROM data',
    ]
    code.extend(create_string_labels(string_dic))
    code.extend(create_data_labels(data_dic))
    if env['db']:
        code.extend([
            '',
            '; debug strings',
            'Debug.af.string: db " A"',
            'Debug.bc.string: db "BC"',
            'Debug.de.string: db "DE"',
            'Debug.hl.string: db "HL"',
            'Debug.sp.string: db "SP"',
            'Debug.ix.string: db "IX"',
            'Debug.iy.string: db "IY"',
        ])
    code.extend([
        '',
        '; cartridge RAM work area',
        'sys_init_sp: equ %s' % hex(env['stack']),
        '               ORG %s' % hex(ram_base),
        '',
    ])

    offset = 0

    def add_word(label):
        nonlocal offset
        code.append('%s: equ %s' % (label, hex(ram_base + offset)))
        offset += 2

    add_word('sys_SP')
    add_word('sys_LOCAL')
    add_word('sys_ARGUMENT')
    code.append('sys_POINTER: equ %s' % hex(ram_base + offset))
    code.append('sys_THIS: equ %s' % hex(ram_base + offset))
    offset += 2
    add_word('sys_THAT')
    code.append('sys_TEMP: equ %s' % hex(ram_base + offset))
    offset += 16
    for label in ('sys_R10', 'sys_R11', 'sys_R12', 'sys_return'):
        add_word(label)

    for label in (
        'mem_free_list',
        'prev_block_link',
        'block_p',
        'next_block_p',
        'new_block_p',
        'size',
        'req_size_2',
    ):
        add_word(label)

    code.append('Sprite.off.original: equ %s' % hex(ram_base + offset))
    offset += 2

    for label in ('timer_ticks', 'timer_installed'):
        add_word(label)
    code.append('timer_old_hook: equ %s' % hex(ram_base + offset))
    offset += 6

    for label in (
        'sound_mixer',
        'sound_remaining_a',
        'sound_remaining_b',
        'sound_remaining_c',
    ):
        add_word(label)

    if env['db']:
        for label in (
            'Debug.af',
            'Debug.bc',
            'Debug.de',
            'Debug.hl',
            'Debug.ix',
            'Debug.iy',
        ):
            add_word(label)

    for static in static_list:
        add_word(static)

    code.append('heap: equ %s' % hex(ram_base + offset))
    return code


def create_string_labels(string_dic):
    code = [
        '',
        '; strings'
    ]
    for key in string_dic:
        length = len(string_dic[key])
        length_string = hex(length)
        string_label = '%s:        db %s, "%s"' % (key, length_string, string_dic[key])
        code.append(string_label)
    return code


def create_data_labels(data_dic):
    code = [
        '',
        '; data'
    ]
    for key in data_dic:
        label = key + ':'
        code.append(label)
        db_string = 'db '
        for i in range(0, int(len(data_dic[key]) / 2)):
            v = '0x'+data_dic[key][i*2:i*2+2]+','
            db_string += v
        db_string = db_string[:len(db_string)-1]
        code.append(db_string)
    return code
