            ;
            ;   Math Library
            ;

            ;
            ;   abs HL
            ;       in      Stack: value to get absolute
            ;       out     Stack: absolute value
            ;       modify  A, HL
            ;       label   Math.abs
            ;       func    function int abs(int value)
            ;
Math.abs:
            pop hl
            bit 7, h
            jr z, Math.abs.return
            xor a
            sub l
            ld l, a
            sbc a, a
            sub h
            ld h, a
Math.abs.return:
            ex (sp), hl
            push hl
            ret