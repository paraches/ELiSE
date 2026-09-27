            ;
            ;   Screen Library
            ;

            ;
            ;   clear screen
            ;
            ;       in      None (Zero flag must be set)
            ;       out     None
            ;       modify  AF, BC, DE
            ;       msx     CLS 0x00C3
            ;       label   Screen.cls
            ;       func    function void cls()
            ;
Screen.cls:
            xor a           ; set Zero flag
            call 0x00C3     ; MSX CLS
            ret


            ;
            ;   Move cursor to the specified position
            ;
            ;       in      H: X coordinate of cursor
            ;               L: Y coordinate of cursor
            ;       modify  A
            ;       label   Screen.locate
            ;       func    function void locate(int x, int y)
            ;
Screen.locate:
            pop hl          ; y position -> l
            pop de          ; x position -> de
            ld h, e         ; x position -> h
            call 0x00C6     ; MSX POSIT
            ret


            ;
            ;   display char on current cursor position
            ;
            ;       in      A: ASCII code to put
            ;       modify  A
            ;       label   Screen.putch
            ;       func    function void putch(int value)
            ;
Screen.putch:
            pop de          ; ASCII code to display
            ld a, e         ; set ASCII code to A
            call 0x00A2     ; MSX CHPUT
            ret


            ;   select screen mode
            ;       in      Stack:  screen 0 - 3 mode
            ;                       0: 0x0078, 1: 0x007B, 2: 0x007E, 3: 0x0081
            ;               Stack:  sprite size 0 - 3
            ;                       0: 8x8 1: 8x8->16x16 2: 16x16 3: 16x16->32x32
            ;               Stack:  key click on: True, off: False
            ;       modify  all
            ;       msx     CLIKSW 0xF3DB
            ;       label   Screen.mode
            ;       func    function void mode(int screen, int sprite, boolean click)
            ;
Screen.mode:
            pop hl          ; hl is key click value
            ld a, h
            or l            ; 0: off, other: on
            ld (0xF3DB), a  ; MSX CLIKSW

            pop hl          ; hl is sprite size/mag
            ld a, l         ; value is 0-3
            and 0x03        ; need .... ..XX
            ld l, a         ; save
            ld a, (0xF3E0)   ; BIOS work area: current VDP R#1 value
            and 0xFC
            or l            ; new R#1 value
            ld c, 1         ; R#1
            ld b, a         ; new value
            call 0x012D     ; MSX WRTVDP

            pop hl          ; hl is screen mode
            ld a, l
            or a
            jr nz, Screen.mode.not0
            call 0x0078     ; MSX
            jr Screen.end
Screen.mode.not0:
            dec a
            jr nz, Screen.mode.not1
            call 0x007B     ; MSX
            jr Screen.end
Screen.mode.not1:
            dec a
            jr nz, Screen.mode.not2
            call 0x007E     ; MSX
            jr Screen.end
Screen.mode.not2:
            call 0x0081     ; MSX
            ret
Screen.end:
            ret


            ;
            ;   change Screen mode
            ;
            ;       in      Stack:  screen mode number
            ;       modify  all
            ;       msx     CHGMOD  0x005F
            ;       label   Screen.changeMode
            ;       func    function void changeMode(int mode_number)
            ;
Screen.changeMode:
            pop hl          ; screen mode number
            ld a, l         ; a <- mode
            call 0x005F
            ret


            ;
            ;   change the colors of screen
            ;
            ;       in      Stack:  Foreground color (0xF3E9)
            ;               Stack:  Background color (0xF3EA)
            ;               Stack:  border color (0xF3EB)
            ;       modify  all
            ;       msx     CHGCLR  0x0062h
            ;       label   Screen.color
            ;       func    function void color(int foreground, int background, int border)
            ;
Screen.color:
            ld hl, 0xF3EB   ; color work area
            pop de          ; border color
            ld (hl), e
            dec hl
            pop de          ; background color
            ld (hl), e
            dec hl
            pop de          ; foreground color
            ld (hl), e
            ld a, (0xFCAF)  ; MSX SCRMOD
            and 0x03        ; mask 00000011
            call 0x0062     ; MSX CHGCLR
            ret


            ;
            ;   Function key off
            ;
            ;       modify  all
            ;       msx     ERAFNK  0x00CC
            ;               This is not work... FNKSB 0x00C9 with work 0xFBCE
            ;       label   Screen.keyoff
            ;       func    function void keyoff()
            ;
Screen.keyoff:
            call 0x00CC
            ret


            ;
            ;   Function key on
            ;
            ;       modify  all
            ;       msx     DSPFNK  0x00CF
            ;       label   Screen.keyon
            ;       func    function void keyon()
            ;
Screen.keyon:
            call 0x00CF
            ret


            ;
            ;   VDP screen mode
            ;
            ;       in      Stack: mode 0-3
            ;       modify  all
            ;       msx     SETTXT 0x0078, SETT32 0x007B, SETGRP 0x007E, SETMLT 0x0081
            ;       label   Screen.vdpScreen
            ;       func    function void vdpScreen(int mode)
            ;
Screen.vdpScreen:
            pop hl          ; mode
            ld a, l         ; a <- screen mode
            or a
            jr nz, Screen.vdpScreen.notTXT
            call 0x0078
            jr Screen.vdpScreen.return
Screen.vdpScreen.notTXT:
            dec a
            jr nz, Screen.vdpScreen.notT32
            call 0x007B
            jr Screen.vdpScreen.return
Screen.vdpScreen.notT32:
            dec a
            jr nz, Screen.vdpScreen.notGRP
            call 0x007E
            jr Screen.vdpScreen.return
Screen.vdpScreen.notGRP:
            dec a
            jr nz, Screen.vdpScreen.return
            call 0x0081
Screen.vdpScreen.return:
            ret
