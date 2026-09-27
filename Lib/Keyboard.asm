            ;
            ;   Keyboard Library
            ;

CHSNS:      equ 0x009C
CHGET:      equ 0x009F

            ;
            ;   check JoyStick
            ;       in      a: JoyStick number to check
            ;               0: space key, 1,2: # of Josystick
            ;       out     a: direction of JoyStick. 0 is no input.
            ;                  direction top value is 1 and clock wise to 8
            ;       msx     GTSTCK 0x00D5
            ;       modify  all
            ;       label   Keyboard.stick
            ;       func    function int new(int number)
            ;
Keyboard.stick:
            pop hl          ; Joystick number
            ld a, l         ; set Joystick number to A
            call 0x00D5     ; MSX GTSTCK
            ld h, 0
            ld l, a         ; set Joystick value to de
            ex (sp), hl     ; hl <- return address, (sp) <- ret val
            push hl         ; return address
            ret


            ;
            ;   check JoyStick(0)
            ;       out     a: direction of JoyStick. 0 is no input.
            ;                  direction top value is 1 and clock wise to 8
            ;       modify  all
            ;       msx     GTSTCK 0x00D5
            ;       label   Keyboard.stick0
            ;       func    function int stick0()
            ;
Keyboard.stick0:
            xor a           ; set 0 to A
            call 0x00D5     ; MSX GTSTCK
            ld h, 0
            ld l, a
            ex (sp), hl     ; hl <- return address, (sp) <- ret val
            push hl         ; return address
            ret


            ;
            ;   check Trigger button
            ;       in      Stack: which trigger button
            ;               0: space key, 1,2: # of Josystick A button 3,4: # of JS B button
            ;       out     Stack: value of button 0: off, 0xFF: on
            ;       modify  af, bc, hl
            ;       msx     GTTRIG 0x00D8
            ;       label   Keyboard.trigger:
            ;       func    function int trigger(int number)
            ;
Keyboard.trigger:
            pop hl          ; hl is trigger number
            ld a, l         ; set trigger number to A
            call 0x00D8
            ld l, a         ; set value to hl
            ld h, a
            ex (sp), hl     ; hl <- return address, (sp) <- ret val
            push hl
            ret


            ;
            ;   check Trigger button 0
            ;       out     Stack: value of button 0: off, 0xFF: on
            ;       modify  af, bc, de, hl
            ;       msx     GTTRIG 0x00D8
            ;       label   Keyboard.trigger0:
            ;       func    function int trigger0()
            ;
Keyboard.trigger0:
            xor a           ; set trigger number 0 to A
            call 0x00D8
            ld l, a
            ld h, 0         ; set value to hl
            ex (sp), hl     ; hl <- return address, (sp) <- ret val
            push hl
            ret


            ;
            ;   check Stop
            ;       out     true or false in stack
            ;       modify  all
            ;       label   Keyboard.isStopKey
            ;       func    function int isStopKey()
            ;
Keyboard.isStopKey:
            call 0x0087     ; MSX BREKX
            jr c, Keyboard.isStopKey.yes
            ld hl, 0x0000
            jr Keyboard.isStopKey.end
Keyboard.isStopKey.yes:
            ld hl, 0xFFFF
Keyboard.isStopKey.end:
            ex (sp), hl     ; (sp) <- return value
            push hl         ; return address
            ret


            ;
            ;   Read one buffered character without waiting.
            ;
            ;       out     Stack: ASCII key code, or 0 when no key is ready
            ;       modify  af, hl
            ;       label   Keyboard.readKey
            ;       func    function int readKey()
            ;       msx     CHSNS, CHGET
            ;
Keyboard.readKey:
            call CHSNS
            jr z, Keyboard.readKey.none
            call CHGET
            ld l, a
            ld h, 0
            jr Keyboard.readKey.return
Keyboard.readKey.none:
            ld hl, 0
Keyboard.readKey.return:
            ex (sp), hl
            push hl
            ret


            ;
            ;   Read Int value
            ;       in      stack:  String object for prompt
            ;       out     stack:  read Int value
            ;       modify  all
            ;       label   Keyboard.readInt
            ;       func    function int readInt(String text)
            ;
Keyboard.readInt:
            ld hl, Keyboard.readInt.printReturn
            ex (sp), hl     ; hl <- obj address, (sp) <- return address
            push hl         ; String object address
            jp Output.printStr255
Keyboard.readInt.printReturn:
            call 0x00B1     ; MSX INLIN or PINLIN 0x00AE? returned HL is buffer -1
            push hl
            ld bc, 0x00FF
Keyboard.read.loop.0:
            inc c
            inc hl
            ld a, (hl)
            or a
            jr nz, Keyboard.read.loop.0
            pop hl
            inc hl
            ld de, Keyboard.readInt.new_return
            push de         ; return address
            push hl         ; entered string address
            push bc         ; entered string length
            jp String.new
Keyboard.readInt.new_return:
            pop de          ; String object ([0] is size)
            inc de          ; point de to string start
            call String._S2I
            ex (sp), hl     ; hl <- return address, (sp) <- ret val
            push hl         ; int value
            ret
