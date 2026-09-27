            ;
            ;   MSX Library
            ;

CHPUT:      equ 0x00a2
INIT32:		equ 0x006F
SETGRP:		equ 0x007E
ROM_FONT:	equ 0x1BBF
WRTVDP:		equ 0x0047
RDVRM:		equ 0x004A
WRTVRM:     equ 0x004D
FILVRM:		equ 0x0056
LDIRVM:		equ 0x005C
CHGMOD:		equ 0x005F
SCRMOD:		equ 0xFCAF
PGT1:		equ 0x0000
PGT2:		equ 0x0800
PGT3:		equ 0x1000
COLT:		equ 0x2000
PNT:		equ 0x1800
GSPSIZ:		equ 0x008A
LINL32:     equ 0xF3AF
CRTCNT:		equ 0xF3B1
GICINI:     equ 0x0090
CLRSPR:     equ 0x0069

            ;
            ;   Screen init
            ;
            ;       screen 1.5,2,0:width 32:Keyoff
            ;       in      None
            ;       out     None
            ;       modify  all
            ;       label   Screen.cls
            ;       func    function void screenInit()
            ;       msx     CLS 0x00C3
            ;
MSX.screenInit:
            call prepare_width_32
			call INIT32
            call SETGRP
            call prepare_line_26
            call setup_color
            call setup_pat_gen
            call CLRSPR         ; before sprite size set, call sprite init
            call set_sprite_size_16
            RET

prepare_line_26:
            ld a, 26
            ld (CRTCNT), a
			RET

prepare_width_32:
			ld a, 32
            ld (LINL32), a
            RET

set_sprite_size_16:
            ld a, (0xF3E0)    ; BIOS work area: current VDP R#1 value
            and 0xFC          ; preserve display/interrupt bits
            or 0x02
            ld b, a
            ld c, 1		; R#1
            call WRTVDP
			RET

setup_pat_gen:
; Pattern Generator Table init
			ld hl, ROM_FONT
			ld de, PGT1
			ld bc, 8*256
			call LDIRVM
			ld hl, ROM_FONT
            ld de, PGT2
            ld bc, 8*256
            call LDIRVM
			ld hl, ROM_FONT
            ld de, PGT3
			ld bc, 8*256
            call LDIRVM
; Color Table init
			ld hl, COLT
			ld a, 0xF4 ; 前景: 15, 背景: 4
            ld bc, 0x800*3
			call FILVRM
; Pattern Name Table fill by ' '
			ld hl, PNT
			ld a, ' '
			ld bc, 32*24
            call FILVRM
            ret


            ;
            ;   Key click sound
            ;
            ;   in      Stack: on:true, off: false
            ;   modify
            ;   label   MSX.keyClick
            ;   func    function void keyClick(int state)
            ;   msx     CLIKSW
            ;
MSX.keyClick:
            pop hl     ; on/off value
            ld a, h
            or l            ; 0: off, other: on
            ld (0xF3DB), a  ; MSX CLIKSW
            ret


            ;
            ;   PSG init
            ;
            ;   in      None
            ;   out     None
            ;   modify  all
            ;   label   MSX.psgInit
            ;   func    function void psgInit()
            ;   MSX     GICINI
            ;
MSX.psgInit:
            call GICINI
            ret

setup_color:
			ld hl, 0xF3EA
            ld (hl), 15
            INC HL
            ld (hl), 1
            INC HL
            ld (hl), 1
			ld a, (0xFCAF)  ; MSX SCRMOD
            and 0x03        ; mask 00000011
            call 0x0062     ; MSX CHGCLR
            RET
