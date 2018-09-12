from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLabel, QListWidget, QListWidgetItem, QDockWidget, QGroupBox, QPushButton, \
    QMainWindow

from BSTrade.Data.const import Provider
from BSTrade.Data.controller import bs_api


class ExchangeInfo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main: 'QMainWindow' = parent
        self.provider = None

        self.market = None  # self.api.store.markets[provider]
        self.vbox = QVBoxLayout(self)
        self.list_widget = None
        self.title_label = QLabel("None", self)
        font = QFont()
        font.setPointSize(20)
        self.title_label.setFont(font)
        self.symbol_info = SymbolInfo(self.main)

        self.setup_ui()

    def setup_ui(self):

        self.list_widget = QListWidget(self)
        self.list_widget.setMaximumWidth(120)

        hbox = QHBoxLayout()
        hbox.addWidget(self.list_widget)
        hbox.addWidget(self.symbol_info)

        self.vbox.addWidget(self.title_label)
        self.vbox.addLayout(hbox)
        self.setLayout(self.vbox)

    @pyqtSlot(Provider)
    def exchange_selected(self, prov):
        self.provider = prov
        market = bs_api.update_markets(prov)
        market.sig.symbol_updated.connect(self.symbols_updated)

    @pyqtSlot(Provider)
    def symbols_updated(self, market):
        market.sig.symbol_updated.disconnect(self.symbols_updated)
        self.market = market
        self.title_label.setText(self.provider.name)
        self.symbol_info.clear_info()
        self.list_widget.clear()

        for k, symbol in self.market.symbols.items():
            if symbol.state in ['Open', 'TRADING']:
                QListWidgetItem(symbol.name, self.list_widget)

        self.list_widget.sortItems()
        self.list_widget.itemClicked.connect(self.symbol_info.symbol_selected)


class SymbolInfo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        self.symbol = None

        self.vbox = QVBoxLayout(self)
        group1 = QGroupBox()

        group1.setTitle('Overview')
        vbox1 = QVBoxLayout()
        self.symbol_name = QLabel(self)
        self.symbol_name.setMaximumHeight(25)
        vbox1.addWidget(self.symbol_name)
        group1.setLayout(vbox1)

        group2 = QGroupBox()
        group2.setTitle('Functions')
        group2.setMaximumHeight(70)
        hbox = QHBoxLayout()

        chart_btn = QPushButton('Chart')
        chart_btn.clicked.connect(self.open_chart)
        chart_btn.setDisabled(True)
        hbox.addWidget(chart_btn)

        trade_btn = QPushButton('Trade')
        trade_btn.clicked.connect(self.open_trade)
        trade_btn.setDisabled(True)
        hbox.addWidget(trade_btn)

        order_btn = QPushButton('Order')
        order_btn.clicked.connect(self.open_order)
        order_btn.setDisabled(True)
        hbox.addWidget(order_btn)
        group2.setLayout(hbox)

        group3 = QGroupBox()
        group3.setTitle('Overview')
        vbox1 = QVBoxLayout()
        symbol_name = QLabel('XBTUSD', self)
        symbol_name.setMaximumHeight(25)
        vbox1.addWidget(symbol_name)
        group3.setLayout(vbox1)

        self.vbox.addWidget(group1)
        self.vbox.addWidget(group2)
        self.vbox.addWidget(group3)

    def clear_info(self):
        pass

    @pyqtSlot(QListWidgetItem)
    def symbol_selected(self, item):
        self.symbol = item.text()
        self.symbol_name.setText(item.text())
        btns = self.findChildren(QPushButton)
        [btn.setDisabled(False) for btn in btns]

    @pyqtSlot()
    def open_chart(self):
        dock3 = QDockWidget(self)
        dock3.setObjectName('dock3')
        dock3.setMinimumWidth(640)
        dock3.setMinimumHeight(480)
        dock3.setWidget(QPushButton(self.symbol))

        win = QMainWindow()
        win.addDockWidget(Qt.TopDockWidgetArea, dock3)
        self.vbox.addWidget(win)
        win.setWindowFlags(Qt.Window)

    @pyqtSlot()
    def open_trade(self):
        pass

    @pyqtSlot()
    def open_order(self):
        pass
