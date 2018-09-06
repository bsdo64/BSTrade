from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QIcon, QFontMetrics, QPalette, QColor
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QAction, \
    QTabWidget, QTabBar, QToolBar, QPlainTextEdit, QWidget, QHBoxLayout, \
    QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy

from BSTrade.util.fn import attach_timer
from BSTrade.Data.Models import Store, Api
from BSTrade.Lib.BSChart import TradeChart
from BSTrade.Widgets.RecentTradeWidget import RecentTradeTableView, RecentTradeTableModel
from BSTrade.Widgets.OrderBookWidget import OrderBookWidget
from BSTrade.Dialogs.SelectIndicator import IndicatorDialog


class LeftMenuButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)


class LeftMenu(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSizeConstraint(vbox.SetDefaultConstraint)
        vbox.setSpacing(0)

        vbox.addWidget(LeftMenuButton('Market'))
        vbox.addWidget(LeftMenuButton('Trade'))
        vbox.addWidget(LeftMenuButton('Account'))
        vbox.addWidget(LeftMenuButton('Exchange'))
        vbox.addWidget(LeftMenuButton('Chart'))
        vbox.addItem(QSpacerItem(60, 10,
                                 QSizePolicy.Minimum,
                                 QSizePolicy.Expanding))


class CentralWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSizeConstraint(hbox.SetDefaultConstraint)
        hbox.setSpacing(0)

        left_menu = LeftMenu(self)

        hbox.addWidget(left_menu)
        hbox.addWidget(QPlainTextEdit())


class Main(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.api = Api(self)
        self.indi_dialog = IndicatorDialog(self)
        self.setup_ui()

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
        chart_model = self.api.store.create_chart_model(
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
