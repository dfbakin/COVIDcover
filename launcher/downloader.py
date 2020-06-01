# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loading.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

import os
from PyQt5 import QtCore, QtGui, QtWidgets
import requests
import zipfile
import sys


class Ui_Downloader(object):
    def setupUi(self, Downloader):
        Downloader.resize(391, 111)
        self.centralwidget = QtWidgets.QWidget(Downloader)
        self.centralwidget.setObjectName("centralwidget")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setEnabled(True)
        self.progressBar.setGeometry(QtCore.QRect(10, 33, 369, 25))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 10, 369, 17))
        self.label.setText("")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setEnabled(True)
        self.pushButton.setGeometry(QtCore.QRect(150, 30, 81, 31))
        self.pushButton.setObjectName("pushButton")
        Downloader.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Downloader)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 391, 22))
        self.menubar.setObjectName("menubar")
        Downloader.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Downloader)
        self.statusbar.setObjectName("statusbar")
        Downloader.setStatusBar(self.statusbar)

        self.retranslateUi(Downloader)
        QtCore.QMetaObject.connectSlotsByName(Downloader)

    def retranslateUi(self, Downloader):
        _translate = QtCore.QCoreApplication.translate
        Downloader.setWindowTitle(_translate("Downloader", "Установка обновления"))
        self.pushButton.setText(_translate("Downloader", "Скачать"))


class LoadingWidget(QtWidgets.QMainWindow, Ui_Downloader):
    host = "127.0.0.1"
    port = "5000"

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.progressBar.hide()
        self.pushButton.clicked.connect(self.install)
        self.show()

    def install(self):
        self.pushButton.hide()
        self.progressBar.setValue(0)
        self.progressBar.show()
        if self.start_download():
            self.start_installation()

    def show_message(self, message):
        buttonReply = QtWidgets.QMessageBox.critical(QtWidgets.QWidget(), 'Ошибка', message,
                                                     QtWidgets.QMessageBox.Retry, QtWidgets.QMessageBox.Cancel)
        if buttonReply == QtWidgets.QMessageBox.Cancel:
            sys.exit(0)
        else:
            self.install()

    def start_download(self):
        self.label.setText('Идёт загрузка игры')
        try:
            response = requests.get(f'http://{self.host}:{self.port}/static/releases/game.zip', stream=True)
            chunks_required = round(int(response.headers.get('content-length', '0')) / 4096)
            if chunks_required:
                chunks_downloaded = 0
                stream = []
                for chunk in response.iter_content(chunk_size=4096):
                    stream.append(chunk)
                    chunks_downloaded += 1
                    self.progressBar.setValue(int(chunks_downloaded / chunks_required * 100))
                    QtWidgets.QApplication.processEvents()
        except requests.exceptions.ConnectionError:
            self.show_message('Отсутствует интернет. Запустите программу позже.')
            return
        except requests.exceptions.Timeout:
            self.show_message('Видимо, у наш сервер сейчас отдыхает ;)')
            return
        except Exception as e:
            self.show_message('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
            return
        if response.status_code == 500:
            self.show_message('Ошибка на сервере. Мы уже работаем.')
            return False
        with open('tmp.zip', mode='wb') as file:
            file.write(b"".join(stream))
        return True

    def start_installation(self):
        self.progressBar.hide()
        self.label.setText('Идёт установка игры')
        QtWidgets.QApplication.processEvents()
        os.mkdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), "COVIDcover"))
        with zipfile.ZipFile("tmp.zip") as zp:
            zp.extractall(os.path.join(os.path.abspath(os.path.dirname(__file__)), "COVIDcover"))
        os.remove(os.path.join(os.path.abspath(os.path.dirname(__file__)), "tmp.zip"))
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = LoadingWidget()
    sys.exit(app.exec())
