import configparser
import sys

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QWidget, QAction, QMainWindow, QFileDialog, QLineEdit)
from win32api import GetSystemMetrics

parser = configparser.ConfigParser()

path = []
folder = []


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
            try:
                parser.add_section('machine_learning')
                parser.set('machine_learning', 'h5', path[0])
                parser.set('machine_learning', 'weight', path[1])
                parser.add_section('folder_protect')
                parser.set('folder_protect', 'folder', folder[0])
            except:
                pass

            with open(self.conf_file, 'w') as configfile:
                parser.write(configfile)
                configfile.close()




class App(QMainWindow, QWidget):

    def __init__(self):
        super().__init__()
        Left = GetSystemMetrics(0)
        Top = GetSystemMetrics(1)
        Width = 600
        Height = 300
        self.title = 'MyDlPy'
        self.left = (Left / 2) - (Width / 2)
        self.top = (Top / 2) - (Height / 2)
        self.width = Width
        self.height = Height
        self.initUI()

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
        editAcess.triggered.connect(self.openFileNameDialog)
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
        self.h5line = QLineEdit(self)
        self.weightLine = QLineEdit(self)
        self.folderLine = QLineEdit(self)

        self.h5line.move(80, 20)
        self.h5line.resize(400, 32)
        self.weightLine.move(80, 60)
        self.weightLine.resize(400, 32)
        self.folderLine.move(80, 100)
        self.folderLine.resize(400, 32)
        self.h5Label.move(20, 20)
        self.weightLabel.move(20, 60)
        self.folderLabel.move(20, 100)


        button = QPushButton('Validate!', self)
        button.setToolTip('Validate the H5 and Weight model')
        button.move(200, 150)
        button.clicked.connect(Config)
        button.clicked.connect(self.on_click)

        self.show()

    @pyqtSlot()
    def on_click(self):
        try:
            parser.read('testong.ini')
            self.h5line.setText(parser.get('machine_learning', 'h5'))
            self.weightLine.setText(parser.get('machine_learning', 'weight'))
            self.folderLine.setText(parser.get('folder_protect', 'folder'))
        except:
            pass

    def openFolderDialog(self):
        folderName = QFileDialog.getExistingDirectory(self, "Select your folder","C:\\",  QFileDialog.ShowDirsOnly)
        folder.insert(0, folderName)
        print(folder[0])
        print("1")

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select your model", "",
                                                  "All Files (*);;h5 Files (*.h5);;json Files (*.json)",
                                                  options=options)
        print(fileName)
        if ".h5" in fileName:
            path.insert(0, fileName)
            print(path[0])
        elif ".json" in fileName:
            path.insert(1, fileName)
            print(path[1])
        else:
            print("unrecognizeable")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())