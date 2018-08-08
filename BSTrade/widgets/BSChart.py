from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from BSTrade.layouts.manager import ChartLayoutManager
from BSTrade.util.fn import attach_timer


class BSChartWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # self.ws = parent.ws

        self.setContentsMargins(0, 0, 0, 0)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(1)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        # self.data = DataManager(self)
        self.layout = ChartLayoutManager(self)
        self.chart = self.layout.chart_pane()
        self.time = self.layout.time_pane()
        self.vbox.addWidget(self.chart)
        self.vbox.addWidget(self.time)

    def wheelEvent(self, event: QWheelEvent):
        super().wheelEvent(event)


attach_timer(BSChartWidget)
