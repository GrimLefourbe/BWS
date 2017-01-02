import BWS
import sys
from PyQt5 import QtGui as Gui, QtWidgets as Widg, QtCore as Core
import os
import logging
import threading
import queue
import ReaderThread
import Weidu

class BWS_GUI:
    def __init__(self, app=None, PicDir = None):
        if app is not None:
            self.app = app
        self.BWS = BWS.BWS(no_gui=False)
        self.weidu = self.BWS.weidu

        self.dir = self.BWS.dir
        if PicDir is None:
            self.PicDir = self.dir + '/Pics'
        else:
            self.PicDir = PicDir
        self.config = self.BWS.config
        MWindow = self.MWindow =  Widg.QMainWindow()
        self.height = 600
        self.width = 600


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
        self.BWS.LoadModsComponents(inifile=selectedpath.rsplit('/', 1)[0] + '/WeiDU-EN.ini')
        self.IniSelect.hide()
        Comps = [(M['Name'], [(i[1], i[0], 32) for i in M['Comp']], M['ID']) for M in self.BWS.ModsData if 'Comp' in M]
        print(Comps)
        self.ModSelect.load(Comps=Comps)
        self.ModSelect.show()
        self.ModSelect.resize(self.width, self.height)
        self.MWindowCtr.resize(self.width, self.height)
        self.MWindow.resize(self.width, self.height)

    def OnModSelect(self, selectedmods):
        self.selectedmods = selectedmods
        self.IDtorowIndex = self.BWS.Indexes()

        WorkingSelection = []
        for ID, comps in selectedmods:
            chosencomps = [i for i in comps if i[1] == 2]
            if len(chosencomps) == 0:
                continue
            WorkingSelection.append((self.IDtorowIndex[ID], ID, chosencomps))

        self.SelectedMods = WorkingSelection
        logging.info("Selection : {}".format(WorkingSelection))
        self.ModSelect.hide()

        self.ProgressRep = ProgressReport(parent=self.MWindowCtr)
        self.ProgressRep.load([("Downloading {}".format(i[1]),) for i in WorkingSelection])
        logging.info("ProgressRep loaded with downloads")
        self.ProgressRep.show()
        self.ProgressRep.resize(self.width, self.height)

        logging.info("Starting creation of rephooks")

        def rephookfactory(func):
            def f(n):
                self.app.processEvents()
                func("{} kb".format(n/1000))
            return f

        rephooks = [rephookfactory(f) for f in self.ProgressRep.tasks]

        logging.info("Done creating rephooks")
        Downloaded = self.BWS.DownloadMods([i[0] for i in WorkingSelection], reporthooks=rephooks)

        self.DownloadedMods = WorkingSelection = [i for i, v in zip(WorkingSelection, Downloaded) if v == 1]
        self.ProgressRep.load([("Extracting {}".format(i[1]),) for i in WorkingSelection])
        taskstextfunc = self.ProgressRep.tasks
        logging.info("Starting preparation")
        q=queue.Queue()
        t = threading.Thread(target=self.BWS.PrepMods, args=([i[0] for i in WorkingSelection],), kwargs={"queue": q})
        t.start()


        res = []
        logging.info("Waiting for preparation")
        for i in range(len(WorkingSelection)):
            while True:
                try:
                    res.append(q.get(block=False))
                except queue.Empty:
                    self.app.processEvents()
                else:
                    taskstextfunc[i + len(self.SelectedMods)]("Done")
                    print(res[-1])
                    break
        logging.info("Setting new tasks for install")
        self.ExtractedMods = WorkingSelection = [i for i, v in zip(WorkingSelection, res) if v[0] == 1]
        self.ProgressRep.load([("Installing {}".format(i[1]),) for i in WorkingSelection])
        self.ProgressRep.toggleInOut()
        taskstextfunc = self.ProgressRep.tasks

        for i in range(len(WorkingSelection)):
            taskstextfunc[i+len(self.SelectedMods)+len(self.DownloadedMods)]("In progress")

        ToInst = [(ind, [i[0] for i in comps]) for ind, name, comps in WorkingSelection]
        logging.info("ToInst : {}".format(ToInst))
        logging.info("Creating thread")
        t = threading.Thread(target=self.BWS.InstallMods, kwargs={"ToInst": ToInst, "queue": q})
        t.start()

        logging.info("Thread started")
        inp = self.ProgressRep.inp
        out = self.ProgressRep.out
        TReader = q.get()
        self.ProgressRep.setOutStream(TReader)
        stdin = q.get()
        stdinstream = open(stdin, 'wb')
        self.ProgressRep.setInStream(stdinstream)
        res = []
        for i in range(len(WorkingSelection)):
            while True:
                try:
                    res.append(q.get(block=False))
                except queue.Empty:
                    try:
                        self.app.processEvents()
                    #logging.info("In stock : {}".format(TReader.instock()))
                        if TReader.instock():
                            self.ProgressRep.onOutAvailable()
                    except:
                        logging.exception("!")
                        sys.exit(1)
                else:
                    logging.debug("Got a popen item")
                    logging.info("Updating old task")
                    if i > 0:
                        taskstextfunc[len(self.SelectedMods)+len(self.DownloadedMods)+i-1]("Done!")
                    w = res[-1]
                    break
        while res[-1].poll() is None:
            self.app.processEvents()
            if TReader.instock():
                self.ProgressRep.onOutAvailable()
        taskstextfunc[-1]("Done!")


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
        out = self.out = Widg.QPlainTextEdit(parent=self)
        inp = self.inp = Widg.QLineEdit(parent=self)
        inbtn = self.inbtn = Widg.QPushButton(parent=self)
        inbtn.setText("Send")
        inbtn.clicked.connect(self.onClick)
        table.setWindowTitle("On-going tasks")
        self.tasks = []
        self.ccount = colcount + 1 #last column is for progress report
        self.rcount = 0

        if tasks is not None:
            self.load(tasks=tasks)

        out.hide()
        inp.hide()
        inbtn.hide()
        self.grid.addWidget(table, 0, 0, 1, 5)
        self.grid.addWidget(out, 1, 0, 1, 5)
        self.grid.addWidget(inp, 2, 0, 1, 4)
        self.grid.addWidget(inbtn, 2, 4, 1, 1)
        self.grid.setSpacing(10)
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
        self.rcount = table.rowCount()

    def setOutStream(self, stream):
        self.OutStream = stream
    def setInStream(self, stream):
        self.InStream = stream

    def onOutAvailable(self):
        s = self.OutStream.read().decode()
        logging.info("Read from stream : {}".format(s))
        try:
            self.out.appendPlainText(s)
        except:
            logging.exception('!')
            sys.exit(1)

    def onClick(self):
        self.InStream.write(self.inp.text().encode())
        self.InStream.flush()

    def toggleInOut(self):
        if self.out.isHidden():
            self.out.show()
            self.inp.show()
            self.inbtn.show()
        else:
            self.out.hide()
            self.inp.hide()
            self.inbtn.hide()

class Starter(Core.QObject):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.f = func
        self.args = args
        self.kwargs = kwargs
    @Core.pyqtSlot()
    def run(self, some_string_arg):
        self.f(*self.args, **self.kwargs)

class GenericWorker(Core.QObject):

    start = Core.pyqtSignal(str)
    finished = Core.pyqtSignal()

    def __init__(self, function, *args, **kwargs):
        super(GenericWorker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.start.connect(self.run)

    @Core.pyqtSlot()
    def run(self, *args, **kwargs):
        self.function(*self.args, **self.kwargs)
        self.finished.emit()