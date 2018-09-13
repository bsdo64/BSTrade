from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor, QShowEvent
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QAction, \
    QToolBar, QPlainTextEdit, QWidget, QHBoxLayout, \
    QListWidget, \
    QListWidgetItem

from BSTrade.Data.controller import Api, bs_api
from BSTrade.Data.const import Provider
from BSTrade.Data.source import bs_ws
from BSTrade.Dialogs.SelectIndicator import IndicatorDialog
from BSTrade.Lib.BSChart import TradeChart
from BSTrade.Widgets.Exchange import ExchangeInfo
from BSTrade.Widgets.Factory import WidgetStore
from BSTrade.Widgets.OrderBookWidget import OrderBookWidget
from BSTrade.Widgets.RecentTradeWidget import RecentTradeTableView, \
    RecentTradeTableModel
from BSTrade.util.fn import attach_timer


class ExchangeList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setMaximumWidth(100)

        for prov in Provider:
            QListWidgetItem(prov.name, self)


class CentralWidget(QWidget):
    def __init__(self, parent: 'Main'):
        super().__init__(parent)
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)

        self.hbox = QHBoxLayout(self)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSizeConstraint(self.hbox.SetDefaultConstraint)
        self.hbox.setSpacing(0)

        self.hbox.addWidget(QPlainTextEdit())

    def toggle_left_pane(self, b):
        pane_at = 0
        if b:
            exchange_list = ExchangeList(self)
            exchange_list.itemClicked.connect(self.select_provider)
            self.hbox.insertWidget(pane_at, exchange_list)
        else:
            btn: QWidget = self.hbox.itemAt(pane_at).widget()
            self.hbox.removeWidget(btn)
            btn.deleteLater()

    def select_provider(self, item: QListWidgetItem):
        prov = Provider[item.text()]
        action: QAction = self.parent.findChild(QAction, 'ex_action')
        action.trigger()

        self.set_exchange_view()
        self.parent.view_store.ExchangeInfo.exchange_selected(prov)

    def set_exchange_view(self):
        layout_item = self.hbox.itemAt(0)
        center_widget = layout_item.widget()
        if isinstance(center_widget, ExchangeInfo):
            return
        else:
            center_widget.deleteLater()
            self.hbox.removeItem(layout_item)
            self.hbox.addWidget(self.parent.view_store.ExchangeInfo)


attach_timer(CentralWidget)


class Main(QMainWindow):
    def __init__(self, database, parent=None):
        super().__init__(parent)

        self.db = database
        self.indi_dialog = IndicatorDialog(self)
        self.setup_ui()

    def showEvent(self, ev: QShowEvent):
        super().showEvent(ev)
        """
        UI finished

        init data
        :param ev:
        :return:
        """
        self.view_store = WidgetStore(self)
        bs_ws.start_all()

    def setup_ui(self):

        self.resize(1024, 768)
        self.setObjectName("MainWindow")
        self.setWindowTitle("BSTrade")
        self.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(CentralWidget(self))
        self.setup_menus()
        self.setup_toolbar()
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
