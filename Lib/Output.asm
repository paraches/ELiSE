            ;
            ;   Output Library
            ;

            ;
            ;   Print HL in Decimal
            ;
            ;   in      HL
            ;   out     None
            ;   modify  AF, BC, HL
            ;   label   Output._printIntDec
Output._printIntDec:
            ld bc, -10000
            call Output._printIntDec.0
            ld bc, -1000
            call Output._printIntDec.0
            ld bc, -100
            call Output._printIntDec.0
            ld bc, -10
            call Output._printIntDec.0
            ld c, -1
Output._printIntDec.0:
            ld a, 0x2F
Output._printIntDec.1:
            inc a
            add hl, bc
            jr c, Output._printIntDec.1
            sbc hl, bc
            call 0x00A2         ; MSX CHPUT
            ret

            ;
            ;   print HL in Hex
            ;   in      HL
            ;   modify  AF, BC, HL
            ;   label   Output._printIntHex
            ;
Output._printIntHex:
            ld c, h
            call Output._printIntHex.0
            ld c, l
Output._printIntHex.0:
            ld a, c
            rra
            rra
            rra
            rra
            call Output._printIntHex.1
            ld a, c
Output._printIntHex.1:
            and 0x0F
            add a, 0x90
            daa
            adc a, 0x40
            daa
            call 0x00A2         ; MSX CHPUT
            ret

            ;
            ;   print string pointed HL
            ;   in      HL: first character of string which end by 0x00.
            ;   modify  A, HL
            ;   label   Output._printStringHL
            ;
Output._printStringHL:
            ld a, (hl)
            cp 0
            ret z
            call 0x00A2         ; MSX CHPUT
            inc hl
            jr Output._printStringHL

            ;
            ;   print Str255 pointed by HL
            ;   in      HL: first character of Str255
            ;   modify  A, HL, B
            ;   label   Output._printStr255HL
            ;
Output._printStr255HL:
            ld b, (hl)
            xor a
            or b
            ret z
Output._printStr255HL_LOOP:
            inc hl
            ld a, (hl)
            call 0x00A2         ; MSX CHPUT
            djnz Output._printStr255HL_LOOP
            ret

            ;
            ;   print LF + CR
            ;   in
            ;   modify  a
            ;   label   Output._printLn
            ;
Output._printLn:
            ld a, 0x0a
            call 0x00A2         ; MSX CHPUT
            ld a, 0x0d
            call 0x00A2         ; MSX CHPUT
            ret

            ;
            ;   print LF + CR
            ;
            ;   in
            ;   modify  a, hl
            ;   label   Output.printLn
            ;   func    function void printLn()
            ;
Output.printLn:
            call Output._printLn
            ret

            ;
            ;   print value on stack in decimal
            ;   in      stack: value to print
            ;   modify  A, BC, DE, HL
            ;   label   Output.printInt
            ;   func    function void printInt(int value)
            ;
Output.printInt:
            pop hl          ; value to print
            call Output._printIntDec
            ret

            ;
            ;   print value on stack in decimal with LF,CR
            ;   in      stack
            ;   modify  A, BC,DE, HL
            ;   label   Output.printIntLn
            ;   func    function void printIntLn(int value)
            ;
Output.printIntLn:
            pop hl          ; value to print
            call Output._printIntDec
            call Output._printLn
            ret

            ;
            ;   print value on stack in hex
            ;   in      stack: value to print
            ;   modify  A, BC,DE, HL
            ;   label   Output.printIntHex
            ;   func    function void printIntHex(int value)
            ;
Output.printIntHex:
            pop hl          ; value to print
            call Output._printIntHex
            ret

            ;
            ;   print value on stack in hex with LF,CR
            ;   in      stack: value to print
            ;   modify  A, BC,DE, HL
            ;   label   Output.printIntHexLn
            ;   func    function void printIntHexLn(int value)
            ;
Output.printIntHexLn:
            pop hl          ; value to print
            call Output._printIntHex
            call Output._printLn
            ret

            ;
            ;   print Str255
            ;   in      stack: address of Str255
            ;   modify  A, BC, DE, HL
            ;   label   Output.printStr255
            ;   func    function void printStr255(int value)
            ;   func    function void printString(int value)
            ;
Output.printString:
Output.printStr255:
            pop hl          ; address of Str255
            call Output._printStr255HL
            ret

            ;
            ;   print Str255 LF + CR
            ;   in      stack: address of Str255
            ;   modify  A, BC, DE, HL
            ;   label   Output.printStr255Ln
            ;   func    function void printStr255Ln(int value)
            ;   func    function void printStringLn(int value)
            ;
Output.printStringLn:
Output.printStr255Ln:
            pop hl          ; address of Str255
            call Output._printStr255HL
            call Output._printLn
            ret


            ;
            ;   print character with code
            ;   in      stack: ascii code of character to print
            ;   modify  A, HL
            ;   label   Output.printChar
            ;   func    function void printChar(int value)
            ;
Output.printChar:
            pop hl
            ld a, l         ; character code to print
            call CHPUT
            ret
