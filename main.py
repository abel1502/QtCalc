import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
from copy import deepcopy


class PREF:
    VERSION = "0.5"
    NAME = "Abel Calculator v{}".format(VERSION)
    INP_NUM = 2
    OUT_LEN = 7
    DBG_UI_PATH = "design.ui"
    INP_BTN_STYLE = ""
    ACT_BTN_STYLE = ""
    VAR_COUNT = 10
    VAR_LABEL = "<{}>={}"
    ABOUT = "Abel Calculator is a small app made by\nAndrew Belyaev (Russia, Moscow, School 179)\nas a scholar micro-project.\n\nThis project is hosted on GitHub at\nhttps://github.com/abel1502/QtCalc"


class MainWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(PREF.DBG_UI_PATH, self)
        self.postInit()
    
    def postInit(self):
        self.curExpr = []
        self.variables = ["0" for _ in range(PREF.VAR_COUNT)]
        
        self.setWindowTitle(PREF.NAME)
        
        self.actionExit.triggered.connect(lambda: sys.exit(0))
        self.actionAbout.triggered.connect(lambda: QMessageBox.about(self, "About " + PREF.NAME, PREF.ABOUT))
        
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
        
        self.GLayoutKbd.setHorizontalSpacing(6)
        self.GLayoutKbd.setVerticalSpacing(6)
        
        def genInpBtn(text, x, y, name="", *args):
            lBtn = QPushButton(name if name else text, self)
            lBtn.clicked.connect(lambda: self.processInput(text))
            lBtn.setMinimumSize(32, 32)
            lBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            lBtn.setStyleSheet(PREF.INP_BTN_STYLE)
            self.GLayoutKbd.addWidget(lBtn, x, y, *args)
            return lBtn
        
        def genActBtn(text, action, x, y, *args):
            lBtn = QPushButton(text, self)
            lBtn.clicked.connect(action)
            lBtn.setMinimumSize(32, 32)
            lBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            lBtn.setStyleSheet(PREF.ACT_BTN_STYLE)
            self.GLayoutKbd.addWidget(lBtn, x, y, *args)
            return lBtn
        
        genInpBtn("1", 0, 0)
        genInpBtn("2", 0, 1)
        genInpBtn("3", 0, 2)
        genInpBtn("4", 1, 0)
        genInpBtn("5", 1, 1)
        genInpBtn("6", 1, 2)
        genInpBtn("7", 2, 0)
        genInpBtn("8", 2, 1)
        genInpBtn("9", 2, 2)
        genActBtn("C", self.clear, 3, 0)
        genInpBtn("0", 3, 1)
        genInpBtn(".", 3, 2)
        
        genInpBtn("/", 0, 3)
        genInpBtn("*", 1, 3)
        genInpBtn("-", 2, 3)
        genInpBtn("+", 3, 3)
        
        genInpBtn("//", 0, 4)
        genInpBtn("%", 1, 4)
        genInpBtn("(", 2, 4)
        genInpBtn(")", 3, 4)
        
        genActBtn("<-", self.backspace, 0, 5)
        genActBtn("=", self.calculate, 2, 5, 2, 1)
    
    def event(self, event):
        if (event.type() == 51) and (event.key() == Qt.Key_Backspace):
            self.backspace()
            return True
        return super().event(event)
    
    def keyPressEvent(self, event):
        if event.text() in "01234567890*/+-%()":
            self.processInput(event.text())
        if event.text() in "\r=":
            self.calculate()
        #print(repr(event.text()), event.key())
        super().keyPressEvent(event)
    
    def handleError(self, err):
        QErrorMessage.qtHandler().showMessage(repr(err))
    
    def updateVarNames(self):
        for i in range(PREF.VAR_COUNT):
            self.saveVarAction[i].setText(PREF.VAR_LABEL.format(i, self.variables[i]))
            self.loadVarAction[i].setText(PREF.VAR_LABEL.format(i, self.variables[i]))
    
    def saveVar(self, varId):
        if len(self.output.text()) == 0:
            value = "0"
        else:
            if "=" not in self.output.text():
                return
            value = self.output.text().split("=")[-1]
        self.variables[varId] = value
        #print(value, varId)
        sys.stdout.flush()
        self.updateVarNames
        self.saveVarAction[varId].setText(PREF.VAR_LABEL.format(varId, value))
        self.loadVarAction[varId].setText(PREF.VAR_LABEL.format(varId, value))
    
    def loadVar(self, varId):
        value = self.variables[varId]
        self.curExpr.extend(list(value))
        self.setOutput()
    
    def processInput(self, value):
        self.curExpr.append(value)
        self.setOutput()
    
    def setOutput(self, value=None):
        if value == None:
            value = ''.join(self.curExpr)
        self.output.setText(value)
    
    def clear(self):
        self.curExpr = []
        self.setOutput('')
    
    def backspace(self):
        if self.curExpr:
            self.curExpr.pop()
        self.setOutput()
    
    def calculate(self):
        try:
            lExpr = ''.join(self.curExpr)
            lExpr = lExpr if lExpr else "0"
            value = eval(lExpr)
            self.setOutput("{}={}".format(lExpr, str(value)))
        except Exception as e:
            self.handleError(e)


def main():
    lApplication = QApplication(sys.argv)
    lMainWidget = MainWidget()
    lMainWidget.show()
    sys.exit(lApplication.exec())


if __name__ == "__main__":
    main()