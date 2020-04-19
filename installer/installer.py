from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import os, sys, shutil
from zipfile import ZipFile
import getpass
import winshell
import time
from threading import Thread
import webbrowser
import requests


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1066, 821)
        MainWindow.setStyleSheet("background-color: rgb(255, 190, 144);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(850, 700, 171, 61))
        self.pushButton_2.setObjectName("pushButton_2")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(30, 230, 991, 31))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(120, 270, 891, 241))
        font = QtGui.QFont()
        font.setFamily("Viner Hand ITC")
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(380, 700, 181, 61))
        self.pushButton_4.setObjectName("pushButton_4")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 50, 981, 41))
        font = QtGui.QFont()
        font.setFamily("Viner Hand ITC")
        font.setPointSize(14)
        font.setItalic(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 120, 991, 31))
        font = QtGui.QFont()
        font.setFamily("Viner Hand ITC")
        font.setPointSize(14)
        font.setUnderline(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 580, 331, 181))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(610, 700, 181, 61))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1066, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Installer"))
        self.pushButton_2.setText(_translate("MainWindow", "Установить"))
        self.label_3.setText(_translate("MainWindow",
                                        "Спасибо за установку нашей игры! Вы можете открыть ее через ярлык на рабочем столе"))
        self.pushButton_4.setText(_translate("MainWindow", "Закрыть программу"))
        self.label.setText(_translate("MainWindow", "Вы открыли установщик игры COVIDcover."))
        self.label_2.setText(_translate("MainWindow", "Проерьте интернет соединение перед началом!!!"))
        self.plainTextEdit.setPlainText(_translate("MainWindow", "Error logs:\n"
                                                                 "OK\n"
                                                                 ""))
        self.pushButton.setText(_translate("MainWindow", "Открыть сайт"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


stop = False


def loading():
    global stop
    while ex.progressBar.value() != 100:
        ex.progressBar.setValue(ex.progressBar.value() + 1)
        time.sleep(0.15)
        if stop:
            break


class MyWidget(QMainWindow, Ui_MainWindow):
    host = '84.201.144.88'
    port = '8080'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(lambda: webbrowser.open(f'http://{MyWidget.host}:{MyWidget.port}', new=0))
        self.pushButton_4.clicked.connect(sys.exit)
        self.pushButton_2.clicked.connect(self.install)

    def install(self):
        Thread(target=loading).start()
        try:
            user = getpass.getuser()
            path = r"C:/Users/" + user + '/COVIDcover/'
            if os.path.isdir(path):
                shutil.rmtree(path)
            os.mkdir(path)

            with open(path + 'game.zip', mode='wb') as f:
                f.write(requests.get(f'http://{MyWidget.host}:{MyWidget.port}/static/releases/game.zip').content)

            with ZipFile(path + 'game.zip') as myzip:
                myzip.extractall(path)

            with open(path + 'launcher.exe', mode='wb') as f:
                f.write(requests.get(f'http://{MyWidget.host}:{MyWidget.port}/static/releases/launcher.exe').content)

            os.remove(path + 'game.zip')

            with winshell.shortcut(f'C:/Users/{user}/Desktop/COVIDcover.lnk') as link:
                link.path = f'C:/Users/{user}/COVIDcover/launcher.exe'
                link.description = "Game 'COVIDcover'"
                link.working_directory = f'C:/Users/{user}/COVIDcover'
        except Exception as e:
            global stop
            stop = True
            time.sleep(0.25)
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
