            ;
            ;   Timer Library
            ;
            ; Timer.waitFrames uses a calibrated Z80 delay loop. This does not
            ; replace H.TIMI and does not depend on the BIOS interrupt state.
            ; Timer.ticks still reads BIOS JIFFY.
            ;

JIFFY:      equ 0xFC9E

            ;
            ;   Start frame timer
            ;       modify  af
            ;       label   Timer.start
            ;       func    function void start()
            ;
Timer.start:
            ld a, 1
            ld (timer_installed), a
            ret


            ;
            ;   Stop frame timer
            ;       modify  af
            ;       label   Timer.stop
            ;       func    function void stop()
            ;
Timer.stop:
            xor a
            ld (timer_installed), a
            ret


            ;
            ;   Read the BIOS VBlank counter
            ;       out     Stack: 16-bit frame count
            ;       modify  af, de, hl
            ;       label   Timer.ticks
            ;       func    function int ticks()
            ;
Timer.ticks:
            call timer_read_jiffy
            ex (sp), hl
            push hl
            ret


            ;
            ;   Wait for a number of 60 Hz frame intervals.
            ;
            ;   The inner loop is approximately 1/60 second on a standard
            ;   3.58 MHz MSX Z80. It deliberately avoids JIFFY and HALT:
            ;   some BIOS initialization paths leave interrupts disabled.
            ;       in      Stack: number of frames
            ;       modify  af, bc, de, hl
            ;       label   Timer.waitFrames
            ;       func    function void waitFrames(int frames)
            ;
Timer.waitFrames:
            pop bc
            ld a, b
            or c
            ret z

Timer.waitFrames.next:
            push bc
            ld de, 2300

Timer.waitFrames.delay:
            dec de
            ld a, d
            or e
            jr nz, Timer.waitFrames.delay

            pop bc
            dec bc
            ld a, b
            or c
            jr nz, Timer.waitFrames.next
            ret


            ;
            ;   Read JIFFY consistently.
            ;
            ; JIFFY is a 16-bit value updated by the interrupt handler. Read
            ; it twice and retry when an interrupt changed it between reads.
            ;
timer_read_jiffy:
            ld hl, (JIFFY)
            ld de, (JIFFY)
            ld a, h
            cp d
            jr nz, timer_read_jiffy
            ld a, l
            cp e
            jr nz, timer_read_jiffy
            ret
