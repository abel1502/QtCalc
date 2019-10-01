import sys
from PyQt5.QtWidgets import *


class PREF:
    VERSION = "0.2a"
    INP_NUM = 2


def btnOper(func):
    def wrapper(self):
        try:
            lRes = func(*map(lambda x: int(x.text()), self.inputs))
            self.output.display(str(lRes)[:PREF.OUT_LEN])
        except Exception as e:
            self.handleError(e)
    return wrapper


class MainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()
    
    def initUI(self):
        # ===[   Window Setup   ]===
        self.resize(*(PREF.WINDOW_SIZE))
        self.setWindowTitle("Abel Calculator v{}".format(PREF.VERSION))
        
        # ===[   Widgets Setup   ]===
        def _genBtn(name, op):
            lBtn = QPushButton(op, self)
            lBtn.clicked.connect(getattr(self, "do_{}".format(name)))
            return lBtn
        addBtn = _genBtn("add", "+")
        subBtn = _genBtn("sub", "-")
        mulBtn = _genBtn("mul", "*")
        divBtn = _genBtn("div", "/")
        modBtn = _genBtn("mod", "%")
        idivBtn = _genBtn("idiv", "//")
        
        self.output = QLCDNumber(self)
        self.output.setMaximumHeight(46)
        
        # ===[   Layouts Setup   ]===
        VLayoutGeneral = QVBoxLayout(self)
        HLayoutIO = QHBoxLayout(self)
        VLayoutInputs = QVBoxLayout(self)
        GLayoutButtons = QGridLayout(self)
        
        GLayoutButtons.addWidget(addBtn, 0, 0)
        GLayoutButtons.addWidget(subBtn, 0, 1)
        GLayoutButtons.addWidget(mulBtn, 1, 0)
        GLayoutButtons.addWidget(divBtn, 1, 1)
        GLayoutButtons.addWidget(modBtn, 2, 0)
        GLayoutButtons.addWidget(idivBtn, 2, 1)
        
        self.inputs = []
        for i in range(PREF.INP_NUM):
            lInput = QLineEdit(self)
            self.inputs.append(lInput)
            VLayoutInputs.addWidget(lInput)
        
        HLayoutIO.addLayout(VLayoutInputs, 1)
        HLayoutIO.addWidget(self.output, 5)
        
        VLayoutGeneral.addLayout(HLayoutIO, 0)
        VLayoutGeneral.addLayout(GLayoutButtons, 1)
        
        self.setLayout(VLayoutGeneral)
        # ===[   End   ]===
    
    def handleError(self, err):
        QErrorMessage.qtHandler().showMessage(repr(err))
    
    @btnOper
    def do_add(a, b):
        return a + b
    
    @btnOper
    def do_sub(a, b):
        return a - b
    
    @btnOper
    def do_mul(a, b):
        return a * b
    
    @btnOper
    def do_div(a, b):
        return a / b
    
    @btnOper
    def do_mod(a, b):
        return a % b
    
    @btnOper
    def do_idiv(a, b):
        return a // b


def main():
    lApplication = QApplication(sys.argv)
    lMainWidget = MainWidget()
    lMainWidget.show()
    sys.exit(lApplication.exec())


if __name__ == "__main__":
    main()