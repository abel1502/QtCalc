import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, \
                            QLCDNumber, QLabel


class PREF:
    VERSION = "0.1a"
    WINDOW_SIZE = (256, 256)
    BTN_GRID_POS = (8, 128)
    BTN_SIZE = (64, 32)
    BTN_SEP = (4, 4)
    INP_GRID_POS = (8, 8)
    INP_NUM = 2
    INP_SIZE = (96, 32)
    INP_SEP = 8
    OUT_POS = (8 + 96 + 16, 8 + 4)
    OUT_SIZE = (128, 64)
    OUT_LEN = 5
    ERR_POS = (4, 128 + 36 * 2 + 4)


def binOper(func):
    def wrapper(self):
        try:
            lA, lB = map(lambda x: int(x.text()), self.inputs)
            lRes = func(lA, lB)
            self.output.display(str(lRes)[:PREF.OUT_LEN])
        except Exception as e:
            self.handleError(e)
    return wrapper


class MainWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()
    
    def initUI(self):
        self.resize(*(PREF.WINDOW_SIZE))
        self.setWindowTitle("Abel Calculator v{}".format(PREF.VERSION))
        
        self.errMsg = QLabel(self)
        self.errMsg.setText("")
        self.errMsg.move(*(PREF.ERR_POS))
        
        self.output = QLCDNumber(self)
        self.output.resize(*(PREF.OUT_SIZE))
        self.output.move(*(PREF.OUT_POS))
        
        self.inputs = [QLineEdit(self) for _ in range(PREF.INP_NUM)]
        for i, lInp in enumerate(self.inputs):
            lInp.resize(*(PREF.INP_SIZE))
            lInp.move(PREF.INP_GRID_POS[0],
                      PREF.INP_GRID_POS[1] + (PREF.INP_SIZE[1] + PREF.INP_SEP) * i)
        
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
        
        self.btnGrid = [[addBtn, subBtn, modBtn], [mulBtn, divBtn, idivBtn]]
        for y, lRow in enumerate(self.btnGrid):
            for x, lBtn in enumerate(lRow):
                lBtn.resize(*(PREF.BTN_SIZE))
                lBtn.move(PREF.BTN_GRID_POS[0] + (PREF.BTN_SIZE[0] + PREF.BTN_SEP[0]) * x,
                          PREF.BTN_GRID_POS[1] + (PREF.BTN_SIZE[1] + PREF.BTN_SEP[1]) * y)
    
    def handleError(self, err):
        self.errMsg.setText(repr(err))
        self.errMsg.adjustSize()
    
    @binOper
    def do_add(a, b):
        return a + b
    
    @binOper
    def do_sub(a, b):
        return a - b
    
    @binOper
    def do_mul(a, b):
        return a * b
    
    @binOper
    def do_div(a, b):
        return a / b
    
    @binOper
    def do_mod(a, b):
        return a % b
    
    @binOper
    def do_idiv(a, b):
        return a // b


def main():
    lApplication = QApplication(sys.argv)
    lMainWidget = MainWidget()
    lMainWidget.show()
    sys.exit(lApplication.exec())


if __name__ == "__main__":
    main()