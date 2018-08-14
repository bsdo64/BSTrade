import ujson as json
from bisect import bisect, bisect_left

from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex, QObject, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTableView, QHeaderView, QWidget, QVBoxLayout, \
    QLabel

from BSTrade.source_clients import BitmexWsClient
from BSTrade.util.fn import attach_timer
from BSTrade.optimize.math import price_from_id, id_from_price
from BSTrade.data.bitmex.instruments import inst


class OrderBookWidget(QWidget):
    def __init__(self, ws: BitmexWsClient, parent=None):
        QWidget.__init__(self, parent)
        self.ws = ws

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(1)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.sell_view = OrderBookView('sell', self)
        self.sell_view.setModel(OrderBookTableModel(self))
        self.sell_view.set_col_width()

        self.current = QLabel('1000', self)
        self.current.setMaximumHeight(30)
        self.current.setLineWidth(0)
        self.current.setTextFormat(Qt.AutoText)
        self.current.setScaledContents(False)
        self.current.setAlignment(Qt.AlignCenter)
        self.current.setIndent(0)
        self.current.setTextInteractionFlags(Qt.NoTextInteraction)

        self.buy_view = OrderBookView('buy', self)
        self.buy_view.setModel(OrderBookTableModel(self))
        self.buy_view.set_col_width()

        self.model = OrderBookModel(ws, inst['XBTUSD'],
                                    self.sell_view,
                                    self.current,
                                    self.buy_view,
                                    self)
        self.set_widget(self.sell_view, self.current, self.buy_view)

    def set_widget(self, sell, current, buy):
        self.layout.addWidget(sell)
        self.layout.addWidget(current)
        self.layout.addWidget(buy)


attach_timer(OrderBookWidget, limit=5)


class OrderBookView(QTableView):
    def __init__(self, order_type='sell', parent=None):
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

        self.order_type = order_type

    def set_data(self, items):
        model: OrderBookTableModel = self.model()
        model.insert_data(items)

    def set_col_width(self):
        # must call after __init__
        self.setColumnWidth(0, 60)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 80)


attach_timer(OrderBookView, limit=5)


class OrderBookModel(QObject):
    def __init__(self,
                 ws: BitmexWsClient, item,
                 sell_view: OrderBookView,
                 current: QLabel,
                 buy_view: OrderBookView,
                 parent=None):
        QObject.__init__(self, parent)

        self.inst = item
        self.ws = ws
        self.ws.sig_message.connect(self.slt_ws_message)

        self.price = 1000.
        self.price_idx = id_from_price(self.inst['idx'], self.price, 0.01)
        self.book_ids = []
        self.book = []

        self.sell_view = sell_view
        self.current_view = current
        self.buy_view = buy_view

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_view)
        self.timer.start()

    def slt_ws_message(self, msg):
        j = json.loads(msg)

        table_name = j.get('table')
        action = j.get('action')
        if table_name == 'orderBookL2':
            items = j.get('data')
            if action == 'partial':
                self.init_book(items)
            elif action == 'delete':
                self.delete_book(items)
            elif action == 'insert':
                self.insert_book(items)
            elif action == 'update':
                self.update_book(items)

        elif table_name == 'trade':
            items = j.get('data')
            self.set_current_text(items)

    def init_book(self, items):
        self.book = items
        self.book_ids = [i['id'] for i in items]

    def delete_book(self, items):
        for i in items:
            idx = bisect(self.book_ids, i['id'])

            if idx > 0:
                del self.book[idx - 1]
                del self.book_ids[idx - 1]

    def insert_book(self, items):
        for i in items:
            idx = bisect(self.book_ids, i['id'])

            if idx > 0:
                self.book_ids.insert(idx, i['id'])
                self.book.insert(idx, i)

    def update_book(self, items):
        for i in items:

            item_idx = bisect(
                self.book_ids,
                i['id']
            ) - 1

            if item_idx > -1:
                self.book[item_idx]['size'] = i['size']
                self.book[item_idx]['side'] = i['side']

    def update_view(self):
        bound_idx = bisect(
            self.book_ids,
            self.price_idx
        ) - 1

        if bound_idx > -1:
            b_idx = bound_idx + 1 if \
                self.book[bound_idx]['side'] == 'Sell' else \
                bound_idx

            self.sell_view.set_data(self.book[b_idx - 10:b_idx])
            self.buy_view.set_data(self.book[b_idx:b_idx + 10])

    def set_current_text(self, items):
        self.price = items[-1]['price']
        self.price_idx = id_from_price(self.inst['idx'], self.price, 0.01)
        self.current_view.setText(str(self.price))


attach_timer(OrderBookModel, limit=5)


class OrderBookTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.max_length = 10
        self.data = []
        self.init_table = False

    def rowCount(self, parent: QModelIndex = QModelIndex()):
        return len(self.data)

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return 3

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
                return data['size']
            elif col == 2:
                return data['total']

        elif role == Qt.ForegroundRole:
            if data['side'] == 'Sell':
                if col == 0:
                    return QColor('#B9654A')
            else:
                if col == 0:
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

        if not self.init_table:
            self.insertRows(0, len(items), idx)
            self.init_table = True

        for i, v in enumerate(items):
            index1 = self.index(i, 0, idx)
            self.setData(index1, v['price'], Qt.EditRole)
            index2 = self.index(i, 1, idx)
            self.setData(index2, v['size'], Qt.EditRole)

            self.data[i]['side'] = v['side']

            self.dataChanged.emit(index1, index2)

    def insertRows(self,
                   position: int, rows: int,
                   index: QModelIndex = QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.data.insert(
                position,
                {'price': '', 'size': '', 'total': '', 'side': ''}
            )
        self.endInsertRows()
        return True

    def removeRows(self,
                   position: int, rows: int,
                   index: QModelIndex = QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self.endRemoveRows()
        return True

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):

        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            d = self.data[row]

            if index.column() == 0:
                d['price'] = "{:10.1f}".format(value)
            elif index.column() == 1:
                d['size'] = "{:,}".format(value)
            elif index.column() == 2:
                d['total'] = ''
            else:
                return False

            return True

        return True


attach_timer(OrderBookTableModel, limit=5)
