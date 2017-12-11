__author__ =  'marina92','ayalap'
import sys
import re
import os

BINARY_ARITH = {'+': 'add','-': 'sub','=': 'eq','>': 'gt','<': 'lt','&': 'and','|': 'or'}
UNARY_ARITH = {'-':'neg', '~':'not'}

subroutines = ["method","function","constructor"]
tokensBegin = "<tokens>"
tokensEnd = "</tokens>"
BEFORE = 0
AFTER = 1
TAB = "  "
statements = ['let','if','do','while','return']
keyWords = ["if","let","do","class","constructor","function","method","field","static","var",\
            "int","char","boolean","void","true","false","null","this","else","while","return"]
symbols = ["{", "}", "(", ")","[", "]", ".", ",", ";" , "+", "-", "*", "/", "&", "|", ">", "<", "=", "~", "\""]

unarytOp = ['-','~']
binaryop = ["+","-","*","/","&","|","<",">","="]
TYPE = 0
KIND = 1
IDX = 2

ifTrueLabel = "IF_TRUE"
ifFalseLabel = "IF_FALSE"
ifEndLabel = "IF_END"
whileLoop = "WHILE_EXP"
whileEnd = "WHILE_END"

KEYWORD = "KEYWORD"
INT_CONS = "INT_CONST"
STRING_CONST = "STRING_CONST"
SYMBOL = "SYMBOL"
IDENTIFIER = "IDENTIFIER"
###################################TOKENIZER############################################################################
class JackTokenizer:
    def __init__(self, file):
      self.inputFile = file
      self.tokenList = []
      self.curTokenIdx = 0
      inComment = False
      for line in self.inputFile:
         stringArray = []
         curString = 0

         #wrap special parts in line with " "
         #if self.isComment(line):
         #   continue

                  #find all strings
         stringArray = re.findall(r'\"(.+?)\"',line)
         for strng in stringArray:
            line = line.replace("\""+strng+"\"", "$STR_"+str(curString))
            curString +=1
         #CALL REMOVE!!!
         if "*/" in line and inComment == True:
             inComment = False
             line = line.split("*/")[1]
         if inComment == True:
             #print(line)
             continue
         if "/*" in line and "*/" not in line:
             #print( line)
             inComment = True
             line = line.split("/*")[0]
         line = self.removeComments(line)

         #line = line.replace("//", " $COMMENT$ ")
         for sym in symbols:
            line = line.replace(sym, " "+sym+" ")
         for token in line.split():
            comment = 0
            if "$STR_" in token:
               token = "\""+stringArray[int(token[-1])]+"\""
            #if token == "$COMMENT$":
            #    comment+=1
            #    break
            #if comment%2 ==0 and token != "$COMMENT$":
            self.tokenList.append(token)

    def hosMoreTokens(self):
      if self.curTokenIdx == self.tokenList.__len__():
         return False
      return True

    def advance(self):
       curToken = self.tokenList[self.curTokenIdx]
       self.curTokenIdx +=1
       return curToken

    #def isComment(self, line):
    #    trimmedLine = line.strip(" ")
    #    if trimmedLine[0] == "/":
    #        if trimmedLine[1] == "/" or trimmedLine[1] == "*":
    #            return True
    #    elif trimmedLine[0] == "*":
    #        return True
    #    return False
    def removeComments(self,line):
        clean = line.split("//")[0];
        clean = re.sub('//.*?//', '', clean)
        clean = re.sub('/\*.*?\*/', '', clean)
        clean = re.sub('\*.*?\*/', '', clean)

        clean = clean.split("/*")[0];
        #clean = clean.split("*")[0];
        if clean.strip(" ").strip("\t").startswith("*"):
            clean = "";
        #print("return clesn:", clean)
        return clean;

    def tokenType(self):
        word = self.tokenList[self.curTokenIdx]
        if word in keyWords:
           return KEYWORD,word
        elif word.isdigit() and (int)(word)<=32768 and (int)(word) >= 0:        #its a int const
            return INT_CONS, word

        elif word[0] == "\"" and word[-1] == "\"": #problem
            return STRING_CONST, word[1:-1]

        elif word in symbols:

            return SYMBOL,word

        else:
            return IDENTIFIER,word

