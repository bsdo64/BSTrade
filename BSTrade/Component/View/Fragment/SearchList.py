from PyQt5.QtWidgets import QGroupBox

from BSTrade.Component.Model import QListModel
from BSTrade.Component.View.Ui import ui_frag_search_box
from BSTrade.Component.conf import load_ui

_ui: ui_frag_search_box.Ui_GroupBox = load_ui('frag_search_box')


class SearchListBoxView(QGroupBox, _ui):
    def __init__(self, model: QListModel, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setMaximumWidth(200)

        self.searchList.setModel(model)

    def set_model(self, model):
        self.searchList.setModel(model)
