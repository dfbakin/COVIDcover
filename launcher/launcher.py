from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import json, os, sys, shutil, webbrowser, requests
from zipfile import ZipFile

stop = False


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1066, 821)
        MainWindow.setStyleSheet("background-color: rgb(255, 190, 144);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(550, 700, 101, 61))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(870, 700, 181, 61))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(410, 700, 121, 61))
        self.pushButton_4.setObjectName("pushButton_4")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(100, 50, 721, 41))
        font = QtGui.QFont()
        font.setFamily("Viner Hand ITC")
        font.setPointSize(14)
        font.setItalic(False)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(100, 100, 721, 31))
        font = QtGui.QFont()
        font.setFamily("Viner Hand ITC")
        font.setPointSize(14)
        font.setUnderline(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 590, 391, 181))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(670, 700, 181, 61))
        self.pushButton_5.setObjectName("pushButton_5")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(42, 360, 241, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(40, 400, 241, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(40, 460, 241, 51))
        self.pushButton.setObjectName("pushButton")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(40, 330, 251, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(360, 340, 671, 111))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
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
        MainWindow.setWindowTitle(_translate("MainWindow", "Launcher"))
        self.pushButton_2.setText(_translate("MainWindow", "Открыть сайт"))
        self.pushButton_3.setText(_translate("MainWindow", "Запустить игру!"))
        self.pushButton_4.setText(_translate("MainWindow", "Закрыть программу"))
        self.label.setText(_translate("MainWindow", "Эта программа обновит клиент игры до последней версии."))
        self.label_2.setText(_translate("MainWindow", "Проверьте интернет соединение!!!"))
        self.plainTextEdit.setPlainText(_translate("MainWindow", "Error logs:\n"
                                                                 "OK"))
        self.pushButton_5.setText(_translate("MainWindow", "Запустить мультиплеер!"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Адрес почты"))
        self.lineEdit_2.setPlaceholderText(_translate("MainWindow", "Пароль"))
        self.pushButton.setText(_translate("MainWindow", "Войти"))
        self.label_3.setText(_translate("MainWindow", "Auth status here"))
        self.label_4.setText(_translate("MainWindow", "Все системы функционируют нормально."))
        self.actionExit.setText(_translate("MainWindow", "Exit"))


class MyWidget(QMainWindow, Ui_MainWindow):
    host = '130.193.45.158'
    port = '8080'

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.pushButton_3.clicked.connect(self.launch_single)
        self.pushButton_2.clicked.connect(lambda: webbrowser.open(f'http://{MyWidget.host}:{MyWidget.port}', new=0))
        self.pushButton_4.clicked.connect(sys.exit)
        self.pushButton_5.clicked.connect(self.launch_multi)
        self.pushButton.clicked.connect(self.auth)

        self.pushButton_3.setVisible(False)
        self.pushButton_5.setVisible(False)

        self.label_3.setText('Войдите в учетную запись')

        self.user = None

        self.update_game()

    def auth(self):
        email = self.lineEdit.text()
        password = self.lineEdit_2.text()
        if not email or not password:
            self.label_3.setText('Заполните все поля!')
            return
        try:
            response = requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/auth',
                                    params={'email': email, 'password': password}, timeout=2.5)
        except requests.exceptions.ConnectionError:
            self.show_error('Отсутствует интернет. Запустите программу позже.')
            return
        except requests.exceptions.Timeout:
            self.show_error('Видимо, у наш сервер сейчас отдыхает ;)')
            return
        except Exception:
            self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
            return

        data = response.json()
        if not data['success']:
            self.label_3.setText('Неверные данные')
            return
        self.user = data.copy()
        self.pushButton_5.setVisible(True)
        self.label_3.setText(self.user['username'])

    def update_game(self):
        path = ''

        update_needed = True
        if os.path.isfile(path + 'versions.json'):
            try:
                response = requests.get(f'http://{MyWidget.host}:{MyWidget.port}/static/releases/versions.json',
                                        timeout=5.)
            except requests.exceptions.ConnectionError:
                self.show_error('Отсутствует интернет. Запустите программу позже.')
                return
            except requests.exceptions.Timeout:
                self.show_error('Видимо, у наш сервер сейчас отдыхает ;)')
                return
            except Exception:
                self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
                return
            versions_list = json.loads(response.content.decode('utf-8'))
            with open(path + 'versions.json', mode='r', encoding='utf-8') as f:
                data = json.load(f)
                update_needed = data['last_version'] != versions_list['last_version']
        if update_needed:
            for i in os.listdir(path):
                if i == 'launcher.exe':
                    continue
                if '.' in i:
                    os.remove(path + i)
                else:
                    try:
                        shutil.rmtree(path + i)
                    except PermissionError:
                        self.show_error('Закройте посторонние программы и перезагрузите лончер')
                        return

            with open(path + 'game.zip', mode='wb') as f:
                f.write(requests.get(f'http://{MyWidget.host}:{MyWidget.port}/static/releases/game.zip').content)

            with ZipFile(path + 'game.zip') as myzip:
                myzip.extractall(path)

            os.remove(path + 'game.zip')
        self.pushButton_3.setVisible(True)
        self.label_3.setVisible(True)

    def launch_multi(self):
        if not self.user:
            return
        try:
            response = requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/join',
                                    params={'user_token': self.user['token']}, timeout=3.)
        except requests.exceptions.ConnectionError:
            self.show_error('Отсутствует интернет. Запустите программу позже.')
            return
        except requests.exceptions.Timeout:
            self.show_error('Видимо, у наш сервер сейчас отдыхает ;)')
            return
        except Exception:
            self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
            return
        stat = response.status_code
        if stat == 404:
            self.show_error('Возникла проблема с Вашей учетной записью. Напишите нам.')
            return
        elif stat == 406:
            self.show_error('Все сервера сейчас заняты. Попробуйте позднее.')
            return

        data = response.json()
        if not data['success']:
            return
        if data['role'] == 'cou':
            role = 'volunteer'
        elif data['role'] == 'pol':
            role = 'policeman'
        elif data['role'] == 'use':
            role = 'citizen'
        else:
            print('invalid role')
            return

        with open('launch.bat', mode='w', encoding='utf-8') as f:
            f.write('cd multi_build\n')
            f.write(f"multi_main {role} {self.user['score']} {data['ip']} {data['port']} {self.user['token']} {self.user['username']}")

        try:
            self.hide()
            os.system('launch')
            self.show()
            with open('multi_build/score.dat', mode='r', encoding='utf-8') as file:
                score, error_code = file.read().strip().split()
                error_code = int(error_code)
            if not score.isdigit():
                self.show_error('Ошибка клиента игры. Напишите нам.')
            if error_code == -5:
                self.show_error('Отсутствует интернет. Запустите программу позже.')
            elif error_code == -6:
                self.show_error('Видимо, у наш сервер сейчас отдыхает ;)')
            elif error_code == -7:
                self.show_error('Ошибка игры. Мы уже работаем над ее устранением.')

        except Exception as e:
            self.plainTextEdit.setPlainText(self.plainTextEdit.toPlainText() + str(e) + '\n\n')
        finally:
            self.show()
            if not score or not score.isdigit() or len(score) > 9 or error_code != 0:
                requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/quit',
                             params={'user_token': self.user['token'], 'score': int(self.user['score'])})
            else:
                print(requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/quit',
                                   params={'user_token': self.user['token'], 'score': int(score)}).content)
            os.remove('launch.bat')

    def launch_single(self):
        with open('launch.bat', mode='w', encoding='utf-8') as f:
            f.write('cd main_build\n')
            f.write("main")

        try:
            self.hide()
            os.system('launch')
            self.show()
        except Exception as e:
            self.plainTextEdit.setPlainText(self.plainTextEdit.toPlainText() + str(e) + '\n\n')
        finally:
            self.show()
            os.remove('launch.bat')

    def show_error(self, error):
        self.label_4.setText(error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
