from PyQt5.QtCore import QAbstractListModel, Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QGroupBox

from BSTrade.Component.Model.App import AppModel
from BSTrade.Component.View.Ui import ui_frag_search_box
from BSTrade.Component.conf import load_ui

_ui: ui_frag_search_box.Ui_GroupBox = load_ui('frag_search_box')


class ListModel(QAbstractListModel):
    def __init__(self, parent):
        super().__init__(parent)
        self._data = ['hello', 'world']

    def data(self, index: QModelIndex, role=None):
        row = index.row()
        if role == Qt.DisplayRole:
            return self._data[row]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)

    def columnCount(self, *args, **kwargs):
        return 1


class SearchListBox(QGroupBox, _ui):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setMaximumWidth(200)

        self.searchList.setModel(ListModel(self))