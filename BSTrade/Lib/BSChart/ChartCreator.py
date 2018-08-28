from .View import ChartView, YAxisView, XAxisView
from .Item import CandleStick, Line, TimeItem
from .Model import ChartModel


class TimeSeriesChartCreator:
    def __init__(self, c_model: ChartModel):
        self.c_model = c_model

    def create_x_time_view(self):
        x_item = TimeItem(self.c_model.time_axis_model)
        return XAxisView(x_item)

    def _create_item(self, chart_type):
        model = self.c_model.create_model(chart_type)

        if chart_type == 'candle':
            item = CandleStick(model)
        elif chart_type == 'line':
            item = Line(model)
        else:
            item = CandleStick(model, )

        return item

    def create_chart_view(self, chart_type):
        item = self._create_item(chart_type)

        chart_view = ChartView(item)
        axis_view = YAxisView(item)

        return chart_view, axis_view
