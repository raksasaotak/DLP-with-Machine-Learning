import configparser
import sys
import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from win32api import GetSystemMetrics

parser = configparser.ConfigParser()

path = []
folder = []
pickle =[]

class Config():
    def __init__(self):
        self.conf_file = "testong.ini"
        self.found = parser.read(self.conf_file)
        try:
            parser.get('machine_learning', 'h5')
            parser.get('machine_learning', 'weight')
            parser.get('folder_protect', 'folder')
        except:
            print("one of them is empty")
        self.rw_config()

    def rw_config(self):
        if not self.found:
            parser.add_section('machine_learning')
            parser.add_section('folder_protect')
            parser.add_section('pickle_file')
            try:
                parser.set('machine_learning', 'h5', path[0])
                parser.set('machine_learning', 'weight', path[1])
                parser.set('pickle_file', 'pickle', pickle[0])
            except:
                pass
            try:
                parser.set('folder_protect', 'folder', folder[0])
            except:
                pass

            with open(self.conf_file, 'w') as configfile:
                parser.write(configfile)
        else:
            try:
                parser.set('folder_protect', 'folder', folder[0])
            except:
                pass
            try:
                parser.set('machine_learning', 'h5', path[0])
                parser.set('machine_learning', 'weight', path[1])
                parser.set('pickle_file', 'pickle', pickle[0])
            except:
                pass

            with open(self.conf_file, 'w') as configfile:
                parser.write(configfile)

class App(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()
        Left = GetSystemMetrics(0)
        Top = GetSystemMetrics(1)
        Width = 500
        Height = 300
        self.title = 'MyDLPy'
        self.left = (Left / 2) - (Width / 2)
        self.top = (Top / 2) - (Height / 2)
        self.width = Width
        self.height = Height
        self.initUI()
        self.gui = gui()
        self.watcher = watcher()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('asdas.png'))
        self.setGeometry(self.left, self.top, self.width, self.height)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        helpMenu = mainMenu.addMenu('Help')

        exitButton = QAction(QIcon('asdas.png'), 'Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        importH5 = QAction('Import model File', self)
        importH5.setShortcut('Ctrl+O')
        importH5.setStatusTip('Import your H5')
        importH5.triggered.connect(self.openFileNameDialog)
        fileMenu.addAction(importH5)

        editAcess = QAction('Edit File Access', self)
        editAcess.setShortcut('Ctrl+E')
        editAcess.setStatusTip('edit your file access')
        editAcess.triggered.connect(self.run_Csv)
        editMenu.addAction(editAcess)

        openFolder = QAction('Import protected folder', self)
        openFolder.setShortcut('Ctrl+F')
        openFolder.setStatusTip('Import your Folder')
        openFolder.triggered.connect(self.openFolderDialog)
        fileMenu.addAction(openFolder)

        self.h5Label = QLabel(self)
        self.h5Label.setText('H5:')
        self.weightLabel = QLabel(self)
        self.weightLabel.setText('Weight: ')
        self.folderLabel = QLabel(self)
        self.folderLabel.setText('Folder: ')
        self.pickleLabel = QLabel(self)
        self.pickleLabel.setText('Pickle: ')
        self.h5line = QLineEdit(self)
        self.weightLine = QLineEdit(self)
        self.folderLine = QLineEdit(self)
        self.pickleLine = QLineEdit(self)

        self.h5line.move(80, 20)
        self.h5line.resize(400, 32)
        self.weightLine.move(80, 60)
        self.weightLine.resize(400, 32)
        self.folderLine.move(80, 100)
        self.folderLine.resize(400, 32)
        self.pickleLine.move(80,140)
        self.pickleLine.resize(400,32)
        self.h5Label.move(20, 20)
        self.weightLabel.move(20, 60)
        self.folderLabel.move(20, 100)
        self.pickleLabel.move(20,140)


        button = QPushButton('Validate!', self)
        button.setToolTip('Validate the H5 and Weight model')
        button.move(200, 180)
        button.clicked.connect(Config)
        button.clicked.connect(self.on_click)

        button = QPushButton('Start!', self)
        button.setToolTip('Start your service')
        button.move(200, 220)
        button.clicked.connect(self.run_Service)

        self.show()

    @pyqtSlot()
    def run_Service(self):
        self.gui.show()
        self.watcher.show()
        # os.system('python Predictor.py')
        # os.system('python watcher.py')
        # os.system('python test.py')

    def run_Csv(self):
        os.system('python runCsv.py acl.csv')

    def on_click(self):
        parser.read('testong.ini')
        try:
            self.h5line.setText(parser.get('machine_learning', 'h5'))
            self.weightLine.setText(parser.get('machine_learning', 'weight'))
            self.pickleLine.setText(parser.get('pickle_file', 'pickle'))
        except:
            pass
        try:
            self.folderLine.setText(parser.get('folder_protect', 'folder'))
        except:
            pass

    def openFolderDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folderName = QFileDialog.getExistingDirectory(self, "Select your folder",".",
                                                      options=options)
        folder.insert(0, folderName)
        print(folder[0])

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select your model", "",
                                                  "All Files (*);;h5 Files (*.h5);;json Files (*.json);; pickle Files(*.pickle)",
                                                  options=options)
        print(fileName)
        if ".h5" in fileName:
            path.insert(0, fileName)
            print(path[0])
        elif ".json" in fileName:
            path.insert(1, fileName)
            print(path[1])
        elif ".pickle" in fileName:
            pickle.insert(0, fileName)
            print(pickle[0])
        else:
            print("unrecognizeable")

