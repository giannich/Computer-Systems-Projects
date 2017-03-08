import re

# Initializes the symbol table and other counters
symbolTab = {}
symbolCount = 0
indent = 0
cursor = 0

# Terminals pattern matching
keyword = re.compile('(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)')
symbol = re.compile('[\{\}\(\)\[\]\.\,\;\+\-\*\/\&\|\<\>\=\~]')
integerConstant = re.compile('[0-9]+')
stringConstant = re.compile('\"')
identifier = re.compile('[a-zA-Z\_][a-zA-Z0-9\_]*')
whitespacePat = re.compile('[\t\n\r\f\v]')
emptyspacePat = re.compile(' ')

#############
# Tokenizer #
#############
def matchTerminals(inputStream):

    global symbolCount

    # Initializes the retstring
    retString = ''

    # Will loop until the inputStream is empty
    while (inputStream != ''):

        # Tries to match any of the patterns
        keywordMatchObject = keyword.search(inputStream)
        symbolMatchObject = symbol.search(inputStream)
        integerMatchObject = integerConstant.search(inputStream)
        stringConstantMatchObject = stringConstant.search(inputStream)
        identifierMatchObject = identifier.search(inputStream)
        whitespaceMatchObject = whitespacePat.search(inputStream)
        emptyspaceMatchObject = emptyspacePat.search(inputStream)

        # These are for matching whitespace characters, and the compiler just takes them off from the input stream
        if (emptyspaceMatchObject and emptyspaceMatchObject.start() == 0):
            inputStream = inputStream[emptyspaceMatchObject.end():]
        elif (whitespaceMatchObject and whitespaceMatchObject.start() == 0):
            inputStream = inputStream[whitespaceMatchObject.end():]

        # Keyword matching
        elif (keywordMatchObject and keywordMatchObject.start() == 0):
            retString += inputStream[keywordMatchObject.start():keywordMatchObject.end()] + '$$' + 'Keyword' + '\n'
            inputStream = inputStream[keywordMatchObject.end():]

        # Symbol matching
        elif (symbolMatchObject and symbolMatchObject.start() == 0):
            retString += inputStream[symbolMatchObject.start():symbolMatchObject.end()] + '$$' + 'Symbol' + '\n'
            inputStream = inputStream[symbolMatchObject.end():]

        # Integer matching
        elif (integerMatchObject and integerMatchObject.start() == 0):
            retString += inputStream[integerMatchObject.start():integerMatchObject.end()] + '$$' + 'Integer' + '\n'
            inputStream = inputStream[integerMatchObject.end():]

        # String matching
        elif (stringConstantMatchObject and stringConstantMatchObject.start() == 0):

            # Eats up the first double-quotation
            inputStream = inputStream[stringConstantMatchObject.end():]

            # Matches the second double-quotation
            stringConstantMatchObject = stringConstant.search(inputStream)

            # Puts the string that ends right before the double-quotation marks  in a symbol table
            strLiteral = inputStream[0:stringConstantMatchObject.start()]
            symbolTab[symbolCount] = strLiteral

            # Puts its reference in the token output
            retString += str(symbolCount) + '$$' + 'String' + '\n'

            # Increments the symbolTab counter
            symbolCount += 1

            # Finally, continues with the usual tokenizing
            inputStream = inputStream[stringConstantMatchObject.end():]

        # Identifier matching
        elif (identifierMatchObject and identifierMatchObject.start() == 0):
            retString += inputStream[identifierMatchObject.start():identifierMatchObject.end()] + '$$' + 'Identifier' + '\n'
            inputStream = inputStream[identifierMatchObject.end():]

        # If nothing matches...
        else:
            print("Error, unidentified stuff!")

    return retString

#########################
# Non-terminal Matching #
#########################
def matchNonTerminals(inputStream, outputFile):

    tokenList = inputStream.split()
    parse(tokenList, outputFile)

##########
# Parser #
##########
def parse(tokenList, outputFile):

    global indent
    global cursor

    indent = 0
    cursor = 0

    compClass(tokenList, outputFile)

############
# Indenter #
############
def printIndent(outputFile):

    global indent

    for i in range(0, indent):
        outputFile.write('  ')

