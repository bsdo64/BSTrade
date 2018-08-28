from typing import TYPE_CHECKING

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter

from BSTrade.util.fn import attach_timer
from .ChartCreator import TimeSeriesChartCreator as ChartCreator
from .Layouts import LayoutManager
from .Model import ChartModel

if TYPE_CHECKING:
    from BSTrade.Data.Models import Store


class TradeChart(QWidget):
    sig_init_gui = pyqtSignal()

    def __init__(self, model: ChartModel, options=None, parent: QWidget = None):
        super().__init__(parent)

        if options is None:
            options = {
                'provider': 'bitmex',
                'symbol': 'XBTUSD'
            }

        # ------ Init Data
        self.options = options
        self.model = model
        self.store: 'Store' = parent.store
        self.chart_creator = ChartCreator(self.model)
        self.tc_layout = LayoutManager(self)

        # ------ Init UI Components
        self.vbox = QVBoxLayout(self)

        # ------ Init setup
        self.setup_ui()
        self.init_signals()

    def setup_ui(self):
        self.setContentsMargins(0, 0, 0, 0)

        self.vbox.setSpacing(1)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        x_axis_view = self.chart_creator.create_x_time_view()
        chart_cont, x_axis_pane = self.tc_layout.init_layout(x_axis_view)
        self.vbox.addWidget(chart_cont)
        self.vbox.addWidget(x_axis_pane)

    def init_signals(self):
        self.store.sig_init.connect(self.slt_finish_read_data)

    def request_data(self):
        self.store.request_initial_data()

    def slt_finish_read_data(self):
        option = self.options
        option['chart_type'] = 'candle'
        self.add_chart(option)

    def add_chart(self, option):
        chart_view, y_axis = self.chart_creator.create_chart_view(option)
        chart_pane = self.tc_layout.create_chart_pane(chart_view, y_axis)
        self.tc_layout.add_pane(chart_pane)

    def set_symbol(self):
        pass

    def add_plot(self, chart_pane_idx):
        pass


attach_timer(TradeChart)
