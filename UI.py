import configparser
import sys
import os
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from win32api import GetSystemMetrics
import time
import predictor

parser = configparser.ConfigParser()

path = []
folder = []
pickle =[]

# class Stream(QtCore.QObject):
#     """Redirects console output to text widget."""
#     newText = QtCore.pyqtSignal(str)
#
#     def write(self, text):
#         self.newText.emit(str(text))
#
# class Debugger(QTextBrowser):
#     def __init__(self, parent):
#         super(Debugger, self).__init__(parent)
#         sys.stdout = self
#
#     def write(self, text):
#         self.moveCursor(QTextCursor.End)
#         self.textCursor().insertText(text)
#
# class MyStream(object):
#     def write(self, text):
#         self.moveCursor(QTextCursor.End)
#         self.textCursor().insertText(text)

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

class embterminal(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.process = QProcess(self)
        self.terminal = QWidget(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.terminal)

        # Works also with urxvt:
        self.process.start(
                'urxvt',['-embed', str(int(self.winId()))])
        print(self.winId())
        self.setGeometry(1, 1, 800, 600)

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
        # self.new_window = new_window()

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
        # os.system('python Predictor.py')
        # os.system('python watcher.py')
        # os.system('python test.py')
        self.new_window.show()

    def run_Csv(self):
        os.system('python runCsv.py')

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

class new_window(QMainWindow, QWidget):
    """Main application window."""

    def __init__(self):
        super(new_window, self).__init__()

        self.initUI()

        # Custom output stream.
        sys.stdout = Stream(newText=self.onUpdateText)

    def onUpdateText(self, text):
        """Write console output to text widget."""
        cursor = self.process.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def closeEvent(self, event):
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)

    def initUI(self):
        """Creates UI window on launch."""
        # Button for generating the master list.
        btnGenMast = QPushButton('Run', self)
        btnGenMast.move(450, 100)
        btnGenMast.resize(100, 100)
        btnGenMast.clicked.connect(self.genMastClicked)

        # Create the text output widget.
        self.process = QTextEdit(self, readOnly=True)
        self.process.ensureCursorVisible()
        self.process.setLineWrapColumnOrWidth(500)
        self.process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.process.setFixedWidth(400)
        self.process.setFixedHeight(150)
        self.process.move(30, 100)

        # Set window size and title, then show the window.
        self.setGeometry(300, 300, 600, 300)
        self.setWindowTitle('Generate Master')

    def genMastClicked(self):
        """Runs the main function."""
        mains = embterminal()
        mains.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
