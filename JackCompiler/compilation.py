import re
import symbolTable

# Initializes the string symbol table and other counters
stringSymbolTab = {}
currentTable = symbolTable.SymbolTable()        # Reset at end of subroutineDec
globalTable = symbolTable.SymbolTable()         # Reset at end of classDec
classList = []                                  # Reset at end of compilation
methodList = {}                                 # Reset at end of compilation

symbolCount = 0         # Reset at end of compilation
cursor = 0              # Reset at beginning of the parsing

currentClass = 'None'   # Reset at beginning of the parsing

staticCounter = 0       # Reset at beginning of the parsing
argCounter = 0          # Reset at end of subroutineDec
fieldCounter = 0        # Reset at beginning of the parsing
localCounter = 0        # Reset at end of subroutineDec
subCallCounter = 0      # Reset at end of subroutineCall
subRetType = 'Null'     # Reset at end of subroutineDec

whileCounter = 0        # Reset at end of the parsing
ifCounter = 0           # Reset at end of the parsing

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
    global stringSymbolTab

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
            stringSymbolTab[symbolCount] = strLiteral

            # Puts its reference in the token output
            retString += str(symbolCount) + '$$' + 'String' + '\n'

            # Increments the stringSymbolTab counter
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

    #for i in tokenList:
    #   print (i)

##########
# Parser #
##########
def parse(tokenList, outputFile):

    global cursor
    global staticCounter
    global fieldCounter
    global currentClass

    cursor = 0
    staticCounter = 0
    fieldCounter = 0
    currentClass = 'None'

    compClass(tokenList, outputFile)

################################
# Adds class names to the list #
################################
def addClass(className):
    classList.append(className)

#################################
# Adds method names to the list #
#################################
def addMethods(className, inputStream):

    global methodList

    classMethods = []

    methodPat = re.compile('method void ')
    lparPat = re.compile('\(')
    methodMatchObject = methodPat.search(inputStream)
    lparMatchObject = lparPat.search(inputStream)

    while (methodMatchObject):
        classMethods.append(inputStream[methodMatchObject.start()+12:lparMatchObject.start()])
        inputStream = inputStream[lparMatchObject.end():]
        methodMatchObject = methodPat.search(inputStream)
        lparMatchObject = lparPat.search(inputStream)

    methodList[className] = classMethods

####################
# Handles a string #
####################
def stringHandler(strVal):

    retStr = ''

    strLength = str(len(strVal))

    retStr += 'push constant ' + strLength + '\n'
    retStr += 'call String.new 1\n'

    for i in strVal:
        retStr += 'push constant ' + str(ord(i)) + '\n'
        retStr += 'call String.appendChar 2\n'

    return retStr

############################
# class Non Terminal: DONE #
############################
def compClass(tokenList, outputFile):

    global cursor
    global currentClass

    # class
    cursor += 1

    # className
    currentClass = compClassName(tokenList, outputFile)

    # {
    cursor += 1

    # (classVarDec)*
    while (tokenList[cursor] == 'static$$Keyword' or tokenList[cursor] == 'field$$Keyword'):
        compClassVarDec(tokenList, outputFile)

    # (subroutineDec)*
    while (tokenList[cursor] == 'constructor$$Keyword' or tokenList[cursor] == 'function$$Keyword' \
           or tokenList[cursor] == 'method$$Keyword'):
        compSubroutineDec(tokenList, outputFile)

    # }
    cursor += 1

    # Clears the global table at the end of the class declaration
    globalTable.flushAll()

