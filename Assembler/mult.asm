// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

(BB0)
	@sum		
	M = 0 		// Set sum to 0
	@count
	M = 0 		// Set count to 0

(LL1)
	@R1
	D = M 		// Get R1 and put it in D
	@count 		// Get count and put its value in M
	D = D - M 	// Set D = D - M or (D = R1 - count)
	@BB3
	D; JLE 		// Jump to BB3 if (D <= 0) or (R1 - count <= 0)

(LL2)
	@R0
	D = M 		// Get R0 and put it in D
	@sum 		// Get sum and put its value in M
	M = D + M 	// Set M = D + M or (sum = R0 + sum)
	@count
	M = M + 1 	// Get count and add 1 to its value
	@LL1
	0; JMP 		// Jump to LL1

(BB3)
	@sum
	D = M 		// Get sum and put it in D
	@R2
	M = D 		// Get R2 and set its value to D, or sum

(BB4)
	@BB4
	0; JMP 		// Endless loop here