######################
# class Non Terminal #
######################
def compClass(tokenList, outputFile):

    global cursor
    global indent

    # Start class
    printIndent(outputFile)
    outputFile.write('<class>\n')
    indent += 1

    # class
    printIndent(outputFile)
    outputFile.write('<keyword> class </keyword>\n')
    cursor += 1

    # className
    compClassName(tokenList, outputFile)

    # {
    printIndent(outputFile)
    outputFile.write('<symbol> { </symbol>\n')
    cursor += 1

    # (classVarDec)*
    while (tokenList[cursor] == 'static$$Keyword' or tokenList[cursor] == 'field$$Keyword'):
        compClassVarDec(tokenList, outputFile)

    # (subroutineDec)*
    while (tokenList[cursor] == 'constructor$$Keyword' or tokenList[cursor] == 'function$$Keyword' \
           or tokenList[cursor] == 'method$$Keyword'):
        compSubroutineDec(tokenList, outputFile)

    # }
    printIndent(outputFile)
    outputFile.write('<symbol> } </symbol>\n')
    cursor += 1

    # End class
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</class>\n')

############################
# classVarDec Non Terminal #
############################
def compClassVarDec(tokenList, outputFile):

    global cursor
    global indent

    # Start classVarDec
    printIndent(outputFile)
    outputFile.write('<classVarDec>\n')
    indent += 1

    # (static|field)
    if (tokenList[cursor] == 'static$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> static </keyword>\n')
        cursor += 1

    elif (tokenList[cursor] == 'field$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> field </keyword>\n')
        cursor += 1

    # error
    else:
        print("Grammar Error at classVarDec at token number: " + cursor)

    # type
    compType(tokenList, outputFile)

    # varName
    compVarName(tokenList, outputFile)

    # (, varName)*
    while(tokenList[cursor] == ',$$Symbol'):

        # ,
        printIndent(outputFile)
        outputFile.write('<symbol> , </symbol>\n')
        cursor += 1

        # varName
        compVarName(tokenList, outputFile)

    # ;
    printIndent(outputFile)
    outputFile.write('<symbol> ; </symbol>\n')
    cursor += 1

    # End classVarDec
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</classVarDec>\n')

#####################
# type Non Terminal #
#####################
def compType(tokenList, outputFile):

    global cursor
    global indent

    # Start type
    #printIndent(outputFile)
    #outputFile.write('<type>\n')
    #indent += 1

    # (int|char|boolean|className)
    if (tokenList[cursor] == 'int$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> int </keyword>\n')
        cursor += 1

    elif (tokenList[cursor] == 'char$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> char </keyword>\n')
        cursor += 1

    elif (tokenList[cursor] == 'boolean$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> boolean </keyword>\n')
        cursor += 1

    # className
    else:
        compClassName(tokenList, outputFile)

    # End type
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</type>\n')

##############################
# subroutineDec Non Terminal #
##############################
def compSubroutineDec(tokenList, outputFile):

    global cursor
    global indent

    printIndent(outputFile)
    outputFile.write('<subroutineDec>\n')
    indent += 1

    # constructor
    if (tokenList[cursor] == 'constructor$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> constructor </keyword>\n')
        cursor += 1

    # function
    elif (tokenList[cursor] == 'function$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> function </keyword>\n')
        cursor += 1

    # method
    elif (tokenList[cursor] == 'method$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> method </keyword>\n')
        cursor += 1

    # error
    else:
        print("Grammar Error at subroutineDec at token number: " + cursor)

    # void
    if (tokenList[cursor] == 'void$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> void </keyword>\n')
        cursor += 1

    # type
    else:
        compType(tokenList, outputFile)

    # subroutineName
    compSubroutineName(tokenList, outputFile)

    # (
    printIndent(outputFile)
    outputFile.write('<symbol> ( </symbol>\n')
    cursor += 1

    # parameterList
    compParameterList(tokenList, outputFile)

    # )
    printIndent(outputFile)
    outputFile.write('<symbol> ) </symbol>\n')
    cursor += 1

    # subroutineBody
    compsubroutineBody(tokenList, outputFile)

    # End subroutineDec
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</subroutineDec>\n')

