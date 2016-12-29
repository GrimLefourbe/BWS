import BWS
import sys
from PyQt5 import QtGui as Gui, QtWidgets as Widg
import os

class BWS_GUI(Widg.QWidget):
    def __init__(self, app=None, PicDir = None):
        super().__init__()
        if app is not None:
            self.app = app
        self.BWS = BWS.BWS(no_gui=False)

        self.dir = self.BWS.dir
        if PicDir is None:
            self.PicDir = self.dir + '/Pics'
        else:
            self.PicDir = PicDir
        self.config = self.BWS.config

        self.setWindowTitle("Big World Setup")
        self.setWindowIcon(Gui.QIcon(self.PicDir+'/BWS.ico'))
        self.show()

        self.IniSelect = IniSelect(parent=self, prefix="ModList-", function=self.OnGameSelect)

        app.exec_()

    def OnGameSelect(self, selectedpath):
        print(selectedpath)
        self.BWS.LoadModsData(inifile=selectedpath)


    def closeEvent(self, event):
        reply = Widg.QMessageBox.question(self, 'Message', "Wait a sec, you sure?", Widg.QMessageBox.Yes | Widg.QMessageBox.No, Widg.QMessageBox.No)

        if reply == Widg.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class IniSelect(Widg.QWidget):
    def __init__(self, function=None, prefix='', parent=None, config=None):
        super().__init__(parent=parent)
        if config is None:
            self.config = self.parent().config
        self.function = function
        self.prefix=prefix

        self.grid = Widg.QGridLayout()
        self.grid.setSpacing(10)

        self.ComboBox = Widg.QComboBox(self)
        self.ConfirmButton = Widg.QPushButton("Let's go!", self)

        offset = len(prefix)
        list = [i[offset:] for i in os.listdir(self.config) if i.startswith(prefix)]
        for i in list:
            self.ComboBox.addItem(i)

        self.ComboBox.activated[str].connect(self.onActivated)
        if function is not None:
            self.ConfirmButton.clicked.connect(self.onConfirm)

        self.lbl = Widg.QLabel(list[0], self)
        self.grid.addWidget(self.ComboBox)
        self.grid.addWidget(self.ConfirmButton, 0 , 1)
        self.grid.addWidget(self.lbl)


        self.setLayout(self.grid)
        self.setWindowTitle('ComboBox!')
        self.show()
    def onConfirm(self):
        self.function(self.config + '/' + self.prefix + self.ComboBox.currentText())

    def onActivated(self, text):
        self.lbl.setText(text)
        self.lbl.adjustSize()
