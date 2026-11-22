// Box.asm  (K = 41)
// Box: starts at row 41, 20 rows tall, 32 pixels wide (2 word(s)), left edge.
// Key pressed -> black box, key released -> box disappears.
// Start address = SCREEN + 32*41 = 17696

(LOOP)
    @KBD
    D=M
    @BLACK
    D;JGT           // key pressed? -> black
    @color
    M=0             // no key -> white (0)
    @PAINT
    0;JMP
(BLACK)
    @color
    M=-1            // black (all 16 bits = 1)

(PAINT)
    @20
    D=A
    @rows
    M=D             // rows = 20
    @17696
    D=A
    @addr
    M=D             // addr = first word of first row

(ROW)
    @2
    D=A
    @cols
    M=D             // cols = 2
    @addr
    D=M
    @p
    M=D             // p = addr of current word in this row

(COL)
    @color
    D=M
    @p
    A=M
    M=D             // RAM[p] = color
    @p
    M=M+1           // next word
    @cols
    M=M-1
    D=M
    @COL
    D;JGT           // more words in this row?

    @addr
    D=M
    @32
    D=D+A
    @addr
    M=D             // addr += 32 (next row)
    @rows
    M=M-1
    D=M
    @ROW
    D;JGT           // more rows?

    @LOOP
    0;JMP
