__author__ = 'ayalap'

import sys
import re
import os
tokensBegin = "<tokens>"
tokensEnd = "</tokens>"
BEFORE = 0
AFTER = 1
TAB = "  "
keyWordBegin = "<keyword>"
keyWordEnd = "</keyword>"
KEYWORD = (keyWordBegin, keyWordEnd)
subroutines = ["constructor", "function", "method"]
symbolBegin = "<symbol>"
symbolEnd = "</symbol>"
SYMBOL = (symbolBegin, symbolEnd)

integerConstantBegin = "<integerConstant>"
integerConstantEnd = "</integerConstant>"
INT_CONST = (integerConstantBegin, integerConstantEnd)


identifierBegin = "<identifier>"
identifierEnd = "</identifier>"
IDENTIFIER = (identifierBegin,identifierEnd)

stringConstantBegin = "<stringConstant>"
stringConstantEnd = "</stringConstant>"
STRING_CONST = (stringConstantBegin, stringConstantEnd)

keyWords = ["if","let","do","class","constructor","function","method","field","static","var",\
            "int","char","boolean","void","true","false","null","this","else","while","return"]
symbols = ["{", "}", "(", ")","[", "]", ".", ",", ";" , "+", "-", "*", "/", "&", "|", ">", "<", "=", "~", "\""]

unarytOp = ['-','~']
op = ["+","-","*","/","&","|","<",">","="]

class JackTokenizer:
    def __init__(self, file):
      self.inputFile = file
      self.tokenList = []
      self.curTokenIdx = 0
      inComment = False;
      for line in self.inputFile:
         stringArray = []
         curString = 0


         #wrap special parts in line with " "
         #if self.isComment(line):
         #   print("line",line,"is a comment")
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
         #line = line.replace("/*", " $COMMENT$ ")
         #line = line.replace("*/", " $COMMENT$ ")
         for sym in symbols:
            line = line.replace(sym, " "+sym+" ")
         for token in line.split():
            #comment = 0
            if "$STR_" in token:
               token = "\""+stringArray[int(token[-1])]+"\""
            #if token.__contains__("$COMMENT$"):
            #    comment+=1
            #    break
            #if comment%2 ==0 and not token.__contains__("$COMMENT$"):
            self.tokenList.append(token)
            #print(token)

    def hosMoreTokens(self):
      if self.curTokenIdx == self.tokenList.__len__():
         return False
      return True

    def advance(self):
       curToken = self.tokenList[self.curTokenIdx]
       self.curTokenIdx +=1
       return  curToken

   # def isComment(self, line):
   #     trimmedLine = line.strip(" ")
   #     trimmedLine = trimmedLine.strip("\t")
   #     if trimmedLine[0] == "/":
   #         if trimmedLine[1] == "/" or trimmedLine[1] == "*":
   #             return True
   #     elif trimmedLine[0] == "*":
   #         return True
   #     return False

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
            return INT_CONST, word

        elif word[0] == "\"" and word[-1] == "\"": #problem
            return STRING_CONST, word[1:-1]

        elif word in symbols:

            return SYMBOL,word

        else:
            return IDENTIFIER,word




