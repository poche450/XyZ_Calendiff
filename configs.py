from config_ui import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QDialog)
                             
class config_ui(QDialog):
    def __init__(self, parent=None):
        super(config_ui, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
       

