            ;
            ;   Memory Library
            ;

            ;
            ;   Memory alloc
            ;
            ;       in      stack:  request memory size
            ;       out     stack:  allocated memory block address
            ;       modify  AF, BC, DE, HL
            ;       label   Memory.alloc
            ;       func    function Memory alloc(int size)
            ;
Memory.alloc:
            ld hl, mem_free_list
            ld (prev_block_link), hl

            pop hl						; req_size * 2
            add hl, hl
            ld (req_size_2), hl

            ld hl, (mem_free_list)		; block_p = LD16(mem_free_list)
            ld (block_p), hl

mem_loop:
            ld hl, (block_p)

            ld a, h
            or l
            jr nz, not_end

            ex (sp), hl
            push hl
            ret                         ; return 0

not_end:
            ld e, (hl)
            inc hl
            ld d, (hl)                  ; next_block_p = LD16(block_p)
            dec hl
            ex de, hl
            ld (next_block_p), hl

            ex de, hl					; size = LD16(block_p + 2)
            inc hl
            inc hl
            ld e, (hl)
            inc hl
            ld d, (hl)
            dec hl                      ; de <- size
            ex de, hl
            ld (size), hl
            push hl						; keep size
            ex de, hl

            ld hl, (req_size_2)			; if size >= req_size_2
            or a
            ex de, hl
            sbc hl, de
            jr c, not_enough_size

            ld hl, (block_p)			; ST16(block_p + 2, req_size_2)
            inc hl
            inc hl
            ex de, hl
            ld hl, (req_size_2)
            ex de, hl
            ld (hl), e
            inc hl
            ld (hl), d
            dec hl

								; if (size - req_size_2) > 4
            ex de, hl					; hl <- req_size_2, de <- block_p + 2
            ld bc , 4
            add hl, bc					; hl <- req_size_2 + 4
            pop de						; get size
            ex de, hl
            or a
            sbc hl, de
            jr nc, can_divide_area		; (size - req_size_2) > 4 is True

            ld hl, (next_block_p)		; ST(prev_block_link, next_block_p)
            ex de, hl
            ld hl, (prev_block_link)
            ld (hl), e
            inc hl
            ld (hl), d
            jr can_divide_end

can_divide_area:
            ld hl, (block_p)            ; hl <- block_p
            ld bc, 4
            add hl, bc
            ex de, hl					; de <- block_p + 4
            ld hl, (req_size_2)			; hl <- req_size_2
            add hl, de					; hl <- new_block_p
            ld (new_block_p), hl

            ex de, hl
            ld hl, (next_block_p)		; hl <- next_block_p
            ex de, hl
            ld (hl), e					; ST16(new_block_p, next_block_p)
            inc hl
            ld (hl), d
            dec hl

            ld hl, (req_size_2)
            ld bc, 4
            add hl, bc					; block_p_size = req_size_2 + 4

            ex de, hl
            ld hl, (size)
            or a
            sbc hl, de					; size - block_p_size
            ex de, hl
            ld hl, (new_block_p)
            inc hl
            inc hl						; new_block_p + 2
            ld (hl), e					; ST16(new_block_p + 2, size - block_p_size)
            inc hl
            ld (hl), d
            dec hl

            dec hl
            dec hl						; new_block_p
            ex de, hl
            ld hl, (prev_block_link)	; prev_block_link
            ld (hl), e					; ST16(prev_block_link, new_block_link)
            inc hl
            ld (hl), d
            dec hl

can_divide_end:
            ld hl, (block_p)
            ld (hl), 0x00				; ST16(block_p, 0)
            inc hl
            ld (hl), 0x00

            ld bc, 3
            add hl, bc					; block_p + 4
            ex (sp), hl
            push hl
            ret							; return block_p + 4

not_enough_size:
            pop hl                      ; unused size in stack
            ld hl, (block_p)
            ld (prev_block_link), hl	; prev_block_link = block_p

            ld hl, (next_block_p)
            ld (block_p), hl
            jp mem_loop


            ;
            ;   Memory deAlloc
            ;
            ;       in      stack:  memory block address to dealloc
            ;       out     stack:
            ;       modify  AF, BC, DE, HL
            ;       label   Memory.deAlloc
            ;       func    function void deAlloc(Memory obj)
            ;
Memory.deAlloc:
            pop hl              ; hl = deAlloc block address
            ld de, 0x0004
            or a
            sbc hl, de          ; hl = &block.link
            ld de, (mem_free_list)   ; de = &
            ld (hl), e
            inc hl
            ld (hl), d          ; *block.link = &freeList
            dec hl              ; hl = &block.link
            ld (mem_free_list), hl   ; freeList = freed block
            ret


            ;
            ;   Memory peek
            ;
            ;       in      stack:  address to peek
            ;       out     stack:  read value
            ;       modify  DE, HL
            ;       label   Memory.peek
            ;       func    function int peek(int address)
            ;
