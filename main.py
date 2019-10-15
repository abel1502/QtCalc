import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
from copy import deepcopy
import math


class STYLE:
    GENERAL_BTN = """QPushButton:pressed {border-style: inset;background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 rgb(69, 209, 209), stop:1 rgb(69, 209, 209))} QPushButton {font-weight:bold;font-size:14px;border-style: outset;border-width: 1px;border-radius: 1px;border-color: grey;margin: 0.5px;}"""
    NUM_BTN = """QPushButton {background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 rgb(210, 210, 210), stop:1 rgb(185, 185, 185))}""" + GENERAL_BTN
    INP_BTN = """QPushButton {background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 rgb(210, 210, 0), stop:1 rgb(185, 185, 0))}""" + GENERAL_BTN
    ACT_BTN = """QPushButton {background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 rgb(0, 150, 0), stop:1 rgb(0, 125, 0))}""" + GENERAL_BTN
    PREVIEW = """QLineEdit {background-color: rgb(238, 238, 238);}"""
    OUTPUT = """QLineEdit {}"""    


class PREF:
    VERSION = "0.6"
    NAME = "Abel Calculator v{}".format(VERSION)
    INP_NUM = 2
    OUT_LEN = 7
    DBG_UI_PATH = "design.ui"
    CONSTS = {"PI" : math.pi, "E" : math.e}
    FUNCS = {"log" : math.log, "cos" : math.cos, "sin" : math.sin, "tg" : math.tan, 
             "arccos" : math.acos, "arcsin" : math.asin, "arctg" : math.atan, "gcd" : math.gcd,
             "factorial" : math.factorial, "abs" : abs, "deg" : math.degrees, "rad" : math.radians,
             "int" : int, "float" : float}
    CURSOR = "_"
    VAR_COUNT = 10
    VAR_LABEL = "<{}>={}"
    ABOUT = "Abel Calculator is a small app made by\nAndrew Belyaev (Russia, Moscow, School 179)\nas a scholar micro-project.\n\nThis project is hosted on GitHub at\nhttps://github.com/abel1502/QtCalc"


class MainWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(PREF.DBG_UI_PATH, self)
        self.init()
    
    def initUI(self):
        self.setWindowTitle(PREF.NAME)
        
        self.output.setStyleSheet(STYLE.OUTPUT)
        self.GLayout.addWidget(self.output, 0, 0, 1, 6)
        
        for const in sorted(PREF.CONSTS):
            lAction = QAction(const, self.menuConstant)
            lAction.triggered.connect((lambda i: lambda: self.addName(i))(const))
            self.menuConstant.addAction(lAction)
        
        for func in sorted(PREF.FUNCS):
            lAction = QAction(func, self.menuFunction)
            lAction.triggered.connect((lambda i: lambda: self.addFunc(i))(func))
            self.menuFunction.addAction(lAction)
        
        self.saveVarAction = []
        self.loadVarAction = []
        for i in range(PREF.VAR_COUNT):
            lAction = QAction(PREF.VAR_LABEL.format(i, self.variables[i]), self.menuSaveVariable)
            lAction.triggered.connect((lambda i: lambda: self.saveVar(i))(i))
            self.menuSaveVariable.addAction(lAction)
            self.saveVarAction.append(lAction)
            
            lAction = QAction(PREF.VAR_LABEL.format(i, self.variables[i]), self.menuLoadVariable)
            lAction.triggered.connect((lambda i: lambda: self.loadVar(i))(i))
            self.menuLoadVariable.addAction(lAction)
            self.loadVarAction.append(lAction)
        
        def genInpBtn(text, x, y, name="", *args):
            lBtn = QPushButton(name if name else text, self)
            lBtn.clicked.connect(lambda: self.processInput(text))
            lBtn.setMinimumSize(32, 32)
            lBtn.setFocusPolicy(Qt.NoFocus)
            lBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            if text in "0123456789":
                lBtn.setStyleSheet(STYLE.NUM_BTN)
            else:
                lBtn.setStyleSheet(STYLE.INP_BTN)
            self.GLayout.addWidget(lBtn, x + 2, y, *args)
            return lBtn
        
        def genActBtn(text, action, x, y, *args):
            lBtn = QPushButton(text, self)
            lBtn.clicked.connect(action)
            lBtn.setMinimumSize(32, 32)
            lBtn.setFocusPolicy(Qt.NoFocus)
            lBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            lBtn.setStyleSheet(STYLE.ACT_BTN)
            self.GLayout.addWidget(lBtn, x + 2, y, *args)
            return lBtn
        
        genInpBtn("1", 1, 0)
        genInpBtn("2", 1, 1)
        genInpBtn("3", 1, 2)
        genInpBtn("4", 2, 0)
        genInpBtn("5", 2, 1)
        genInpBtn("6", 2, 2)
        genInpBtn("7", 3, 0)
        genInpBtn("8", 3, 1)
        genInpBtn("9", 3, 2)
        genInpBtn(",", 4, 0)
        genInpBtn("0", 4, 1)
        genInpBtn(".", 4, 2)
        
        genInpBtn("/", 1, 3)
        genInpBtn("*", 2, 3)
        genInpBtn("-", 3, 3)
        genInpBtn("+", 4, 3)
        
        genInpBtn("//", 1, 4)
        genInpBtn("%", 2, 4)
        genInpBtn("(", 3, 4)
        genInpBtn(")", 4, 4)
        
        genActBtn("C", self.clear, 0, 5)
        genActBtn("<-", self.backspace, 1, 5)
        genInpBtn("**", 2, 5)
        genActBtn("=", self.calculate, 3, 5, 2, 1)
        
        genActBtn("<", self.moveLeft, 0, 3)
        genActBtn(">", self.moveRight, 0, 4)
        
        self.preOutput = QLineEdit(self)
        self.preOutput.setReadOnly(True)
        self.preOutput.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preOutput.setStyleSheet(STYLE.PREVIEW)
        self.preOutput.setFocusPolicy(Qt.NoFocus)
        self.GLayout.addWidget(self.preOutput, 2, 0, 1, 3)        
    
    def init(self):
        self.curExpr = []
        self.variables = ["0" for _ in range(PREF.VAR_COUNT)]
        self.cursorPos = 0
        
        self.initUI()
        
        self.actionExit.triggered.connect(lambda: sys.exit(0))
        self.actionAbout.triggered.connect(lambda: QMessageBox.about(self, "About " + PREF.NAME, PREF.ABOUT))
        
        self.setOutput()
        self.preCalculate()
    
    def event(self, event):
        if event.type() == 51:
            if event.key() == Qt.Key_Backspace:
                self.backspace()
                return True
            if event.key() == Qt.Key_Left:
                self.moveLeft()
                return True
            if event.key() == Qt.Key_Right:
                self.moveRight()
                return True
            #print(event.key())
        return super().event(event)
    
    def keyPressEvent(self, event):
        if event.text() in list("01234567890*/+-%().,"):
            self.processInput(event.text())
        if event.text() in list("\r\n= "):
            self.calculate()
        #print(repr(event.text()), event.key())
        super().keyPressEvent(event)
    
    def moveLeft(self):
        self.cursorPos -= 1
        self.clampCPos()
        self.setOutput()
    
    def moveRight(self):
        self.cursorPos += 1
        self.clampCPos()
        self.setOutput()
    
    def clampCPos(self):
        self.cursorPos = min(len(self.curExpr), max(0, self.cursorPos))
    
    def getExpr(self, showCursor=False):
        if showCursor:
            lRes = self.curExpr[:self.cursorPos] + [PREF.CURSOR] + self.curExpr[self.cursorPos:]
            #if lRes[-1] == PREF.CURSOR:
            #    lRes = lRes[:-1]
            return lRes
        return self.curExpr
    
    def addExpr(self, item):
        self.curExpr.insert(self.cursorPos, item)
        self.cursorPos += 1
    
    def handleError(self, err):
        QErrorMessage.qtHandler().showMessage(repr(err))
    
    def updateVarNames(self):
        for i in range(PREF.VAR_COUNT):
            self.saveVarAction[i].setText(PREF.VAR_LABEL.format(i, self.variables[i]))
            self.loadVarAction[i].setText(PREF.VAR_LABEL.format(i, self.variables[i]))
    
    def saveVar(self, varId):
        if self.preOutput.text() == "~":
            self.handleError("Can't save a wrong variable")
            return
        if len(self.preOutput.text()) == 0:
            value = "0"
        else:
            value = self.preOutput.text()
        if value[-2:] == ".0":
            value = value[:-2]
        #if "e" in value:
        #    self.handleError("Value too big for variable")
        #    return
        self.variables[varId] = value
        #print(value, varId)
        sys.stdout.flush()
        self.updateVarNames
        self.saveVarAction[varId].setText(PREF.VAR_LABEL.format(varId, value))
        self.loadVarAction[varId].setText(PREF.VAR_LABEL.format(varId, value))
    
    def loadVar(self, varId):
        self.addName("var{}".format(varId))
    
    def addName(self, name):
        self.addExpr("({})".format(name))
        self.setOutput()
        self.preCalculate()
    
    def addFunc(self, func):
        self.addExpr("{}(".format(func))
        self.setOutput()
        self.preCalculate()
    
    def processInput(self, value):
        self.addExpr(value)
        self.setOutput()
        self.preCalculate()
    
    def setOutput(self, value=None):
        if value == None:
            value = ''.join(self.getExpr(True))
        self.output.setText(value)
    
    def setPreOutput(self, value):
        self.preOutput.setText(value)
    
    def clear(self):
        self.curExpr = []
        self.cursorPos = 0
        self.setOutput('')
        self.preCalculate()
    
    def backspace(self):
        if self.cursorPos > 0:
            i = self.cursorPos - 1
            self.curExpr.pop(i)
            self.cursorPos -= 1
        self.setOutput()
        self.preCalculate()
    
    def _calculate(self, expr):
        lExpr = ''.join(expr)
        lExpr = lExpr if lExpr else "0"
        value = self.evaluate(lExpr)
        if not isinstance(value, (int, float)):
            raise Exception("Invalid statement")
        return value, lExpr
    
    def calculate(self):
        try:
            value, lExpr = self._calculate(self.curExpr)
            self.setOutput("{}={}".format(lExpr, value))
        except Exception as e:
            self.handleError(e)
    
    def preCalculate(self):
        try:
            value, lExpr = self._calculate(self.curExpr)
            self.setPreOutput(str(value))
        except Exception as e:
            self.setPreOutput("~")
    
    def evaluate(self, expr):
        lLocals = {}
        for i in range(PREF.VAR_COUNT):
            lLocals["var{}".format(i)] = float(self.variables[i])
        lLocals.update(PREF.CONSTS)
        lLocals.update(PREF.FUNCS)
        return eval(expr, globals(), lLocals)

def main():
    lApplication = QApplication(sys.argv)
    lMainWidget = MainWidget()
    lMainWidget.show()
    sys.exit(lApplication.exec())


if __name__ == "__main__":
    main()