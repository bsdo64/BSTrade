from PyQt5.QtWidgets import QWidget, QVBoxLayout

from BSTrade.Lib.BSChart.Layouts import LayoutManager
from BSTrade.util.fn import attach_timer
from BSTrade.data.bitmex.reader import DataReader


class ChartWidget(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.ws = parent.ws
        self.r = DataReader('bitmex', 'XBTUSD')

        self.setContentsMargins(0, 0, 0, 0)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(1)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.init_data()

    def init_data(self):
        self.r.start()
        self.r.sig_finished.connect(self.slt_finish_read_data)

    def is_ready(self):
        return hasattr(self, 'layout_mng')

    def get_manager(self):
        return self.layout_mng

    def slt_finish_read_data(self, df):
        self.layout_mng = LayoutManager(df, self)
        self.vbox.addWidget(self.layout_mng.get_chart())
        self.vbox.addWidget(self.layout_mng.get_time())


attach_timer(ChartWidget)
