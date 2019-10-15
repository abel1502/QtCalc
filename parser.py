from enum import Enum


class EmptyExprException(Exception):
    pass


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
        try:
            lRes = self.parseExpr()
        except EmptyExprException:
            lRes = 0
        assert self.pCurLex.isEnd()
        return lRes
    
    def clear(self):
        self.pLexems = [EndLexem]
        self.pCurId = 0
        self.pCurLex = None
    
    #def parseChar(self, char):  # ?
    
    def parseExpr(self):
        ans = self.parseTerm()
        while self.pCurLex.pType in (LexType.add, LexType.sub):
            oper = self.pCurLex.getOper()
            self.nextLex()
            ans = oper(ans, self.parseTerm())
        return ans
    
    def parseTerm(self):
        ans = self.parseFactor()
        while self.pCurLex.pType in (LexType.mul, LexType.div, LexType.mod):
            if self.pCurLex.pType is LexType.div and self.previewLex().pType is LexType.div:
                oper = lambda a, b: a // b
                self.nextLex()
            else:
                oper = self.pCurLex.getOper()
            self.nextLex()
            ans = oper(ans, self.parseFactor())
        return ans
    
    def parseFactor(self):
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
        if self.pCurLex.pType is LexType.sub:
            self.nextLex()
            return -self.parseDeg()
        if self.pCurLex.pType is LexType.add:
            self.nextLex()
            return self.parseDeg()
        if self.pCurLex.pType is LexType.bracketOpen:
            self.nextLex()
            lRes = self.parseDeg()
            assert self.pCurLex.pType is LexType.bracketClose
            self.nextLex()
            return lRes
        if self.pCurLex.pType is LexType.digit:
            return self.parseNumber()
        if self.pCurLex.pType is LexType.name:
            return self.parseName()
        raise EmptyExprException()  # ?
    
    def parseNumber(self):
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
        lName = self.pCurLex.pStr
        self.nextLex()
        if self.pCurLex.pType is LexType.bracketOpen:
            self.nextLex()
            lRes = self.parseSequence()
            assert self.pCurLex.pType is LexType.bracketClose
            self.nextLex()
            return self.pFuncs[lName](*lRes)  # TODO: Verify int/float
        else:
            return self.pVars[lName]
    
    def parseSequence(self):
        try:
            lRes = [self.parseExpr()]
        except EmptyExprException:
            return []
        while self.pCurLex.pType is LexType.comma:
            self.nextLex()
            lRes.append(self.parseExpr())
        return lRes
    
    def updateVarsFuncs(self, aVars={}, aFuncs={}):
        self.pVars.update(aVars)
        self.pFuncs.update(aFuncs)


def main():
    p = Parser(aFuncs={"int" : int})
    p.feed(["int", "(", ")"])
    print(p.evaluate())
    p.clear()

    p.feed(["2", "*", "*", "3", "*", "*", "2"])
    print(p.evaluate())


if __name__ == "__main__":
    main()