##############################
# parameterList Non Terminal #
##############################
def compParameterList(tokenList, outputFile):

    global cursor
    global indent

    # Start parameterList
    printIndent(outputFile)
    outputFile.write('<parameterList>\n')
    indent += 1

    # ((type varName) (',' type varName)*)?

    if (tokenList[cursor] == 'int$$Keyword' or tokenList[cursor] == 'int$$Keyword' \
            or tokenList[cursor] == 'int$$Keyword' or '$$Identifier' in tokenList[cursor]):

        # type
        compType(tokenList, outputFile)

        # varName
        compVarName(tokenList, outputFile)

        # (',' type varName)*
        while (tokenList[cursor] == ',$$Symbol'):

            # ,
            printIndent(outputFile)
            outputFile.write('<symbol> , </symbol>\n')
            cursor += 1

            # type
            compType(tokenList, outputFile)

            # varName
            compVarName(tokenList, outputFile)

    # End parameterList
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</parameterList>\n')


###############################
# subroutineBody Non Terminal #
###############################
def compsubroutineBody(tokenList, outputFile):

    global cursor
    global indent

    # Start subroutineBody
    printIndent(outputFile)
    outputFile.write('<subroutineBody>\n')
    indent += 1

    # {
    printIndent(outputFile)
    outputFile.write('<symbol> { </symbol>\n')
    cursor += 1

    # (varDec)*
    while (tokenList[cursor] == 'var$$Keyword'):
        compVarDec(tokenList, outputFile)

    # statements
    compStatements(tokenList, outputFile)

    # }
    printIndent(outputFile)
    outputFile.write('<symbol> } </symbol>\n')
    cursor += 1

    # End subroutineBody
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</subroutineBody>\n')

#######################
# varDec Non Terminal #
#######################
def compVarDec(tokenList, outputFile):

    global cursor
    global indent

    # Start varDec
    printIndent(outputFile)
    outputFile.write('<varDec>\n')
    indent += 1

    # var
    printIndent(outputFile)
    outputFile.write('<keyword> var </keyword>\n')
    cursor += 1

    # type
    compType(tokenList, outputFile)

    # varName
    compVarName(tokenList, outputFile)

    # (',' varName)*
    while (tokenList[cursor] == ',$$Symbol'):
        # ,
        printIndent(outputFile)
        outputFile.write('<symbol> , </symbol>\n')
        cursor += 1

        # varName
        compVarName(tokenList, outputFile)

    # ;
    printIndent(outputFile)
    outputFile.write('<symbol> ; </symbol>\n')
    cursor += 1

    # End varDec
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</varDec>\n')

##########################
# className Non Terminal #
##########################
def compClassName(tokenList, outputFile):

    global cursor
    global indent

    # Start className
    #printIndent(outputFile)
    #outputFile.write('<className>\n')
    #indent += 1

    # identifier
    printIndent(outputFile)
    identName = 'Error: No Match at className'
    idMatchObject = re.compile('\$\$Identifier').search(tokenList[cursor])
    if (idMatchObject):
        identName = tokenList[cursor][:idMatchObject.start()]
    outputFile.write('<identifier> ' + identName + ' </identifier>\n')
    cursor += 1

    # End className
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</className>\n')

###############################
# subroutineName Non Terminal #
###############################
def compSubroutineName(tokenList, outputFile):

    global cursor
    global indent

    # Start subroutineName
    #printIndent(outputFile)
    #outputFile.write('<subroutineName>\n')
    #indent += 1

    # identifier
    printIndent(outputFile)
    identName = 'Error: No Match at subroutineName'
    idMatchObject = re.compile('\$\$Identifier').search(tokenList[cursor])
    if (idMatchObject):
        identName = tokenList[cursor][:idMatchObject.start()]
    outputFile.write('<identifier> ' + identName + ' </identifier>\n')
    cursor += 1

    # End subroutineName
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</subroutineName>\n')

########################
# varName Non Terminal #
########################
def compVarName(tokenList, outputFile):

    global cursor
    global indent

    # Start varName
    #printIndent(outputFile)
    #outputFile.write('<varName>\n')
    #indent += 1

    # identifier
    printIndent(outputFile)
    identName = 'Error: No Match at varName'
    idMatchObject = re.compile('\$\$Identifier').search(tokenList[cursor])
    if (idMatchObject):
        identName = tokenList[cursor][:idMatchObject.start()]
    outputFile.write('<identifier> ' + identName + ' </identifier>\n')
    cursor += 1

    # End varName
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</varName>\n')

