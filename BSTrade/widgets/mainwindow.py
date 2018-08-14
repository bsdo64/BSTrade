from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon, QFontMetrics
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QDockWidget, QAction, \
    QTabWidget, QTabBar

from BSTrade.source_clients.auth.bitmex import api_keys
from BSTrade.source_clients.bitmexwsclient import BitmexWsClient
from BSTrade.util.fn import attach_timer

from .BSChart import BSChartWidget
from .recenttrade import RecentTradeTableView, RecentTradeTableModel
from .orderbook import OrderBookWidget


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        f = self.property('font')
        fm = QFontMetrics(f)
        w = fm.boundingRect(QRect(0, 0, 0, 0),
                            Qt.AlignLeft,
                            self.tabText(index)).width()
        return QSize(w + 30, size.height())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.tabs = QTabWidget()
        self.ws = BitmexWsClient(test=False,
                                 api_key=api_keys['real']['order']['key'],
                                 api_secret=api_keys['real']['order']['secret'])

        self.setup_ws(self.ws)
        self.setup_main_ui()
        self.setup_menus()
        self.setup_docks()

    def setup_ws(self, ws):
        ws.sig_connected.connect(self.slt_ws_connected)
        ws.start()

    def setup_main_ui(self):
        self.resize(1024, 768)
        self.setObjectName("MainWindow")
        self.setWindowTitle("BSTrade")

        self.setCentralWidget(QTextEdit())

    def setup_menus(self):
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
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')  # keyboard shortcut, window has focus
        file_menu.addAction(exit_action)

        # ---------------------------------
        edit_menu = menubar.addMenu('Edit')  # add a second menu

    def setup_docks(self):
        self.create_trade_dock()
        self.order_book_dock()
        self.create_chart_dock()

    def create_trade_dock(self):
        dock1 = QDockWidget()
        dock1.setMinimumWidth(200)
        dock1.setMinimumHeight(100)
        dock1.setWindowTitle("Recent Trade")

        recent_trade_view = RecentTradeTableView(self, ws=self.ws)
        recent_trade_model = RecentTradeTableModel(self, view=recent_trade_view)
        recent_trade_view.setModel(recent_trade_model)
        recent_trade_view.setup_ui()
        dock1.setWidget(recent_trade_view)

        self.addDockWidget(Qt.RightDockWidgetArea, dock1)

    def order_book_dock(self):
        dock2 = QDockWidget()
        dock2.setMinimumWidth(200)
        dock2.setMinimumHeight(100)
        dock2.setWindowTitle("OrderBook")

        dock2.setWidget(OrderBookWidget(self.ws, self))

        self.addDockWidget(Qt.LeftDockWidgetArea, dock2)

    def create_chart_dock(self):
        self.tabs.setTabBar(TabBar())
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setUsesScrollButtons(True)
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

        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.addTab(BSChartWidget(self), 'Bitmex:XBTUSD')

        # self.tabs.addTab(QTextEdit(), 'text{}'.format(i))

        dock3 = QDockWidget()
        dock3.setMinimumWidth(200)
        dock3.setMinimumHeight(100)
        dock3.setWidget(self.tabs)

        self.addDockWidget(Qt.TopDockWidgetArea, dock3)
        self.resizeDocks([dock3], [500], Qt.Vertical)

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        widget.deleteLater()
        self.tabs.removeTab(index)

    def slt_ws_connected(self):
        # web socket client connected

        self.ws.auth()

        self.ws.subscribe('trade:XBTUSD',
                          'tradeBin1m:XBTUSD',
                          'orderBookL2:XBTUSD')


attach_timer(MainWindow)
