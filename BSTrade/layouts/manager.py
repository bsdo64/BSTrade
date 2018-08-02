import pandas

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QWidget

from BSTrade.widgets.chart.graphic_views import ChartView, \
    ChartAxisView, TimeAxisView
from BSTrade.layouts.panes import ChartPane, ChartTimePane
from BSTrade.util.fn import attach_timer
from BSTrade.data.model import Model


class ChartLayoutManager:
    def __init__(self, parent=None):
        self.parent = parent

        data = pandas.read_pickle('BSTrade/data/bitmex_1m_2018.pkl')
        self.model = Model(data)

        # Create default main chart pane
        self._chart_panes = [
            ChartPane(ChartView(self.model), ChartAxisView(self.model)),
        ]

        # Create main time axis pane
        self._time_pane = ChartTimePane(TimeAxisView(self.model))

        for pane in self._chart_panes:
            pane.chart.sig_chart_wheel.connect(
                self._time_pane.axis.slot_wheel_re_model
            )

        # Create chart pane container
        self._container = QSplitter(parent)
        self.init_layout(self._container)

    def init_layout(self, container):
        container.setOrientation(Qt.Vertical)
        container.setChildrenCollapsible(False)
        container.setHandleWidth(2)
        container.setContentsMargins(0, 0, 0, 0)

        # init chart panes
        for pane in self._chart_panes:
            container.addWidget(pane.create(self.parent))

    def del_last_pane(self, checked=False):
        print(checked)

        count = self._container.count()
        if count > 1:
            self._chart_panes.pop(count - 1)
            self._container.widget(count - 1).deleteLater()

    def del_pane(self, index):
        if index == 0:
            return False

        self._chart_panes.pop(index)
        self._container.widget(index).deleteLater()

    def add_pane(self, pane=None):
        if not pane:
            pane = ChartPane(ChartView(self.model), ChartAxisView(self.model))

        self._chart_panes.append(pane)
        self._container.addWidget(pane.create(self.parent))

    def chart_pane(self) -> QSplitter:
        return self._container

    def time_pane(self) -> QWidget:
        return self._time_pane.create(self.parent)


attach_timer(ChartLayoutManager)
