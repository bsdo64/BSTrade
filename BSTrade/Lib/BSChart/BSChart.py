from PyQt5.QtWidgets import QWidget, QVBoxLayout

from BSTrade.Data.Models import DataManager
from BSTrade.Lib.BSChart.Layouts import LayoutManager
from BSTrade.Widgets import Main
from BSTrade.util.fn import attach_timer
from BSTrade.Data.bitmex.reader import DataReader


class BSChart(QWidget):
    def __init__(self, options=None, parent: Main = None):
        QWidget.__init__(self, parent)

        if options is None:
            options = {
                'provider': 'bitmex',
                'symbol': 'XBTUSD'
            }

        self.options = options
        self.ws = parent.ws
        self.store: DataManager = parent.store

        self.setContentsMargins(0, 0, 0, 0)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(1)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.init_data()

    def init_data(self):
        self.store.set_initial_data()
        self.store.sig_init.connect(self.slt_finish_read_data)

    def is_ready(self):
        return hasattr(self, 'layout_mng')

    def get_manager(self):
        return self.layout_mng

    def slt_finish_read_data(self):
        self.layout_mng = LayoutManager(self.store, self)
        self.vbox.addWidget(self.layout_mng.get_chart())
        self.vbox.addWidget(self.layout_mng.get_time())


attach_timer(BSChart)
