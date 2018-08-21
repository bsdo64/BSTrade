from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QWidget, QHBoxLayout

from BSTrade.Lib.BSChart.Charts import ChartView
from BSTrade.Lib.BSChart.Axis import YAxis, XAxis
from BSTrade.util.fn import attach_timer
from BSTrade.Data.Models import ChartModel, DataManager


class ChartPane:
    def __init__(self, chart: ChartView, axis: YAxis.AxisView):
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


class ChartTimePane:
    def __init__(self, axis: XAxis.TimeAxis):
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
    def __init__(self, data_manager: DataManager, parent=None,):
        self.parent = parent
        self.data_mng = data_manager

        chart_model = ChartModel(data)
        # Create default main BSChart pane
        self._chart_panes = [
            ChartPane(ChartView(chart_model), YAxis.AxisView(chart_model)),
        ]

        # Create main time axis pane
        self._time_pane = ChartTimePane(XAxis.TimeAxis(chart_model, parent))

        pane = self._chart_panes[0]
        self.connect_wheel(pane)

        # Create BSChart pane container
        self._container = QSplitter(parent)
        self.init_layout(self._container)

    def connect_wheel(self, pane):
        pane.chart.sig_chart_wheel.connect(
            self._time_pane.axis.wheelEvent
        )
        pane.chart.sig_chart_wheel.connect(
            pane.axis.wheelEvent
        )

    def disconnect_wheel(self, pane):
        pane.chart.sig_chart_wheel.disconnect(
            self._time_pane.axis.wheelEvent
        )
        pane.chart.sig_chart_wheel.disconnect(
            pane.axis.wheelEvent
        )

    def init_layout(self, container):
        container.setOrientation(Qt.Vertical)
        container.setChildrenCollapsible(False)
        container.setHandleWidth(2)
        container.setContentsMargins(0, 0, 0, 0)

        # init BSChart panes
        for pane in self._chart_panes:
            container.addWidget(pane.widget(self.parent))

    def del_last_pane(self, checked=False):

        count = self._container.count()
        if count > 1:
            pane = self._chart_panes.pop(count - 1)
            self._container.widget(count - 1).deleteLater()
            self.disconnect_wheel(pane)

    def del_pane(self, index: int):
        if index == 0:
            return False

        pane = self._chart_panes.pop(index)
        self._container.widget(index).deleteLater()
        self.disconnect_wheel(pane)

    def add_pane(self, chart_type='candle', indi=None):
        chart_model = ChartModel(self.data)

        pane = ChartPane(
            ChartView(chart_model, chart_typ=chart_type, indi=indi),
            YAxis.AxisView(chart_model)
        )

        self.connect_wheel(pane)

        self._chart_panes.append(pane)
        self._container.addWidget(pane.widget(self.parent))

    def get_chart(self) -> QSplitter:
        return self._container

    def get_time(self) -> QWidget:
        return self._time_pane.widget(self.parent)


attach_timer(LayoutManager)
