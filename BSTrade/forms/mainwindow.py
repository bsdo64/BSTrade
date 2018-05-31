import json

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QDockWidget, QTableView

from source_clients.bitmexwsclient import BitmexWsClient
from queue import Queue


class OrderBookModel(QAbstractTableModel):
    def __init__(self, parent=None, ws_source=None):
        super(OrderBookModel, self).__init__(parent)
        self.ws = ws_source
        self.ws.sig_connected.connect(self.slot_ws_connected)
        self.ws.sig_message.connect(self.slot_ws_append_text)
        self.ws.sig_subscribed.connect(self.slot_ws_subscribed)
        self.ws.start()

        self.data = []

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.data)

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self.data[index].get('table')

        return None

    def slot_ws_connected(self):
        self.ws.subscribe("trade:XBTUSD")

    def slot_ws_subscribed(self, types):
        print(types)

    def slot_ws_append_text(self, msg):
        j = json.loads(msg)

        is_table = j.get('table')
        if is_table == 'trade':
            print(msg)
            self.data.append(msg)


class OrderBookTableView(QTableView):
    pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ws = BitmexWsClient(test=False)


        self.setup_ui()

    def setup_ui(self):
        self.resize(1024, 768)
        self.setObjectName("MainWindow")
        self.setWindowTitle("BSTrade")

        center = QTextEdit()
        center.setMinimumSize(200, 480)
        self.setCentralWidget(center)

        self.setup_dock_widgets()

    def setup_dock_widgets(self):
        dock1 = QDockWidget()
        dock1.setMinimumWidth(200)
        dock1.setMinimumHeight(100)
        dock1.setWindowTitle("Right dock")

        orderbook = OrderBookTableView()
        orderbook_model = OrderBookModel(ws_source=self.ws)
        orderbook.setModel(orderbook_model)
        dock1.setWidget(orderbook)

        self.addDockWidget(Qt.RightDockWidgetArea, dock1)

        dock2 = QDockWidget()
        dock2.setMinimumWidth(200)
        dock2.setMinimumHeight(100)
        dock2.setWindowTitle("Left dock")
        self.addDockWidget(Qt.LeftDockWidgetArea, dock2)
