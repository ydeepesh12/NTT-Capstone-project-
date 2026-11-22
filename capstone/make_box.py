"""Box.asm generate karta hai. Usage: python make_box.py K"""
import sys
K = int(sys.argv[1]) if len(sys.argv) > 1 else 41
ROW = K                         # starting row
HEIGHT = 20                     # rows
WORDS = (K % 4) + 1             # width = 16 * WORDS pixels
START = 16384 + 32 * ROW        # SCREEN + 32*row

asm = f"""// Box.asm  (K = {K})
// Box: starts at row {ROW}, {HEIGHT} rows tall, {16*WORDS} pixels wide ({WORDS} word(s)), left edge.
// Key pressed -> black box, key released -> box disappears.
// Start address = SCREEN + 32*{ROW} = {START}

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
    @{HEIGHT}
    D=A
    @rows
    M=D             // rows = {HEIGHT}
    @{START}
    D=A
    @addr
    M=D             // addr = first word of first row

(ROW)
    @{WORDS}
    D=A
    @cols
    M=D             // cols = {WORDS}
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
"""
open("Box.asm", "w").write(asm)
print("Box.asm ban gaya for K =", K)