Memory.peek:
            pop hl              ; address to read
            ld e, (hl)
            inc hl
            ld d, (hl)          ; de is address's value
            ex de, hl           ; hl is address's value
            ex (sp), hl         ; hl <- return address
            push hl
            ret


            ;
            ;   Memory peek byte
            ;
            ;       in      stack:  address to peek
            ;       out     stack:  read value
            ;       modify  DE, HL
            ;       label   Memory.peek8
            ;       func    function int peek8(int address)
            ;
Memory.peek8:
            pop hl              ; address to read
            ld l, (hl)
            ld h, 0             ; hl is address's value
            ex (sp), hl         ; hl <- return address
            push hl
            ret


            ;
            ;   Memory poke
            ;
            ;       in      stack:  memory address to write
            ;               stack:  value to write
            ;       modify  DE, HL
            ;       label   Memory.poke
            ;       func    function void poke(int address, int value)
            ;
Memory.poke:
            pop de              ; value to write
            pop hl              ; address to write
            ld (hl), e
            inc hl
            ld (hl), d          ; done to write
            ret


            ;
            ;   Memory poke byte
            ;
            ;       in      stack:  memory address to write
            ;               stack:  value to write
            ;       modify  DE, HL
            ;       label   Memory.poke8
            ;       func    function void poke8(int address, int value)
            ;
Memory.poke8:
            pop de              ; value to write
            pop hl              ; address to write
            ld (hl), e
            ret


            ;
            ;   Video Memory Peek
            ;
            ;       in      stack:  memory address to peek (14bit -> 1 page 16k)
            ;       out     stack:  read value
            ;       modify  AF, HL
            ;       msx     RDVRM   0x004A  MSX2: NRDVRM  0x0174H
            ;       label   Memory.vpeek, Memory.vpeek8
            ;       func    function int vpeek(int address)
            ;       func    function int vpeek8(int address)
            ;
Memory.vpeek:
Memory.vpeek8:
            pop hl              ; hl <- address to read
            call 0x004A
            ld l, a
            ld h, 0
            ex (sp), hl         ; hl <- return address, (SP) <- ret val
            push hl
            ret


            ;
            ;   Video Memory Poke
            ;
            ;       in      stack:  memory address to poke (14bit)
            ;               stack:  value to write
            ;       modify  AF, HL
            ;       msx     WRTVRM  0x004D  MSX2: NWRVRM  0x0177H
            ;       label   Memory.vpoke
            ;       func    function void vpoke(int address, int value)
            ;       func    function void vpoke8(int address, int value)
            ;
Memory.vpoke:
Memory.vpoke8:
            pop hl              ; hl <- value to poke
            ld a, l             ; A <- value to poke
            pop hl              ; hl <- address to poke
            call 0x004D
            ret


            ;
            ;   Memory block transfer
            ;   from VRAM to Memory
            ;
            ;       in      Stack:  VRAM address
            ;               Stack:  Memory address
            ;               Stack:  count (byte)
            ;       modify  all
            ;       msx     LDIRMV  0x0059
            ;       label   Memory.LDIRMV
            ;       func    function void LDIRMV(int v_address, int m_address, int count)
            ;
Memory.LDIRMV:
            pop bc              ; count
            pop de              ; memory address
            pop hl              ; VRAM address
            call 0x0059
            ret


            ;
            ;   Memory block transfer
            ;   from Memory to VRAM
            ;
            ;       in      Stack:  memory address
            ;               Stack:  VRAM address
            ;               Stack:  count (byte)
            ;       modify  all
            ;       msx     LDIRVM  0x005C
            ;       label   Memory.LDIRVM
            ;       func    function void LDIRVM(int m_address, int v_address, int count)
            ;
Memory.LDIRVM:
            pop bc              ; count
            pop de              ; VRAM address
            pop hl              ; Memory address
            call 0x005C
            ret


            ;
            ;   Fill VRAM with data
            ;
            ;       in      Stack: start address to write
            ;               Stack: count
            ;               Stack: data
            ;       modify  all
            ;       msx     FilVRM  0x0056
            ;       label   Memory.fillVRAM
            ;       func    function void fillVRAM(int address, int count, int data)
            ;
Memory.fillVRAM:
			pop hl
			ld a, l         ; data
			pop bc          ; count
			pop hl          ; address
			call FILVRM
			ret


            ;
            ;   Write data to VDP register
            ;
            ;       in      Stack:  VDP register number
            ;               Stack:  value to write
            ;       modify  AF, BC, HL
            ;       msx     WRTVDP  0x0047
            ;       label   Memory.WriteVDP
            ;       func    function void writeVDP(int reg_number, int value)
            ;
Memory.WriteVDP:
            pop hl              ; write data
            pop bc              ; c <- VDP register number
            ld b, l             ; b <- write data
            call 0x0047
            ret
