import json
import dateutil.parser

from PyQt5.QtCore import Qt, QAbstractTableModel, QSize, QRect, \
    QAbstractItemModel, QModelIndex
from PyQt5.QtGui import QIcon, QFontMetrics, QColor, QFont, QPainter
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QDockWidget, QTableView, \
    QAction, QTabWidget, QTabBar, QHeaderView, QApplication

from BSTrade.source_clients.bitmexwsclient import BitmexWsClient
from BSTrade.util.fn import attach_timer
from .BSChart import BSChartWidget


class RecentTradeTableModel(QAbstractTableModel):
    def __init__(self, parent=None, view=None):
        QAbstractTableModel.__init__(self, parent)

        self.view = view
        self.data = []
        self.dataChanged.connect(self.haha)

    def haha(self,QModelIndex, QModelIndex_1, Iterable, p_int=None):
        self.view.update()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.data)

    def columnCount(self, parent=None, *args, **kwargs):
        return 4

    def data(self, index, role=None):
        row = index.row()
        col = index.column()
        data = self.data[row]

        if not index.isValid():
            return None

        if row >= len(self.data) or row < 0:
            return None

        if role == Qt.DisplayRole:
            if col == 0:
                return data['price']
            elif col == 1:
                return data['volume']
            elif col == 2:
                return data['timestamp']

        # elif role == Qt.BackgroundRole:
        #     if data['side'] == 'Sell':
        #         return QColor(Qt.red)

        elif role == Qt.ForegroundRole:
            if data['side'] == 'Sell':
                return QColor('#B9654A')
            else:
                return QColor('#6CA068')

        elif role == Qt.TextAlignmentRole:
            if col in (0, 1):
                return Qt.AlignRight

        return None

    def headerData(self, section, orientation, role=None):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return 'price'
            elif section == 1:
                return 'volume'
            elif section == 2:
                return 'time'
            elif section == 3:
                return 's'
            else:
                return None

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

    def insertRows(self, position: int, rows: int, index=None, *args, **kwargs):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.data.insert(position,
                             {'price': '', 'volume': '', 'timestamp': '', 'side': ''})
        self.endInsertRows()
        return True

    def removeRows(self, position: int, rows: int, index=None, *args, **kwargs):
        self.beendRemoveRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.data.pop(position)
        self.endRemoveRows()
        return True

    def setData(self, index, value, role=None):

        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            d = self.data[row]

            if index.column() == 0:
                d['price'] = "{:10.1f}".format(value)
            elif index.column() == 1:
                d['volume'] = "{:,}".format(value)
            elif index.column() == 2:
                p = dateutil.parser.parse(value)

                d['timestamp'] = "{:02}:{:02}:{:02}:{:03}".format(
                    p.hour, p.minute, p.second, p.microsecond // 1000)
            elif index.column() == 3:
                d['side'] = str(value)
            else:
                return False

            self.dataChanged.emit(index, index)
            return True

        return True


attach_timer(RecentTradeTableModel, limit=1)


class RecentTradeTableView(QTableView):
    def __init__(self, parent=None, ws: BitmexWsClient = None):
        QTableView.__init__(self, parent)

        self.ws = ws
        self.ws.sig_subscribed.connect(self.slot_ws_subscribed)
        self.ws.sig_message.connect(self.slot_ws_message)

        row_header: QHeaderView = self.verticalHeader()
        row_header.setSectionResizeMode(QHeaderView.Fixed)
        row_header.setDefaultSectionSize(15)

        col_header: QHeaderView = self.horizontalHeader()

        self.setColumnWidth(0, 20)
        self.setColumnWidth(1, 30)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(3, 5)

        self.setShowGrid(False)

    def slot_ws_subscribed(self, schema):
        print(schema)

    def slot_ws_message(self, msg):
        j = json.loads(msg)

        table_name = j.get('table')
        if table_name == 'trade':
            items = j.get('data')
            model: QAbstractItemModel = self.model()
            model.insert_data(items)


attach_timer(RecentTradeTableView)


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        f = self.property('font')
        fm = QFontMetrics(f)
        w = fm.boundingRect(QRect(0, 0, 0, 0), Qt.AlignLeft,
                            self.tabText(index)).width()
        return QSize(w + 30, size.height())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.ws = BitmexWsClient(test=False)
        self.ws.start()

        self.setup_ui()

        self.ws.sig_connected.connect(self.ws_connected)

    def ws_connected(self):
        # web socket client connected

        self.ws.subscribe("trade:XBTUSD")

    def closeTab(self, index):
        tab = self.tabs.widget(index)
        tab.deleteLater()
        self.tabs.removeTab(index)

    def setup_ui(self):
        self.resize(1024, 768)
        self.setObjectName("MainWindow")
        self.setWindowTitle("BSTrade")

        self.tabs = QTabWidget()
        self.tabs.setTabBar(TabBar())
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setUsesScrollButtons(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: lightgray;
                color: black;
                border: 0;
                /* min-width: 100px; */
                max-width: 200px;
                /* width: 150px; */
                height: 12px;
                padding: 5px;
                font-size: 11px;
                border: 1px solid #ebebeb;
            }
        
            QTabBar::tab:selected {
                background: gray;
                color: white;
            }
            
        """)

        self.tabs.addTab(BSChartWidget(self), 'Big with test title')

        for i in range(10):
            self.tabs.addTab(QTextEdit(), 'text{}'.format(i))

        self.setCentralWidget(self.tabs)

        self.add_menus_and_exit()
        self.setup_dock_widgets()

    def add_menus_and_exit(self):
        # self.statusBar().showMessage('Text in statusbar')

        menubar = self.menuBar()  # create menu bar

        file_menu = menubar.addMenu('File')  # add first menu

        new_icon = QIcon('BSTrade/icons/new_icon.png')  # create icon
        new_action = QAction(new_icon, 'New', self)  # add icon to menu
        new_action.setStatusTip('New File')  # update statusBar
        file_menu.addAction(new_action)  # add Action to menu item

        file_menu.addSeparator()  # add separator line between menu items

        exit_icon = QIcon('BSTrade/icons/exit_icon.png')  # create icon
        exit_action = QAction(exit_icon, 'Exit', self)  # create Exit Action
        exit_action.setStatusTip('Click to exit the application')
        exit_action.triggered.connect(
            self.close)  # close application when clicked
        exit_action.setShortcut('Ctrl+Q')  # keyboard shortcut, window has focus
        file_menu.addAction(exit_action)

        # ---------------------------------
        edit_menu = menubar.addMenu('Edit')  # add a second menu

    def setup_dock_widgets(self):
        dock1 = QDockWidget()
        dock1.setMinimumWidth(200)
        dock1.setMinimumHeight(100)
        dock1.setWindowTitle("Recent Trade")

        recent_trade_view = RecentTradeTableView(self, ws=self.ws)
        recent_trade_model = RecentTradeTableModel(self, view=recent_trade_view)
        recent_trade_view.setModel(recent_trade_model)
        dock1.setWidget(recent_trade_view)

        self.addDockWidget(Qt.RightDockWidgetArea, dock1)

        dock2 = QDockWidget()
        dock2.setMinimumWidth(200)
        dock2.setMinimumHeight(100)
        dock2.setWindowTitle("Left dock")
        self.addDockWidget(Qt.LeftDockWidgetArea, dock2)


attach_timer(MainWindow)
