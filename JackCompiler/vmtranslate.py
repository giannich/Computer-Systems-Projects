# I copied most of the code from assembler.py
# Note: The input file is assumed to be a directory with .vm files, and not a .vm file itself
# Note: @FRAME is set to @R14 while @RET is set to @R15

import re
import sys
import os

# This slaps some code at the beginning to set the SP to 256 and a function call to sys.init
def bootstrap():

    return '@256\nD=A\n@SP\nM=D\n' + functioncall('call', 'Sys.init', '0', 0, 'main')

# This function accepts the arithmetic operation and returns a string with the corresponding ASM code
def arithmeticOp(operation, conditionalNumber):

    twoVarHeader = '@SP\nAM=M-1\nD=M\nA=A-1\n'
    conditionEnd = '@SP\nA=M-1\nM=-1\n@CONTINUE' + str(conditionalNumber) + '\n0;JMP\n(FALSE' + str(conditionalNumber) \
                   + ')\n@SP\nA=M-1\nM=0\n(CONTINUE' + str(conditionalNumber) + ')\n'

    return {
        'add':    twoVarHeader + 'M=M+D\n',
        'sub':    twoVarHeader + 'M=M-D\n',
        'and':    twoVarHeader + 'M=M&D\n',
        'or':     twoVarHeader + 'M=M|D\n',
        'eq':     twoVarHeader + 'D=M-D\n@FALSE' + str(conditionalNumber) + '\nD;JNE\n' + conditionEnd,
        'gt':     twoVarHeader + 'D=M-D\n@FALSE' + str(conditionalNumber) + '\nD;JLE\n' + conditionEnd,
        'lt':     twoVarHeader + 'D=M-D\n@FALSE' + str(conditionalNumber) + '\nD;JGE\n' + conditionEnd,
        'neg':    'D=0\n@SP\nA=M-1\nM=D-M\n',
        'not':    '@SP\nA=M-1\nM=!M\n'
    }.get(operation, 'Match Error with arithmenticOp\n')

def restoreVirtual():

    compoundLine = ''

    compoundLine += '@LCL\nD=M\n@R14\nM=D\n'                                        # FRAME = lcl
    compoundLine += '@R14\nD=M\n@5\nA=D-A\nD=M\n@R15\nM=D\n'                        # RET = *(FRAME - 5)
    compoundLine += pushpop('pop', 'argument', '0', 'uselessStr')                   # *ARG = pop()
    compoundLine += '@ARG\nD=M\n@SP\nM=D+1\n'                                       # SP = ARG + 1
    compoundLine += '@R14\nD=M\n@1\nA=D-A\nD=M\n@THAT\nM=D\n'                       # THAT = *(FRAME - 1)
    compoundLine += '@R14\nD=M\n@2\nA=D-A\nD=M\n@THIS\nM=D\n'                       # THIS = *(FRAME - 2)
    compoundLine += '@R14\nD=M\n@3\nA=D-A\nD=M\n@ARG\nM=D\n'                        # ARG = *(FRAME - 3)
    compoundLine += '@R14\nD=M\n@4\nA=D-A\nD=M\n@LCL\nM=D\n'                        # LCL = *(FRAME - 4)
    compoundLine += '@R15\nD=M\nA=D\n0;JMP\n'                                       # go to RET
    return compoundLine

def functioncall(command, name, n, retNum, fileName):

    if command == 'function':
        retLine = '(' + name + ')\n'

        for i in range(int(n)):
            retLine += pushpop('push', 'constant', '0', fileName)

        return retLine

    elif command == 'call':
        compoundLine = ''
        returnLabel = 'RETURN_' + str(retNum)

        compoundLine += '@' + returnLabel + '\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'    # Push ret-add
        compoundLine += '@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'                    # Push lcl
        compoundLine += '@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'                    # Push arg
        compoundLine += '@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'                   # Push this
        compoundLine += '@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'                   # Push that

        compoundLine += '@SP\nD=M\n@' + n + '\nD=D-A\n@5\nD=D-A\n@ARG\nM=D\n'       # arg = sp - n - 5
        compoundLine += '@SP\nD=M\n@LCL\nM=D\n'                                     # lcl = sp
        compoundLine += '@' + name + '\n0;JMP\n'                                    # jump to callee
        compoundLine += '(' + returnLabel + ')\n'                                   # create a return label

        return compoundLine

    else:
        return 'Match Error with functioncall\n'

# This function accepts a full push/pop string into 3 arguments and returns the corresponding ASM code
def pushpop(command, segment, i, fileName):

    pushTail = '@SP\nA=M\nM=D\n@SP\nM=M+1\n'
    popTail  = '@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n'

    return {
        'push':    pushSeg(segment, i, fileName) + pushTail,
        'pop':     popSeg(segment, i, fileName) + popTail
    }.get(command, 'Match Error with pushpop\n')

# This function accepts a segment and variable for a push command and returns its ASM code segment
def pushSeg(segment, i, fileName):

    ptrHeader = '@' + i + '\nA=D+A\nD=M\n'

    return {
        'constant': '@' + i + '\nD=A\n',
        'pointer':  '@3\nD=A\n' + ptrHeader,
        'temp':     '@5\nD=A\n' + ptrHeader,
        'static':   '@' + fileName + '.' + i + '\nD=M\n',
        'local':    '@LCL\nD=M\n' + ptrHeader,
        'argument': '@ARG\nD=M\n' + ptrHeader,
        'this':     '@THIS\nD=M\n' + ptrHeader,
        'that':     '@THAT\nD=M\n' + ptrHeader
    }.get(segment, 'Match Error with pushSeg\n')

