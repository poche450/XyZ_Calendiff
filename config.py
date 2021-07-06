import json
from config_ui import Ui_Dialog
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog)

class config_ui(QDialog):
    def __init__(self, parent=None):
        super(config_ui, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButton_apply.clicked.connect(self.save_Setting_clicked)

    def save_Setting_clicked(self):
        for option in self.ui.gridLayout_12.parentWidget().findChildren(QCheckBox):
            print(option.text())

class config():
    def __init__(self):
        path="config.json"
        with open(path, "r") as c:
            self.param=json.load(c)
        self.api_key=self.api_config()
    def api_config(self):
        api_key=[]
        api_key=self.param['api_key']
        return str(api_key)
        
    def event_config(self):
        pass
    def database_config(self):
        pass
    def scanner_config(self):
        pass
    def requests_config(self):
        return self.param['request']
        

print(config().api_key)      