#######################SYMBOLTABLE######################################################################################
class SymbolTable:

    def __init__(self):
        self.classMap = {}
        self.subroutineMap = {}
        self.staticIdx = 0
        self.varIdx = 0
        self.fieldIdx = 0
        self.argIdx = 0
    def startSubroutine(self):
        self.subroutineMap  = {}

    def define(self, name, type, kind):
        propertys = ['', '', '']
        propertys[TYPE] = type
        propertys[KIND] = kind
        if kind == "static":
            propertys[IDX] = self.staticIdx
            self.staticIdx += 1
            self.classMap[name] = propertys
        elif kind == "var":
            propertys[IDX] = self.varIdx
            self.varIdx += 1
            propertys[KIND] = "local"
            self.subroutineMap[name] = propertys
        elif kind == "field":
            propertys[IDX] = self.fieldIdx
            self.fieldIdx += 1
            self.classMap[name] = propertys
            propertys[KIND] = "this"
        elif kind == "argument":
            propertys[IDX] = self.argIdx
            self.argIdx += 1
            self.subroutineMap[name] = propertys
        else:
            
            exit(-100)


    def varCount(self, kind):
        if kind == "static":
            return self.staticIdx
        elif kind == "var":
            return self.varIdx
        elif kind == "field":
            return self.fieldIdx
        elif kind == "argument":
            return self.argIdx
        else:
            
            exit(-101)

    def kindOf(self, name):
        if name in self.subroutineMap:
            return self.subroutineMap.get(name)[KIND]
        if name in self.classMap:
            return self.classMap.get(name)[KIND]
        return None

    def typeOf(self, name):
        if name in self.subroutineMap:
            return self.subroutineMap.get(name)[TYPE]
        if name in self.classMap:
            return self.classMap.get(name)[TYPE]

    def indexOf(self, name):
        if name in self.subroutineMap:
            return self.subroutineMap.get(name)[IDX]
        if name in self.classMap:
            return self.classMap.get(name)[IDX]

    def isInTable(self, name):
        if name in self.subroutineMap:
            return True
        if name in self.classMap:
            return True
        return False


##################################VM_WRITER#############################################################################
CONST = "constant"
ARG = "argument"
LCL = "local"
STATIC = "static"
THIS = "this"
THAT = "that"
POINTER = "pointer"
TEMP = "temp"

ADD = "add"
SUB = "sub"
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or"
NOT = "not"


class VMWriter:

    def __init__(self, outputFile):
        self.outFile = outputFile


    def writePush(self, segment, index):
        self.outFile.write("push "+segment+" "+str(index)+"\n")

    def writePop(self, segment, index):
        self.outFile.write("pop "+segment+" "+str(index)+"\n")

    def writeArithmetic(self, command):
        self.outFile.write(command+"\n")

    def writeLabel(self, label):
        self.outFile.write("label "+label+" "+"\n")

    def writeGoto(self, label):
        self.outFile.write("goto "+label+" "+"\n")

    def writeIf(self, label):
        self.outFile.write("if-goto "+label+" "+"\n")

    def writeCall(self, name, nArgs):
        self.outFile.write("call "+name+" "+str(nArgs)+"\n")

    def writeFunction(self, name, nLocals):
        self.outFile.write("function "+name+" "+str(nLocals)+"\n")

    def writeReturn(self):
        self.outFile.write("return\n")

    def close(self):
        self.outputFile.close()

