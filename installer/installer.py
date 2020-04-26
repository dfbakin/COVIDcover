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
        MainWindow.resize(723, 437)
        MainWindow.setStyleSheet("background-color: rgb(172, 216, 230);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(350, 330, 311, 61))
        self.pushButton_2.setStyleSheet("backgr:!hover{\n"
                                        "background-color: rgb(172, 216, 230);\n"
                                        "}\n"
                                        "\n"
                                        ":hover{\n"
                                        "    border: 4px solid black; \n"
                                        "    background: rgb(105, 185, 211); \n"
                                        "    padding: 10px;\n"
                                        "}ound-color: rgb(172, 216, 230);")
        self.pushButton_2.setObjectName("pushButton_2")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(10, 160, 691, 31))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 371, 41))
        font = QtGui.QFont()
        font.setFamily("Viner Hand ITC")
        font.setPointSize(14)
        font.setItalic(False)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: rgb(172, 216, 230);")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(260, 80, 471, 31))
        font = QtGui.QFont()
        font.setFamily("Viner Hand ITC")
        font.setPointSize(14)
        font.setUnderline(True)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("background-color: rgb(172, 216, 230);")
        self.label_2.setObjectName("label_2")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 220, 331, 171))
        self.plainTextEdit.setStyleSheet("background-color: rgb(172, 216, 230);")
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(350, 250, 311, 61))
        self.pushButton.setStyleSheet("backgr:!hover{\n"
                                      "background-color: rgb(172, 216, 230);\n"
                                      "}\n"
                                      "\n"
                                      ":hover{\n"
                                      "    border: 4px solid black; \n"
                                      "    background: rgb(105, 185, 211); \n"
                                      "    padding: 10px;\n"
                                      "}ound-color: rgb(172, 216, 230);")
        self.pushButton.setObjectName("pushButton")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(350, 210, 371, 21))
        self.label_3.setStyleSheet("background-color: rgb(172, 216, 230);")
        self.label_3.setObjectName("label_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 723, 21))
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
        self.label.setText(_translate("MainWindow", "Вы открыли установщик игры COVIDcover."))
        self.label_2.setText(_translate("MainWindow", "Проверьте интернет соединение перед началом!!!"))
        self.plainTextEdit.setPlainText(_translate("MainWindow", "Error logs:\n"
                                                                 "OK\n"
                                                                 ""))
        self.pushButton.setText(_translate("MainWindow", "Открыть сайт"))
        self.label_3.setText(_translate("MainWindow", "Все системы функционируют нормально"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


stop = False


def loading():
    global stop
    while ex.progressBar.value() <= 98:
        ex.progressBar.setValue(ex.progressBar.value() + 1)
        time.sleep(0.3)
        if stop:
            break


class MyWidget(QMainWindow, Ui_MainWindow):
    host = '127.0.0.1'
    port = '8080'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(lambda: webbrowser.open(f'http://{MyWidget.host}:{MyWidget.port}', new=0))
        self.pushButton_2.clicked.connect(self.install)

    def install(self):
        global stop
        Thread(target=loading).start()
        try:
            user = getpass.getuser()
            path = r"C:/Users/" + user + '/COVIDcover/'
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except PermissionError:
                    self.show_error('Закройте посторонние программы и попробуйте снова.')
                    return
            os.mkdir(path)

            with open(path + 'game.zip', mode='wb') as f:
                try:
                    response = requests.get(f'http://{MyWidget.host}:{MyWidget.port}/static/releases/game.zip',
                                            timeout=120.)
                except requests.exceptions.ConnectionError:
                    self.show_error('Отсутствует интернет. Запустите программу позже.')
                    return
                except requests.exceptions.Timeout:
                    self.show_error('Ваш интернет слишком медленный. Попробуйте позже.')
                    return
                except Exception:
                    self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
                    return
                if response.status_code != 200:
                    self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
                    return
                try:
                    f.write(response.content)
                except Exception as e:
                    self.plainTextEdit.appendPlainText('\n' + str(e))
                    print(e)
                    self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
                    return

            with ZipFile(path + 'game.zip') as myzip:
                myzip.extractall(path)

            with open(path + 'launcher.exe', mode='wb') as f:
                try:
                    response = requests.get(f'http://{MyWidget.host}:{MyWidget.port}/static/releases/launcher.exe',
                                            timeout=60.)
                except requests.exceptions.ConnectionError:
                    self.show_error('Отсутствует интернет. Запустите программу позже.')
                    return
                except requests.exceptions.Timeout:
                    self.show_error('Ваш интернет слишком медленный. Попробуйте позже.')
                    return
                except Exception:
                    self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
                    return
                if response.status_code != 200:
                    self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
                    return
                try:
                    f.write(response.content)
                except Exception as e:
                    self.plainTextEdit.appendPlainText('\n' + str(e))
                    print(e)
                    self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
                    return
            try:
                os.remove(path + 'game.zip')
            except PermissionError:
                self.show_error('Закройте посторонние программы и попробуйте снова.')
                return

            with winshell.shortcut(f'C:/Users/{user}/Desktop/COVIDcover.lnk') as link:
                link.path = f'C:/Users/{user}/COVIDcover/launcher.exe'
                link.description = "Game 'COVIDcover'"
                link.working_directory = f'C:/Users/{user}/COVIDcover'
            self.progressBar.setValue(100)

        except Exception as e:
            print(e)
            self.plainTextEdit.appendPlainText('\n' + str(e))
        finally:
            stop = True
            time.sleep(0.1)
            if self.progressBar.value() != 100:
                self.progressBar.setValue(0)
            stop = False

    def show_error(self, error):
        global stop
        stop = True
        self.label_3.setText(error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    app.exec()
    stop = True
    time.sleep(1.)
    sys.exit()
