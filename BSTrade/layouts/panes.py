from PyQt5.QtWidgets import QWidget, QHBoxLayout

from BSTrade.widgets.chart.graphic_views import TimeAxisView, ChartView, ChartAxisView


class ChartPane:
    def __init__(self, chart: ChartView, axis: ChartAxisView):
        self.chart = chart
        self.axis = axis

    def create(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        hbox = QHBoxLayout()
        hbox.addWidget(self.chart)
        hbox.addWidget(self.axis)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(1)
        widget.setLayout(hbox)
        return widget


class ChartTimePane:
    def __init__(self, axis: TimeAxisView):
        self.axis = axis
        self.empty_view = QWidget()
        self.empty_view.setFixedSize(56, 20)

    def create(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        widget.setMaximumHeight(20)
        hbox = QHBoxLayout()
        hbox.addWidget(self.axis)
        hbox.addWidget(self.empty_view)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(1)
        widget.setLayout(hbox)
        return widget
