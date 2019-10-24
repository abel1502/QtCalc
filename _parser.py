from enum import Enum

_DEBUG = False
def dbg(stage, lex, id):
    if _DEBUG:
        print("[{0}] #{2} '{1}'".format(stage, lex, id))


class ParserException(Exception):
    def __init__(self, text, pos, lex=None, *args, **kwargs):
        super().__init__("{} at lexem #{}".format(text, pos) + (" \"{}\"".format(lex.pStr) if lex else ""), *args, **kwargs)

class BracketException(ParserException):
    def __init__(self, pos, lex=None, *args, **kwargs):
        super().__init__("Expected a bracket", pos, lex, *args, **kwargs)

class UnknownNameException(ParserException):
    def __init__(self, name, pos, lex=None, *args, **kwargs):
        super().__init__("Unknown name '{}'".format(name), pos, lex, *args, **kwargs)

class LexType(Enum):
    end = 0
    digit = 1
    add = 2
    sub = 3
    mul = 4
    div = 5
    mod = 6
    bracketOpen = 7
    bracketClose = 8
    name = 9
    dot = 10
    comma = 11
    
    def __str__(self):
        return "<LexType:{}>".format(self.name)


class Lexem:
    lexDict = dict(zip("0123456789+-*/%().,", [LexType.digit] * 10 + [LexType.add, LexType.sub, LexType.mul, LexType.div, LexType.mod, LexType.bracketOpen, LexType.bracketClose, LexType.dot, LexType.comma]))
    
    @staticmethod
    def getLexType(aStr):
        if aStr in Lexem.lexDict:
            return Lexem.lexDict[aStr]
        return LexType.name  # TODO: Verify?
    
    def __init__(self, aStr, aType=None):
        self.pStr = aStr
        if aType is not None:
            self.pType = aType
        else:
            self.pType = self.getLexType(aStr)
    
    def isEnd(self):
        return self.pType is LexType.end
    
    def getOper(self):
        if self.pType is LexType.add:
            return lambda a, b: a + b
        if self.pType is LexType.sub:
            return lambda a, b: a - b
        if self.pType is LexType.mul:
            return lambda a, b: a * b
        if self.pType is LexType.div:
            return lambda a, b: a / b
        if self.pType is LexType.mod:
            return lambda a, b: a % b
        return None
    
    def __str__(self):
        return "<Lex:{},\"{}\">".format(self.pType, self.pStr)


EndLexem = Lexem("", LexType.end)


