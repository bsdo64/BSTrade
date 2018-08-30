from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon, QFontMetrics, QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QAction, \
    QTabWidget, QTabBar, QToolBar, QPlainTextEdit, QWidget

from BSTrade.util.fn import attach_timer
from BSTrade.Data.Models import Store, Api
from BSTrade.Lib.BSChart import TradeChart
from BSTrade.Widgets.RecentTradeWidget import RecentTradeTableView, RecentTradeTableModel
from BSTrade.Widgets.OrderBookWidget import OrderBookWidget
from BSTrade.Dialogs.SelectIndicator import IndicatorDialog


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        f = self.property('font')
        fm = QFontMetrics(f)
        w = fm.boundingRect(QRect(0, 0, 0, 0),
                            Qt.AlignLeft,
                            self.tabText(index)).width()
        return QSize(w + 30, size.height())


class CentralWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)


class Main(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tabs = QTabWidget()
        self.api = Api(self)
        self.indi_dialog = IndicatorDialog(self)
        self.setup_ui()

    def setup_ui(self):
        self.resize(1024, 768)
        self.setObjectName("MainWindow")
        self.setWindowTitle("BSTrade")

        self.setCentralWidget(CentralWidget(self))
        self.setup_menus()
        self.setup_toolbar()
        # self.setup_docks()
        # self.setup_indicators(self.indi_dialog)

    def setup_data(self):
        self.api.Candle.request(self.config['provider'], 'XBTUSD', '1m')

    def setup_menus(self):
        # self.statusBar().showMessage('Text in statusbar')

        menubar = self.menuBar()  # create menu bar

        file_menu = menubar.addMenu('File')  # add first menu

        new_icon = QIcon('BSTrade/Resource/icons/new_icon.png')  # create icon
        new_action = QAction(new_icon, 'New', self)  # add icon to menu
        new_action.setStatusTip('New File')  # update statusBar
        file_menu.addAction(new_action)  # add Action to menu item

        file_menu.addSeparator()  # add separator line between menu items

        exit_icon = QIcon('BSTrade/Resource/icons/exit_icon.png')  # create icon
        exit_action = QAction(exit_icon, 'Exit', self)  # create Exit Action
        exit_action.setStatusTip('Click to exit the application')
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut('Ctrl+Q')  # keyboard shortcut, window has focus
        file_menu.addAction(exit_action)

        # ---------------------------------
        edit_menu = menubar.addMenu('Edit')  # add a second menu

    def setup_toolbar(self):
        palette = QPalette()
        palette.setColor(QPalette.Text, QColor('#ffffff'))

        chartbar: QToolBar = self.addToolBar('BSChart')
        chartbar.setPalette(palette)

        add_chart_act = chartbar.addAction('add')
        add_chart_act.triggered.connect(self.slt_add_chart)

        del_chart_act = chartbar.addAction('del')
        del_chart_act.triggered.connect(self.slt_del_chart)

        indicator_act = chartbar.addAction('indi')
        indicator_act.triggered.connect(self.slt_open_indicator)

    def slt_add_chart(self, checked):
        bschart: TradeChart = self.tabs.widget(0)
        pass
        # if bschart.is_ready():
        #     layout_manager = bschart.get_manager()
        #     layout_manager.add_pane()

    def slt_del_chart(self, checked):
        bschart: TradeChart = self.tabs.widget(0)
        pass

    def setup_indicators(self, dialog):
        dialog.sig_open_indicator.connect(self.slt_add_indicator)

    def slt_open_indicator(self, checked):
        self.indi_dialog.show()

    def slt_add_indicator(self, indi):
        bschart: TradeChart = self.tabs.widget(0)
        pass
        # if bschart.is_ready():
        #     layout_manager = bschart.get_manager()
        #     layout_manager.add_pane(chart_type='indicator', indi=indi)

    def setup_docks(self):
        # self.create_trade_dock()
        # self.order_book_dock()
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
        chart_model = self.api.store.create_chart_model(
            'bitmex:XBTUSD',
            'tradebin1m'
        )
        chart = TradeChart(
            model=chart_model, parent=self
        )
        self.tabs.addTab(chart, 'Bitmex:XBTUSD')
        chart.request_data()

        # self.tabs.addTab(QTextEdit(), 'text{}'.format(i))

        dock3 = QDockWidget()
        dock3.setWindowTitle("BSChart")
        dock3.setMinimumWidth(200)
        dock3.setMinimumHeight(100)
        dock3.setWidget(self.tabs)

        self.addDockWidget(Qt.TopDockWidgetArea, dock3)
        self.resizeDocks([dock3], [500], Qt.Vertical)

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        widget.deleteLater()
        self.tabs.removeTab(index)


attach_timer(Main)