##################################
# classVarDec Non Terminal: DONE #
##################################
def compClassVarDec(tokenList, outputFile):

    # Nothing gets printed here since it is only declarations

    global cursor
    global staticCounter
    global fieldCounter

    static = False

    varName = ''
    type = ''
    segment = ''
    index = 0

    # (static|field)
    if (tokenList[cursor] == 'static$$Keyword'):
        segment = 'static'
        index = staticCounter
        staticCounter += 1
        cursor += 1
        static = True

    elif (tokenList[cursor] == 'field$$Keyword'):
        segment = 'this'
        index = fieldCounter
        fieldCounter += 1
        cursor += 1

    # error
    else:
        print("Grammar Error at classVarDec at token number: " + cursor)

    # type
    type = compType(tokenList, outputFile)

    # varName
    varName = compVarName(tokenList, outputFile)

    # Adds static or field variable to the symbol table
    globalTable.addSymbol(varName, type, segment, index)

    # (, varName)*
    while(tokenList[cursor] == ',$$Symbol'):

        # ,
        cursor += 1

        # varName
        varName = compVarName(tokenList, outputFile)

        if (static):
            index = staticCounter
            staticCounter += 1
        else:
            index = fieldCounter
            fieldCounter += 1

        # Adds subsequent static or field variable to the symbol table
        globalTable.addSymbol(varName, type, segment, index)

    # ;
    cursor += 1

###########################
# type Non Terminal: DONE #
###########################
def compType(tokenList, outputFile):

    global cursor

    # (int|char|boolean|className)
    if (tokenList[cursor] == 'int$$Keyword'):
        cursor += 1
        return 'int'

    elif (tokenList[cursor] == 'char$$Keyword'):
        cursor += 1
        return 'char'

    elif (tokenList[cursor] == 'boolean$$Keyword'):
        cursor += 1
        return 'boolean'

    else:
        return compClassName(tokenList, outputFile)

####################################
# subroutineDec Non Terminal: DONE #
####################################
def compSubroutineDec(tokenList, outputFile):

    global cursor
    global currentClass
    global localCounter
    global subRetType
    global argCounter

    label = ''
    type = ''
    subRoutineName = currentClass
    subRoutineBody = ''
    paramCount = 0
    extraBuffer = ''

    finalStr = ''

    # constructor
    if (tokenList[cursor] == 'constructor$$Keyword'):
        label += 'function '
        extraBuffer += 'push constant ' + str(globalTable.countField()) + '\n'
        extraBuffer += 'call Memory.alloc 1\n'
        extraBuffer += 'pop pointer 0\n'
        cursor += 1

    # function
    elif (tokenList[cursor] == 'function$$Keyword'):
        label += 'function '
        cursor += 1

    # method
    elif (tokenList[cursor] == 'method$$Keyword'):
        label += 'function '
        extraBuffer += 'push argument 0\n'
        extraBuffer += 'pop pointer 0\n'
        argCounter += 1
        cursor += 1

    # error
    else:
        print("Grammar Error at subroutineDec at token number: " + cursor)

    # void
    if (tokenList[cursor] == 'void$$Keyword'):
        type = 'void'
        subRetType = 'void'
        cursor += 1

    # type
    else:
        type = compType(tokenList, outputFile)

    # subroutineName
    subRoutineName += '.'
    subRoutineName += compSubroutineName(tokenList, outputFile)

    # (
    cursor += 1

    # parameterList
    compParameterList(tokenList, outputFile)

    # )
    cursor += 1

    # subroutineBody
    subRoutineBody = compSubroutineBody(tokenList, outputFile)

    # Get the number of local variables in the local table
    localVarCount = str(currentTable.countLocal())

    finalStr += label
    finalStr += subRoutineName
    finalStr += ' ' + localVarCount + '\n'
    finalStr += extraBuffer
    finalStr += subRoutineBody

    # Resets the local and arg counters and the ret type
    localCounter = 0
    argCounter = 0
    subRetType = 'Null'

    outputFile.write(finalStr + '\n')

    # Clears the current local table
    currentTable.flushAll()

