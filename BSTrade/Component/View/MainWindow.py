from PyQt5.QtWidgets import QMainWindow

from BSTrade.Component.conf import load_ui
from BSTrade.Component.ViewModel import MainWindowViewModel
from BSTrade.Component.View.Fragment.SearchList import SearchListBoxView
from BSTrade.Component.View.Ui import ui_mainwindow

_ui: ui_mainwindow.Ui_MainWindow = load_ui('mainwindow')


class MainWindowView(QMainWindow, _ui):
    def __init__(self, model: MainWindowViewModel, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.model = model

        self.exchangeNameLb.setText(model.exchange.name)
        self.search_box = SearchListBoxView(model.sym_list_model)
        self.symbol_layout.insertWidget(0, self.search_box)