# This function accepts a segment and variable for a pop command and returns its ASM code segment
def popSeg(segment, i, fileName):

    ptrHeader = '@' + i + '\nD=D+A\n@R13\nM=D\n'

    return {
        'constant': '@' + i + '\nD=A\n' + ptrHeader,
        'pointer':  '@3\nD=A\n' + ptrHeader,
        'temp':     '@5\nD=A\n' + ptrHeader,
        'static':   '@' + fileName + '.' + i + '\nD=A\n@R13\nM=D\n',
        'local':    '@LCL\nD=M\n' + ptrHeader,
        'argument': '@ARG\nD=M\n' + ptrHeader,
        'this':     '@THIS\nD=M\n' + ptrHeader,
        'that':     '@THAT\nD=M\n' + ptrHeader
    }.get(segment, 'Match Error with popSeg\n')

def ctrlFlow(command, label):

    return {
        'label':    '(' + label + ')\n',
        'goto':     '@' + label + '\n0;JMP\n',
        'if-goto':  '@SP\nAM=M-1\nD=M\n@' + label + '\nD;JNE\n'
    }.get(command, 'Match Error with ctrlFlow\n')

###############################
# MAIN LOOPING FUNCTION BLOCK #
###############################

def vmToAsm(fileName, inputFile, outputFile, conditionalNumber, returnCounter):

        # Loops through the lines to output the ASM code
        for line in inputFile:

            #################################
            # COMMENTS AND WHITESPACE BLOCK #
            #################################

            commentMatchObject = commentPat.search(line)

            if (commentMatchObject):
                line = line[:commentMatchObject.start()]

            # The following lines of code take off newlines if they are the only characters in that line
            commLine = line

            if (commLine == '\n'):
                commLine += ''

            # This line initializes the asmLines string
            asmLines = ''

            # Takes off all the newlines for lines that do have them
            commLine = commLine[:-1]

            commLineList = commLine.split()

            ###############################
            # ARITHMETIC OPERATIONS BLOCK #
            ###############################

            # If commLine is in the arithmeticList, it will get the asm code using arithmeticOp
            # The conditionalNumber is also incremented if there are asm lines that deal with conditional jumps

            if len(commLineList) == 1:
                operation = commLineList[0]

                if operation in arithmeticList:
                    if operation in condList:
                        conditionalNumber += 1
                    asmLines = arithmeticOp(operation, conditionalNumber)

            ################
            # RETURN BLOCK #
            ################

                elif operation == 'return':
                    asmLines = restoreVirtual()

            ######################
            # CONTROL FLOW BLOCK #
            ######################

            elif len(commLineList) == 2:
                command = commLineList[0]
                label = commLineList[1]
                asmLines = ctrlFlow(command, label)

            ###########################
            # MEMORY OPERATIONS BLOCK #
            ###########################

            # Else, it firstly splits the commLine and puts each token into commListList
            # If there are 3 tokens, it then passes those tokens into the pushpop function to get the asm code
            elif len(commLineList) == 3:
                    command = commLineList[0]
                    segment = commLineList[1]
                    var     = commLineList[2]

                    if command == 'push' or command == 'pop':
                        asmLines = pushpop(command, segment, var, fileName)

            #######################
            # FUNCTION CALL BLOCK #
            #######################

                    elif command == 'function':
                        asmLines = functioncall(command, segment, var, returnCounter, fileName)
                    elif command == 'call':
                        returnCounter += 1
                        asmLines = functioncall(command, segment, var, returnCounter, fileName)

            #########################
            # NOTHING MATCHES BLOCK #
            #########################

            # Otherwise, the final asmLines is just whatever was in the commLine, which can be an empty string
            else:
                asmLines = commLine

            #################
            # OUTPUT  BLOCK #
            #################

            # Finally, the modified output line is written in the output file
            outputFile.write(asmLines)

##############################
# MAIN FUNCTION STARTS HERE  #
##############################

# Gets the directory name and puts all of its files into fileList
# It then creates an outputFilePath with the same name as the directory in the same location
inputDirectory = sys.argv[1]
fileList = os.listdir(inputDirectory)
outputFilePath = inputDirectory
outputFilePath += '.asm'
outputFile = open(outputFilePath, 'w')

# Creates a pattern to match for comments
commentPat = re.compile('//')

# Creates a list of things to check for the grammar
arithmeticList = ['add', 'sub', 'eq', 'gt', 'lt', 'and', 'or', 'neg', 'not']
pushpopList = ['push', 'pop']
condList = ['eq', 'gt', 'lt']
controlFlowList = ['label', 'goto', 'if-goto']

# This variable is used for keeping track of the conditional naming
conditionalNumber = 0
returnCounter = 0

# This line right here writes out the bootstrap function
outputFile.write(bootstrap())

# Loops through the rest of the .vm files and appends the ASM output to outputFile
for file in fileList:
    filePath = inputDirectory + '/' + file
    if filePath.endswith('.vm'):
        inputFile = open(filePath, 'r')
        vmToAsm(file[:-3], inputFile, outputFile, conditionalNumber, returnCounter)
        inputFile.close()

# Closes the input and output files
outputFile.close()