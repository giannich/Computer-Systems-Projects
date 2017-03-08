import re
import sys
import os
import compilation

# Removes whitespace and comments, and returns a single-line string
def getStream(inputFile):

    notInComment = True
    retString = ''

    # Loops through the lines to take off whitespace and comments
    for line in inputFile:

        #################################
        # COMMENTS AND WHITESPACE BLOCK #
        #################################

        # If not in a multi-line comment
        if (notInComment):

            commentSimpleMatchObject = commentSimplePat.search(line)
            commentComplexStartMatchObject = commentComplexStart.search(line)
            whitespaceMatchObject = whitespacePat.search(line)

            if (commentSimpleMatchObject):
                line = line[:commentSimpleMatchObject.start()]

            if (commentComplexStartMatchObject):

                commentComplexEndMatchObject = commentComplexEnd.search(line)

                # If the complex comment is in one single line, just take that off
                if (commentComplexEndMatchObject):
                    line = line[:commentComplexStartMatchObject.start()] + line[commentComplexEndMatchObject.end():]

                else:
                    notInComment = False
                    continue

            # This action strips the whitespace
            while (whitespaceMatchObject):
                line = line[:whitespaceMatchObject.start()] + line[whitespaceMatchObject.end():]
                whitespaceMatchObject = whitespacePat.search(line)

            # Skips empty lines
            if (line == ''):
                continue

            retString += line

        # If in a multi-line comment, try to see if the comment ends
        else:

            # Tries to match an end
            commentComplexEndMatchObject = commentComplexEnd.search(line)

            # If end is matched, it goes out of the not in comment state
            # Careful, this compiler does not support the beginning of a new comment here
            if (commentComplexEndMatchObject):
                line = line[commentComplexEndMatchObject.end():]
                notInComment = True
                retString += line

    return retString

##############################
# MAIN FUNCTION STARTS HERE  #
##############################

# Reads the file path of the input argument and creates a path for the output path
inputDirectory = sys.argv[1]
fileList = os.listdir(inputDirectory)

# Creates a pattern to match for comments
commentSimplePat = re.compile('\/\/')
commentComplexStart = re.compile('\/\*')
commentComplexEnd = re.compile('\*\/')
whitespacePat = re.compile('[\t\n\r\f\v]')
emptyspacePat = re.compile(' ')

# Loops through the rest of the .vm files and appends the ASM output to outputFile
for file in fileList:
    inputfilePath = inputDirectory + '/' + file

    if inputfilePath.endswith('.jack'):

        outputFilePath = inputfilePath[:-5]
        outputFilePath += '.xml'

        inputFile = open(inputfilePath, 'r')
        outputFile = open(outputFilePath, 'w')

        # Removes comments and whitespace
        noComments = getStream(inputFile)

        # Tokenizes the inputstream
        tokenStream = compilation.matchTerminals(noComments)

        # Parses everything into the outputFile
        compilation.matchNonTerminals(tokenStream, outputFile)

        inputFile.close()
        outputFile.close()
