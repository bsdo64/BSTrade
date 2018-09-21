from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt


class QListModel(QAbstractListModel):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self._data = items

    def data(self, index: QModelIndex, role=None):
        row = index.row()
        if role == Qt.DisplayRole:
            return self._data[row]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)

    def columnCount(self, *args, **kwargs):
        return 1

    def append_item(self, item):
        self._data.append(item)
        idx = self.createIndex(len(self._data), 0)
        self.dataChanged.emit(idx, idx)