import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic


class PREF:
    VERSION = "0.3a"
    INP_NUM = 2
    OUT_LEN = 7
    DBG_UI_PATH = "design.ui"
    INP_BTN_STYLE = ""
    ACT_BTN_STYLE = ""
    VAR_COUNT = 10


class MainWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(PREF.DBG_UI_PATH, self)
        self.postInit()
    
    def postInit(self):
        self.curExpr = []
        self.variables = ["0" for _ in range(PREF.VAR_COUNT)]
        
        self.setWindowTitle("Abel Calculator v{}".format(PREF.VERSION))
        
        self.actionExit.triggered.connect(lambda: sys.exit(0))
        self.actionSaveVariable.triggered.connect(self.saveVar)
        self.actionLoadVariable.triggered.connect(self.loadVar)
        
        def genInpBtn(text, x, y, name="", *args):
            lBtn = QPushButton(name if name else text, self)
            lBtn.clicked.connect(lambda: self.processInput(text))
            lBtn.setMinimumSize(32, 32)
            lBtn.setStyleSheet(PREF.INP_BTN_STYLE)
            self.GLayoutKbd.addWidget(lBtn, x, y, *args)
            return lBtn
        
        def genActBtn(text, action, x, y, *args):
            lBtn = QPushButton(text, self)
            lBtn.clicked.connect(action)
            lBtn.setMinimumSize(32, 32)
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
        	
        lEq = genActBtn("=", self.calculate, 2, 5, 2, 1)
        lEq.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        
    
    def handleError(self, err):
        QErrorMessage.qtHandler().showMessage(repr(err))
    
    def saveVar(self):
        if "=" not in self.output.text():
            return
        value = self.output.text().split("=")[-1]
        varId = QInputDialog.getInt(self, "Select Variable", "In which slot to save the value?", 0, 0, PREF.VAR_COUNT)
        self.variables[varId] = value
        self.curExpr.extend(list(value))
        self.setOutput()
    
    def loadVar(self):
        varId = QInputDialog.getInt(self, "Select Variable", "From which slot to load the value?", 0, 0, PREF.VAR_COUNT)
        value = self.variables[varId]
        # TODO
    
    def processInput(self, value):
        self.curExpr.append(value)
        self.setOutput()
    
    def setOutput(self, value=None):
        if value == None:
            value = ''.join(self.curExpr)
            #value = value if value else "0"
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