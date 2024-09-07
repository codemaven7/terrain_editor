



from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QFileDialog, QApplication)
from PyQt5.QtGui import QIcon

import sys

class Primary(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.statusBar()

        openFile = QAction(QIcon('replace_this.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open Rom File')
        openFile.triggered.connect(self.showOpenDialog)

        saveFile = QAction(QIcon('replace_this_also.png'), 'Save As', self)
        saveFile.setShortcut('Ctrl+S')  # this shortcut key combination can either be for SAVE or SAVE AS
        saveFile.setStatusTip('Save As New Rom File')
        saveFile.triggered.connect(self.showSaveDialog)



        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('File dialog')
        self.show()


    def showOpenDialog(self):

        fname = QFileDialog.getOpenFileName(self, 'Open File', '/', "ROM (*.sfc *.smc)")

        if fname[0]:


            with open(fname[0], 'r') as f:
                data = f.read()
                self.textEdit.setText(data)

            print("put some code here")


    def showSaveDialog(self):

        fname = QFileDialog.getSaveFileName(self, 'Save As File', '/', "SFC (*.sfc);;SMC (*.smc)")

        data = "bla bla bla"

        if fname[0]:
            with open(fname[0], 'w') as f:  # change to 'wb' later!!!

                f.write(data)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Primary()
    sys.exit(app.exec_())