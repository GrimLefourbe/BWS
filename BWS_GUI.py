import BWS
import sys
from PyQt5 import QtGui as Gui, QtWidgets as Widg, QtCore as Core
import os
import logging

class BWS_GUI:
    def __init__(self, app=None, PicDir = None):
        if app is not None:
            self.app = app
        self.BWS = BWS.BWS(no_gui=False)

        self.dir = self.BWS.dir
        if PicDir is None:
            self.PicDir = self.dir + '/Pics'
        else:
            self.PicDir = PicDir
        self.config = self.BWS.config
        MWindow = self.MWindow =  Widg.QMainWindow()


        MWindow.setWindowTitle("Big World Setup")
        MWindow.setWindowIcon(Gui.QIcon(self.PicDir+'/BWS.ico'))
        MWindow.setCentralWidget(Widg.QWidget(MWindow))
        MWindowCtr = self.MWindowCtr = MWindow.centralWidget()


        self.IniSelect = IniSelect(parent=MWindowCtr, prefix="ModList-", function=self.OnGameSelect, config=self.config)
        self.ModSelect = ModSelect(parent=MWindowCtr, NextFunction=self.OnModSelect)
        self.ModSelect.hide()
        MWindow.show()
        app.exec_()

    def OnGameSelect(self, selectedpath):
        self.selectedpath = selectedpath
        print(selectedpath)
        self.BWS.LoadModsData(inifile=selectedpath)
        self.BWS.LoadModsComponents(inifile=selectedpath.rsplit('/', 1)[0] + '/WeiDu-EN.ini')
        self.IniSelect.hide()
        Comps = [(M['Name'], [(i[1], i[0], 32) for i in M['Comp']], M['ID']) for M in self.BWS.ModsData if 'Comp' in M]
        print(Comps)
        self.ModSelect.load(Comps=Comps)
        self.ModSelect.show()
        self.ModSelect.resize(400, 400)
        self.MWindowCtr.resize(400, 400)
        self.MWindow.resize(400, 400)

    def OnModSelect(self, selectedmods):
        self.selectedmods = selectedmods
        selection = []
        for ID, comps in selectedmods:
            chosencomps = [i for i in comps if i[1] == 2]
            if len(chosencomps) == 0:
                continue
            selection.append((ID, chosencomps))
        logging.info("Selection : {}".format(selection))
        self.ModSelect.hide()

        self.ProgressRep = ProgressReport(parent=self.MWindowCtr)
        self.ProgressRep.load([("Downloading {}".format(i[0]),) for i in selection] + [("Extracting {}".format(i[0]),) for i in selection])
        logging.info("ProgressRep loaded")
        self.ProgressRep.show()
        self.ProgressRep.resize(400,400)

        taskstextfunc = self.ProgressRep.tasks
        rephooks = []
        logging.info("Starting creation of rephooks")
        for func in taskstextfunc[:len(selection)]:
            def f(n):
                print(n)
                func("test")
            rephooks.append(f)
        logging.info("Done creating rephooks")

        self.IDtorowIndex = self.BWS.Indexes()

        #self.BWS.DownloadMods([self.IDtorowIndex[i[0]] for i in selection],reporthooks=rephooks)


    def closeEvent(self, event):
        reply = Widg.QMessageBox.question(self, 'Message', "Wait a sec, you sure?", Widg.QMessageBox.Yes | Widg.QMessageBox.No, Widg.QMessageBox.No)

        if reply == Widg.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class IniSelect(Widg.QWidget):
    def __init__(self, function=None, prefix='', parent=None, config=None):
        super().__init__(parent=parent)
        self.grid = Widg.QGridLayout()
        self.grid.setSpacing(10)

        self.ComboBox = Widg.QComboBox(parent=self)
        self.ConfirmButton = Widg.QPushButton("Let's go!", parent=self)
        self.lbl = Widg.QLabel(parent=self)

        self.ComboBox.activated[str].connect(self.onActivated)

        self.grid.addWidget(self.ComboBox)
        self.grid.addWidget(self.ConfirmButton, 0 , 1)
        self.grid.addWidget(self.lbl)

        self.setLayout(self.grid)
        self.setWindowTitle('ComboBox!')
        self.show()

        self.load(function=function, prefix=prefix, config=config)
    def load(self, function=None, prefix='', config=None):
        if config is None:
            self.config = self.parent().config
        else:
            self.config = config

        self.function = function
        self.prefix = prefix

        self.ComboBox.clear()
        offset = len(prefix)
        list = [i[offset:] for i in os.listdir(self.config) if i.startswith(prefix)]
        for i in list:
            self.ComboBox.addItem(i)

        if function is not None:
            self.ConfirmButton.clicked.connect(self.onConfirm)

        self.lbl.setText(list[0])

    def onConfirm(self):
        self.function(self.config + '/' + self.prefix + self.ComboBox.currentText())

    def onActivated(self, text):
        self.lbl.setText(text)
        self.lbl.adjustSize()

