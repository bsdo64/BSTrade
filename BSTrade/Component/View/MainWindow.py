from PyQt5.QtWidgets import QMainWindow

from BSTrade.Component.conf import load_ui
from BSTrade.Component.Model.App import AppModel
from BSTrade.Component.View.Ui import ui_mainwindow
from BSTrade.Component.View.Fragment.SearchList import SearchListBox

_ui: ui_mainwindow.Ui_MainWindow = load_ui('mainwindow')


class MainWindowView(QMainWindow, _ui):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.model: AppModel = model

        self.exchangeNameLb.setText(model.selected_exchange.name)
        self.search_box = SearchListBox(None)
        self.symbol_layout.insertWidget(0, self.search_box)