####################################
# parameterList Non Terminal: DONE #
####################################
def compParameterList(tokenList, outputFile):

    global cursor
    global argCounter

    varName = ''
    type = ''
    segment = 'argument'
    index = argCounter

    # ((type varName) (',' type varName)*)?
    if (tokenList[cursor] == 'int$$Keyword' or tokenList[cursor] == 'int$$Keyword' \
            or tokenList[cursor] == 'int$$Keyword' or '$$Identifier' in tokenList[cursor]):

        # type
        type = compType(tokenList, outputFile)

        # varName
        varName = compVarName(tokenList, outputFile)

        # Adds varName to the current local table
        currentTable.addSymbol(varName, type, segment, index)

        # Increments the arg counter
        index += 1

        # (',' type varName)*
        while (tokenList[cursor] == ',$$Symbol'):

            # ,
            cursor += 1

            # type
            type = compType(tokenList, outputFile)

            # varName
            varName = compVarName(tokenList, outputFile)

            # Adds varName to the current local table
            currentTable.addSymbol(varName, type, segment, index)

            # Increments the arg counter
            index += 1

#####################################
# subroutineBody Non Terminal: DONE #
#####################################
def compSubroutineBody(tokenList, outputFile):

    global cursor

    # {
    cursor += 1

    # (varDec)*
    while (tokenList[cursor] == 'var$$Keyword'):
        compVarDec(tokenList, outputFile)

    # statements
    retStr = compStatements(tokenList, outputFile)

    # }
    cursor += 1

    return retStr

#############################
# varDec Non Terminal: DONE #
#############################
def compVarDec(tokenList, outputFile):

    global cursor
    global localCounter

    varName = ''
    type = ''
    segment = 'local'
    index = localCounter

    # var
    cursor += 1

    # type
    type = compType(tokenList, outputFile)

    # varName
    varName = compVarName(tokenList, outputFile)

    # Adds varName to the current local table
    currentTable.addSymbol(varName, type, segment, index)

    # Increments the local count
    localCounter += 1
    index = localCounter

    # (',' varName)*
    while (tokenList[cursor] == ',$$Symbol'):
        # ,
        cursor += 1

        # varName
        varName = compVarName(tokenList, outputFile)

        # Adds varName to the current local table
        currentTable.addSymbol(varName, type, segment, index)

        # Increments the local count
        localCounter += 1
        index = localCounter

    # ;
    cursor += 1

################################
# className Non Terminal: DONE #
################################
def compClassName(tokenList, outputFile):

    global cursor

    # identifier
    idMatchObject = re.compile('\$\$Identifier').search(tokenList[cursor])
    if (idMatchObject):
        identName = tokenList[cursor][:idMatchObject.start()]
    else:
        return 'Error'
    cursor += 1

    return identName

#####################################
# subroutineName Non Terminal: DONE #
#####################################
def compSubroutineName(tokenList, outputFile):

    global cursor

    # identifier
    idMatchObject = re.compile('\$\$Identifier').search(tokenList[cursor])
    if (idMatchObject):
        identName = tokenList[cursor][:idMatchObject.start()]
    else:
        return 'Error'

    cursor += 1

    return identName

##############################
# varName Non Terminal: DONE #
##############################
def compVarName(tokenList, outputFile):

    global cursor

    # identifier
    idMatchObject = re.compile('\$\$Identifier').search(tokenList[cursor])
    if (idMatchObject):
        identName = tokenList[cursor][:idMatchObject.start()]
    else:
        return 'Error'

    cursor += 1

    return identName

#################################
# statements Non Terminal: DONE #
#################################
def compStatements(tokenList, outputFile):

    global cursor

    retStr = ''

    # (statement)*
    while (tokenList[cursor] == 'let$$Keyword' or tokenList[cursor] == 'if$$Keyword' \
           or tokenList[cursor] == 'while$$Keyword' or tokenList[cursor] == 'do$$Keyword' \
           or tokenList[cursor] == 'return$$Keyword'):
        retStr += compStatement(tokenList, outputFile)

    return retStr

