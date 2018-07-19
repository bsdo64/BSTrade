from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSplitter, QWidget

from BSTrade.widgets.chart.graphic_views import ChartView, ChartAxisView, TimeAxisView
from BSTrade.layouts.panes import ChartPane, ChartTimePane
from BSTrade.util.fn import attach_timer


class ChartLayoutManager:
    def __init__(self, parent=None):
        self.parent = parent

        # Create default main chart pane
        self.chart_panes = [
            ChartPane(ChartView(), ChartAxisView()),
        ]

        # Create main time axis pane
        self.time_axis_pane = ChartTimePane(TimeAxisView())

        # Create chart pane container
        self.container = QSplitter(parent)
        self.init_layout(self.container)

    def init_layout(self, container):
        container.setOrientation(Qt.Vertical)
        container.setChildrenCollapsible(False)
        container.setHandleWidth(2)
        container.setContentsMargins(0, 0, 0, 0)

        # init chart panes
        for chart_pane in self.chart_panes:
            container.addWidget(chart_pane.create(self.parent))

    def del_last_pane(self, checked=False):
        count = self.container.count()
        if count > 1:
            self.chart_panes.pop(count - 1)
            self.container.widget(count - 1).deleteLater()

    def del_pane(self, index):
        if index == 0:
            return False

        self.chart_panes.pop(index)
        self.container.widget(index).deleteLater()

    def add_pane(self, pane=None):
        if not pane:
            pane = ChartPane(ChartView(), ChartAxisView())

        self.chart_panes.append(pane)
        self.container.addWidget(pane.create(self.parent))

    def get_chart_panes(self) -> QSplitter:
        return self.container

    def get_time_axis(self) -> QWidget:
        return self.time_axis_pane.create(self.parent)


attach_timer(ChartLayoutManager)
