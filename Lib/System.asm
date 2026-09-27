            ;
            ;   System Library
            ;

            ;
            ;   System return
            ;
            ;       label   Sys.return
            ;       func    function void return()
            ;
Sys.return:
			ld sp, (sys_return) ; size	need byte
			ret