################################
# statement Non Terminal: DONE #
################################
def compStatement(tokenList, outputFile):

    global cursor

    # (letStatement|ifStatement|whileStatement|doStatement|returnStatement)*

    # letStatement
    if (tokenList[cursor] == 'let$$Keyword'):
        return compLetStatement(tokenList, outputFile)

    # ifStatement
    elif (tokenList[cursor] == 'if$$Keyword'):
        return compIfStatement(tokenList, outputFile)

    # whileStatement
    elif (tokenList[cursor] == 'while$$Keyword'):
        return compWhileStatement(tokenList, outputFile)

    # doStatement
    elif (tokenList[cursor] == 'do$$Keyword'):
        return compDoStatement(tokenList, outputFile)

    # returnStatement
    elif (tokenList[cursor] == 'return$$Keyword'):
        return compReturnStatement(tokenList, outputFile)

    # error
    else:
        print("Grammar Error at statement at token number: " + cursor)

###################################
# letStatement Non Terminal: DONE #
###################################
def compLetStatement(tokenList, outputFile):

    global cursor

    finalStr = ''
    leftExp = ''
    rightExp = ''
    arrayIndex = ''

    # let
    cursor += 1

    # varName
    identName = compVarName(tokenList, outputFile)

    # Check in local table
    if (currentTable.lookupSymbol(identName) != False):
        location = currentTable.lookupSymbol(identName).getLocation()

    # Check in global table
    elif (globalTable.lookupSymbol(identName) != False):
        location = globalTable.lookupSymbol(identName).getLocation()

    else:
        location = 'Error'

    # ('[' expression ']')?
    if (tokenList[cursor] == '[$$Symbol'):

        # [
        cursor += 1

        # expression
        arrayIndex += compExpression(tokenList, outputFile)

        # ]
        cursor += 1

        # Add the array indexing padding
        pointerStr = arrayIndex
        pointerStr += 'push ' + location + '\n'
        pointerStr += 'add\n'
        pointerStr += 'pop pointer 1\n'

        finalStr += pointerStr

        # change the location to that 0
        location = 'that 0'

    leftExp = 'pop ' + location + '\n'

    # =
    cursor += 1

    # expression
    rightExp += compExpression(tokenList, outputFile)

    # ;
    cursor += 1

    finalStr += rightExp
    finalStr += leftExp

    return finalStr

##################################
# ifStatement Non Terminal: DONE #
##################################
def compIfStatement(tokenList, outputFile):

    global cursor
    global ifCounter

    ifCounterStr = str(ifCounter)

    retStr = ''

    # if
    cursor += 1

    # (
    cursor += 1

    # expression
    retStr += compExpression(tokenList, outputFile)
    retStr += 'if-goto ifTrueLabel_' + ifCounterStr + '\ngoto ifFalseLabel_' + ifCounterStr + '\nlabel ifTrueLabel_' + ifCounterStr + '\n'

    # )
    cursor += 1

    # {
    cursor += 1

    # statements
    retStr += compStatements(tokenList, outputFile)
    retStr += 'goto ifContLabel_' + ifCounterStr + '\nlabel ifFalseLabel_' + ifCounterStr + '\n'

    # }
    cursor += 1

    # ('else' '{' statements '}')?
    if (tokenList[cursor] == 'else$$Keyword'):

        # else
        cursor += 1

        # {
        cursor += 1

        # statements
        retStr += compStatements(tokenList, outputFile)

        # }
        cursor += 1

    retStr += 'label ifContLabel_' + ifCounterStr + '\n'

    # Increment if counter
    ifCounter += 1

    return retStr

#####################################
# whileStatement Non Terminal: DONE #
#####################################
def compWhileStatement(tokenList, outputFile):

    global cursor
    global whileCounter

    whileCounterStr = str(whileCounter)

    retStr = 'label whileLabel_' + whileCounterStr + '\n'

    # while
    cursor += 1

    # (
    cursor += 1

    # expression
    retStr += compExpression(tokenList, outputFile)
    retStr += 'if-goto whileLoopLabel_' + whileCounterStr + '\ngoto whileContLabel_' + whileCounterStr + '\nlabel whileLoopLabel_' + whileCounterStr + '\n'

    # )
    cursor += 1

    # {
    cursor += 1

    # statements
    retStr += compStatements(tokenList, outputFile)
    retStr += 'goto whileLabel_' + whileCounterStr + '\nlabel whileContLabel_' + whileCounterStr + '\n'

    # }
    cursor += 1

    # Increment while counter
    whileCounter += 1

    return retStr

