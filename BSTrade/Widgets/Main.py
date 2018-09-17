from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor, QShowEvent
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QAction, \
    QToolBar

from BSTrade.Data.controller import bs_api
from BSTrade.Data.source import bs_ws
from BSTrade.Lib.BSChart import TradeChart
from BSTrade.Widgets.Factory import WidgetStore
from BSTrade.Widgets.OrderBookWidget import OrderBookWidget
from BSTrade.Widgets.RecentTradeWidget import RecentTradeTableView, \
    RecentTradeTableModel
from BSTrade.util.fn import attach_timer


class Main(QMainWindow):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.init_size = (1024, 768)
        self.is_gui_init = False
        self.db = database

    def showEvent(self, ev: QShowEvent):
        super().showEvent(ev)
        """
        UI finished

        init data
        :param ev:
        :return:
        """
        if self.is_gui_init:
            return

        self.view_store = WidgetStore(self)
        self.setup_ui()

        bs_ws.start_all()

        self.is_gui_init = True

    def setup_ui(self):
        self.view_store.LoadingDialog.show()

        self.resize(self.init_size[0], self.init_size[1])
        self.setObjectName("MainWindow")
        self.setWindowTitle("BSTrade")
        self.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(self.view_store.CentralWidget)
        self.setup_menus()
        self.setupToolbar()
        # self.setup_docks()
        # self.setup_indicators(self.indi_dialog)

    def setup_menus(self):
        menubar = self.menuBar()  # create menu bar

        file_menu = menubar.addMenu('File')  # add first menu

        new_icon = QIcon('BSTrade/Resource/icons/new_icon.png')  # create icon
        new_action = QAction(new_icon, 'New', self)  # add icon to menu
        new_action.setStatusTip('New File')  # update statusBar
        file_menu.addAction(new_action)  # add Action to menu item

        file_menu.addSeparator()  # add separator line between menu items

        exit_icon = QIcon(
            'BSTrade/Resource/icons/exit_icon.png')  # create icon
        exit_action = QAction(exit_icon, 'Exit', self)  # create Exit Action
        exit_action.setStatusTip('Click to exit the application')
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut(
            'Ctrl+Q')  # keyboard shortcut, window has focus
        file_menu.addAction(exit_action)

        # ---------------------------------
        edit_menu = menubar.addMenu('Edit')  # add a second menu

    def setupToolbar(self):
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

        menubar2 = QToolBar(self)
        menubar2.setOrientation(Qt.Vertical)
        ex_action: QAction = menubar2.addAction('Exchange')
        ex_action.setObjectName('ex_action')
        ex_action.setCheckable(True)
        ex_action.triggered.connect(self.centralWidget().toggle_left_pane)
        menubar2.addAction('Market').setCheckable(True)
        menubar2.addAction('Chart').setCheckable(True)
        menubar2.addAction('Trade').setCheckable(True)
        menubar2.addAction('Account').setCheckable(True)
        self.addToolBar(Qt.LeftToolBarArea, menubar2)

    def slt_add_chart(self, checked):
        print(self.findChild(QDockWidget, 'chart'))
        # bschart: TradeChart = self.tabs.widget(0)

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
        bschart: TradeChart = self.findChildren()
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
        recent_trade_model = RecentTradeTableModel(self,
                                                   view=recent_trade_view)
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
        chart_model = bs_api.store.create_chart_model(
            'bitmex:XBTUSD',
            'tradebin1m'
        )
        chart = TradeChart(
            model=chart_model, parent=self
        )

        chart.request_data()

        # self.tabs.addTab(QTextEdit(), 'text{}'.format(i))

        dock3 = QDockWidget()
        dock3.setObjectName('chart')
        dock3.setWindowTitle("BSChart")
        dock3.setMinimumWidth(200)
        dock3.setMinimumHeight(100)
        dock3.setWidget(chart)

        self.addDockWidget(Qt.TopDockWidgetArea, dock3)
        self.resizeDocks([dock3], [500], Qt.Vertical)


attach_timer(Main)
