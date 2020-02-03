# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from openexchangerate import OpenExchangeRates
import requests,json
from datetime import date, timedelta
from datetime import date, timedelta
from dateutil.parser import parse
import matplotlib.pyplot as plt
import numpy as np

# Pulls currency codes from openexchange rate and populates list
def populate_currency_list(self):
    client = OpenExchangeRates(api_key="083da16291e5447e8bc66ee1d43ae960")
    currencies = client.currencies().dict
    for currency_code in currencies:
        # print(str(currency_code) + ":" + str(currencies[currency_code]))
        self.from_currency_list.addItem(str(currency_code) + " : " + str(currencies[currency_code]))
        self.to_currency_list.addItem(str(currency_code) + " : " + str(currencies[currency_code]))

# Function to get real time currency exchange
def get_todays_rate(from_currency,to_currency,self):

    from_currency = from_currency[:3]
    to_currency = to_currency[:3]

    print(from_currency)
    print(to_currency)

    # base_url variable store base url
    base_url = r"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE"

    # main_url variable store complete url
    main_url = base_url + "&from_currency=" + from_currency +"&to_currency=" + to_currency + "&apikey=2MFOB84WZRAIGROV"

    # Debug Message Json Requests
    # print(main_url)

    # get method of requests module
    # return response object
    req_ob = requests.get(main_url)

    # json method return json format
    # data into python dictionary data type.

    # result contains list of nested dictionaries
    result = req_ob.json()

    rate = result["Realtime Currency Exchange Rate"]['5. Exchange Rate']
    print(type(rate))
   # self.todays_rate_label.setText(["Realtime Currency Exchange Rate"]['5. Exchange Rate'])

    self.todays_rate_label.setText(from_currency + " : " + to_currency + " = " + rate)

# Displays matplotlib chart with input (x) and input_values (y)
def plot_histogram(input_date,input_values, from_currency, to_currency):

    #Puts in x and y values into matplotlib plot
    plt.plot(input_date, input_values, marker='o', linestyle='-')
    plt.ylabel("Exchange Rate")
    plt.xlabel("Date")

    #Configure ticks
    plt.yticks(np.arange(min(input_values), max(input_values), step=(max(input_values) - min(input_values))/8))
    plt.xticks(rotation=45)
    plt.grid(True)

    #Extra parameters to make the plot nicer
    plt.title("Exchange rate between " + from_currency + " and " + to_currency)

    plt.show()

def fx_daily(from_currency, to_currency, self):
    # piece together api for
    base_url = r"https://www.alphavantage.co/query?function=FX_DAILY"

    from_currency = from_currency[:3]
    to_currency = to_currency[:3]

    # main_url variable store complete url
    main_url = base_url + "&from_symbol=" + from_currency + "&to_symbol=" + to_currency + "&apikey=2MFOB84WZRAIGROV"

    # Debug Message Json Requests
    # print(main_url)

    # get method of requests module
    # return response object
    req_ob = requests.get(main_url)

    # json method return json format
    # data into python dictionary data type.

    # result contains list of nested dictionaries1
    result = req_ob.json()

    print(" Result before parsing the json data :\n", result)

    # Parse the results from the all time highs
    today = str(date.today())

    # This variable is used to control the while loop, initialize with today's date
    start_date = date.today()

    # Initialize an empty dictionary
    time_series_fx_highs = {}

    # Find the earliest date in dictionary key
    result_earliest_date = min(result['Time Series FX (Daily)'])
    print("The Earliest Date in String is: " + result_earliest_date)

    # Convert the earliest time string into datetime
    result_earliest_date_datetime = parse(result_earliest_date).date()

    # Initiate two variables as empty arrays
    plot_date = []
    plot_highs = []

    while start_date >= result_earliest_date_datetime:
        if (str(start_date) in result['Time Series FX (Daily)']):
            intermediate_date = str(start_date)
            plot_date.append(start_date)
            plot_highs.append(float(result['Time Series FX (Daily)'][intermediate_date]['2. high']))
            print(intermediate_date)
        start_date = start_date - timedelta(days=1)

    # Initiate Matplotlib Library
    #print(time_series_fx_highs)
    plot_histogram(plot_date, plot_highs,from_currency,to_currency)


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(805, 680)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(0, 0, 800, 50))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)

        self.label.setFont(font)
        self.label.setAutoFillBackground(False)
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")

        self.from_currency_list = QtWidgets.QListWidget(self.centralwidget)
        self.from_currency_list.setGeometry(QtCore.QRect(20, 60, 200, 551))
        self.from_currency_list.setObjectName("from_currency_list")
        self.from_currency_list.currentItemChanged.connect(
            lambda: print("From List Selected: " + self.from_currency_list.currentItem().text()))

        self.to_currency_list = QtWidgets.QListWidget(self.centralwidget)
        self.to_currency_list.setGeometry(QtCore.QRect(250, 60, 200, 551))
        self.to_currency_list.setObjectName("to_currency_list")
        self.to_currency_list.currentItemChanged.connect(
            lambda: print("To List Selected:" + self.to_currency_list.currentItem().text()))

        self.todays_rate_button = QtWidgets.QPushButton(self.centralwidget)
        self.todays_rate_button.setGeometry(QtCore.QRect(480, 520, 141, 91))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.todays_rate_button.setFont(font)
        self.todays_rate_button.setObjectName("todays_rate_button")
        self.todays_rate_button.clicked.connect(
            lambda: get_todays_rate(self.from_currency_list.currentItem().text(), self.to_currency_list.currentItem().text(), self))

        self.historica_rate_button = QtWidgets.QPushButton(self.centralwidget)
        self.historica_rate_button.setGeometry(QtCore.QRect(650, 520, 141, 91))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.historica_rate_button.setFont(font)
        self.historica_rate_button.setObjectName("historica_rate_button")
        self.todays_rate_label = QtWidgets.QLabel(self.centralwidget)
        self.todays_rate_label.setGeometry(QtCore.QRect(470, 70, 321, 71))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.historica_rate_button.clicked.connect(
            lambda: fx_daily(self.from_currency_list.currentItem().text(),
                                    self.to_currency_list.currentItem().text(), self))

        self.todays_rate_label.setFont(font)
        self.todays_rate_label.setText("")
        self.todays_rate_label.setAlignment(QtCore.Qt.AlignCenter)
        self.todays_rate_label.setObjectName("todays_rate_label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 805, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        populate_currency_list(self)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Currency Exchange"))
        self.todays_rate_button.setText(_translate("MainWindow", "Convert Today\'s Rate"))
        self.historica_rate_button.setText(_translate("MainWindow", "Historical Rate"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