class CompilationEngine:

    def __init__(self, infile, outfile):
        self.input = open(infile,'r')
        self.output = open(outfile,'w')
        self.tokenizer = JackTokenizer(self.input)
        self.indent = 0
        self.compileClass()


    def printToken(self,type, tok):
        tok = tok.replace("&", "&amp;")
        tok = tok.replace("\"", "&quot;")
        tok = tok.replace(">", "&gt;")
        tok = tok.replace("<", "&lt;")
        self.output.write(self.indent*TAB+type[BEFORE]+" "+tok+" "+type[AFTER]+"\n")

    def compileClass(self):
      #  print("compiling class")
        self.output.write("<class>\n")
        self.indent +=1

        #i assume the input is fine
        (type,tok)= self.tokenizer.tokenType()
        self.printToken(type,tok)#should be "<keyword>class</keyword>\n"
       # print(tok)
        # class name is next (should be tokened as identifier):
        self.tokenizer.advance()
        (type,tok)= self.tokenizer.tokenType()
      #  print(tok)
        self.printToken(type,tok)#open {

        self.tokenizer.advance()
        (typ,tok)= self.tokenizer.tokenType()
      #  print(tok)
        self.printToken(typ,tok)
        nxt = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
        while nxt == "field" or nxt == "static":
            self.compileClassVarDec();
            nxt = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
            #print(" before calling compileSubroutine nxt is",nxt)
        while nxt in subroutines:
            #print("calling compileSubroutine nxt is",nxt)
            self.compileSubroutine();
            nxt = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
        (typ,tok)= self.tokenizer.tokenType()
        self.printToken(typ,tok)
        self.indent -= 1
        self.output.write("</class>\n")
        return

    def compileClassVarDec(self):
        self.tokenizer.advance()
        self.output.write(TAB*self.indent+"<classVarDec>\n")
        self.indent +=1
        (typ,tok)= self.tokenizer.tokenType()
        while tok != ";":
            self.printToken(typ,tok)
            self.tokenizer.advance()
            (typ,tok)= self.tokenizer.tokenType()
        self.printToken(typ,tok)
        self.indent -=1
        self.output.write(self.indent*TAB+"</classVarDec>\n")

    def compileSubroutine(self):
        self.output.write(TAB*self.indent+"<subroutineDec>\n")
        self.indent+=1
        self.tokenizer.advance()
        typ, token = self.tokenizer.tokenType()
        while token != "(":
            self.printToken(typ,token)
            self.tokenizer.advance()
            typ, token = self.tokenizer.tokenType()
        self.printToken(typ,token)
        self.compileParameterList()
        typ, token = self.tokenizer.tokenType()
        self.printToken(typ, token) #should be ")"
        self.output.write(TAB*self.indent+"<subroutineBody>\n")
        self.indent+=1
        self.tokenizer.advance()
        typ, token = self.tokenizer.tokenType() #should be "{"
        self.printToken(typ, token)
        self.tokenizer.advance()
        typ, token = self.tokenizer.tokenType()
        while token != "}":
            self.compileVarDec()
            self.compileStatments()

            typ, token = self.tokenizer.tokenType() #should be "}"

        self.printToken(typ, token)
        self.indent -= 1
        self.output.write(TAB*self.indent+"</subroutineBody>\n")
        self.indent -= 1
        self.output.write(TAB*self.indent+"</subroutineDec>\n")
        return

    def compileParameterList(self):
        self.output.write(self.indent*TAB+"<parameterList>\n")
        self.indent +=1
        self.tokenizer.advance()
        type, token = self.tokenizer.tokenType()
        while token != ")":
            self.printToken(type,token)
            self.tokenizer.advance()
            type, token = self.tokenizer.tokenType()
        self.indent -=1

        self.output.write(self.indent*TAB+"</parameterList>\n")
        return

    def compileVarDec(self):

        nxt = self.tokenizer.tokenList[self.tokenizer.curTokenIdx]

        if nxt != "var":

            return
        self.output.write(TAB*self.indent+"<varDec>\n")
        self.indent += 1
        typ, token = self.tokenizer.tokenType() # assume its "var"

        #while token not in ["let", "if", "while", "do", "return"]:
        while token != ";":
            self.printToken(typ, token)
            self.tokenizer.advance()
            typ, token = self.tokenizer.tokenType()
        self.printToken(typ, token)
        self.indent -= 1
        self.output.write(self.indent*TAB+"</varDec>\n")
        self.tokenizer.advance()
        self.compileVarDec()

    def compileStatments(self):
        self.output.write(self.indent*TAB+"<statements>\n")
        self.indent += 1
        type, token = self.tokenizer.tokenType()
        while token !="}":
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
                exit(-100)
        self.indent -= 1
        self.output.write(self.indent*TAB+"</statements>\n")
        return

    def compileLet(self):
        self.output.write(self.indent*TAB+"<letStatement>\n")
        self.indent+=1
        typ, token = self.tokenizer.tokenType()
        while token != "=":
            self.printToken(typ,token)
            if token == "[":
                self.compileExpression()
                typ, token = self.tokenizer.tokenType()
                self.printToken(typ, token)
            self.tokenizer.advance()
            (typ, token) = self.tokenizer.tokenType()
        if token == "=":
            self.printToken(typ, token)
            self.compileExpression() # dont eat ;

        self.indent -=1
        self.output.write(self.indent*TAB+"</letStatement>\n")
        self.tokenizer.advance()
        return


    def compileDo(self):
        self.output.write(self.indent*TAB+"<doStatement>\n")
        self.indent+=1
        typ, token = self.tokenizer.tokenType()
        self.printToken(typ,token)
        self.tokenizer.advance()
        self.compileSubroutineCall()
        self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()
        self.printToken(typ,token)
        self.indent -=1
        self.output.write(self.indent*TAB+"</doStatement>\n")
        self.tokenizer.advance()
        return


    def compileIf(self):
        self.output.write(self.indent*TAB+"<ifStatement>\n")
        self.indent += 1
        typ, token = self.tokenizer.tokenType()
        self.printToken(typ, token)
        self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()
        self.printToken(typ,token) # should be "("
        self.compileExpression()
        #self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()
        self.printToken(typ,token) # should be ")"
        self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()
        self.printToken(typ,token) # should be "{"

        self.tokenizer.advance()
        self.compileStatments()
        #self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()
        self.printToken(typ, token) # should be "}"

        if self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1] == "else":
            self.tokenizer.advance() #else
            (typ, token) = self.tokenizer.tokenType()
            self.printToken(typ,token); #print else
            self.tokenizer.advance() #{
            (typ, token) = self.tokenizer.tokenType()
            self.printToken(typ, token) # should be "{"
            self.tokenizer.advance() #into statments
            self.compileStatments()
            #self.tokenizer.advance()
            (typ, token) = self.tokenizer.tokenType()
            self.printToken(typ,token) # should be "}"
        self.indent -=1
        self.output.write(self.indent*TAB+"</ifStatement>\n")
        self.tokenizer.advance()

        return

    def compileWhile(self): #TODO
        self.output.write(self.indent*TAB+"<whileStatement>\n")
        self.indent += 1
        typ, token = self.tokenizer.tokenType()
        self.printToken(typ,token)
        self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()
        self.printToken(typ,token) # should be "("
        self.compileExpression()
        #self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()
        self.printToken(typ,token) # should be ")"
        self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()
        self.printToken(typ,token) # should be "{"
        self.tokenizer.advance()
        self.compileStatments()

        (typ, token) = self.tokenizer.tokenType()
        self.tokenizer.advance()

        self.printToken(typ,token) # should be "}"
        self.indent -=1
        self.output.write(self.indent*TAB+"</whileStatement>\n")
        #self.tokenizer.advance()
        return

    def compileReturn(self): #TODO
        self.output.write(self.indent*TAB+"<returnStatement>\n")
        self.indent +=1
        typ, token = self.tokenizer.tokenType()
        self.printToken(typ,token) #print return
        #self.tokenizer.advance()
        #(typ, token) = self.tokenizer.tokenType()
        self.compileExpression()
        self.indent -=1
        self.output.write(self.indent*TAB+"</returnStatement>\n")
        self.tokenizer.advance()
        return

    def compileExpression(self):
        self.tokenizer.advance()
        (typ, token) = self.tokenizer.tokenType()#CHECK!
        if token is ";":
            sym, tok = self.tokenizer.tokenType()
            self.printToken(sym, tok)
            return
        #if token in symbols:
        #    return
        self.output.write(self.indent*TAB+"<expression>\n")
        self.indent +=1
      #  print("calling compile term from compile expression current is: ",self.tokenizer.tokenList[self.tokenizer.curTokenIdx])
        self.compileTerm()
        nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
       # print("in expression after term, next is:", nextToken)
        #if nextToken in op:
        while nextToken in op:
            self.tokenizer.advance()
            sym, tok = self.tokenizer.tokenType()
            self.printToken(sym, tok)
            self.tokenizer.advance()
            self.compileTerm()
            nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]
         #   print(nextToken)
        self.indent -=1
        self.output.write(self.indent*TAB+"</expression>\n")
        self.tokenizer.advance() #??????????????????????????
        sym, tok = self.tokenizer.tokenType()
        if tok == ";":
            self.printToken(sym,tok)
        return

    def compileTerm(self):
        self.output.write(self.indent*TAB+"<term>\n")
        self.indent +=1
        nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx+1]

        if self.tokenizer.tokenList[self.tokenizer.curTokenIdx] == "(":
            #write (
            t, tok = self.tokenizer.tokenType()
            self.printToken(t,tok)
            #write expression
          #  print("shold be ( is: ",tok)
            self.compileExpression()
            t, tok = self.tokenizer.tokenType() #write )
          #  print("should be )", tok)
            self.printToken(t,tok)

        elif self.tokenizer.tokenList[self.tokenizer.curTokenIdx] in unarytOp:
            t, tok = self.tokenizer.tokenType()
            self.printToken(t,tok)
            self.tokenizer.advance()
            self.compileTerm()

        elif nextToken == "." or nextToken == "(" :   #subroutine  call
            self.compileSubroutineCall() #TODO

        elif nextToken == "[": # array entry
            t, tok = self.tokenizer.tokenType()
            self.printToken(t,tok) #printing "["
            self.tokenizer.advance()
            t, tok = self.tokenizer.tokenType()
            self.printToken(t,tok)
            self.compileExpression()
            #should advance????????????????
            #self.tokenizer.advance()
            t, tok = self.tokenizer.tokenType()
            self.printToken(t,tok) # should be ]

        else:
            t, tok = self.tokenizer.tokenType()
            self.printToken(t,tok)
            #self.tokenizer.advance()
        self.indent -=1
        self.output.write(self.indent*TAB+"</term>\n")

    def compileSubroutineCall(self):
        tp, curTok = self.tokenizer.tokenType()
        while curTok != "(":
            self.printToken(tp,curTok)
            self.tokenizer.advance()
            tp,curTok = self.tokenizer.tokenType()
        self.printToken(tp,curTok) # (
        self.tokenizer.advance()
        self.compileExpressionList()
        tp,curTok = self.tokenizer.tokenType()
        self.printToken(tp,curTok) # ) 

    def compileExpressionList(self):
        self.output.write(self.indent*TAB+"<expressionList>\n")
        self.indent += 1
        nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx]
        while nextToken != ")":
            self.tokenizer.curTokenIdx -= 1
            self.compileExpression()
            #self.tokenizer.advance()
            tp, tk = self.tokenizer.tokenType()
            if tk == ",":
                self.printToken(tp,tk)
                self.tokenizer.advance()
            nextToken = self.tokenizer.tokenList[self.tokenizer.curTokenIdx]
        self.indent -= 1
        self.output.write(self.indent*TAB+"</expressionList>\n")

###############################################MAIN#####################################################################
inputFileName = sys.argv[1]
if os.path.isdir(inputFileName):
    for file in os.listdir(inputFileName):
        if file.endswith(".jack"):
            file = inputFileName+"/"+file
            outputFileName = file.replace(".jack",".xml")
            compiler = CompilationEngine(file, outputFileName)
elif os.path.isfile(inputFileName):
    outputFileName = inputFileName.replace(".jack",".xml")
    compiler = CompilationEngine(inputFileName, outputFileName)