            ;
            ;   Array Library
            ;

            ;
            ;   alloc array
            ;       in      Stack: size(Word) of Array
            ;       out     Stack: array[0] address
            ;       modify  all
            ;       label   Array.new
            ;       func    function Array new(int size)
            ;
Array.new:
            ld hl, Array.new.ret
            ex (sp), hl         ; (SP) <- return address
            push hl             ; size(Word) of Array
            jp Memory.alloc
Array.new.ret:
            pop hl              ; array address
            ex (sp), hl         ; hl <- return address
            push hl             ; return address
            ret

            ;
            ;   dealloc array
            ;       in      Stack: array top address to dealloc
            ;       out     None
            ;       modify  all
            ;       label   Array.deAlloc
            ;       func    function void deAlloc(Array obj)
            ;
Array.deAlloc:
            ld hl, Array.deAlloc.ret
            ex (sp), hl
            push hl             ; array address
            jp Memory.deAlloc
Array.deAlloc.ret:
            ret

            ;
            ;   size of array
            ;       in      Stack: array top address
            ;       out     Stack: size of array
            ;       modify  all
            ;       label   Array.count
            ;       func    function int count(Array obj)
            ;
Array.count:
            pop hl
            dec hl          ; high byte of array size
            ld d, (hl)
            dec hl          ; low byte of array size
            ld e, (hl)
            ex de, hl       ; hl <- array size (word)
            sra h           ; r7 <- r7, C <- r0
            rr l            ; r7 <- C , C <- r0
            ex (sp), hl
            push hl
            ret