##################################
# doStatement Non Terminal: DONE #
##################################
def compDoStatement(tokenList, outputFile):

    global cursor

    # do
    cursor += 1

    # subroutineCall
    retStr = compSubroutineCall(tokenList, outputFile)
    retStr += 'pop temp 0\n'

    # ;
    cursor += 1

    return retStr

######################################
# returnStatement Non Terminal: DONE #
######################################
def compReturnStatement(tokenList, outputFile):

    global cursor
    global subRetType

    retStr = ''

    # return
    cursor += 1

    # (expression)?
    if ('$$Integer' in tokenList[cursor] or '$$String' in tokenList[cursor] or '$$Identifier' in tokenList[cursor] \
        or tokenList[cursor] == 'true$$Keyword' or tokenList[cursor] == 'false$$Keyword' \
        or tokenList[cursor] == 'null$$Keyword' or tokenList[cursor] == 'this$$Keyword' \
        or tokenList[cursor] == '($$Symbol' or tokenList[cursor] == '-$$Symbol' or tokenList[cursor] == '~$$Symbol'):

        retStr += compExpression(tokenList, outputFile)

    # ;
    cursor += 1

    if (subRetType == 'void'):
        retStr += 'push constant 0\n'

    retStr += 'return\n'

    return retStr

#################################
# expression Non Terminal: DONE #
#################################
def compExpression(tokenList, outputFile):

    global cursor

    retStr = ''
    tempTerm = ''
    tempOp = ''

    # term
    retStr += compTerm(tokenList, outputFile)

    # (op term)*
    while(tokenList[cursor] == '+$$Symbol' or tokenList[cursor] == '-$$Symbol' or tokenList[cursor] == '*$$Symbol' \
          or tokenList[cursor] == '/$$Symbol' or tokenList[cursor] == '&$$Symbol' or tokenList[cursor] == '|$$Symbol' \
          or tokenList[cursor] == '<$$Symbol' or tokenList[cursor] == '>$$Symbol' or tokenList[cursor] == '=$$Symbol'):

        # op
        tempOp = compOp(tokenList, outputFile)

        # term
        tempTerm = compTerm(tokenList, outputFile)

        retStr += tempTerm + tempOp

    return retStr

###########################
# term Non Terminal: DONE #
###########################
def compTerm(tokenList, outputFile):

    global cursor
    global stringSymbolTab

    retStr = ''

    # integerConstant
    if ('$$Integer' in tokenList[cursor]):

        # Grabs the integer right before the $$ signs...
        retStr = 'push constant ' + tokenList[cursor][0:re.compile('\$\$Integer').search(tokenList[cursor]).start()] + '\n'
        cursor += 1

    # stringConstant
    elif ('$$String' in tokenList[cursor]):

        # Gets the number that's right before $$String in order to access the symbol table
        index = int(tokenList[cursor][0:re.compile('\$\$String').search(tokenList[cursor]).start()])
        retStr = stringHandler(stringSymbolTab[index])
        cursor += 1

    # keywordConstant
    elif (tokenList[cursor] == 'true$$Keyword' or tokenList[cursor] == 'false$$Keyword' \
            or tokenList[cursor] == 'null$$Keyword' or tokenList[cursor] == 'this$$Keyword'):
        retStr = 'push ' + compKeywordConstant(tokenList, outputFile) + '\n'

    # varName | varName '[' expression ']'      OR      subroutineCall
    elif ('$$Identifier' in tokenList[cursor]):

        # subroutineCall
        if (tokenList[cursor+1] == '($$Symbol' or tokenList[cursor+1] == '.$$Symbol'):
            retStr = compSubroutineCall(tokenList, outputFile)

        # varName | varName '[' expression ']'
        else:

            # varName
            identName = compVarName(tokenList, outputFile)

            # Check in local table
            if (currentTable.lookupSymbol(identName) != False):
                location = currentTable.lookupSymbol(identName).getLocation()

            # Check in global table
            elif (globalTable.lookupSymbol(identName) != False):
                location = globalTable.lookupSymbol(identName).getLocation()

            else:
                location = 'Error'

            # varName '[' expression ']'
            if (tokenList[cursor] == '[$$Symbol'):

                # [
                cursor += 1

                # expression
                arrayIndex = compExpression(tokenList, outputFile)

                # ]
                cursor += 1

                # Get the address of the array
                pointerStr = arrayIndex
                pointerStr += 'push ' + location + '\n'
                pointerStr += 'add\n'
                pointerStr += 'pop pointer 1\n'

                # Modify location to that 0
                location = 'that 0'

                retStr += pointerStr

            retStr += 'push ' + location + '\n'

    # '(' expression ')'
    elif (tokenList[cursor] == '($$Symbol'):

        # (
        cursor += 1

        # expression
        retStr = compExpression(tokenList, outputFile)

        # )
        cursor += 1

    # unaryOp term
    elif (tokenList[cursor] == '-$$Symbol' or tokenList[cursor] == '~$$Symbol'):

        # unaryOp
        tempUnaryOp = compUnaryOp(tokenList, outputFile)

        # term
        tempTerm = compTerm(tokenList, outputFile)

        retStr = tempTerm
        retStr += tempUnaryOp

    else:
        print("Grammar Error at term at token number: " + cursor)

    return retStr

