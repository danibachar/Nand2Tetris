// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

//Init Screen Base Addr
@SCREEN
D=A
@ScreenAddr
M=D

(LOOP)

@KBD
D=M
@BLACK //if > 0 -> go to blacken
D;JGT
@WHITE  //else go to whiten
0;JMP

(BLACK)

//if - end of the screen, do nothing
@24576
D=A
@ScreenAddr
D=D-M
@LOOP
D;JLE

//Make Screen Black
@ScreenAddr
A=M
M=-1

//Jump to next Address
//@32
//D=A
@ScreenAddr
M=M+1

//Loop!
@LOOP
0;JMP

//Make Screen White
(WHITE)

//if position is at left top of the screen, do nothing
@SCREEN
D=A
@ScreenAddr
D=D-M
@LOOP
D;JEQ

@ScreenAddr
A=M
M=0

//Jump to next address
@ScreenAddr
M=M-1

//Loop!
@LOOP
0;JMP