###########################
# statements Non Terminal #
###########################
def compStatements(tokenList, outputFile):

    global cursor
    global indent

    # Start statements
    printIndent(outputFile)
    outputFile.write('<statements>\n')
    indent += 1

    # (statement)*
    while (tokenList[cursor] == 'let$$Keyword' or tokenList[cursor] == 'if$$Keyword' \
           or tokenList[cursor] == 'while$$Keyword' or tokenList[cursor] == 'do$$Keyword' \
           or tokenList[cursor] == 'return$$Keyword'):
        compStatement(tokenList, outputFile)

    # End statements
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</statements>\n')

##########################
# statement Non Terminal #
##########################
def compStatement(tokenList, outputFile):

    global cursor
    global indent

    # Start statement
    #printIndent(outputFile)
    #outputFile.write('<statement>\n')
    #indent += 1

    # (letStatement|ifStatement|whileStatement|doStatement|returnStatement)*

    # letStatement
    if (tokenList[cursor] == 'let$$Keyword'):
        compLetStatement(tokenList, outputFile)

    # ifStatement
    elif (tokenList[cursor] == 'if$$Keyword'):
        compIfStatement(tokenList, outputFile)

    # whileStatement
    elif (tokenList[cursor] == 'while$$Keyword'):
        compWhileStatement(tokenList, outputFile)

    # doStatement
    elif (tokenList[cursor] == 'do$$Keyword'):
        compDoStatement(tokenList, outputFile)

    # returnStatement
    elif (tokenList[cursor] == 'return$$Keyword'):
        compReturnStatement(tokenList, outputFile)

    # error
    else:
        print("Grammar Error at statement at token number: " + cursor)

    # End statement
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</statement>\n')

#############################
# letStatement Non Terminal #
#############################
def compLetStatement(tokenList, outputFile):

    global cursor
    global indent

    # Start letStatement
    printIndent(outputFile)
    outputFile.write('<letStatement>\n')
    indent += 1

    # let
    printIndent(outputFile)
    outputFile.write('<keyword> let </keyword>\n')
    cursor += 1

    # varName
    compVarName(tokenList, outputFile)

    # ('[' expression ']')?
    if (tokenList[cursor] == '[$$Symbol'):

        # [
        printIndent(outputFile)
        outputFile.write('<symbol> [ </symbol>\n')
        cursor += 1

        # expression
        compExpression(tokenList, outputFile)

        # ]
        printIndent(outputFile)
        outputFile.write('<symbol> ] </symbol>\n')
        cursor += 1

    # =
    printIndent(outputFile)
    outputFile.write('<symbol> = </symbol>\n')
    cursor += 1

    # expression
    compExpression(tokenList, outputFile)

    # ;
    printIndent(outputFile)
    outputFile.write('<symbol> ; </symbol>\n')
    cursor += 1

    # End letStatement
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</letStatement>\n')

############################
# ifStatement Non Terminal #
############################
def compIfStatement(tokenList, outputFile):

    global cursor
    global indent

    # Start ifStatement
    printIndent(outputFile)
    outputFile.write('<ifStatement>\n')
    indent += 1

    # if
    printIndent(outputFile)
    outputFile.write('<keyword> if </keyword>\n')
    cursor += 1

    # (
    printIndent(outputFile)
    outputFile.write('<symbol> ( </symbol>\n')
    cursor += 1

    # expression
    compExpression(tokenList, outputFile)

    # )
    printIndent(outputFile)
    outputFile.write('<symbol> ) </symbol>\n')
    cursor += 1

    # {
    printIndent(outputFile)
    outputFile.write('<symbol> { </symbol>\n')
    cursor += 1

    # statements
    compStatements(tokenList, outputFile)

    # }
    printIndent(outputFile)
    outputFile.write('<symbol> } </symbol>\n')
    cursor += 1

    # ('else' '{' statements '}')?
    if (tokenList[cursor] == 'else$$Keyword'):

        # else
        printIndent(outputFile)
        outputFile.write('<keyword> else </keyword>\n')
        cursor += 1

        # {
        printIndent(outputFile)
        outputFile.write('<symbol> { </symbol>\n')
        cursor += 1

        # statements
        compStatements(tokenList, outputFile)

        # }
        printIndent(outputFile)
        outputFile.write('<symbol> } </symbol>\n')
        cursor += 1

    # End ifStatement
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</ifStatement>\n')

