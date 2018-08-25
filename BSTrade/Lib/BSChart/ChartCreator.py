from .Layouts import LayoutManager
from .View import ChartView
from .Model import CandleModel
from .Item import CandleStick


class TimeSeriesChartCreator:
    def __init__(self, store, x_axis=None, parent=None):
        if x_axis is None:
            self.x_axis = TimeAxisModel()

        self.parent = parent
        self.store = store
        self.x_axis = x_axis
        self.tc_layout = LayoutManager(self.store, parent)

    def _create_item(self, chart_type):
        if chart_type == 'candle':
            model = CandleModel(self.store, self.x_axis)
            item = CandleStick(model, self.parent)
        else:
            model = CandleModel(self.store, self.x_axis)
            item = CandleStick(model, self.parent)

        item.set_model(model)

        return item

    def init_layout(self):
        return (
            self.tc_layout.create_chart_containter(),
            self.tc_layout.create_time_pane()
        )

    def create_chart(self, chart_type):
        item = self._create_item(chart_type)
        chart_view = ChartView(item)
        # view.set_item(item)

        return chart_view, self.x_axis