##################################COMPILATIION_ENGINE##################################################################
class CompilationEngine:
    def __init__(self, infile, outfile):
        self.input = open(infile,'r')
        self.output = open(outfile,'w')
        self.tokenizer = JackTokenizer(self.input)
        self.vmWriter = VMWriter(self.output)
        self.symbolTable = SymbolTable()
        self.className = ""
        self.curSubRoutine = ""
        self.ifLabelCount = 0
        self.whileLabelCount = 0
        self.compileClass()

    def compileClass(self):
        self.symbolTable.classMap = {}
        self.symbolTable.fieldIdx = 0;
        self.symbolTable.staticIdx = 0;
        (type,tok)= self.tokenizer.tokenType() #class
        self.tokenizer.advance()
        (type,tok)= self.tokenizer.tokenType()
        self.className = tok
        self.tokenizer.advance() #class name
        (typ,tok)= self.tokenizer.tokenType()

        nxt = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
        while nxt == "field" or nxt == "static":
            self.compileClassVarDec();
            nxt = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
        while nxt in subroutines:
            self.compileSubroutine();
            nxt = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
        return

    def compileClassVarDec(self):
        self.tokenizer.advance()
        (t, kind)= self.tokenizer.tokenType() # field or static
        self.tokenizer.advance()
        (t,tok)= self.tokenizer.tokenType()
        typ = tok
        self.tokenizer.advance()
        (t,tok)= self.tokenizer.tokenType()
        while tok != ";":
            if tok == ",":
                self.tokenizer.advance()
                (t,tok)= self.tokenizer.tokenType()
                continue
             #name
            (t,tok)= self.tokenizer.tokenType()
            name = tok
            self.symbolTable.define(name,typ,kind)
            self.tokenizer.advance()
            (t,tok)= self.tokenizer.tokenType()


    def compileSubroutine(self):
        self.symbolTable.subroutineMap = {}
        self.symbolTable.varIdx = 0
        self.symbolTable.argIdx = 0
        self.tokenizer.advance()
        typ, funcKind = self.tokenizer.tokenType() # func or method or constructor

        self.tokenizer.advance()
        typ, ret = self.tokenizer.tokenType()
        self.tokenizer.advance()
        typ, name = self.tokenizer.tokenType()
        
        self.curSubRoutine = self.className+"."+name
        self.tokenizer.advance() # (
        if funcKind == "method":
            self.symbolTable.argIdx = 1
        self.compileParameterList()
        #subroutineBody:
        self.tokenizer.advance()#should be "{"
        self.tokenizer.advance()#body begins
        typ, token = self.tokenizer.tokenType()
        numLocals = 0

        while token not in statements:
            numLocals += self.compileVarDec()
            self.tokenizer.advance()
            typ, token = self.tokenizer.tokenType()

        self.vmWriter.writeFunction(self.curSubRoutine, numLocals)
        if funcKind == "constructor":
            fieldNum = self.symbolTable.varCount("field")
            self.vmWriter.writePush(CONST,fieldNum)
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop(POINTER, 0)
        elif funcKind == "method":
            self.vmWriter.writePush(ARG,0)
            self.vmWriter.writePop(POINTER, 0)
        while token != "}":
            self.compileStatments()
            typ, token = self.tokenizer.tokenType()
            if token == ';':
                self.tokenizer.advance()
                typ, token = self.tokenizer.tokenType() #should be "}"

        return

    def compileParameterList(self):

        self.tokenizer.advance()
        t, token = self.tokenizer.tokenType()

        while token != ")":
            if token == ",":
                self.tokenizer.advance()
                t, token = self.tokenizer.tokenType()
                continue
            tpe = token
            self.tokenizer.advance()
            t, name = self.tokenizer.tokenType()
            self.symbolTable.define(name, tpe, ARG)#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            self.tokenizer.advance()
            t, token = self.tokenizer.tokenType()
        return

    def compileVarDec(self):
        numLocals = 0;
        (t, kind)= self.tokenizer.tokenType() # var
        self.tokenizer.advance()
        (t, tok)= self.tokenizer.tokenType()
        typ = tok
        self.tokenizer.advance()
        while tok != ";":
            if tok == ",":
                self.tokenizer.advance()
                (t, tok)= self.tokenizer.tokenType()
                continue
            #self.tokenizer.advance() #name
            (t, name)= self.tokenizer.tokenType()
            self.symbolTable.define(name, typ, kind)
    #        print("in compileVarDec, added:",kind , typ, name)
            #print(name)
            numLocals += 1;
            self.tokenizer.advance()
            (t, tok)= self.tokenizer.tokenType()
        return numLocals;

    def compileStatments(self):
        type, token = self.tokenizer.tokenType()
        if token == "let":
            self.compileLet()
            typ, token = self.tokenizer.tokenType()
        elif token == "do":
            self.compileDo()
            typ, token = self.tokenizer.tokenType()
        elif token == "while":
            self.compileWhile()
            typ, token = self.tokenizer.tokenType()
        elif token == "if":
            self.compileIf()
            typ, token = self.tokenizer.tokenType()
        elif token == "return":
            self.compileReturn()
            typ, token = self.tokenizer.tokenType()
        else:
            typ, token = self.tokenizer.tokenType()
            
            exit(-1000)


        return

    def compileLet(self):
        self.tokenizer.advance()
        typ, assignesName = self.tokenizer.tokenType()
        addrSeg = self.symbolTable.kindOf(assignesName)
        addrIdx = self.symbolTable.indexOf(assignesName)

        self.tokenizer.advance()
        sym = self.tokenizer.tokenList[self.tokenizer.curTokenIdx] # [ or =
        if sym == "[":
           # self.vmWriter.writePush(addrSeg, addrIdx) # push addres
            ##self.tokenizer.advance()
            #self.compileExpression()                  #push location
            #self.vmWriter.writeArithmetic(ADD)      #add
            #self.vmWriter.writePop(POINTER ,1)
            #self.tokenizer.advance()  #=
            #self.compileExpression() #push it
            #self.vmWriter.writePop(THAT, 0)
            self.vmWriter.writePush(addrSeg, addrIdx) # push addres
            self.compileExpression()
            self.vmWriter.writeArithmetic(ADD)
            self.tokenizer.advance()  #=
            self.compileExpression() #push it
            self.vmWriter.writePop(TEMP,0)
            self.vmWriter.writePop(POINTER ,1)
            self.vmWriter.writePush(TEMP ,0)
            self.vmWriter.writePop(THAT,0)
            return
        if sym == "=":
            self.compileExpression() # push assigmett
            self.vmWriter.writePop(addrSeg, addrIdx)

        return

    def compileDo(self):
        self.tokenizer.advance()
        self.compileSubroutineCall()
        self.vmWriter.writePop(TEMP, 0)
        self.tokenizer.advance() ###???????????????????????????????????????????
        return


    def compileIf(self):
        self.tokenizer.advance() #(
        
        self.compileExpression()
        self.tokenizer.advance() # should be "{"
        # print("in if, after expression token is token is",self.tokenizer.tokenList[self.tokenizer.curTokenIdx])
        self.tokenizer.advance() # should be statment
        while self.tokenizer.tokenList[self.tokenizer.curTokenIdx] == ")":
            self.tokenizer.advance()
        index = self.ifLabelCount
        self.ifLabelCount += 1
        self.vmWriter.writeIf(ifTrueLabel+str(index))
        self.vmWriter.writeGoto(ifFalseLabel+str(index))
        self.vmWriter.writeLabel(ifTrueLabel+str(index))
