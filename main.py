# This Python file uses the following encoding: utf-8
import csv
import os
import sys

import concurrent.futures
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QErrorMessage, QFileDialog,
                             QMainWindow)

from credentials import credential
import data.ticker_data as td
import engine
from forms import Ui_mainwindow

import config

class mainwindow(QMainWindow):
    def __init__(self, parent=None):
        super(mainwindow, self).__init__(parent)
        self.ui = Ui_mainwindow()
        self.ui.setupUi(self)
        self.ui.pushButton_connection.clicked.connect(self.authorize_clicked)
        self.ui.pushButton_loadCSV.clicked.connect(self.loadCSV_clicked)
        self.ui.pushButton_execute.clicked.connect(self.execute_clicked)
        self.ui.pushButton_updateDB.clicked.connect(self.update_DB_clicked)
        #self.ui.pushButton_save.clicked.connect(self.save_ticker_list)
        self.ui.actionContact_Info.triggered.connect(self.config_show)
        self.validate_token()
        self.request_box_init()

    def request_box_init(self):
        self.ui.comboBox_requests.insertItems(0,config.config().requests_config())

    def update_DB_clicked(self):
        begin_date,end_date=self.ui.dateEdit_From.text(),self.ui.dateEdit_to.text()
        request=self.ui.comboBox_requests.currentText()
        if not self.ui.radioButton_db.isChecked():
            try:
                tickers=self.ui.lineEdit.text()
                tickerList=tickers.split(',')
                
            except:self.ui.plainTextEdit_log.appendPlainText("There was a problem with the database update.")
        msg_log=engine.database_update().database_iterator(
                    request=request,list=tickerList,all_pop=False,period=None,interval=None,begin_date=begin_date,end_date=end_date)
        return self.print_msg(msg_log)

    def print_msg(self, msg=None):
        for m in msg:
            self.ui.plainTextEdit_log.appendPlainText(m)

    def config_show(self):
        return config.config_ui(self).show()
 
    def validate_token(self):
        if os.path.exists('token.json'):
            self.ui.plainTextEdit_log.appendPlainText("Statut : Token found.")
        elif not os.path.exists('token.json'):
            self.ui.plainTextEdit_log.appendPlainText("Statut : Token not found. Please connect to your account")
            
    def authorize_clicked(self):
        credential.calendar().authorize()
        self.google_api_authorized=True
    def update_ticker_view(self):
        tickerlist=""
        for ticker in self.tickerList:
            ticker=ticker+","
            tickerlist=tickerlist+ticker
        self.ui.plainTextEdit.setPlainText(tickerlist)
    def save_ticker_list(self):
        tickers=self.ui.plainTextEdit.toPlainText()
        tickerList=tickers.split(',')
        try:
            print(tickerList)
            """with open("Stock Ticker List.csv", "w") as saveFile:
                saveFile.write(tickerList)
                saveFile.close()"""
        except:
            error="Unknown Error"
            self.error_show(error=error)
        
    def loadCSV_clicked(self):
        try:
            tickerFile=loadCSV()
            ticker_list=[]
            with open (tickerFile) as csv_file:
                ticker_csv = csv.reader(csv_file,delimiter=",")
                for row in ticker_csv:
                    ticker_list.append(row[0])
            self.tickerList=ticker_list
            self.update_ticker_view()

        except FileNotFoundError:
            error="File Not Found Error"
            self.error_show(error=error)
            self.tickerList=None
        except IndexError:
            error="Wrong Type of File. Please Choose a CSV File"
            self.error_show(error=error)
            self.tickerList=None
        except:
            error="Unknown Error"
            self.error_show(error=error)         
        return self.tickerList

    def execute_clicked(self):
        try:
            tickers=self.ui.lineEdit.text()
            tickerList=tickers.split(',')
            try:tickerList.remove("")
            except:pass
            finally: 
                print(config.config().requests_config())
                self.ui.plainTextEdit_log.appendPlainText(str(config.config().requests_config()))
        except AttributeError:
            self.ui.plainTextEdit_log.appendPlainText("No ticker")
    """def execute_clicked_test(self):
        ticker,date,rate,divYield="VICI","2021-06-23","123","123"
        credential.calendar().create_events(ticker,date,rate,divYield)"""

    def ticker_iterator(self,tickers):
        print(tickers)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_ticker = {executor.submit(self.engine,t): t for t in tickers}
            for future in concurrent.futures.as_completed(future_to_ticker):
                tick=future_to_ticker[future]
                try:tick=future.result()
                except:pass
        return tick
    def engine(self,ticker):
        print(ticker)
        date=td.stock_data(ticker).get_exdividend()
        rate=td.stock_data(ticker).get_div_rate()

        param=[ticker,date,rate]
        print(param)
        credential.calendar().create_events(ticker,date,rate)

    def uninstall_service(self):
        pass
    
    def error_show(self, error):
        dlg = QErrorMessage(self)
        dlg.showMessage(error)

        
def loadCSV():
    file = QFileDialog.getOpenFileName(
        caption="Select The File to Choose Data From (Excel Worksheet or CSV Files", filter="*.csv")
    return file[0]

if __name__ == "__main__":
    app = QApplication([])
    File = open('Hookmark.qss', 'r')
    with File:
        qss = File.read()
        app.setStyleSheet(qss)
    window = mainwindow()
    window.show()
    sys.exit(app.exec_())