class ModSelect(Widg.QWidget):
    def __init__(self, parent=None, Comps=None, NextFunction=None):
        """
        Comps indicates the items to load into the tree
        :param parent:
        :param Comps:
        """
        super().__init__(parent=parent)
        self.Tree = Widg.QTreeWidget(parent=self)
        self.grid = Widg.QGridLayout()
        self.NxtFnc = NextFunction
        self.NxtBtn=Widg.QPushButton("Next!",parent=self)

        self.NxtBtn.clicked.connect(self.onNxtClick)
        self.grid.addWidget(self.Tree, 0, 0, 1, 2)
        self.grid.addWidget(self.NxtBtn, 1, 1)
        self.setLayout(self.grid)
        if Comps is not None:
            self.load(Comps=Comps)

    def load(self, Comps, NextFunction=None):
        tree = self.Tree
        for ptext, childinfo, pdata in Comps:
            parent = Widg.QTreeWidgetItem(tree)
            parent.setText(0, "{}".format(ptext))
            parent.setData(0, 32, pdata)
            parent.setFlags(parent.flags() | Core.Qt.ItemIsTristate | Core.Qt.ItemIsUserCheckable)
            for text, data, datatype in childinfo:
                child = Widg.QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Core.Qt.ItemIsTristate | Core.Qt.ItemIsUserCheckable)
                child.setText(0, "{}".format(text))
                child.setData(0, 32, data)
                child.setCheckState(0, Core.Qt.Unchecked)
        tree.setSortingEnabled(1)
        tree.sortByColumn(0, Core.Qt.AscendingOrder)
        tree.show()
    def get_state(self, root=None):
        if root is None:
            root = self.Tree.invisibleRootItem()
        node_count = root.childCount()
        if node_count == 0:
            return root.data(0, 32), root.checkState(0)
        return root.data(0, 32), [self.get_state(root.child(i)) for i in range(node_count)]
    def onNxtClick(self):
        n=self.get_state()
        self.NxtFnc(n[1])

class ProgressReport(Widg.QWidget):
    def __init__(self, tasks=None, parent=None, colcount=1):
        super().__init__(parent)
        self.grid = Widg.QGridLayout()
        table = self.table = Widg.QTableWidget(parent=self)
        table.setWindowTitle("On-going tasks")
        self.tasks = []
        self.ccount = colcount + 1 #last column is for progress report
        self.rcount = 0

        if tasks is not None:
            self.load(tasks=tasks)

        self.grid.addWidget(table)
        self.setLayout(self.grid)
        table.show()

    def load(self, tasks):
        logging.info("tasks : {}".format(tasks))
        table = self.table
        table.setColumnCount(self.ccount)
        table.setRowCount(self.rcount + len(tasks))
        for row, task in enumerate(tasks):
            for col, text in enumerate(task):
                table.setItem(row + self.rcount, col, Widg.QTableWidgetItem(text))
            item = Widg.QTableWidgetItem("0")
            self.tasks.append(item.setText)
            table.setItem(row + self.rcount, self.ccount-1, item)
        table.show()