class gui(QtWidgets.QMainWindow):
    def __init__(self):
        super(gui, self).__init__()
        self.initUI()

    def dataReady(self):
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(str(self.process.readAll(), 'utf-8'))
        self.output.ensureCursorVisible()

    def callProgram(self):
        # run the process
        # `start` takes the exec and a list of arguments
        self.process.start('python',['predictor.py'])


    def initUI(self):
        # Layout are better for placing widgets
        self.setWindowTitle('Prediction Program')
        layout = QtWidgets.QHBoxLayout()
        self.runButton = QtWidgets.QPushButton('Run ML')
        self.runButton.clicked.connect(self.callProgram)

        self.output = QtWidgets.QTextEdit()

        layout.addWidget(self.output)
        layout.addWidget(self.runButton)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # QProcess object for external app
        self.process = QtCore.QProcess(self)
        # QProcess emits `readyRead` when there is data to be read
        self.process.readyRead.connect(self.dataReady)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(lambda: self.runButton.setEnabled(False))
        self.process.finished.connect(lambda: self.runButton.setEnabled(True))

class watcher(QtWidgets.QMainWindow):
    def __init__(self):
        super(watcher, self).__init__()
        self.initUI()

    def dataReady(self):
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(str(self.process.readAll(), 'utf-8'))
        self.output.ensureCursorVisible()

    def callProgram(self):
        # run the process
        # `start` takes the exec and a list of arguments
        self.process.start('python',['watcher.py'])

    def initUI(self):
        # Layout are better for placing widgets
        self.setWindowTitle('Watcher Program')
        layout = QtWidgets.QHBoxLayout()
        self.runButton = QtWidgets.QPushButton('Run Watcher')
        self.runButton.clicked.connect(self.callProgram)

        self.output = QtWidgets.QTextEdit()

        layout.addWidget(self.output)
        layout.addWidget(self.runButton)

        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # QProcess object for external app
        self.process = QtCore.QProcess(self)
        # QProcess emits `readyRead` when there is data to be read
        self.process.readyRead.connect(self.dataReady)

        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(lambda: self.runButton.setEnabled(False))
        self.process.finished.connect(lambda: self.runButton.setEnabled(True))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
