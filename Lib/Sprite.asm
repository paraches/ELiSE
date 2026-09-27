            ;
            ;   Sprite Library
            ;

Sprite.att.table: equ 0x1b00

            ;
            ;   Sprite Init
            ;
            ;   in      None
            ;   out     None
            ;   modify  AF, BC, DE, HL
            ;   label   Sprite.init
            ;   func    function void init()
            ;   msx     CLRSPR 0x0069
            ;
Sprite.init:
            call CLRSPR
            ret


            ;
            ;   Sprite configure
            ;
            ;   in      Stack:  size/Mag    0: 8x8, Std
            ;                               1: 8x8, x2
            ;                               2: 16x16, Std
            ;                               3: 16x16, x2
            ;   modify  all
            ;   label   Sprite.config
            ;   func    function void config(int value)
            ;
Sprite.config:
            pop de
            ld a, e
            and 0x03
            ld e, a
            ld a, (0xF3E0)    ; BIOS work area: current VDP R#1 value
            and 0xFC        ; clear sprite size/magnification bits
            or e
            ld b, a
            ld c, 1		; R#1
            call WRTVDP
			RET


            ;
            ;   Sprite put
            ;
            ;   in      Stack:  x position
            ;           Stack:  y position
            ;           Stack:  sprite table number
            ;           Stack:  color
            ;           Stack:  sprite number
            ;   modify  all
            ;   label   Sprite.put
            ;   func    function void put(int x, int y, int table_num, int color, int sprite_number)
            ;
Sprite.put:
            pop de
            ld b, e         ; b <- sprite number
            pop de
            ld c, e         ; c <- color
            pop de
            sla e
            sla e           ; de <- address offset
            ld hl, Sprite.att.table
            add hl, de      ; hl <- address of table
            pop de          ; e <- y position
            ld a, e
            call WRTVRM
            inc hl
            pop de          ; e <- x position
            ld a, e
            call WRTVRM
            inc hl
            ld a, b
            call WRTVRM
            inc hl
            ld a, c
            call WRTVRM
            ret

            ;
            ;   Sprite off
            ;
            ;   in
            ;   modify  a, hl
            ;   label   Sprite.off
            ;   func    function void off()
            ;
Sprite.off:
            ld hl, Sprite.att.table
            call RDVRM
            ld (Sprite.off.original), a
            ld a, 208
            call WRTVRM
            ret


            ;
            ;   Sprite on
            ;
            ;   in
            ;   modify  a, hl
            ;   label   Sprite.on
            ;   func    function void on()
            ;
Sprite.on:
            ld a, (Sprite.off.original)
            ld hl, Sprite.att.table
            call WRTVRM
            ret


            ;
            ;   Sprite off #
            ;   number is sprite table number (0-31)
            ;
            ;   in      stack: number of sprite
            ;   modify  all
            ;   label   Sprite.offNum
            ;   func    function void offNum(int spriteTableNumber)
            ;
Sprite.offNum:
            ld hl, Sprite.att.table
            ld de, 4
            pop bc                      ; table number
            ld b, c
Sprite.off.number.loop:
            djnz Sprite.off.table.calc
            add hl, de
            jr Sprite.off.number.loop
Sprite.off.table.calc:
            ld a, 209
            call WRTVRM
            ret


            ;
            ;   Sprite on #
            ;   number is sprite table number (0-31)
            ;
            ;   in      stack: number of sprite
            ;           stack: new y pos
            ;   modify  all
            ;   label   Sprite.onNum
            ;   func    function void onNum(int spriteTableNumber, int yPos)
            ;
Sprite.onNum:
            pop hl
            ld a, l                     ; new y pos
            ld hl, Sprite.att.table
            ld de, 4
            pop bc                      ; table number
            ld b, c
Sprite.on.number.loop:
            djnz Sprite.off.table.calc
            add hl, de
            jr Sprite.off.number.loop
Sprite.on.table.calc:
            call WRTVRM
            ret