#####################################
# subroutineCall Non Terminal: DONE #
#####################################
def compSubroutineCall(tokenList, outputFile):

    global cursor
    global subCallCounter
    global classList
    global methodList
    global currentClass

    finalStr = ''
    subRoutineName = ''
    objectName = ''
    arguments = ''
    className = False
    foundMethod = False


    # subroutineName '(' expressionList ')'
    if (tokenList[cursor+1] == '($$Symbol'):

        # subroutineName
        subRoutineName = compSubroutineName(tokenList, outputFile)

        # (
        cursor += 1

        # expressionList
        arguments = compExpressionList(tokenList, outputFile)

        # )
        cursor += 1

        # Checks first if the subRoutineName is a method of the current class
        if (subRoutineName in methodList[currentClass]):
            finalStr += 'push pointer 0\n'
            finalStr += arguments
            finalStr += 'call ' + currentClass + '.' + subRoutineName
            finalStr += ' ' + str(subCallCounter + 1) + '\n'

        # Otherwise if it is outside the class
        else:
            finalStr += arguments
            finalStr += 'call '
            finalStr += subRoutineName
            finalStr += ' ' + str(subCallCounter) + '\n'

    # (className|varName) '.' subRoutineName '(' expressionList ')'
    elif (tokenList[cursor+1] == '.$$Symbol'):

        # (className|varName)
        objectName = compVarName(tokenList, outputFile)

        # Gets the object's type, if it is a class type, then use the objectClass instead

        # Look into local table
        if (currentTable.lookupSymbol(objectName) != False):
            objectClass = currentTable.lookupSymbol(objectName).getType()
            objectLocation = currentTable.lookupSymbol(objectName).getLocation()

            # If it is in the classList, it is then a className
            if (objectClass in classList):
                className = True

            # Otherwise it is an external function
            else:
                className = False

        # Look into global table
        elif (globalTable.lookupSymbol(objectName) != False):
            objectClass = globalTable.lookupSymbol(objectName).getType()
            objectLocation = globalTable.lookupSymbol(objectName).getLocation()

            # If it is in the classList, it is then a className
            if (objectClass in classList):
                className = True

            # Otherwise it is an external function
            else:
                className = False

        # .
        cursor += 1

        # subRoutineName
        subRoutineName = compSubroutineName(tokenList, outputFile)

        # (
        cursor += 1

        # expressionList
        arguments += compExpressionList(tokenList, outputFile)

        # )
        cursor += 1

        if (className):
            finalStr += 'push ' + objectLocation + '\n'
            finalStr += arguments
            finalStr += 'call '
            finalStr += objectClass + '.' + subRoutineName
            finalStr += ' ' + str(subCallCounter + 1) + '\n'

        else:
            finalStr += arguments
            finalStr += 'call '
            finalStr += objectName + '.' + subRoutineName
            finalStr += ' ' + str(subCallCounter) + '\n'

    return finalStr

