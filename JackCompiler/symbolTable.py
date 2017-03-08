class Symbol:
    """A symbol containing data type, segment, and index"""

    def __init__(self, type, segment, index):
        self.type = type
        self.segment = segment
        self.index = index

    # Returns the type
    def getType(self):
        return self.type

    # Returns the segment
    def getSegment(self):
        return self.segment

    # Returns the segment + index
    def getLocation(self):
        return (self.segment + ' ' + str(self.index))

class SymbolTable:
    """A symbol table with its methods"""

    def __init__(self):
        self.symbolTable = {}

    # Adds a new Symbol to the symbol table
    def addSymbol(self, varName, type, segment, index):

        # Symbol is not present
        if (self.lookupSymbol(varName) == False):
            tempSymbol = Symbol(type, segment, index)
            self.symbolTable[varName] = tempSymbol
            return 1

        # Symbol is already present
        else:
            print('Error: symbol ' + varName + ' is already present in the symbol table')
            return 0

    # Deletes a Symbol from the symbol table
    def deleteSymbol(self, varName):
        # Symbol is not present
        if (self.lookupSymbol(varName) == False):
            print('Error: symbol ' + varName + ' is not present in the symbol table')
            return 0
        # Symbol is present
        else:
            del self.symbolTable[varName]
            return 1

    # Lookps up a Symbol, and returns False if it not present
    def lookupSymbol(self, varName):

        for key, dict in self.symbolTable.items():
            if (varName == key):
                return self.symbolTable[key]

        return False

    # Returns the number of local variables from the current table
    def countLocal(self):

        localCount = 0

        for key, dict in self.symbolTable.items():
            if (dict.getSegment() == 'local'):
                localCount += 1

        return localCount

    # Returns the number of field variables from the current table
    def countField(self):

        fieldCount = 0

        for key, dict in self.symbolTable.items():
            if (dict.getSegment() == 'this'):
                fieldCount += 1

        return fieldCount

    # Deletes all local and argument symbols
    def flushLocal(self):

        delList = []

        for key, dict in self.symbolTable.items():
            if (dict.getSegment() == 'local' or dict.getSegment() == 'argument'):
                delList.append(key)

        for key in delList:
            self.deleteSymbol(key)

    # Deletes all field symbols
    def flushField(self):

        delList = []

        for key, dict in self.symbolTable.items():
            if (dict.getSegment() == 'this'):
                delList.append(key)

        for key in delList:
            self.deleteSymbol(key)

    # Deletes all symbols
    def flushAll(self):

        delList = []

        for key, dict in self.symbolTable.items():
            delList.append(key)

        for key in delList:
            self.deleteSymbol(key)