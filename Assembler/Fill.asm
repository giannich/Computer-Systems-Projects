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

(BEGIN)
	@SCREEN
	D = A 			// Set D equals to the address of SCREEN
	@cursor
	M = D 			// Set the value of the cursor to be equal to D, or SCREEN's address

(LOOP)
	@KBD
	D = M 			// Set D equals to the value of KBD
	@BLACK
	D; JEQ 			// Jump to BLACK if the value of D is 0
	@WHITE
	0; JMP 			// Else jump to WHITE

(BLACK)

	@cursor
	D = M 			// Get the value of the cursor and put it in D
	@KBD
	D = A - D 		// Set D = 24576 - D, or (D = KBD - cursor)
	@LOOP
	D; JLE 			// Jump back to LOOP if the cursor is crossing into the KBD address

	@cursor
	A = M 			// Set the value of A equals to the value of cursor; in other words, get the current address
	M = - 1 		// Set the value of the current address to black
	@cursor
	M = M + 1 		// Get the value of the cursor and increment it by 1; in other words, the address grows by 1

	@LOOP
	0; JMP 			// Jump back to LOOP

(WHITE)

	@cursor
	D = M 			// Get the value of the cursor and put it in D
	@SCREEN
	D = A - D 		// Set D = 16384 - D, or (D = KBD - cursor)
	@LOOP
	D; JGT 			// Jump back to LOOP if the cursor is crossing above the SCREEN address

	@cursor
	A = M 			// Set the value of A equals to the value of cursor; in other words, get the current address
	M = 0 			// Set the value of the current address to white
	@cursor
	M = M - 1 		// Get the value of the cursor and increment it by 1; in other words, the address shrinks by 1

	@LOOP
	0; JMP 			// Jump back to LOOP