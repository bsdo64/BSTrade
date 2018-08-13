import ujson as json

import ciso8601
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTableView, QHeaderView, QWidget, QVBoxLayout

from BSTrade.source_clients import BitmexWsClient
from BSTrade.util.fn import attach_timer


class OrderBookWidget(QWidget):
    def __init__(self, ws: BitmexWsClient, parent=None):
        QWidget.__init__(self, parent)
        self.ws = ws

        self.layout = QVBoxLayout()
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.model = OrderBookModel(ws)

        self.set_widget()

    def set_widget(self):
        self.layout.addWidget(OrderBookViewUp(self))
        self.layout.addWidget(OrderBookViewDown(self))


class OrderBookModel:
    def __init__(self, ws: BitmexWsClient):
        self.ws = ws
        self.ws.sig_message.connect(self.slt_ws_message)

    def slt_ws_message(self, msg):
        j = json.loads(msg)

        table_name = j.get('table')
        if table_name == 'orderBookL2':
            items = j.get('data')
            print(j.get('action'), items)
            # model: OrderBookUpModel = self.model()
            # model.insert_data(items)


class OrderBookViewUp(QTableView):
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(self.NoSelection)
        self.setShowGrid(False)
        self.setAutoScroll(False)

        row_header: QHeaderView = self.verticalHeader()
        row_header.setSectionResizeMode(QHeaderView.Fixed)
        row_header.setDefaultSectionSize(15)
        row_header.setHidden(True)

        column_header: QHeaderView = self.horizontalHeader()
        column_header.setHidden(True)

    def slot_ws_message(self, msg):

        j = json.loads(msg)

        table_name = j.get('table')
        if table_name == 'trade':
            items = j.get('data')
            model: OrderBookUpModel = self.model()
            model.insert_data(items)

    def setup_ui(self):
        self.setColumnWidth(0, 60)
        self.setColumnWidth(1, 70)
        self.setColumnWidth(2, 90)


class OrderBookViewDown(QTableView):
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(self.NoSelection)
        self.setShowGrid(False)
        self.setAutoScroll(False)

        row_header: QHeaderView = self.verticalHeader()
        row_header.setSectionResizeMode(QHeaderView.Fixed)
        row_header.setDefaultSectionSize(15)
        row_header.setHidden(True)

        column_header: QHeaderView = self.horizontalHeader()
        column_header.setHidden(True)

    def slot_ws_message(self, msg):

        j = json.loads(msg)

        table_name = j.get('table')
        if table_name == 'trade':
            items = j.get('data')
            model: OrderBookUpModel = self.model()
            model.insert_data(items)

    def setup_ui(self):
        self.setColumnWidth(0, 60)
        self.setColumnWidth(1, 70)
        self.setColumnWidth(2, 90)


class OrderBookUpModel(QAbstractTableModel):
    def __init__(self, parent=None, view=None):
        QAbstractTableModel.__init__(self, parent)

        self.max_length = 100
        self.view = view
        self.data = []

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        return len(self.data)

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return 4

    def data(self, index, role: int = Qt.DisplayRole):
        row = index.row()
        col = index.column()
        data = self.data[row]

        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            if col == 0:
                return data['price']
            elif col == 1:
                return data['volume']
            elif col == 2:
                return data['timestamp']

        elif role == Qt.ForegroundRole:
            if data['side'] == 'Sell':
                return QColor('#B9654A')
            else:
                return QColor('#6CA068')

        elif role == Qt.TextAlignmentRole:
            if col in (0, 1):
                return Qt.AlignRight

        elif role == Qt.FontRole:
            font = QFont()
            font.setPixelSize(11)
            return font

        return None

    def insert_data(self, items):

        idx = QModelIndex()
        self.insertRows(0, len(items), idx)
        for i, v in enumerate(reversed(items)):
            index = self.index(i, 0, idx)
            self.setData(index, v['price'], Qt.EditRole)
            index = self.index(i, 1, idx)
            self.setData(index, v['size'], Qt.EditRole)
            index = self.index(i, 2, idx)
            self.setData(index, v['timestamp'], Qt.EditRole)
            index = self.index(i, 3, idx)
            self.setData(index, v['side'], Qt.EditRole)

        if len(self.data) > self.max_length:
            self.removeRows(self.max_length,
                            len(self.data) - self.max_length,
                            idx)

    def insertRows(self,
                   position: int, rows: int,
                   index: QModelIndex = QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.data.insert(
                position,
                {'price': '', 'volume': '', 'timestamp': '', 'side': ''}
            )
        self.endInsertRows()
        return True

    def removeRows(self,
                   position: int, rows: int,
                   index: QModelIndex = QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.data.pop(position)
        self.endRemoveRows()
        return True

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):

        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            d = self.data[row]

            if index.column() == 0:
                d['price'] = "{:10.1f}".format(value)
            elif index.column() == 1:
                d['volume'] = "{:,}".format(value)
            elif index.column() == 2:
                p = ciso8601.parse_datetime(value)

                d['timestamp'] = "{:02}:{:02}:{:02}:{:03}".format(
                    p.hour, p.minute, p.second, p.microsecond//1000)
            elif index.column() == 3:
                d['side'] = str(value)
            else:
                return False

            self.dataChanged.emit(index, index)
            return True

        return True


attach_timer(OrderBookUpModel, limit=5)
