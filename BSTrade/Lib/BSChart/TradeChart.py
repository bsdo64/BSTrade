from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QWidget, QVBoxLayout

from BSTrade.util.fn import attach_timer
from .ChartCreator import TimeSeriesChartCreator as ChartCreator

if TYPE_CHECKING:
    from BSTrade.Data.Models import Store


class TradeChart(QWidget):
    def __init__(self, options=None, parent: QWidget = None):
        super().__init__(parent)

        if options is None:
            options = {
                'provider': 'bitmex',
                'symbol': 'XBTUSD'
            }

        # ------ Init Data
        self.options = options
        self.store: 'Store' = parent.store
        self.chart_creator = ChartCreator(self.store, parent=self)

        # ------ Init UI Components
        self.vbox = QVBoxLayout(self)

        # ------ Init setup
        self.setup_ui()
        self.init_signals()

    def setup_ui(self):
        self.setContentsMargins(0, 0, 0, 0)

        self.vbox.setSpacing(1)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        chart_cont, x_axis_pane = self.chart_creator.init_layout()
        self.vbox.addWidget(chart_cont)
        self.vbox.addWidget(x_axis_pane)

    def init_signals(self):
        self.store.sig_init.connect(self.slt_finish_read_data)

    def request_data(self):
        self.store.request_initial_data()

    def slt_finish_read_data(self):
        chart_cont = self.vbox.itemAt(0).widget()
        x_axis_pane = self.vbox.itemAt(1).widget()


attach_timer(TradeChart)
