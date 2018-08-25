from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QWidget, QHBoxLayout

from .View import ChartView, XAxisView, YAxisView
from BSTrade.util.fn import attach_timer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from BSTrade.Data.Models import Store


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


class ChartTimePane:
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
    def __init__(self, data_manager: 'Store', parent=None, ):
        self.parent = parent
        self.data_mng = data_manager
        self.chart_model = self.data_mng.create_chart_model(
            'bitmex:XBTUSD',
            'tradebin1m'
        )

        candle_model = self.chart_model.create_model('candle')
        time_model = self.chart_model.create_time()

        chart_pane = ChartPane(
            ChartView(candle_model),
            YAxisView(candle_model)
        )
        # Create default main BSChart pane
        self._chart_panes = [chart_pane]
        self._time_pane = ChartTimePane(
            XAxisView(time_model, parent))
        self.connect_wheel(chart_pane)

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
        line_model = self.chart_model.create_model('line')
        line_model.set_chart('indi', indi)

        pane = ChartPane(
            ChartView(line_model), YAxisView(line_model)
        )

        self.connect_wheel(pane)

        self._chart_panes.append(pane)
        self._container.addWidget(pane.widget(self.parent))

    def get_chart(self) -> QSplitter:
        return self._container

    def get_time(self) -> QWidget:
        return self._time_pane.widget(self.parent)


attach_timer(LayoutManager)