class Parser:
    def __init__(self, aVars={}, aFuncs={}):
        self.pLexems = [EndLexem]
        self.pCurId = 0
        self.pCurLex = None
        self.pVars = aVars
        self.pFuncs = aFuncs
    
    def feed(self, aData):
        self.pLexems.pop()
        for lItem in aData:
            self.pLexems.append(Lexem(lItem))
        self.pLexems.append(EndLexem)
    
    def nextLex(self):
        self.pCurLex = self.pLexems[self.pCurId]
        self.pCurId += 1
    
    def previewLex(self):
        return self.pLexems[self.pCurId]
    
    def evaluate(self):
        self.nextLex()
        if self.pCurLex.isEnd():
            return 0
        lRes = self.parseExpr()
        if not self.pCurLex.isEnd():
            raise ParserException("Expression has an extra appendix", self.pCurId, self.pCurLex)
        #if type(lRes) not in {int, float}:
        #    raise ParserException("Result is not a number", -1)
        return lRes
    
    def clear(self):
        self.pLexems = [EndLexem]
        self.pCurId = 0
        self.pCurLex = None
    
    #def parseChar(self, char):  # ?
    
    def parseExpr(self):
        dbg("expr", self.pCurLex, self.pCurId)
        ans = self.parseTerm()
        while self.pCurLex.pType in (LexType.add, LexType.sub):
            oper = self.pCurLex.getOper()
            self.nextLex()
            ans = oper(ans, self.parseTerm())
        return ans
    
    def parseTerm(self):
        dbg("term", self.pCurLex, self.pCurId)
        lCurType = self.pCurLex.pType
        ans = self.parseFactor()
        while (self.pCurLex.pType in (LexType.mul, LexType.div, LexType.mod, LexType.name, LexType.bracketOpen)) or (lCurType in (LexType.bracketOpen, LexType.name) and self.pCurLex.pType is LexType.digit):
            lPrevType = lCurType
            if self.pCurLex.pType is LexType.name or (lPrevType in (LexType.bracketOpen, LexType.name) and self.pCurLex.pType is LexType.digit):
                oper = lambda a, b: a * b
                lCurType = self.pCurLex.pType
                ans = oper(ans, self.parseFactor())
                continue
            if self.pCurLex.pType is LexType.bracketOpen:
                oper = lambda a, b: a * b
                lCurType = self.pCurLex.pType
                ans = oper(ans, self.parseDeg())
                continue
            if self.pCurLex.pType is LexType.div and self.previewLex().pType is LexType.div:
                oper = lambda a, b: a // b
                self.nextLex()
            else:
                oper = self.pCurLex.getOper()
            self.nextLex()
            lCurType = self.pCurLex.pType
            ans = oper(ans, self.parseFactor())
        return ans
    
    def parseFactor(self):
        dbg("factor", self.pCurLex, self.pCurId)
        ans = self.parseDeg()
        if self.pCurLex.pType is LexType.mul and self.previewLex().pType is LexType.mul:
            oper = lambda a, b: a ** b
            self.nextLex()
            self.nextLex()
            ans = oper(ans, self.parseFactor())
        return ans
        
        #ans = self.parseDeg()
        #while self.pCurLex.pType is LexType.mul and self.previewLex().pType is LexType.mul:
        #    oper = lambda a, b: a ** b
        #    self.nextLex()
        #    self.nextLex()
        #    ans = oper(ans, self.parseDeg())
        #return ans
    
    def parseDeg(self):
        dbg("deg", self.pCurLex, self.pCurId)
        if self.pCurLex.pType is LexType.sub:
            self.nextLex()
            return -self.parseDeg()
        if self.pCurLex.pType is LexType.add:
            self.nextLex()
            return self.parseDeg()
        if self.pCurLex.pType is LexType.bracketOpen:
            self.nextLex()
            lRes = self.parseExpr()
            if self.pCurLex.pType is not LexType.bracketClose:
                raise BracketException(self.pCurId, self.pCurLex)
            self.nextLex()
            return lRes
        if self.pCurLex.pType is LexType.digit:
            return self.parseNumber()
        if self.pCurLex.pType is LexType.name:
            return self.parseName()
        raise ParserException("Unexpected lexem", self.pCurId, self.pCurLex)
    
    def parseNumber(self):
        dbg("number", self.pCurLex, self.pCurId)
        lRes = []
        while self.pCurLex.pType is LexType.digit:
            lRes.append(self.pCurLex.pStr)
            self.nextLex()
        if self.pCurLex.pType is not LexType.dot:
            return int("".join(lRes))
        lRes.append(self.pCurLex.pStr)
        self.nextLex()
        while self.pCurLex.pType is LexType.digit:
            lRes.append(self.pCurLex.pStr)
            self.nextLex()
        return float("".join(lRes))
    
    def parseName(self):
        dbg("name", self.pCurLex, self.pCurId)
        lName = self.pCurLex.pStr
        self.nextLex()
        if lName in self.pVars:
            return self.pVars[lName]
        elif lName in self.pFuncs:
            if self.pCurLex.pType is not LexType.bracketOpen:
                raise BracketException(self.pCurId, self.pCurLex)
            self.nextLex()
            if self.pCurLex.pType is LexType.bracketClose:
                lRes = []
            else:
                lRes = self.parseSequence()
            if self.pCurLex.pType is not LexType.bracketClose:
                raise BracketException(self.pCurId, self.pCurLex)
            self.nextLex()
            lVal = self.pFuncs[lName](*lRes)
            #assert isinstance(lVal, (int, float))
            return lVal
        else:
            raise UnknownNameException(lName, self.pCurId)
        
    def parseSequence(self):
        dbg("sequence", self.pCurLex, self.pCurId)
        lRes = [self.parseExpr()]
        while self.pCurLex.pType is LexType.comma:
            self.nextLex()
            lRes.append(self.parseExpr())
        return lRes
    
    def updateVarsFuncs(self, aVars={}, aFuncs={}):
        self.pVars.update(aVars)
        self.pFuncs.update(aFuncs)


def main():
    p = Parser(aFuncs={"int" : int}, aVars={"x" : 2})
    p.feed(["int", "(", "x", "1", "7", "*", "*", "2", ")"])
    print(p.evaluate())
    p.clear()
    
    p.updateVarsFuncs(aVars={"x":4})
    p.feed(["7", "*", "*", "3", "x"])
    print(p.evaluate())


if __name__ == "__main__":
    main()