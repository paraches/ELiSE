            ;
            ;   Debug Library
            ;

            ;
            ;   memory dump
            ;
            ;   in      HL: start address to dump
            ;           E:  number of row (8 byte / row)
            ;   out     None
            ;   modify  AF, BC, DE, HL
            ;
Debug._memoryDump:
            call Output._printIntHex    ; print address
            ld a, 0x20                  ; space
            call 0x00A2                 ; MSX CHPUT
            ld b, 0x08                  ; 8 byte / row
Debug._memoryPrintByte:
            ld c, (hl)
            call Output._printIntHex.0  ; print c in hex
            ld a, 0x20                  ; space
            call 0x00A2                 ; MSX CHPUT
            inc hl
            djnz Debug._memoryPrintByte
            ld a, 0x0a                  ; LF
            call 0x00A2                 ; MSX CHPUT
            ld a, 0x0d                  ; CR
            call 0x00A2                 ; MSX CHPUT
            dec e
            jr nz, Debug._memoryDump
            ret

            ;
            ;   memory dump
            ;
            ;   in      stack: start address
            ;           stack: row (8 byte / row)
            ;   out     None
            ;   label   Debug.memDump
            ;   func    function void memDump(int address, int row)
            ;
Debug.memDump:
            pop de
            pop hl
            call Debug._memoryDump
            ret

            ;
            ;   print value in stack
            ;   in      stack: value to print
            ;   out     None
            ;   modify  AF, BC, DE, HL
            ;   label   Debug.printStack
            ;   func    function void printStack(int value)
            ;
Debug.printStack:
            pop hl                      ; return address
            pop de                      ; value to print
            push de                     ; restore value
            push hl                     ; return address
            ld c, d
            call Output._printIntHex.0  ; print D
            ld c, e
            call Output._printIntHex.0  ; print E
            call Output._printLn        ; LF+CR
            ret

            ;
            ;   return System
            ;   label   Debug.halt
            ;   func    function void halt()
            ;
Debug.halt:
            jp Sys.return

            ;
            ;   show SP
            ;   label   Debug._showSP
            ;   actual SP is sp + 2 (when call this, push return address)
            ;
Debug._showSP:
            ld hl, 2
            add hl, sp
            call Output._printIntHex
            ret

            ;
            ;   show SP
            ;   actual SP is sp + 2 (when call this, push return address)
            ;
            ;   label   Debug.showSP
            ;   func    function void showSP()
            ;
Debug.showSP:
            ld hl, 0x0002
            add hl, sp
            call Output._printIntHex
            ret

            ;
            ;   show SP
            ;   actual SP is sp + 2 (when call this, push return address)
            ;
            ;   label   Debug.showSPLn
            ;   func    function void showSPLn()
            ;
Debug.showSPLn:
            ld hl, 0x0002
            add hl, sp
            call Output._printLn
            ret

            ;
            ;   show registers
            ;   label Debug.showReg
            ;   func    function void showReg()
            ;
Debug.showReg:
            ld (Debug.af), a
            ld (Debug.hl), hl
            ex de, hl
            ld (Debug.de), hl
            ld h, b
            ld l, c
            ld (Debug.bc), hl
            ld (Debug.ix), ix
            ld (Debug.iy), iy

            ; print SP
            ld de, Debug.sp.string
            ld hl, 2        ; SP is already pushed to call this
            add hl, sp
            call Debug._printReg

            ; print IX
            ld de, Debug.ix.string
            ld hl, (Debug.ix)
            call Debug._printReg

            ; print IY
            ld de, Debug.iy.string
            ld hl, (Debug.iy)
            call Debug._printReg

            call Output._printLn

            ; print bc
            ld de, Debug.bc.string
            ld hl, (Debug.bc)
            call Debug._printReg

            ; print de
            ld de, Debug.de.string
            ld hl, (Debug.de)
            call Debug._printReg

            ; print hl
            ld de, Debug.hl.string
            ld hl, (Debug.hl)
            call Debug._printReg

            call Output._printLn

            ; print A
            ld de, Debug.af.string
            ld a, (Debug.af)
            ld l, a
            ld h, 0
            call Debug._printReg

            call Output._printLn
            ret

Debug._printReg:
            ld a, (de)
            call CHPUT
            inc de
            ld a, (de)
            call CHPUT
            ld a, ':'
            call CHPUT
            call Output._printIntHex
            ld a, ' '
            call CHPUT
            ret

            ;
            ;   show system work area
            ;   label Debug.printWork
            ;
Debug.printWork:
            ld hl, sys_SP
            ld e, 6
            call Debug._memoryDump
            ret

            ;
            ;   Memory debug setMemFreeList
            ;
            ;       in      stack:  address to set
            ;       out     stack:
            ;       modify  DE, HL
            ;       label   Debug.setMemFreeList
            ;       func    function void setMemFreeList(int address)
            ;
Debug.setMemFreeList:
            pop hl
            ld (mem_free_list), hl
            ret

            ;
            ;   Memory debug memFreeList
            ;
            ;       in      stack:
            ;       out     stack:  value of mem_free_list
            ;       modify  HL
            ;       label   Debug.memFreeList
            ;       func    function int memFreeList()
            ;
Debug.memFreeList:
            ld hl, (mem_free_list)
            ex (sp), hl
            push hl
            ret

            ;
            ;   Memory debug free heap area
            ;
            ;       in      stack:
            ;       out     stack:  value of free area of heap
            ;       modify  DE, HL
            ;       label   Debug.freeHeap
            ;       func    function int freeHeap()
            ;
Debug.freeHeap:
            ld bc, 0x0000
            ld hl, (mem_free_list)

debug_mem_free_loop
            inc hl
            inc hl
            ld e, (hl)
            inc hl
            ld d, (hl)
            ex de, hl
            add hl, bc
            ld b, h
            ld c, l
            ex de, hl
            dec hl
            dec hl
            ld d, (hl)
            dec hl
            ld e, (hl)
            ld a, d
            or e
            jr z, debug_mem_free_end

            ex de, hl
            jr debug_mem_free_loop

debug_mem_free_end:
            ld h, b
            ld l, c
            ex (sp), hl
            push hl
            ret


            ;
            ;   Memory debug heapAddress
            ;
            ;       in
            ;       out     stack: heap top address
            ;       modify  HL
            ;       label   Debug.heapAddress
            ;       func    function int heapAddress()
            ;
Debug.heapAddress:
            ld hl, heap
            ex (sp), hl
            push hl
            ret
