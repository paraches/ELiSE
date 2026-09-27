#
# MathLib info
# http://ngs.no.coocan.jp/doc/wiki.cgi/TechHan?page=Appendix+A%2E2+Math%2DPack
# UMULt 314AH   de = bc * de
# ISUB  3167H   hl = de - hl
# IADD  3172H   hl = de + hl
# IMULT 3193H   hl = de * hl
# IDIV  31E6H   hl = de / hl
# IMOD  323AH   hl = de % hl, de = de / hl
#
call_address_dic = {
    'MSXMath.multiply': '0x3193',
    'MSXMath.divide': '0x31E6',
    'MSXMath.modulo': '0x323A',
}

code = {
    'multiply': [
        '',
        '; multiply 2 args',
        ';',
        '; return hl',
        '; use MSX Math library'
        '',
        'Math.multiply:',
        'call 0x3193',  # MSX IMULT
        'ret',
    ],
    'divide': [
        '',
        '; divide 2 args',
        ';',
        '; hl = de / hl',
        '; return hl',
        '; use MSX Math library'
        '',
        'Math.divide:',
        'call 0x31E6',  # MSX IDIV
        'ret',
    ],
    'modulo': [
        '',
        '; modulo 2 args',
        ';',
        '; hl = de mod hl',
        '; return hl',
        '; use MSX Math library'
        '',
        'Math.divide:',
        'call 0x323A',  # MSX IDIV
        'ret',
    ]
}