###############################
# whileStatement Non Terminal #
###############################
def compWhileStatement(tokenList, outputFile):

    global cursor
    global indent

    # Start whileStatement
    printIndent(outputFile)
    outputFile.write('<whileStatement>\n')
    indent += 1

    # while
    printIndent(outputFile)
    outputFile.write('<keyword> while </keyword>\n')
    cursor += 1

    # (
    printIndent(outputFile)
    outputFile.write('<symbol> ( </symbol>\n')
    cursor += 1

    # expression
    compExpression(tokenList, outputFile)

    # )
    printIndent(outputFile)
    outputFile.write('<symbol> ) </symbol>\n')
    cursor += 1

    # {
    printIndent(outputFile)
    outputFile.write('<symbol> { </symbol>\n')
    cursor += 1

    # statements
    compStatements(tokenList, outputFile)

    # }
    printIndent(outputFile)
    outputFile.write('<symbol> } </symbol>\n')
    cursor += 1

    # End whileStatement
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</whileStatement>\n')

############################
# doStatement Non Terminal #
############################
def compDoStatement(tokenList, outputFile):

    global cursor
    global indent

    # Start doStatement
    printIndent(outputFile)
    outputFile.write('<doStatement>\n')
    indent += 1

    # do
    printIndent(outputFile)
    outputFile.write('<keyword> do </keyword>\n')
    cursor += 1

    # subroutineCall
    compSubroutineCall(tokenList, outputFile)

    # ;
    printIndent(outputFile)
    outputFile.write('<symbol> ; </symbol>\n')
    cursor += 1

    # End doStatement
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</doStatement>\n')

################################
# returnStatement Non Terminal #
################################
def compReturnStatement(tokenList, outputFile):

    global cursor
    global indent

    # Start returnStatement
    printIndent(outputFile)
    outputFile.write('<returnStatement>\n')
    indent += 1

    # return
    printIndent(outputFile)
    outputFile.write('<keyword> return </keyword>\n')
    cursor += 1

    # (expression)?
    if ('$$Integer' in tokenList[cursor] or '$$String' in tokenList[cursor] or '$$Identifier' in tokenList[cursor] \
        or tokenList[cursor] == 'true$$Keyword' or tokenList[cursor] == 'false$$Keyword' \
        or tokenList[cursor] == 'null$$Keyword' or tokenList[cursor] == 'this$$Keyword' \
        or tokenList[cursor] == '($$Symbol' or tokenList[cursor] == '-$$Symbol' or tokenList[cursor] == '~$$Symbol'):

        compExpression(tokenList, outputFile)

    # ;
    printIndent(outputFile)
    outputFile.write('<symbol> ; </symbol>\n')
    cursor += 1

    # End returnStatement
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</returnStatement>\n')

###########################
# expression Non Terminal #
###########################
def compExpression(tokenList, outputFile):

    global cursor
    global indent

    # Start expression
    printIndent(outputFile)
    outputFile.write('<expression>\n')
    indent += 1

    # term
    compTerm(tokenList, outputFile)

    # (op term)*
    while(tokenList[cursor] == '+$$Symbol' or tokenList[cursor] == '-$$Symbol' or tokenList[cursor] == '*$$Symbol' \
          or tokenList[cursor] == '/$$Symbol' or tokenList[cursor] == '&$$Symbol' or tokenList[cursor] == '|$$Symbol' \
          or tokenList[cursor] == '<$$Symbol' or tokenList[cursor] == '>$$Symbol' or tokenList[cursor] == '=$$Symbol'):

        # op
        compOp(tokenList, outputFile)

        # term
        compTerm(tokenList, outputFile)

    # End expression
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</expression>\n')

