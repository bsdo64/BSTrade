from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QWidget, QHBoxLayout

from .View import ChartView, XAxisView, YAxisView
from BSTrade.util.fn import attach_timer

class ChartPane:
    def __init__(self, chart: ChartView, axis: YAxisView):
        self.chart = chart
        self.axis = axis

    def widget(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        h_box = QHBoxLayout()
        h_box.addWidget(self.chart)
        h_box.addWidget(self.axis)
        h_box.setContentsMargins(0, 0, 0, 0)
        h_box.setSpacing(1)
        widget.setLayout(h_box)
        return widget


class TimePane:
    def __init__(self, axis: XAxisView):
        self.axis = axis
        self.empty_view = QWidget()
        self.empty_view.setFixedSize(56, 20)

    def widget(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        widget.setMaximumHeight(20)
        h_box = QHBoxLayout()
        h_box.addWidget(self.axis)
        h_box.addWidget(self.empty_view)
        h_box.setContentsMargins(0, 0, 0, 0)
        h_box.setSpacing(1)
        widget.setLayout(h_box)
        return widget


class LayoutManager:
    def __init__(self, parent=None, ):
        self.tc = parent

        # Create default main BSChart pane
        self._chart_panes = []
        self._x_axis_pane = None

        # Create BSChart pane container
        self._container = QSplitter(parent)
        self.setup_ui(self._container)

    def init_layout(self, x_view):
        self._x_axis_pane = TimePane(x_view)

        return (
            self.create_chart_containter(),
            self._x_axis_pane.widget(self.tc)
        )

    def connect_wheel(self, pane, time_pane):
        pane.chart.sig_chart_wheel.connect(
            time_pane.axis.wheelEvent
        )
        pane.chart.sig_chart_wheel.connect(
            pane.axis.wheelEvent
        )

    def disconnect_wheel(self, pane, time_pane):
        pane.chart.sig_chart_wheel.disconnect(
            time_pane.axis.wheelEvent
        )
        pane.chart.sig_chart_wheel.disconnect(
            pane.axis.wheelEvent
        )

    def setup_ui(self, container):
        container.setOrientation(Qt.Vertical)
        container.setChildrenCollapsible(False)
        container.setHandleWidth(2)
        container.setContentsMargins(0, 0, 0, 0)

    def del_last_pane(self, checked=False):

        count = self._container.count()
        if count > 1:
            pane = self._chart_panes.pop(count - 1)
            self._container.widget(count - 1).deleteLater()
            self.disconnect_wheel(pane, self._x_axis_pane)

    def del_pane(self, index: int):
        if index == 0:
            return False

        pane = self._chart_panes.pop(index)
        self._container.widget(index).deleteLater()
        self.disconnect_wheel(pane, self._x_axis_pane)

    def add_pane(self, pane):
        self.connect_wheel(pane, self._x_axis_pane)

        self._chart_panes.append(pane)
        self._container.addWidget(pane.widget(self.tc))

    def create_chart_containter(self) -> QSplitter:
        return self._container

    def create_chart_pane(self, chart_view, axis_view) -> ChartPane:
        pane = ChartPane(chart_view, axis_view)
        self._chart_panes.append(pane)
        return pane


attach_timer(LayoutManager)