#        self.tokenizer.advance() #{
        token = self.tokenizer.tokenList[self.tokenizer.curTokenIdx] #first statement


        while token != "}":
          
            self.compileStatments()
            #print("in if, after compileStatments current is",self.tokenizer.tokenList[self.tokenizer.curTokenIdx])
            typ, token = self.tokenizer.tokenType()#should be "}"
            if token != '}' and token not in statements:
                self.tokenizer.advance()
                typ, token = self.tokenizer.tokenType()#should be "}"
           # print("in if, after compileStatments222222 current is",self.tokenizer.tokenList[self.tokenizer.curTokenIdx])
            ## if self.tokenizer.tokenList[self.tokenizer.curTokenIdx] == "else":
            ##    break
        self.vmWriter.writeGoto(ifEndLabel+str(index))
        self.vmWriter.writeLabel(ifFalseLabel+str(index))
        self.tokenizer.advance() # should skip "}"
        if self.tokenizer.tokenList[self.tokenizer.curTokenIdx] == "else":
            self.tokenizer.advance() # should be "{"
            self.tokenizer.advance()
            typ, token = self.tokenizer.tokenType()
            # print("in else, before compileStatments token is",token)
            while token != "}":
                #print("in else, before compileStatments token is",token)
                self.compileStatments()
                typ, token = self.tokenizer.tokenType()
                if token != '}' and token not in statements:
                    self.tokenizer.advance()
                    typ, token = self.tokenizer.tokenType()
                #print("in else, after compileStatments token is",token)
            self.tokenizer.advance() # should skip "}"
            typ, token = self.tokenizer.tokenType()
       
        self.vmWriter.writeLabel(ifEndLabel+str(index))
       # self.ifLabelCount +=1
        return


    def compileWhile(self):
        
        self.tokenizer.advance()# should be "("
        index = self.whileLabelCount
        self.whileLabelCount += 1
        self.vmWriter.writeLabel(whileLoop+str(index))
        self.compileExpression()
        self.tokenizer.advance() # {
        self.vmWriter.writeArithmetic("not")
        self.vmWriter.writeIf(whileEnd+str(index))

        self.tokenizer.advance()
        t,token = self.tokenizer.tokenType() #first stament

        while token != "}":

            self.compileStatments()
            typ, token = self.tokenizer.tokenType()
            if token !='}' and token not in statements:
                self.tokenizer.advance()
                typ, token = self.tokenizer.tokenType() #should be "}"

        self.tokenizer.advance() #?
         # should be "}"
        self.vmWriter.writeGoto(whileLoop+str(index))
        self.vmWriter.writeLabel(whileEnd+str(index))
        #self.tokenizer.advance()
        return

    def compileReturn(self):
        typ, token = self.tokenizer.tokenType()
        #self.tokenizer.advance()
        self.tokenizer.advance()
        typ, next = self.tokenizer.tokenType()
        if next == ";":
            self.vmWriter.writePush(CONST, 0)
            self.vmWriter.writeReturn()
            return
        self.tokenizer.curTokenIdx -= 1
        self.compileExpression()
        self.vmWriter.writeReturn() #current should be ;
        return

    def compileExpression(self):
        self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()

        if token is ";":
            return
        if token == "(":
            self.compileExpression()
  #      print("first compile term in compileExpression", token)
        self.compileTerm()
        nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1] #peek
        while nextToken in binaryop:
        #if nextToken in binaryop:
            self.tokenizer.advance()
            sym, op = self.tokenizer.tokenType()
            self.tokenizer.advance()
   #         print("calling compile term from expression second after operation",op)
            self.compileTerm()
            nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1] #fixer
            #self.tokenizer.curTokenIdx -=1
            #self.compileExpression()
            if op == "*":
                self.vmWriter.writeCall("Math.multiply", 2)
            elif op == "/":
                self.vmWriter.writeCall("Math.divide", 2)

            else:
                operWrite = BINARY_ARITH[op]
                self.vmWriter.writeArithmetic(operWrite)

        self.tokenizer.advance() #??????????????????????????
        return

    def compileTerm(self):
        nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
        t, varName = self.tokenizer.tokenType()
        if varName == ")":
            return
  #      print("in compile term varName is:", varName)
        varKind = self.symbolTable.kindOf(varName)
        varIdx = self.symbolTable.indexOf(varName)
        if self.tokenizer.tokenList[self.tokenizer.curTokenIdx] == "(":
            #(
            #write expression
            #self.tokenizer.advance()
            self.compileExpression()
            #)

        elif self.tokenizer.tokenList[self.tokenizer.curTokenIdx] in unarytOp:
 #           print("in term unary op")
            t, op = self.tokenizer.tokenType()
            writeOp = UNARY_ARITH[op]
            self.tokenizer.advance()
            self.compileTerm()
            self.vmWriter.writeArithmetic(writeOp)


        elif nextToken == "." or nextToken == "(" :   #subroutine call
            self.compileSubroutineCall()

        elif nextToken == "[":
             self.vmWriter.writePush(varKind,varIdx)
             self.tokenizer.advance()
             self.compileExpression() #push location
             self.vmWriter.writeArithmetic(ADD)
             self.vmWriter.writePop(POINTER,1)
             self.vmWriter.writePush(THAT,0)


        elif t == INT_CONS:
            self.compileIntConst()
        elif t == KEYWORD:
            self.compileKeyword()
        elif t == STRING_CONST:
            self.compileStringConst()

     #   elif t == "[": # array entry
            #"["
      #      self.compileExpression()
            # should be ]
       #     self.vmWriter.writePush(varKind, varIdx)
        #    self.vmWriter.writeArithmetic(ADD)
         #   self.vmWriter.writePop(POINTER, 1)
          #  self.vmWriter.writePush(THAT, 0)
        else:
            
            self.vmWriter.writePush(varKind, varIdx)
            #self.tokenizer.advance()


    def compileSubroutineCall(self):
