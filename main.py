import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic


class PREF:
    VERSION = "0.3a"
    INP_NUM = 2
    OUT_LEN = 7
    DBG_UI_PATH = "design.ui"


#def btnOper(func):
    #def wrapper(self):
        #try:
            #lRes = str(func(*map(lambda x: float(x.text()), self.inputs)))[:PREF.OUT_LEN]
            #self.output.setDigitCount(lRes)
            #self.output.display(lRes)
        #except Exception as e:
            #self.handleError(e)
    #return wrapper


class MainWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(PREF.DBG_UI_PATH, self)
        self.postInit()
    
    def postInit(self):
        self.curExpr = ""
        self.curNumber = ""
        
        self.setWindowTitle("Abel Calculator v{}".format(PREF.VERSION))
        
        self.actionExit.triggered.connect(lambda: sys.exit(0))
        
        def genInpBtn(text, x, y, name="", *args):
            lBtn = QPushButton(name if name else text, self)
            lBtn.clicked.connect(lambda: self.processInput(text))
            lBtn.setMinimumSize(32, 32)
            self.GLayoutKbd.addWidget(lBtn, x, y, *args)
            return lBtn
        
        def genActBtn(text, action, x, y, *args):
            lBtn = QPushButton(text, self)
            lBtn.clicked.connect(action)
            lBtn.setMinimumSize(32, 32)
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
        lEq.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        
    
    def handleError(self, err):
        QErrorMessage.qtHandler().showMessage(repr(err))
    
    def processInput(self, value):
        self.curExpr += value
        if value in ".0123456789":
            self.curNumber += value
        else:
            self.curNumber = ""
        self.setOutput(self.curNumber)
    
    def setOutput(self, value):
        self.output.setDigitCount(len(value))
        self.output.display(value)
    
    def clear(self):
        pass
    
    def backspace(self):
        pass
    
    def calculate(self):
        pass


def main():
    lApplication = QApplication(sys.argv)
    lMainWidget = MainWidget()
    lMainWidget.show()
    sys.exit(lApplication.exec())


if __name__ == "__main__":
    main()