#####################
# term Non Terminal #
#####################
def compTerm(tokenList, outputFile):

    global cursor
    global indent
    global symbolTab

    # Start term
    printIndent(outputFile)
    outputFile.write('<term>\n')
    indent += 1

    # integerConstant
    if ('$$Integer' in tokenList[cursor]):
        printIndent(outputFile)

        # Grabs the integer right before the $$ signs...
        outputFile.write('<integerConstant> ' + tokenList[cursor][0: \
            re.compile('\$\$Integer').search(tokenList[cursor]).start()] + ' </integerConstant>\n')

        cursor += 1

    # stringConstant
    elif ('$$String' in tokenList[cursor]):
        printIndent(outputFile)

        # Gets the number that's right before $$String in order to access the symbol table
        index = int(tokenList[cursor][0:re.compile('\$\$String').search(tokenList[cursor]).start()])

        outputFile.write('<stringConstant> ' + symbolTab[index] + ' </stringConstant>\n')
        cursor += 1

    # keywordConstant
    elif (tokenList[cursor] == 'true$$Keyword' or tokenList[cursor] == 'false$$Keyword' \
            or tokenList[cursor] == 'null$$Keyword' or tokenList[cursor] == 'this$$Keyword'):
        compKeywordConstant(tokenList, outputFile)

    # varName | varName '[' expression ']'      OR      subroutineCall
    elif ('$$Identifier' in tokenList[cursor]):

        # subroutineCall
        if (tokenList[cursor+1] == '($$Symbol' or tokenList[cursor+1] == '.$$Symbol'):
            compSubroutineCall(tokenList, outputFile)

        # varName | varName '[' expression ']'
        else:

            # varName
            compVarName(tokenList, outputFile)

            # varName '[' expression ']'
            if (tokenList[cursor] == '[$$Symbol'):

                # [
                printIndent(outputFile)
                outputFile.write('<symbol> [ </symbol>\n')
                cursor += 1

                # expression
                compExpression(tokenList, outputFile)

                # ]
                printIndent(outputFile)
                outputFile.write('<symbol> ] </symbol>\n')
                cursor += 1

    # '(' expression ')'
    elif (tokenList[cursor] == '($$Symbol'):

        # (
        printIndent(outputFile)
        outputFile.write('<symbol> ( </symbol>\n')
        cursor += 1

        # expression
        compExpression(tokenList, outputFile)

        # )
        printIndent(outputFile)
        outputFile.write('<symbol> ) </symbol>\n')
        cursor += 1

    # unaryOp term
    elif (tokenList[cursor] == '-$$Symbol' or tokenList[cursor] == '~$$Symbol'):

        # unaryOp
        compUnaryOp(tokenList, outputFile)

        # term
        compTerm(tokenList, outputFile)

    else:
        print("Grammar Error at term at token number: " + cursor)

    # End term
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</term>\n')

###############################
# subroutineCall Non Terminal #
###############################
def compSubroutineCall(tokenList, outputFile):

    global cursor
    global indent

    # Start subroutineCall
    #printIndent(outputFile)
    #outputFile.write('<subroutineCall>\n')
    #indent += 1

    # subroutineName '(' expressionList ')'
    if (tokenList[cursor+1] == '($$Symbol'):

        # subroutineName
        compSubroutineName(tokenList, outputFile)

        # (
        printIndent(outputFile)
        outputFile.write('<symbol> ( </symbol>\n')
        cursor += 1

        # expressionList
        compExpressionList(tokenList, outputFile)

        # )
        printIndent(outputFile)
        outputFile.write('<symbol> ) </symbol>\n')
        cursor += 1

    # (className|varName) '.' subRoutineName '(' expressionList ')'
    elif (tokenList[cursor+1] == '.$$Symbol'):

        # (className|varName) << NEED TO FIX!
        compVarName(tokenList, outputFile)

        # .
        printIndent(outputFile)
        outputFile.write('<symbol> . </symbol>\n')
        cursor += 1

        # subRoutineName
        compSubroutineName(tokenList, outputFile)

        # (
        printIndent(outputFile)
        outputFile.write('<symbol> ( </symbol>\n')
        cursor += 1

        # expressionList
        compExpressionList(tokenList, outputFile)

        # )
        printIndent(outputFile)
        outputFile.write('<symbol> ) </symbol>\n')
        cursor += 1


    # End subroutineCall
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</subroutineCall>\n')

