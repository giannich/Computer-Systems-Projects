# I looked up the binary string formatting documentation from this site:
# https://docs.python.org/2/library/string.html
# This stack overflow question simplified my life a lot:
# http://stackoverflow.com/questions/60208/replacements-for-switch-statement-in-python
# I didn't know that python does not have switch case statements, so a dictionary really helped.
# It also keeps the file organized

import re
import sys

# This function accepts an integer and returns its binary 16 value as a string
def intToBinary16(value):

    endStr = '{0:b}'.format(int(value))
    padding = 16 - len(endStr)
    finalStr = ''
    for i in range(0, padding):
        finalStr += '0'
    finalStr += endStr
    return finalStr

# This function accepts a string and returns a string with the binary specification for the destination part
def destDict(str):

    return {
        '0':    '000',
        'M':    '001',
        'D':    '010',
        'MD':   '011',
        'A':    '100',
        'AM':   '101',
        'AD':   '110',
        'AMD':  '111'
    }.get(str, '000')

# This function accepts a string and returns a string with the binary specification for the jump part
def jumpDict(str):

    return {
        'JGT':    '001',
        'JEQ':    '010',
        'JGE':    '011',
        'JLT':    '100',
        'JNE':    '101',
        'JLE':    '110',
        'JMP':    '111'
    }.get(str, '000')

# This function accepts a string and returns a string with the binary specification for the computation part
def compDict(str):

    return {
        '0':     '0101010',
        '1':     '0111111',
        '-1':    '0111010',
        'D':     '0001100',
        'A':     '0110000',
        '!D':    '0001101',
        '!A':    '0110001',
        '-D':    '0001111',
        '-A':    '0110011',
        'D+1':   '0011111',
        'A+1':   '0110111',
        'D-1':   '0001110',
        'A-1':   '0110010',
        'D+A':   '0000010',
        'D-A':   '0010011',
        'A-D':   '0000111',
        'D&A':   '0000000',
        'D|A':   '0010101',
        'M':     '1110000',
        '!M':    '1110001',
        '-M':    '1110011',
        'M+1':   '1110111',
        'M-1':   '1110010',
        'D+M':   '1000010',
        'D-M':   '1010011',
        'M-D':   '1000111',
        'D&M':   '1000000',
        'D|M':   '1010101'
    }.get(str, '1111111')

# Reads the file path of the input argument and creates a path for the output path
inputFilePath = sys.argv[1]
outputFilePath = inputFilePath[:-4]
outputFilePath += '.hack'

# Creates the input and output file objects for reading and writing only respectively
inputFile = open(inputFilePath, 'r')
outputFile = open(outputFilePath, 'w')

# Creates a pattern to match for comments
commentPat = re.compile('//')

# Creates a pattern to match for labels
labelPat = re.compile('[\(](.)*[\)]')

# Creates pattens to match for keywords
spPat = re.compile('@SP')
lclPat = re.compile('@LCL')
argPat = re.compile('@ARG')
thisPat = re.compile('@THIS')
thatPat = re.compile('@THAT')
screenPat = re.compile('@SCREEN')
kbdPat = re.compile('@KBD')
RAMaddressPat = re.compile('[@][R][0-9]+')

# Creates patterns to match for identifiers, and numbers
identPat = re.compile('[@][$_\.a-zA-Z][$_\.a-zA-Z0-9]*')
addressPat = re.compile('[@][0-9]+')

# Creates patterns to match for instructions
jumpPat = re.compile('[AMD01\-!][AMD1+\-&|]?[AMD1]?;[J][GELNM][TQEP]')
equalityPat = re.compile('[AMD0][AMD]?[AMD]?=[AMD01\-!][AMD1+\-&|]?[AMD1]?')
newLinePat = re.compile('\n')

# This initializes the variable list dictionary
varList = {}

# These is used for the routine recognition and for storing variables respectively
# I am assuming that we can start storing variables starting at R16
lineNumber = 0
staticCursor = 16

# This array is used to store the lines without comments and labels
lineStorageArr = []

# Loops through the lines to take off whitespace and comments
for line in inputFile:

    #################################
    # COMMENTS AND WHITESPACE BLOCK #
    #################################

    commentMatchObject = commentPat.search(line)

    if (commentMatchObject):
        line = line[:commentMatchObject.start()]

    # Regardless of what happens with the comments, the whitespace is stripped and newline gets appended where needed
    commLine = ''.join(line.split())
    if (commLine != ''):
        commLine += '\n'
    # This keeps in mind that lines that are deleted do not count towards the label line count
    else:
        lineNumber -= 1

    ############################
    # LABEL SUBSTITUTION BLOCK #
    ############################

    labelMatchObject = labelPat.search(commLine)

    # Gets the routine block name and stores the current lineNumber as its value
    if (labelMatchObject):
        varName = commLine[labelMatchObject.start()+1:labelMatchObject.end()-1]
        # Inserts varName with value lineNumber into the varList dict
        varList[varName] = lineNumber
        # Since the information is stored in the dictionary, we set the current line as an
        # empty string and set back the lineNumber back by 1
        commLine = ''
        lineNumber -= 1

    #################
    # OUTPUT  BLOCK #
    #################

    # Finally appends the uncommented and unlabelled line in the lineStorageArr
    lineStorageArr.append(commLine)

    # This increments line number, used for the routine variable storing
    lineNumber += 1

