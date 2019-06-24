// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

//COUNTER = R0 (RAM[0])
@R0 //A = 0
D=M //D = RAM[A] = RAM[0]
@COUNTER
M=D

//Zero value in R2
@R2
M=0

(LOOP)
@COUNTER
D=M
@END
D;JLE

@R1
D=M
@R2
M=M+D

@COUNTER
M=M-1

@LOOP
0;JMP

(END)
@END
0;JMP
