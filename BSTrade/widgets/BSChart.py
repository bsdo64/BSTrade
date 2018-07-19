from PyQt5.QtWidgets import QWidget, QVBoxLayout

from BSTrade.util.fn import attach_timer
from BSTrade.layouts.manager import ChartLayoutManager


class BSChartWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setContentsMargins(0, 0, 0, 0)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(1)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.layout = ChartLayoutManager(self)
        self.vbox.addWidget(self.layout.get_chart_panes())
        self.vbox.addWidget(self.layout.get_time_axis())


attach_timer(BSChartWidget)