#####################################
# expressionList Non Terminal: DONE #
#####################################
def compExpressionList(tokenList, outputFile):

    global cursor
    global subCallCounter

    subCallCounter = 0
    retStr = ''

    # (expression(',' expression)*)?
    if ('$$Integer' in tokenList[cursor] or '$$String' in tokenList[cursor] or '$$Identifier' in tokenList[cursor] \
        or tokenList[cursor] == 'true$$Keyword' or tokenList[cursor] == 'false$$Keyword' \
        or tokenList[cursor] == 'null$$Keyword' or tokenList[cursor] == 'this$$Keyword' \
        or tokenList[cursor] == '($$Symbol' or tokenList[cursor] == '-$$Symbol' or tokenList[cursor] == '~$$Symbol'):

        # expression
        retStr = compExpression(tokenList, outputFile)
        subCallCounter += 1

        # (',' expression)*
        while (tokenList[cursor] == ',$$Symbol'):

            # ,
            cursor += 1

            # expression
            retStr += compExpression(tokenList, outputFile)
            subCallCounter += 1

    return retStr

#########################
# op Non Terminal: DONE #
#########################
def compOp(tokenList, outputFile):

    global cursor

    retStr = ''

    # +
    if (tokenList[cursor] == '+$$Symbol'):
        retStr = 'add\n'
        cursor += 1

    # -
    elif (tokenList[cursor] == '-$$Symbol'):
        retStr = 'sub\n'
        cursor += 1

    # *
    elif (tokenList[cursor] == '*$$Symbol'):
        retStr = 'call Math.multiply 2\n'
        cursor += 1

    # /
    elif (tokenList[cursor] == '/$$Symbol'):
        retStr = 'call Math.divide 2\n'
        cursor += 1

    # &
    elif (tokenList[cursor] == '&$$Symbol'):
        retStr = 'and\n'
        cursor += 1

    # |
    elif (tokenList[cursor] == '|$$Symbol'):
        retStr = 'or\n'
        cursor += 1

    # <
    elif (tokenList[cursor] == '<$$Symbol'):
        retStr = 'lt\n'
        cursor += 1

    # >
    elif (tokenList[cursor] == '>$$Symbol'):
        retStr = 'gt\n'
        cursor += 1

    # =
    elif (tokenList[cursor] == '=$$Symbol'):
        retStr = 'eq\n'
        cursor += 1

    # error
    else:
        print("Grammar Error at op at token number: " + cursor)

    return retStr

##############################
# unaryOp Non Terminal: DONE #
##############################
def compUnaryOp(tokenList, outputFile):

    global cursor

    retStr = ''

    # -
    if (tokenList[cursor] == '-$$Symbol'):
        retStr = 'neg\n'
        cursor += 1

    # ~
    elif (tokenList[cursor] == '~$$Symbol'):
        retStr = 'not\n'
        cursor += 1

    # error
    else:
        print("Grammar Error at unaryOp at token number: " + cursor)

    return retStr

######################################
# keywordConstant Non Terminal: DONE #
######################################
def compKeywordConstant(tokenList, outputFile):

    global cursor

    retStr = ''

    # true
    if (tokenList[cursor] == 'true$$Keyword'):
        retStr = 'constant 0\nnot'
        cursor += 1

    # false
    elif (tokenList[cursor] == 'false$$Keyword'):
        retStr = 'constant 0'
        cursor += 1

    # null
    elif (tokenList[cursor] == 'null$$Keyword'):
        retStr = 'constant 0'
        cursor += 1

    # this
    elif (tokenList[cursor] == 'this$$Keyword'):
        retStr = 'pointer 0'
        cursor += 1

    # error
    else:
        print("Grammar Error at unaryOp at token number: " + cursor)

    return retStr