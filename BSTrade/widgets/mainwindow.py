import json

from PyQt5.QtCore import Qt, QAbstractTableModel, QSize, QRect
from PyQt5.QtGui import QIcon, QFont, QFontMetrics, QPixmap
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QDockWidget, QTableView, QAction, QTabWidget, QTabBar, QPushButton, \
    QLabel

from source_clients.bitmexwsclient import BitmexWsClient


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

    def slot_ws_subscribed(self, schema):
        print(schema)

    def slot_ws_append_text(self, msg):
        j = json.loads(msg)

        table_name = j.get('table')
        if table_name == 'trade':
            print(msg)
            self.data.append(msg)
        elif table_name == 'quote':
            print(msg)
            self.data.append(msg)


class OrderBookTableView(QTableView):
    pass


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        f = self.property('font')
        fm = QFontMetrics(f)
        w = fm.boundingRect(QRect(0, 0, 0, 0), Qt.AlignLeft, self.tabText(index)).width()
        return QSize(w + 30, size.height())


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ws = BitmexWsClient(test=False)

        self.setup_ui()

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

        button = QPushButton()
        font = QFont()
        font.setFamily('fontawesome')
        font.setPixelSize(32)

        button.setFont(font)
        button.setText('haahaahha')
        button.setIcon(QIcon(QPixmap(":/svg/regular/home.svg")))

        self.tabs.addTab(button, 'Big with test title')

        for i in range(10):
            self.tabs.addTab(QTextEdit(), 'text{}'.format(i))

        self.setCentralWidget(self.tabs)

        self.add_menus_and_exit()
        self.setup_dock_widgets()

    def add_menus_and_exit(self):
        self.statusBar().showMessage('Text in statusbar')

        menubar = self.menuBar()  # create menu bar

        file_menu = menubar.addMenu('File')  # add first menu

        new_icon = QIcon(':/icons/new_icon.png')  # create icon
        new_action = QAction(new_icon, 'New', self)  # add icon to menu
        new_action.setStatusTip('New File')  # update statusBar
        file_menu.addAction(new_action)  # add Action to menu item

        file_menu.addSeparator()  # add separator line between menu items

        exit_icon = QIcon(':/icons/exit_icon.png')  # create icon
        exit_action = QAction(exit_icon, 'Exit', self)  # create Exit Action
        exit_action.setStatusTip('Click to exit the application')
        exit_action.triggered.connect(self.close)  # close application when clicked
        exit_action.setShortcut('Ctrl+Q')  # keyboard shortcut, window has focus
        file_menu.addAction(exit_action)

        # ---------------------------------
        edit_menu = menubar.addMenu('Edit')  # add a second menu

    def setup_dock_widgets(self):
        dock1 = QDockWidget()
        dock1.setMinimumWidth(200)
        dock1.setMinimumHeight(100)
        dock1.setWindowTitle("Recent Trade")

        orderbook = OrderBookTableView(self)
        orderbook_model = OrderBookModel(parent=self, ws_source=self.ws)
        orderbook.setModel(orderbook_model)
        dock1.setWidget(orderbook)

        self.addDockWidget(Qt.RightDockWidgetArea, dock1)

        dock2 = QDockWidget()
        dock2.setMinimumWidth(200)
        dock2.setMinimumHeight(100)
        dock2.setWindowTitle("Left dock")
        self.addDockWidget(Qt.LeftDockWidgetArea, dock2)
