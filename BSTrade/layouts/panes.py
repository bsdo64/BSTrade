from PyQt5.QtWidgets import QWidget, QHBoxLayout

from BSTrade.widgets.chart.graphic_views import TimeAxisView, ChartView, \
    ChartAxisView


class ChartPane:
    def __init__(self, chart: ChartView, axis: ChartAxisView):
        self.chart = chart
        self.axis = axis

    def create(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        h_box = QHBoxLayout()
        h_box.addWidget(self.chart)
        h_box.addWidget(self.axis)
        h_box.setContentsMargins(0, 0, 0, 0)
        h_box.setSpacing(1)
        widget.setLayout(h_box)
        return widget


class ChartTimePane:
    def __init__(self, axis: TimeAxisView):
        self.axis = axis
        self.empty_view = QWidget()
        self.empty_view.setFixedSize(56, 20)

    def create(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        widget.setMaximumHeight(20)
        h_box = QHBoxLayout()
        h_box.addWidget(self.axis)
        h_box.addWidget(self.empty_view)
        h_box.setContentsMargins(0, 0, 0, 0)
        h_box.setSpacing(1)
        widget.setLayout(h_box)
        return widget

    def slot_set_model(self, model):
        print('hah')
        self.axis.add_model(model)