###############################
# expressionList Non Terminal #
###############################
def compExpressionList(tokenList, outputFile):

    global cursor
    global indent

    # Start expressionList
    printIndent(outputFile)
    outputFile.write('<expressionList>\n')
    indent += 1

    # (expression(',' expression)*)?
    if ('$$Integer' in tokenList[cursor] or '$$String' in tokenList[cursor] or '$$Identifier' in tokenList[cursor] \
        or tokenList[cursor] == 'true$$Keyword' or tokenList[cursor] == 'false$$Keyword' \
        or tokenList[cursor] == 'null$$Keyword' or tokenList[cursor] == 'this$$Keyword' \
        or tokenList[cursor] == '($$Symbol' or tokenList[cursor] == '-$$Symbol' or tokenList[cursor] == '~$$Symbol'):

        # expression
        compExpression(tokenList, outputFile)

        # (',' expression)*
        while (tokenList[cursor] == ',$$Symbol'):

            # ,
            printIndent(outputFile)
            outputFile.write('<symbol> , </symbol>\n')
            cursor += 1

            # expression
            compExpression(tokenList, outputFile)

    # End expression
    indent -= 1
    printIndent(outputFile)
    outputFile.write('</expressionList>\n')

###################
# op Non Terminal #
###################
def compOp(tokenList, outputFile):

    global cursor
    global indent

    # Start op
    #printIndent(outputFile)
    #outputFile.write('<op>\n')
    #indent += 1

    # +
    if (tokenList[cursor] == '+$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> + </symbol>\n')
        cursor += 1

    # -
    elif (tokenList[cursor] == '-$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> - </symbol>\n')
        cursor += 1

    # *
    elif (tokenList[cursor] == '*$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> * </symbol>\n')
        cursor += 1

    # /
    elif (tokenList[cursor] == '/$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> / </symbol>\n')
        cursor += 1

    # &
    elif (tokenList[cursor] == '&$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> &amp; </symbol>\n')
        cursor += 1

    # |
    elif (tokenList[cursor] == '|$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> | </symbol>\n')
        cursor += 1

    # <
    elif (tokenList[cursor] == '<$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> &lt; </symbol>\n')
        cursor += 1

    # >
    elif (tokenList[cursor] == '>$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> &gt; </symbol>\n')
        cursor += 1

    # =
    elif (tokenList[cursor] == '=$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> = </symbol>\n')
        cursor += 1

    # error
    else:
        print("Grammar Error at op at token number: " + cursor)

    # End op
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</op>\n')

########################
# unaryOp Non Terminal #
########################
def compUnaryOp(tokenList, outputFile):

    global cursor
    global indent

    # Start unaryOp
    #printIndent(outputFile)
    #outputFile.write('<unaryOp>\n')
    #indent += 1

    # -
    if (tokenList[cursor] == '-$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> - </symbol>\n')
        cursor += 1

    # ~
    elif (tokenList[cursor] == '~$$Symbol'):
        printIndent(outputFile)
        outputFile.write('<symbol> ~ </symbol>\n')
        cursor += 1

    # error
    else:
        print("Grammar Error at unaryOp at token number: " + cursor)

    # End unaryOp
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</unaryOp>\n')

################################
# keywordConstant Non Terminal #
################################
def compKeywordConstant(tokenList, outputFile):

    global cursor
    global indent

    # Start keywordConstant
    #printIndent(outputFile)
    #outputFile.write('<keywordConstant>\n')
    #indent += 1

    # true
    if (tokenList[cursor] == 'true$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> true </keyword>\n')
        cursor += 1

    # false
    elif (tokenList[cursor] == 'false$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> false </keyword>\n')
        cursor += 1

    # null
    elif (tokenList[cursor] == 'null$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> null </keyword>\n')
        cursor += 1

    # this
    elif (tokenList[cursor] == 'this$$Keyword'):
        printIndent(outputFile)
        outputFile.write('<keyword> this </keyword>\n')
        cursor += 1

    # error
    else:
        print("Grammar Error at unaryOp at token number: " + cursor)

    # End keywordConstant
    #indent -= 1
    #printIndent(outputFile)
    #outputFile.write('</keywordConstant>\n')