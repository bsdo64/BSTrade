from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLabel, QListWidget, QListWidgetItem, QDockWidget, QGroupBox, QPushButton, \
    QMainWindow

from BSTrade.Data.const import Provider


class ExchangeInfo(QWidget):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.main: 'QMainWindow' = parent
        self.provider = None
        self.api = api

        self.market = None  # self.api.store.markets[provider]
        self.vbox = QVBoxLayout(self)
        self.list_widget = QListWidget(self)
        self.title_label = QLabel("test", self)
        font = QFont()
        font.setPointSize(20)
        self.title_label.setFont(font)
        self.symbol_info = SymbolInfo()

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
        self.market = self.api.store.markets[prov]
        self.title_label.setText(prov.name)
        self.symbol_info.clear_info()

        self.list_widget.clear()
        for k, symbol in self.market.symbols.items():
            QListWidgetItem(symbol.name, self.list_widget)
        self.list_widget.sortItems()
        self.list_widget.itemClicked.connect(self.symbol_info.symbol_selected)

    def open_chart(self):
        dock3 = QDockWidget(self)
        dock3.setObjectName('dock3')
        dock3.setMinimumWidth(100)
        dock3.setMinimumHeight(100)
        dock3.setWidget(QWidget())

        self.main.addDockWidget(Qt.TopDockWidgetArea, dock3)
        dock3.setFloating(True)
        dock3.setAllowedAreas(Qt.NoDockWidgetArea)


class SymbolInfo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vbox = QVBoxLayout(self)
        group1 = QGroupBox()

        group1.setTitle('Overview')
        vbox1 = QVBoxLayout()
        self.symbol_name = QLabel('XBTUSD', self)
        self.symbol_name.setMaximumHeight(25)
        vbox1.addWidget(self.symbol_name)
        group1.setLayout(vbox1)

        group2 = QGroupBox()
        group2.setTitle('Functions')
        group2.setMaximumHeight(80)
        hbox = QHBoxLayout()
        hbox.addWidget(QPushButton('Chart'))
        hbox.addWidget(QPushButton('Trade'))
        hbox.addWidget(QPushButton('Orders'))
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
        self.symbol_name.setText(item.text())