            ;
            ;   String Library
            ;

            ;
            ;   alloc String object
            ;       in      Stack:  address of string (label)
            ;                       length of string (byte)
            ;       out     Stack:  String object address
            ;       modify  all
            ;       label   String.new
            ;       func    function String new(int address, int length)
            ;
String.new:
            pop hl          ; size of string
            push hl         ; restore size of string
            inc hl          ; add area for string length
            ; string is packed into array
            ; size is 1/2
            srl l           ; r7 <- 0, C <- r0
            jr nc, String.no_modulo
            inc l           ; add modulo memory
String.no_modulo:
            ld de, String.new.ret
            push de         ; return address
            push hl         ; actual required memory size
            jp Memory.alloc
String.new.ret:
            pop hl          ; hl is allocated memory addres for string object
            ld (sys_TEMP + 4), hl   ; store allocated memory address
            pop bc          ; byte size of string
            ld (hl), c      ; String[0] is length of string
            inc hl          ; string is start from this address
            pop de          ; passed string address
            ex de, hl
            ldir            ; block move (de) <- (hl)
            ld hl, (sys_TEMP + 4)   ; String object address
            ex (sp), hl
            push hl
            ret


            ;
            ;   dispose String object
            ;       in      Stack:  String object address
            ;       modify  all
            ;       label   String.dispose
            ;       func    function void dispose(String obj)
            ;
String.dispose:
            ld hl, String.dispose.ret
            ex (sp), hl
            push hl
            jp Memory.deAlloc
String.dispose.ret:
            ret


            ;
            ;   get String length
            ;       in      Stack:  String object address
            ;       out     Stack:  String length
            ;       modify  None
            ;       label   String.length
            ;       func    function int length(String obj)
            ;
String.length:
            pop de
            ld a, (de)
            ld l, a
            ld h, 0
            ex (sp), hl
            push hl
            ret


            ;
            ;   get character at
            ;       in      Stack:  String object address
            ;               Stack:  index to get
            ;       out     Stack:  value of character at index
            ;       modify  BC, HL
            ;       label   String.charAt
            ;       func    function int charAt(String obj, int index)
            ;
String.charAt:
            pop bc          ; index
            pop hl          ; String object
            inc hl          ; character start from here
            add hl, bc      ; hl <- indexed address
            ld c, (hl)      ; c <- character at index
            ld b, 0         ; return a zero-extended character
            pop hl          ; return address
            push bc         ; return value
            push hl
            ret


            ;
            ;   String to Integer
            ;       in      DE: String object address
            ;       out     HL: Integer value
            ;               A : Integer value in 8bit
            ;       modify  all
            ;       label   String._S2I
            ;
            ;       Need to care string is not finish 0x30-0x39
String._S2I:
            ld hl, 0
String._S2I.loop:
            ld a, (de)
            sub 0x30
            cp 10
            ret nc
            inc de
            ld b, h
            ld c, l
            add hl, hl
            add hl, hl
            add hl, bc
            add hl, hl
            add a, l
            ld l, a
            jr nc, String._S2I.loop
            inc h
            jr String._S2I.loop


            ;
            ;   2digit Hex String to Integer
            ;       in      HL: character address to transfer
            ;       out     A : Integer value
            ;       modify  all
            ;       label   String._H2I
            ;
String._H2I:
            ld a, (hl)
            inc hl
            ld e, (hl)

            call String._H2I.Hex1digit
            add a, a
            add a, a
            add a, a
            add a, a
            ld d, a
            ld a, e
            call String._H2I.Hex1digit
            or d
            ret
String._H2I.Hex1digit:
            sub '0'
            cp 10
            ret c
            sub 'A'-'0'-10
            ret