# Now the program iterates through the lines again
for commLine in lineStorageArr:

    # Match objects are created on the commLine for addresses and instructions

    spMatchObject = spPat.search((commLine))
    lclMatchObject = lclPat.search((commLine))
    argMatchObject = argPat.search((commLine))
    thisMatchObject = thisPat.search((commLine))
    thatMatchObject = thatPat.search((commLine))
    screenMatchObject = screenPat.search((commLine))
    kbdMatchObject = kbdPat.search((commLine))
    RAMaddressMatchObject = RAMaddressPat.search((commLine))

    identMatchObject = identPat.search((commLine))
    addressMatchObject = addressPat.search(commLine)

    jumpMatchObject = jumpPat.search(commLine)
    equalMatchObject = equalityPat.search(commLine)
    newLineMatchObject = newLinePat.search(line)

    # Initializes the addLine string
    hackLine = ''

    ######################
    # SP ADDRESSES BLOCK #
    ######################

    # This substitutes in @SP address calls
    if (spMatchObject):
        hackLine += intToBinary16(0) + '\n'

    #######################
    # LCL ADDRESSES BLOCK #
    #######################

    # This substitutes in @LCL address calls
    elif (lclMatchObject):
        hackLine += intToBinary16(1) + '\n'

    #######################
    # ARG ADDRESSES BLOCK #
    #######################

    # This substitutes in @ARG address calls
    elif (argMatchObject):
        hackLine += intToBinary16(2) + '\n'

    ########################
    # THIS ADDRESSES BLOCK #
    ########################

    # This substitutes in @THIS address calls
    elif (thisMatchObject):
        hackLine += intToBinary16(3) + '\n'

    ########################
    # THAT ADDRESSES BLOCK #
    ########################

    # This substitutes in @THAT address calls
    elif (thatMatchObject):
        hackLine += intToBinary16(4) + '\n'

    ########################
    # SCREEN ADDRESS BLOCK #
    ########################

    # This substitutes in @SCREEN address calls
    elif (screenMatchObject):
        hackLine += intToBinary16(16384) + '\n'

    #######################
    # KBD ADDRESSES BLOCK #
    #######################

    # This substitutes in @KBD address calls
    elif (kbdMatchObject):
        hackLine += intToBinary16(24576) + '\n'

    #######################
    # RAM ADDRESSES BLOCK #
    #######################

    # This substitutes in @R calls
    elif (RAMaddressMatchObject):
        hackLine += intToBinary16(commLine[RAMaddressMatchObject.start()+2:RAMaddressMatchObject.end()]) + '\n'

    ##########################
    # VARIABLE ADDRESS BLOCK #
    ##########################

    elif (identMatchObject):
        # Gets the name of the variable and puts it inot varName
        varName = commLine[identMatchObject.start()+1:identMatchObject.end()]

        # Now that we have the identifier, we need to check the symbol table
        varInDic = varList.get(varName, 'NOPE')

        # Otherwise, assign its value as the cursor and increment cursor by 1
        if (varInDic == 'NOPE'):
            varList[varName] = staticCursor
            hackLine += intToBinary16(staticCursor) + '\n'
            staticCursor += 1

        # If there is a varname, then get its value
        else:
            hackLine += intToBinary16(varInDic) + '\n'

    ########################
    # NUMBER ADDRESS BLOCK #
    ########################

    # If it is a number address, then do this
    elif (addressMatchObject):
        value = commLine[addressMatchObject.start()+1:addressMatchObject.end()]
        hackLine += intToBinary16(value) + '\n'

    #####################
    # INSTRUCTION BLOCK #
    #####################

    # If it is a normal instruction then do this
    else:
        # The first 3 bits are always 111 for an instruction
        instructionLine = '111'

        if (jumpMatchObject):
            # This splits the instruction into the destination and the jump part
            jumpLine = commLine[jumpMatchObject.start():jumpMatchObject.end()]
            computation = str.split(jumpLine, ';')[0]
            jump = str.split(jumpLine, ';')[1]
            # This adds the computation
            instructionLine += compDict(computation)
            # There is no destination for a jump instruction
            instructionLine += '000'
            # This adds the jump condition
            instructionLine += jumpDict(jump) + '\n'

        elif (equalMatchObject):
            equalLine = commLine[equalMatchObject.start():equalMatchObject.end()]
            destination = str.split(equalLine, '=')[0]
            computation = str.split(equalLine, '=')[1]
            # This adds the computation
            instructionLine += compDict(computation)
            # This adds the destination
            instructionLine += destDict(destination)
            # There is no jump for a computation instruction
            instructionLine += '000' + '\n'

        else:
            instructionLine = ''

        # Puts the instruction line together and sets hackLine equal to its value
        hackLine = instructionLine

    #################
    # OUTPUT  BLOCK #
    #################

    # Finally, the modified output line is written in the output file
    outputFile.write(hackLine)

# Closes the input and output files
inputFile.close()
outputFile.close()

