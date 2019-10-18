import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtMultimedia import *
import math
import _parser
from collections import deque
#import resources
import time
import platform
import os
import random
from copy import copy  # deepcopy?
import resources

#QResource.registerResource("./resources.qrc")


class STYLE:
    GENERAL_BTN = """QPushButton:pressed {{border-style: inset;background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 rgb(69, 209, 209), stop:1 rgb(69, 209, 209))}} QPushButton {{font-weight:bold;font-size:{0[button_font]}px;border-style: outset;border-width: 1px;border-radius: 1px;border-color: grey;margin: 0.5px;}}"""
    NUM_BTN = """QPushButton {{background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 rgb(210, 210, 210), stop:1 rgb(185, 185, 185))}}""" + GENERAL_BTN
    INP_BTN = """QPushButton {{background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 rgb(210, 210, 0), stop:1 rgb(185, 185, 0))}}""" + GENERAL_BTN
    ACT_BTN = """QPushButton {{background: qlineargradient(x1:0, y1:0, x2:0, y2:1,stop:0 rgb(0, 150, 0), stop:1 rgb(0, 125, 0))}}""" + GENERAL_BTN
    PREVIEW = """QLineEdit {{font-size: {0[output_font]}px; background-color: rgb(238, 238, 238);}}"""
    OUTPUT = """QLineEdit {{font-size: {0[output_font]}px;}}"""
    
    def get(name):
        return getattr(STYLE, name).format(USERPREF.STYLE)


class USERPREF:
    CALCULATION = {"output_round" : -1}
    STYLE = {"output_font" : 16, "button_font" : 14}


class PREF:
    VERSION = "1.3"
    NAME = "Abel Calculator v{}".format(VERSION)
    DBG_UI_PATH = ":/main.ui"
    DBG_UI_SETTINGS_PATH = ":/settings.ui"
    CONSTS = {"PI" : math.pi, "E" : math.e}
    FUNCS = {"log" : math.log, "cos" : math.cos, "sin" : math.sin, "tg" : math.tan, 
             "arccos" : math.acos, "arcsin" : math.asin, "arctg" : math.atan, "gcd" : math.gcd,
             "factorial" : math.factorial, "abs" : abs, "deg" : math.degrees, "rad" : math.radians,
             "int" : int, "float" : float, "sqrt" : lambda x: x ** 0.5}
    CURSOR = "_"
    VAR_COUNT = 10
    VAR_LABEL = "<{}>={}"
    HISTORY_SIZE = 100
    ABOUT = "Abel Calculator is a small app made by\nAndrew Belyaev (Russia, Moscow, School 179)\nas a scholar micro-project.\n\nThis project is hosted on GitHub at\nhttps://github.com/abel1502/QtCalc"


class SignalController(QObject):
    redrawStyleSignal = pyqtSignal()
    recalcSignal = pyqtSignal()
    
    def __init__(self):
        super().__init__()