#        print("in compile subroutine call")
        tp, functionName = self.tokenizer.tokenType()
        numArgs = 1

        if self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1] == '.' \
                and not self.symbolTable.isInTable(self.tokenizer.tokenList[self.tokenizer.curTokenIdx]): #it's a function
            numArgs = 0
        else:
            if self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1] == '.': #function of our var
                segment = self.symbolTable.kindOf(functionName)
                index = self.symbolTable.indexOf(functionName)
                self.vmWriter.writePush(segment, index)
                functionName = self.symbolTable.typeOf(functionName)
            else:                                                               # our method
                
                functionName = self.className+"."+functionName
                self.vmWriter.writePush(POINTER, 0)
        self.tokenizer.advance()
        tp, curTok = self.tokenizer.tokenType()
        while curTok != "(":
            functionName += curTok
            self.tokenizer.advance()
            tp,curTok = self.tokenizer.tokenType()
        self.tokenizer.advance() #after (
        numArgs += self.compileExpressionList()
         # )


        self.vmWriter.writeCall(functionName, numArgs)
        #if its a void???

    def compileExpressionList(self):
        listArgs = 0;
        nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx]
        while nextToken != ")":
            if nextToken == ",":
                self.tokenizer.advance()
                nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx]
                continue
            self.tokenizer.curTokenIdx -= 1
            self.compileExpression()
            listArgs += 1
            nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx] # where is the idx?
            if nextToken == ";":
                return listArgs
        return listArgs
        #)
    def compileIntConst(self):
        intgrStr = self.tokenizer.tokenList[self.tokenizer.curTokenIdx]
        intgr = int(intgrStr)
        self.vmWriter.writePush(CONST,intgr)

    def compileStringConst(self):
        str = self.tokenizer.tokenList[self.tokenizer.curTokenIdx]
        str =  str.replace("\"", "")
        length = len(str)
     
        self.vmWriter.writePush(CONST, length)
        self.vmWriter.writeCall("String.new", 1)
        for letter in str:
            asc = ord(letter)
            self.vmWriter.writePush(CONST,asc)
            self.vmWriter.writeCall("String.appendChar", 2)

    def compileKeyword(self):

   #     print("compiling keyWord")
        word = self.tokenizer.tokenList[self.tokenizer.curTokenIdx]
        #print("compiling keyWord",word)
        if word == "null" or word == "false":
            self.vmWriter.writePush(CONST, 0)
        elif word == "true":
            self.vmWriter.writePush(CONST, 0)
            self.vmWriter.writeArithmetic(NOT)
        elif word == "this":
            self.vmWriter.writePush(POINTER, 0)
        else:
    #        print("problem in compileKeyword")
            exit(-222)
        #self.tokenizer.advance()

###############################################MAIN#####################################################################
inputFileName = sys.argv[1]
if os.path.isdir(inputFileName):
    for file in os.listdir(inputFileName):
        if file.endswith(".jack"):
            file = inputFileName+"/"+file
            outputFileName = file.replace(".jack", ".vm")
            compiler = CompilationEngine(file, outputFileName)
elif os.path.isfile(inputFileName):
    outputFileName = inputFileName.replace(".jack", ".vm")
    compiler = CompilationEngine(inputFileName, outputFileName)
