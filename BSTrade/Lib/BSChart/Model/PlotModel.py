import ciso8601
import sys
import time
import ujson as json
import numpy as np
import talib

from PyQt5.QtCore import QObject, pyqtSignal, QRectF

from BSTrade.Opt import vec
from BSTrade.util.fn import attach_timer
from . import ChartModel, TimeAxisModel


class BaseChart(QObject):
    INT_MAX = sys.maxsize // 10 ** 11 * 10

    def __init__(self, _c_model: 'ChartModel', axis_model: 'TimeAxisModel'):
        super().__init__()

        self._c_model = _c_model
        self.series = _c_model.get_data()
        self.store = _c_model.get_store()

        self.x_axis = axis_model

    def change_x(self, pos, rng):
        self.x_axis.change_axis(pos, rng)

    def x_model(self):
        return self.x_axis

    def c_model(self):
        return self._c_model


class LineModel(BaseChart):
    CHART_TYPE = 'line'

    def __init__(self, c_model, axis_model=None):
        super().__init__(c_model, axis_model)

    def slt_ws_message(self, j):
        pass


class CandleModel(BaseChart):
    CHART_TYPE = 'candle'
    Y_VAL = 0  # (sec // 60s) * marker_gap -> scaled min

    sig_add_point = pyqtSignal(dict)
    sig_update_point = pyqtSignal(dict)

    def __init__(self, c_model: 'ChartModel', axis_model: 'TimeAxisModel'):
        super().__init__(c_model, axis_model)

        self.y_range = 100
        self.y_ratio = self.c_model().view_height / self.y_range  # 480 / 100 = 4.8
        self.y_val_pos = 9876540
        self.y_gap_pos = 2
        self.y_gaps = [2, 2, 2.5]
        self.y_val_gap = 50

        self.rect = QRectF(0, 0, 0, 0)

        self.indicators = {}
        self.print_data = {}
        self.c_data = self.init_printing_data()

    def init_printing_data(self):
        for i in ['close', 'open', 'low', 'high']:
            self.print_data['r_' + i] = vec.sub(self.INT_MAX,
                                                self.series.get(i, np.array([])))

        return self.current_data()

    def current_data(self, indi=None):
        chart = self.c_model()
        x_axis = self.x_axis

        if chart.data_len:
            s = -x_axis.current_x_range()
            p = x_axis.current_x_pos()
            e = -p if 0 < p else None

            if 0 < -s < chart.data_len:
                self.c_data = self._create_data(s, e)

            # if e - s > 0:
            x_axis.calc_marker()

            rh = self.print_data['r_high']
            rl = self.print_data['r_low']
            self.Y_VAL = np.min(rh)  # min value
            remain = self.Y_VAL % self.y_val_gap  # 9875421 % 50
            self.y_val_pos = (self.Y_VAL - remain)  # first y grid
            self.y_range = np.max(rl) - self.Y_VAL  # min value
            self.y_ratio = chart.view_height / self.y_range
            self.set_y_gap(self.y_val_gap * self.y_ratio)  # y gap 50 * 4.8
        else:
            self.c_data = {}

        return self.c_data

    def rect_x(self):
        return self.x_axis.get_rectx()

    def prev_data(self, d_s, d_len=None):
        if d_len is None:
            d_len = self.x_axis.DEFAULT_X_RANGE

        d_s += 1
        s = -(d_s + d_len)
        e = -d_s or None

        return self._create_data(s, e)

    def _create_data(self, start, end):
        data = self.c_model().get_data()

        return {
            'time_axis_scaled': data['time_axis_scaled'][start: end],
            'time_axis': data['time_axis'][start: end],
            'high': data['high'][start: end],
            'low': data['low'][start: end],
            'close': data['close'][start: end],
            'open': data['open'][start: end],
            'r_high': self.print_data['r_high'][start: end],
            'r_low': self.print_data['r_low'][start: end],
            'r_close': self.print_data['r_close'][start: end],
            'r_open': self.print_data['r_open'][start: end],
            'len': len(self.print_data['r_open'][start: end])
        }

    def set_y_gap(self, gap):
        sc = 100  # scale ( * 100) ex) 29.9423 ~ 30.1382
        g = gap * sc
        len_gaps = len(self.y_gaps)

        if 0 < g <= 30 * sc:
            """
                default = 50, 2.5(2)
                1. 50   *   2(0)   = 100
                2. 100  *   2(1)   = 200 
                3. 200  * 2.5(2)   = 500 
                4. 500  *   2(0)   = 1000 
                5. 1000 *   2(1)   = 2000 
                ...
            """
            self.y_gap_pos = (self.y_gap_pos + 1) % len_gaps  # 1 % 3 -> 1
            self.y_val_gap *= self.y_gaps[self.y_gap_pos]  # 50 * 2 -> 100
        elif 60 * sc < g:
            """
                default = 50, 2.5(2)
                1. 50   / 2.5(2)   = 20
                2. 20   /   2(1)   = 10 
                3. 10   /   2(0)   = 5 
                4. 5    / 2.5(2)   = 2
                5. 2    /   2(1)   = 1 
                ...
            """
            self.y_val_gap /= self.y_gaps[self.y_gap_pos]  # 50 / 2.5 -> 20.0
            self.y_gap_pos = (self.y_gap_pos - 1) % len_gaps  # -1 % 3 -> 2

    def slt_ws_message(self, msg):
        j = json.loads(msg)

        if j.get('table') == 'trade':
            items = j.get('data')

            for data in items:
                t = ciso8601.parse_datetime(data['timestamp'])
                t_int = np.datetime64(t).astype(np.int64)
                t_axis = t_int / 10 ** 6 // 60
                is_same_time = self.is_same_time(t_axis)

                # print(t_axis, self.np_data['time_axis'][-1])
                if is_same_time == 0:
                    # same time -> change price

                    """
                    {
                        'timestamp': '2018-08-08T14:51:15.377Z',
                        'symbol': 'XBTUSD', 
                        'side': 'Buy', 
                        'size': 3000,
                        'price': 6458, 
                        'tickDirection': 'ZeroPlusTick',
                        'trdMatchID': 
                            'dc6e6001-3ee5-fddf-d2b5-8b2f967c5d2e',
                        'grossValue': 46455000, 
                        'homeNotional': 0.46455,
                        'foreignNotional': 3000
                    }
                    """

                    close = data['price']
                    if self.series['close'][-1] == close:
                        return

                    opn = self.series['open'][-1]  # 6410
                    low = self.series['low'][-1]  # 6400
                    high = self.series['high'][-1]  # 6460

                    low = low if close > low else close
                    high = close if close > high else high

                    d = {
                        'time_axis': t_axis,
                        'time_axis_scaled': t_axis * self.marker_gap,
                        'open': opn,
                        'close': close,
                        'low': low,
                        'high': high,
                        'r_open': self.INT_MAX - opn,
                        'r_close': self.INT_MAX - close,
                        'r_low': self.INT_MAX - low,
                        'r_high': self.INT_MAX - high,
                        'plus_cond': opn < close,
                    }

                    self.update_np_data(d)

                elif is_same_time > 0:
                    # current data > store data
                    # add new bar
                    print("# add new bar")

                    price = float(data['price'])
                    r_price = self.INT_MAX - float(data['price'])

                    d = {
                        'time_axis': t_axis,
                        'time_axis_scaled': t_axis * self.marker_gap,
                        'open': price,
                        'close': price,
                        'low': price,
                        'high': price,
                        'r_open': r_price,
                        'r_close': r_price,
                        'r_low': r_price,
                        'r_high': r_price,
                        'plus_cond': False,  # == 0
                    }

                    self.append_np_data(d)
                    self.update_X_TIME()

    def is_same_time(self, t_axis):
        last = int(self.series['time_axis'][-1])
        return 0 if int(t_axis) == last else 1 if int(t_axis) >= last else -1

    def update_X_TIME(self):
        """
        Set X_TIME to current time

        """
        # X_TIME    = (       sec // 60s) * marker_gap -> scaled min
        self.X_TIME = (time.time() // 60) * self.marker_gap

    def update_np_data(self, data):
        for i in ['close', 'open', 'low', 'high']:
            self.print_data['r_' + i][-1] = data['r_' + i]
            self.series[i][-1] = data[i]

        self.sig_update_point.emit(data)

    def append_np_data(self, data):
        self.series['time_axis'] = np.append(
            self.series['time_axis'], data['time_axis']
        )
        self.series['time_axis_scaled'] = np.append(
            self.series['time_axis_scaled'],
            data['time_axis'] * self.marker_gap
        )

        for i in ['close', 'open', 'low', 'high']:
            self.print_data['r_' + i] = np.append(
                self.print_data['r_' + i], data['r_open']
            )
            self.series[i] = np.append(
                self.series[i], data['open']
            )

        self.sig_add_point.emit(data)

    def create_indicator(self, indi):
        indi_func = getattr(talib, indi)
        values = indi_func(self.series['close'])
        values = values[~np.isnan(values)]
        r_data = self.INT_MAX - values
        print(r_data)
        print(r_data.max())
        print(r_data.min())
        v = {
            indi: values,
            'time_axis': self.series['time_axis'],
            'time_axis_scaled': self.series['time_axis_scaled'],
            'r_' + indi: r_data,
            'len': len(values)
        }
        self.indicators[indi] = v
        return self.indicators[indi]


attach_timer(CandleModel, limit=5)
