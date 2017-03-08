# I looked into the following stack overflow question to solve this project:
# http://stackoverflow.com/questions/1798465/python-remove-last-3-characters-of-a-string
#
# Also consulted 'Input and Output':
# https://docs.python.org/3/tutorial/inputoutput.html
#
# And 'Regular Expressions HOWTO' documentations:
# https://docs.python.org/3/howto/regex.html

import sys
import re

# Reads the file path of the input argument and creates a path for the output path
inputFilePath = sys.argv[1]
outputFilePath = inputFilePath[:-3]
outputFilePath += '.out'

# Checks for the no-comments argument; this is location sensitive, so it has to be the second argument

noComments = (False, True)[len(sys.argv) > 2 and sys.argv[2] == 'no-comments']

# Creates the input and output file objects for reading and writing only respectively
inputFile = open(inputFilePath, 'r')
outputFile = open(outputFilePath, 'w')

# Creates a pattern to match for the no-comments argument

commentPattern = re.compile('//')

# Loops through the lines to take off whitespace and comments

for line in inputFile:

    # Creates a match object and deletes the comments if the pattern is matched in the line
    if (noComments):
        commentMatchObject = commentPattern.search(line)

        if (commentMatchObject):
            line = line[:commentMatchObject.start()]

    # Regardless of what happens with the comments, the whitespace is stripped and newline gets appended where needed
    tempLine = ''.join(line.split())
    if (tempLine != ''):
        tempLine += '\n'

    # Finally, the modified output line is written in the output file
    outputFile.write(tempLine)

# Closes the files
inputFile.close()
outputFile.close()