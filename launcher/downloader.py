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




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = LoadingWidget()
    sys.exit(app.exec())