class MainWidget(QMainWindow):
    mainSC = SignalController()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uifile = QFile(PREF.DBG_UI_PATH)
        uifile.open(QFile.ReadOnly)
        uic.loadUi(uifile, self)
        uifile.close()
        #uic.loadUi(PREF.DBG_UI_PATH, self)
        self.init()
    
    def initUI(self):
        self.setWindowTitle(PREF.NAME)
        
        self.output.setStyleSheet(STYLE.get("OUTPUT"))
        self.mainSC.redrawStyleSignal.connect(lambda: self.output.setStyleSheet(STYLE.get("OUTPUT")))
        self.GLayout.addWidget(self.output, 0, 0, 1, 6)
        
        for const in sorted(PREF.CONSTS):
            lAction = QAction(const, self.menuConstant)
            lAction.triggered.connect((lambda i: lambda: self.addName(i))(const))
            self.menuConstant.addAction(lAction)
        
        for func in sorted(PREF.FUNCS):
            lAction = QAction(func, self.menuFunction)
            lAction.triggered.connect((lambda i: lambda: self.addName(i))(func))
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
                lBtn.setStyleSheet(STYLE.get("NUM_BTN"))
                self.mainSC.redrawStyleSignal.connect((lambda i: lambda: i.setStyleSheet(STYLE.get("NUM_BTN")))(lBtn))
            else:
                lBtn.setStyleSheet(STYLE.get("INP_BTN"))
                self.mainSC.redrawStyleSignal.connect((lambda i: lambda: i.setStyleSheet(STYLE.get("INP_BTN")))(lBtn))
            self.GLayout.addWidget(lBtn, x + 2, y, *args)
            return lBtn
        
        def genActBtn(text, action, x, y, *args):
            lBtn = QPushButton(text, self)
            lBtn.clicked.connect(action)
            lBtn.setMinimumSize(32, 32)
            lBtn.setFocusPolicy(Qt.NoFocus)
            lBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            lBtn.setStyleSheet(STYLE.get("ACT_BTN"))
            self.mainSC.redrawStyleSignal.connect((lambda i: lambda: i.setStyleSheet(STYLE.get("ACT_BTN")))(lBtn))
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
        #genActBtn("Ctrl-Z", lambda: None, 3, 5)
        genActBtn("=", self.calculate, 3, 5, 2, 1)
        
        genActBtn("<", self.moveLeft, 0, 3)
        genActBtn(">", self.moveRight, 0, 4)
        
        self.preOutput = QLineEdit(self)
        self.preOutput.setReadOnly(True)
        self.preOutput.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preOutput.setStyleSheet(STYLE.get("PREVIEW"))
        self.mainSC.redrawStyleSignal.connect(lambda: self.preOutput.setStyleSheet(STYLE.get("PREVIEW")))
        self.preOutput.setFocusPolicy(Qt.NoFocus)
        self.GLayout.addWidget(self.preOutput, 2, 0, 1, 3)        
    
    def init(self):
        self.curExpr = []
        self.history = deque([[]])
        self.historyPos = 0
        self.variables = ["0" for _ in range(PREF.VAR_COUNT)]
        self.cursorPos = 0
        self.parser = _parser.Parser(aVars=PREF.CONSTS, aFuncs=PREF.FUNCS)
        
        self.initUI()
        
        self.settingsForm = SettingsWidget()
        
        self.actionExit.triggered.connect(lambda: sys.exit(0))
        self.actionAbout.triggered.connect(lambda: QMessageBox.about(self, "About " + PREF.NAME, PREF.ABOUT))
        self.actionPreferences.triggered.connect(lambda: self.settingsForm.show())
        self.mainSC.recalcSignal.connect(self.preCalculate)
        self.actionUndo.triggered.connect(self.undo)  # TODO: Disable inapplicable
        self.actionRedo.triggered.connect(self.redo)
        self.actionUndo.setShortcut(QKeySequence("Ctrl+Z"))
        self.actionRedo.setShortcut(QKeySequence("Ctrl+Y"))  # R?
        
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
            if event.key() == Qt.Key_Delete:
                self.clear()
                return True
            #print(event.key())
        return super().event(event)
    
    def keyPressEvent(self, event):
        if event.text() in list("01234567890*/+-%().,"):
            self.processInput(event.text())
        if event.text() in list("\r\n="):
            self.calculate()
        #print(repr(event.text()), event.key())
        super().keyPressEvent(event)
    
    def addHistory(self):
        self.historyPos += 1
        if self.historyPos > PREF.HISTORY_SIZE:
            self.history.popleft()
            self.historyPos -= 1
        while len(self.history) > self.historyPos:
            self.history.pop()
        self.history.append(copy(self.curExpr))
    
    def undo(self):
        if self.historyPos <= 0:
            return
        self.historyPos -= 1
        self.curExpr = copy(self.history[self.historyPos])
        self.clampCPos()
        self.setOutput()
        self.preCalculate()
    
    def redo(self):
        if self.historyPos >= len(self.history) - 1:
            return
        self.historyPos += 1
        self.curExpr = copy(self.history[self.historyPos])
        self.clampCPos()
        self.setOutput()
        self.preCalculate()
        if random.random() > 0.11:
            return
        if platform.system() == "Windows" or (platform.system() == "Linux" and "ANDROID_ARGUMENT" not in os.environ):
            try:
                mp = QMediaPlayer()
                mp.mediaStatusChanged.connect(lambda x: mp.play() if x == 3 else None)
                mp.setMedia(QMediaContent(QUrl(":/Redo.mp3")))
            except Exception as e:
                self.handleError(e)
        else:
            QMessageBox.information(self, "Oops", "This should have triggered an easter egg, but your OS doesn't seem to be capable of showing it. We're sorry")
    
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
        if item in ("**", "//"):
            self.addExpr(item[0])
            self.addExpr(item[0])
            return
        self.curExpr.insert(self.cursorPos, item)
        self.cursorPos += 1
        self.addHistory()
    
    def setExpr(self, expr, cursorPos=0):
        self.curExpr = expr
        self.cursorPos = cursorPos
    
    def handleError(self, err):
        #QErrorMessage.qtHandler().showMessage(repr(err))
        QMessageBox.critical(self, "Error", "{}: {}".format(type(err).__name__, str(err)))
        #QMessageBox.warning(self, "Error", repr(err))
    
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
        self.addExpr(name)
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
        self.addHistory()
        self.setOutput()
        self.preCalculate()
    
    def backspace(self):
        if self.cursorPos > 0:
            i = self.cursorPos - 1
            self.curExpr.pop(i)
            self.cursorPos -= 1
        self.addHistory()
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
            #self.setOutput("{}={}".format(lExpr, value))
            self.curExpr = list(str(value))
            self.cursorPos = len(self.curExpr)
            self.addHistory()
            self.setOutput()
            self.preCalculate()
        except Exception as e:
            self.handleError(e)
    
    def preCalculate(self):
        try:
            value, lExpr = self._calculate(self.curExpr)
            self.setPreOutput(str(value))
        except Exception as e:
            self.setPreOutput("~")
    
    def evaluate(self, expr):
        lVars = {}
        for i in range(PREF.VAR_COUNT):
            lVars["var{}".format(i)] = float(self.variables[i])
        self.parser.clear()
        lExpr = self.getExpr()
        self.parser.feed(lExpr)
        self.parser.updateVarsFuncs(aVars=lVars)
        lRes = self.parser.evaluate()
        if isinstance(lRes, float) and USERPREF.CALCULATION["output_round"] != -1:
            lRes = round(lRes, USERPREF.CALCULATION["output_round"])
        return lRes
        

class SettingsWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uifile = QFile(PREF.DBG_UI_SETTINGS_PATH)
        uifile.open(QFile.ReadOnly)
        uic.loadUi(uifile, self)
        uifile.close()
        #uic.loadUi(PREF.DBG_UI_SETTINGS_PATH, self)
        self.init()
    
    def init(self):
        def genSpinBoxInput(settingsDict, settingName, settingLabel=None, min=0, max=100):
            fieldWidget = QSpinBox()
            fieldWidget.setMinimum(min)
            fieldWidget.setMaximum(max)
            fieldWidget.setValue(settingsDict[settingName])
            fieldWidget.valueChanged[int].connect(lambda v: self.setSetting(settingsDict, settingName, v))
            if settingLabel is None:
                settingLabel = settingName
            self.formLayout.addRow(settingLabel, fieldWidget)
            return fieldWidget
        
        genSpinBoxInput(USERPREF.STYLE, "button_font", "Button font size", 5, 50)
        genSpinBoxInput(USERPREF.STYLE, "output_font", "Input-output font size", 5, 50)
        genSpinBoxInput(USERPREF.CALCULATION, "output_round", "Output precision (-1 = no rounding)", -1, 20)
    
    def setSetting(self, settingsDict, key, value):
        settingsDict[key] = value
        if settingsDict is USERPREF.STYLE:
            MainWidget.mainSC.redrawStyleSignal.emit()
        if settingsDict is USERPREF.CALCULATION:
            MainWidget.mainSC.recalcSignal.emit()


def main():
    lApplication = QApplication(sys.argv)
    lMainWidget = MainWidget()
    lMainWidget.show()
    sys.exit(lApplication.exec())


if __name__ == "__main__":
    main()