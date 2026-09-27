            ;
            ;   Sound Library
            ;
            ;   PSG tone playback with independent channel durations.
            ;   Channel A/C can carry BGM while channel B plays effects.
            ;

WRTPSG:     equ 0x0093
GICINI:     equ 0x0090

            ;
            ;   Initialize the PSG and stop every active channel.
            ;
            ;       modify  all
            ;       label   Sound.init
            ;       func    function void init()
            ;
Sound.init:
            call GICINI
            jp Sound.stop


            ;
            ;   Play a tone on PSG channel A without affecting B or C.
            ;
            ;       in      Stack: tone period (12-bit value)
            ;               Stack: volume (0-15)
            ;               Stack: duration in frames
            ;       modify  af, bc, de, hl
            ;       label   Sound.play
            ;       func    function void play(int period, int volume, int frames)
            ;
Sound.play:
            pop bc                  ; duration
            pop de                  ; volume
            pop hl                  ; tone period
            ld a, b
            or c
            jp z, Sound._stopA

            ld (sound_remaining_a), bc
            ld a, e
            and 0x0f
            ld e, a
            ld a, 8                  ; PSG channel A volume
            call Sound._write

            ld e, l                 ; channel A tone period, low byte
            ld a, 0
            call Sound._write
            ld a, h
            and 0x0f
            ld e, a
            ld a, 1
            call Sound._write
            jp Sound._enableA


            ;
            ;   Play a tone on PSG channel B without affecting A or C.
            ;
            ;       in      Stack: tone period (12-bit value)
            ;               Stack: volume (0-15)
            ;               Stack: duration in frames
            ;       modify  af, bc, de, hl
            ;       label   Sound.playB
            ;       func    function void playB(int period, int volume, int frames)
            ;
Sound.playB:
            pop bc                  ; duration
            pop de                  ; volume
            pop hl                  ; tone period
            ld a, b
            or c
            jp z, Sound._stopB

            ld (sound_remaining_b), bc
            ld a, e
            and 0x0f
            ld e, a
            ld a, 9                  ; PSG channel B volume
            call Sound._write

            ld e, l
            ld a, 2
            call Sound._write
            ld a, h
            and 0x0f
            ld e, a
            ld a, 3
            call Sound._write
            jp Sound._enableB


            ;
            ;   Play a tone on PSG channel C without affecting A or B.
            ;
            ;       in      Stack: tone period (12-bit value)
            ;               Stack: volume (0-15)
            ;               Stack: duration in frames
            ;       modify  af, bc, de, hl
            ;       label   Sound.playC
            ;       func    function void playC(int period, int volume, int frames)
            ;
Sound.playC:
            pop bc                  ; duration
            pop de                  ; volume
            pop hl                  ; tone period
            ld a, b
            or c
            jp z, Sound._stopC

            ld (sound_remaining_c), bc
            ld a, e
            and 0x0f
            ld e, a
            ld a, 10                 ; PSG channel C volume
            call Sound._write

            ld e, l
            ld a, 4
            call Sound._write
            ld a, h
            and 0x0f
            ld e, a
            ld a, 5
            call Sound._write
            jp Sound._enableC


            ;
            ;   Play synchronized BGM notes on PSG channels A and C.
            ;   Channel B is left available for sound effects.
            ;
            ;       in      Stack: channel A tone period (12-bit value)
            ;               Stack: channel A volume (0-15)
            ;               Stack: channel C tone period (12-bit value)
            ;               Stack: channel C volume (0-15)
            ;               Stack: duration in frames
            ;       modify  af, bc, de, hl
            ;       label   Sound.playAC
            ;       func    function void playAC(int periodA, int volumeA, int periodC, int volumeC, int frames)
            ;
Sound.playAC:
            pop bc                  ; duration
            ld a, b
            or c
            jr z, Sound.playAC.silent
            ld (sound_remaining_a), bc
            ld (sound_remaining_c), bc

            pop de                  ; channel C volume
            ld a, e
            and 0x0f
            ld e, a
            ld a, 10
            call Sound._write
            pop hl                  ; channel C tone period
            ld e, l
            ld a, 4
            call Sound._write
            ld a, h
            and 0x0f
            ld e, a
            ld a, 5
            call Sound._write

            pop de                  ; channel A volume
            ld a, e
            and 0x0f
            ld e, a
            ld a, 8
            call Sound._write
            pop hl                  ; channel A tone period
            ld e, l
            ld a, 0
            call Sound._write
            ld a, h
            and 0x0f
            ld e, a
            ld a, 1
            call Sound._write
            jp Sound._enableAC

Sound.playAC.silent:
            pop hl                  ; channel C volume
            pop hl                  ; channel C period
            pop hl                  ; channel A volume
            pop hl                  ; channel A period
            call Sound._stopA
            jp Sound._stopC


            ;
            ;   Play three PSG tones at once.
            ;   This convenience function starts all channels together.
            ;
            ;       in      Stack: channel A tone period (12-bit value)
            ;               Stack: channel A volume (0-15)
            ;               Stack: channel B tone period (12-bit value)
            ;               Stack: channel B volume (0-15)
            ;               Stack: channel C tone period (12-bit value)
            ;               Stack: channel C volume (0-15)
            ;               Stack: duration in frames
            ;       modify  af, bc, de, hl
            ;       label   Sound.play3
            ;       func    function void play3(int periodA, int volumeA, int periodB, int volumeB, int periodC, int volumeC, int frames)
            ;
