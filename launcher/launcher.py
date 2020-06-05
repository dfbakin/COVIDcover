from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit
from PyQt5 import QtCore, QtGui, QtWidgets
import json, os, sys, shutil, webbrowser, requests, hashlib
from zipfile import ZipFile

log_filename = 'covid_cover.log'
user_registration = "f5d9063b-ccb1-4a60-b4a1-8abf6ed38708"

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
    port = "8080"
    closed_signal = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
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
        if os.path.isdir(os.path.join(os.path.dirname(__file__), 'COVIDcover')):
            try:
                shutil.rmtree(os.path.join(os.path.dirname(__file__), 'COVIDcover'))
            except PermissionError:
                self.show_error('Закройте посторонние программы и перезагрузите лончер')
                return
        if self.start_download():
            self.start_installation()
        self.closed_signal.emit()
        self.close()

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
        os.mkdir(os.path.join(os.path.dirname(__file__), "COVIDcover"))
        with ZipFile("tmp.zip") as zp:
            zp.extractall(os.path.join(os.path.dirname(__file__), "COVIDcover"))
        os.remove(os.path.join(os.path.dirname(__file__), "tmp.zip"))
        self.close()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(703, 543)
        MainWindow.setStyleSheet("background-color: rgb(172, 216, 230);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(420, 350, 181, 61))
        self.pushButton_2.setStyleSheet(":!hover{\n"
"background-color: rgb(172, 216, 230);\n"
"}\n"
"\n"
":hover{\n"
"    border: 4px solid black; \n"
"    background: rgb(105, 185, 211); \n"
"    padding: 10px;\n"
"}")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(520, 430, 171, 61))
        self.pushButton_3.setStyleSheet("backgr:!hover{\n"
"background-color: rgb(172, 216, 230);\n"
"}\n"
"\n"
":hover{\n"
"    border: 4px solid black; \n"
"    background: rgb(105, 185, 211); \n"
"    padding: 10px;\n"
"}ound-color: rgb(172, 216, 230);")
        self.pushButton_3.setObjectName("pushButton_3")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 340, 301, 151))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_5.setGeometry(QtCore.QRect(320, 430, 191, 61))
        self.pushButton_5.setStyleSheet(":!hover{\n"
"background-color: rgb(172, 216, 230);\n"
"}\n"
"\n"
":hover{\n"
"    border: 4px solid black; \n"
"    background: rgb(105, 185, 211); \n"
"    padding: 10px;\n"
"}")
        self.pushButton_5.setObjectName("pushButton_5")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 80, 681, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10, 10, 681, 61))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("background-color: rgb(172, 216, 230);")
        self.label_4.setObjectName("label_4")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 110, 301, 221))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setGeometry(QtCore.QRect(10, 10, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit.setFont(font)
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_2.setGeometry(QtCore.QRect(10, 50, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton = QtWidgets.QPushButton(self.tab)
        self.pushButton.setGeometry(QtCore.QRect(100, 130, 81, 51))
        self.pushButton.setStyleSheet(":!hover{\n"
"background-color: rgb(172, 216, 230);\n"
"}\n"
"\n"
":hover{\n"
"    border: 4px solid black; \n"
"    background: rgb(105, 185, 211); \n"
"    padding: 10px;\n"
"}")
        self.pushButton.setObjectName("pushButton")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(10, 50, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_3.setFont(font)
        self.lineEdit_3.setText("")
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_4.setGeometry(QtCore.QRect(10, 90, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_4.setFont(font)
        self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_5 = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_5.setGeometry(QtCore.QRect(10, 10, 271, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_5.setFont(font)
        self.lineEdit_5.setText("")
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.pushButton_4 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_4.setGeometry(QtCore.QRect(50, 130, 181, 51))
        self.pushButton_4.setStyleSheet(":!hover{\n"
"background-color: rgb(172, 216, 230);\n"
"}\n"
"\n"
":hover{\n"
"    border: 4px solid black; \n"
"    background: rgb(105, 185, 211); \n"
"    padding: 10px;\n"
"}")
        self.pushButton_4.setObjectName("pushButton_4")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 703, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Launcher"))
        self.pushButton_2.setText(_translate("MainWindow", "Открыть сайт"))
        self.pushButton_3.setText(_translate("MainWindow", "Запустить игру!"))
        self.plainTextEdit.setPlainText(_translate("MainWindow", "Error logs:\n"
"OK"))
        self.pushButton_5.setText(_translate("MainWindow", "Запустить мультиплеер!"))
        self.label_3.setText(_translate("MainWindow", "Auth status here"))
        self.label_4.setText(_translate("MainWindow", "Все системы функционируют нормально."))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Email"))
        self.lineEdit_2.setPlaceholderText(_translate("MainWindow", "Пароль"))
        self.pushButton.setText(_translate("MainWindow", "Войти"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Войти"))
        self.lineEdit_3.setPlaceholderText(_translate("MainWindow", "Email"))
        self.lineEdit_4.setPlaceholderText(_translate("MainWindow", "Пароль"))
        self.lineEdit_5.setPlaceholderText(_translate("MainWindow", "Имя пользователя"))
        self.pushButton_4.setText(_translate("MainWindow", "Зарегестрироваться"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Зарегестрироваться"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))




class MyWidget(QMainWindow, Ui_MainWindow):
    """ host = '130.193.46.251'
        port = '8080'
    """
    host = "127.0.0.1"
    port = "8080"

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.update_game()
        if not self.update_needed:
            self.show()



    def initUI(self):
        self.pushButton_3.clicked.connect(self.launch_single)
        self.pushButton_2.clicked.connect(lambda: webbrowser.open(f'http://{MyWidget.host}:{MyWidget.port}', new=0))
        self.pushButton_5.clicked.connect(self.launch_multi)
        self.pushButton.clicked.connect(self.login)

        self.pushButton_4.clicked.connect(self.register)
        self.pushButton_5.setVisible(False)
        self.label_3.setText('Войдите в учетную запись, чтобы зайти в мультиплеер')

        self.user = None
        self.password = None


    def check_hash(self, script_path=str(os.path.join(os.path.dirname(__file__), "COVIDcover"))):
        lst = []
        hash = hashlib.md5()
        for path, dirs, files in os.walk(script_path):
            for file in files:
                with open(os.path.join(path, file), mode='rb') as f:
                    hash.update(f.read())
                lst.append(hash.digest())
        hash.update(b''.join(lst))
        output = hash.hexdigest()
        try:
            response = requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/check_hash/{output}')
        except requests.exceptions.ConnectionError:
            self.show_error('Отсутствует интернет. Запустите программу позже.')
            return True
        except requests.exceptions.Timeout:
            self.show_error('Видимо, у наш сервер сейчас отдыхает ;)')
            return True
        except Exception:
            self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
            return True
        if response.status_code == 500:
            self.show_error('Ошибка на сервере. Мы уже работаем.')
            return True
        if response.status_code != 200:
            self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
            return True
        if response:
            return response.json()['success']
        return True

    def register(self):
        email = self.lineEdit_3.text()
        password = self.lineEdit_4.text()
        username = self.lineEdit_5.text()
        if not all((email, password, username)):
            self.show_error('Заполните все поля!')
            return
        try:
            response = requests.post(f'http://{MyWidget.host}:{MyWidget.port}/api/users/token/{user_registration}', data={'email': email, 'password': password, "username": username})
        except requests.exceptions.ConnectionError:
            self.show_error('Отсутствует интернет. Запустите программу позже.')
            return
        except requests.exceptions.Timeout:
            self.show_error('Видимо, у наш сервер сейчас отдыхает ;)')
            return
        except Exception:
            self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
            return
        if response.status_code == 500:
            self.show_error('Ошибка на сервере. Мы уже работаем.')
            return
        elif response.status_code == 406:
            self.show_error('Пользователь с таким именем или адресом был уже зарегестрирован')
        else:
            self.auth(email, password)

    def login(self):
        email = self.lineEdit.text()
        if not self.password or not self.user:
            self.password = self.lineEdit_2.text()
        password = self.password
        self.lineEdit_2.setText('')
        if not email or not password:
            self.show_error('Заполните все поля!')
            return
        self.auth(email, password)


    def auth(self, email, password):
        try:
            response = requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/auth',
                                    params={'email': email, 'password': password}, timeout=3.)
        except requests.exceptions.ConnectionError:
            self.show_error('Отсутствует интернет. Запустите программу позже.')
            return
        except requests.exceptions.Timeout:
            self.show_error('Видимо, у наш сервер сейчас отдыхает ;)')
            return
        except Exception:
            self.show_error('Возникла непредвиденная ошибка. Вы можете написать в тех. поддержку.')
            return
        if response.status_code == 500:
            self.show_error('Ошибка на сервере. Мы уже работаем.')
            return False
        data = response.json()
        if not data['success']:
            self.label_3.setText('Неверные данные')
            return
        self.user = data.copy()
        self.pushButton_5.setVisible(True)
        self.label_3.setText(self.user['username'])
        return True

    def update_game(self):
        self.update_needed = False
        if os.path.isfile(os.path.join(os.path.dirname(__file__), 'COVIDcover/versions.json')):
            try:
                response = requests.get(f'http://{MyWidget.host}:{MyWidget.port}/static/releases/versions.json',
                                        timeout=5.)
            except requests.exceptions.ConnectionError:
                self.show_error('Отсутствует интернет. Вам недоступна сетевая игра')
                return
            except requests.exceptions.Timeout:
                self.show_error('Видимо, у наш сервер сейчас отдыхает ;) Вам недоступна сетевая игра')
                return
            except Exception:
                self.show_error('Возникла непредвиденная ошибка.\nВы можете написать в тех. поддержку.\nВам недоступна сетевая игра')
                return
            if response.status_code == 500:
                self.show_error('Ошибка на сервере. Мы уже работаем.\nВам недоступна сетевая игра')
                return False
            versions_list = json.loads(response.content.decode('utf-8'))
            with open(os.path.join(os.path.dirname(__file__), 'COVIDcover/versions.json'), mode='r', encoding='utf-8') as f:
                data = json.load(f)
                self.update_needed = data['last_version'] != versions_list['last_version']
        if not self.update_needed:
            self.update_needed = not self.check_hash()
        if self.update_needed:
            self.hide()
            self.updater = LoadingWidget(self) # TODO Update launcher
            self.updater.closed_signal.connect(self.show)


    def launch_multi(self):
        self.show_error('Все системы функционируют нормально.')
        if not self.user:
            self.auth()
        if not self.user:
            return
        if not self.check_hash():
            self.show_error('Файлы игры повреждены. Попробуйте позже.')
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
        if response.status_code == 500:
            self.show_error('Ошибка на сервере. Мы уже работаем.')
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

        try:
            error_code = None
            self.hide()
            os.system(f"cd COVIDcover && \"{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'COVIDcover', 'multi_build/multi_main.exe')}\" {data['ip']} {data['port']} {self.user['token']} {self.user['username']}")
            self.show()
            if os.path.isfile('score.dat'):
                with open('score.dat', mode='r', encoding='utf-8') as file:
                    score, error_code = file.read().strip().split()
                    error_code = int(error_code)
                os.remove('score.dat')
            else:
                score, error_code = 0, -7

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
            try:
                if not score or not score.isdigit() or len(score) > 6 or error_code != 0:
                    requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/quit',
                                 params={'user_token': self.user['token'], 'score': int(self.user['score'])})
                else:
                    requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/quit',
                                 params={'user_token': self.user['token'], 'score': int(score)})
            except Exception as e:
                self.plainTextEdit.appendPlainText(str(e) + '\n')
                requests.get(f'http://{MyWidget.host}:{MyWidget.port}/game_api/quit',
                             params={'user_token': self.user['token'], 'score': 0})
            finally:
                if os.path.isfile('score.dat'):
                    os.remove('score.dat')
                if os.path.isfile('covid_cover.log'):
                    os.remove('covid_cover.log')
                if error_code and error_code != 0:
                    if os.path.isfile(log_filename):
                        try:
                            os.remove(log_filename)
                        except Exception as e:
                            print(e)

                    with open(log_filename, mode='r', encoding='utf-8') as file:
                        try:
                            response = requests.post(f'http://{host}:{port}/game_api/get_log', files={'log': file})
                        except Exception as e:
                            self.show_error(str(e))
                if os.path.isfile(log_filename):
                    try:
                        os.remove(log_filename)
                    except PermissionError:
                        pass
                    except Exception as e:
                        self.show_error(str(e))

    def launch_single(self):
        try:
            self.hide()
            os.system('cd COVIDcover && "main_build/main"')
            self.show()
        except Exception as e:
            self.plainTextEdit.setPlainText(self.plainTextEdit.toPlainText() + str(e) + '\n\n')
        finally:
            self.show()

    def show_error(self, error):
        self.label_4.setText(error)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    sys.exit(app.exec())