Sound.play3:
            pop bc                  ; duration
            ld a, b
            or c
            jr z, Sound.play3.silent
            ld (sound_remaining_a), bc
            ld (sound_remaining_b), bc
            ld (sound_remaining_c), bc

            pop de                  ; channel C volume
            ld a, e
            and 0x0f
            ld e, a
            ld a, 10
            call Sound._write
            pop hl                  ; channel C tone period
            ld e, l
            ld a, 4
            call Sound._write
            ld a, h
            and 0x0f
            ld e, a
            ld a, 5
            call Sound._write

            pop de                  ; channel B volume
            ld a, e
            and 0x0f
            ld e, a
            ld a, 9
            call Sound._write
            pop hl                  ; channel B tone period
            ld e, l
            ld a, 2
            call Sound._write
            ld a, h
            and 0x0f
            ld e, a
            ld a, 3
            call Sound._write

            pop de                  ; channel A volume
            ld a, e
            and 0x0f
            ld e, a
            ld a, 8
            call Sound._write
            pop hl                  ; channel A tone period
            ld e, l
            ld a, 0
            call Sound._write
            ld a, h
            and 0x0f
            ld e, a
            ld a, 1
            call Sound._write

            ld a, 0xb8              ; enable tone A/B/C, disable noise
            ld (sound_mixer), a
            ld e, a
            ld a, 7
            call Sound._write
            ret

Sound.play3.silent:
            pop hl                  ; channel C volume
            pop hl                  ; channel C period
            pop hl                  ; channel B volume
            pop hl                  ; channel B period
            pop hl                  ; channel A volume
            pop hl                  ; channel A period
            jp Sound.stop


            ;
            ;   Advance active channel durations by one VBlank frame.
            ;
            ;       modify  af, hl
            ;       label   Sound.update
            ;       func    function void update()
            ;
Sound.update:
            ld hl, (sound_remaining_a)
            ld a, h
            or l
            jr z, Sound.update.B
            dec hl
            ld (sound_remaining_a), hl
            ld a, h
            or l
            call z, Sound._stopA

Sound.update.B:
            ld hl, (sound_remaining_b)
            ld a, h
            or l
            jr z, Sound.update.C
            dec hl
            ld (sound_remaining_b), hl
            ld a, h
            or l
            call z, Sound._stopB

Sound.update.C:
            ld hl, (sound_remaining_c)
            ld a, h
            or l
            ret z
            dec hl
            ld (sound_remaining_c), hl
            ld a, h
            or l
            call z, Sound._stopC
            ret


            ;
            ;   Stop all PSG tone channels.
            ;
            ;       modify  af, de, hl
            ;       label   Sound.stop
            ;       func    function void stop()
            ;
Sound.stop:
            ld hl, 0
            ld (sound_remaining_a), hl
            ld (sound_remaining_b), hl
            ld (sound_remaining_c), hl

            ld e, 0
            ld a, 8
            call Sound._write
            ld e, 0
            ld a, 9
            call Sound._write
            ld e, 0
            ld a, 10
            call Sound._write
            ld a, 0xbf              ; disable tone/noise, preserve PSG I/O
            ld (sound_mixer), a
            ld e, a
            ld a, 7
            call Sound._write
            ret


            ;
            ;   Internal channel enable/disable helpers.
            ;
Sound._enableA:
            ld a, (sound_mixer)
            and 0xfe
            jr Sound._writeMixer

Sound._enableB:
            ld a, (sound_mixer)
            and 0xfd
            jr Sound._writeMixer

Sound._enableC:
            ld a, (sound_mixer)
            and 0xfb
            jr Sound._writeMixer

Sound._enableAC:
            ld a, (sound_mixer)
            and 0xfa
            jr Sound._writeMixer

Sound._stopA:
            ld hl, 0
            ld (sound_remaining_a), hl
            ld e, 0
            ld a, 8
            call Sound._write
            ld a, (sound_mixer)
            or 0x01
            jr Sound._writeMixer

Sound._stopB:
            ld hl, 0
            ld (sound_remaining_b), hl
            ld e, 0
            ld a, 9
            call Sound._write
            ld a, (sound_mixer)
            or 0x02
            jr Sound._writeMixer

Sound._stopC:
            ld hl, 0
            ld (sound_remaining_c), hl
            ld e, 0
            ld a, 10
            call Sound._write
            ld a, (sound_mixer)
            or 0x04

Sound._writeMixer:
            ld (sound_mixer), a
            ld e, a
            ld a, 7
            call Sound._write
            ret


            ;
            ;   Internal PSG register writer.
            ;
            ;       in      A: PSG register number
            ;               E: value
            ;
Sound._write:
            ; WRTPSG preserves the register/value transaction from
            ; interrupt interference. The BIOS contract is A=register, E=data.
            call WRTPSG
            ret
