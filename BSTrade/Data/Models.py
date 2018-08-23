import ujson as json
import sys
import time
from typing import Iterable, Union

import pandas as pd
import numpy as np
import ciso8601
import talib
import talib.stream
import random

from PyQt5.QtCore import QRectF, pyqtSignal, QObject, QSize

from BSTrade.Api.auth.bitmex import api_keys
from BSTrade.Api import BitmexWsClient
from BSTrade.Api.wsclient import WsClient
from BSTrade.util.fn import attach_timer
from BSTrade.Opt import vec
from BSTrade.Opt.math import cache_x_range, cache_x_pos
from BSTrade.Data.bitmex.reader import DataReader


class DataManager(QObject):
    sig_init = pyqtSignal()

    def __init__(self, config, parent=None):
        QObject.__init__(self, parent)

        self.config = config
        self.master_data = {}
        self.chart_models = []
        self.data_len = 100000
        self.reader = DataReader(config['provider'],
                                 config['symbol'],
                                 self.data_len)
        self.ws: BitmexWsClient = None

        self.setup_ws(config)

    def set_initial_data(self):
        self.reader.start()
        self.reader.sig_finished.connect(self.slt_finish_init_data)

    def slt_finish_init_data(self, data: dict):
        df: pd.DataFrame = data['data']
        provider = data['provider']
        symbol = data['symbol']
        data_type = data['data_type']

        """
        Structure :
        data = {
            'provider': self.provider,
            'symbol': self.instrument,
            'data_type': 'tradebin1m',
            'data': self.r.df
        }
        """

        if hasattr(df, 'timestamp'):
            df['timestamp_str'] = df['timestamp']
            df['timestamp'] = df['timestamp'].astype('datetime64')

        np_data = {key: df[key].values for key in df.keys()}

        self.master_data[provider] = {
            'price': {
                symbol: {
                    data_type: np_data
                },
            }
        }

        self.sig_init.emit()

    def setup_ws(self, config):
        provider = config.get('provider')
        if provider == 'bitmex':
            self.ws = BitmexWsClient(
                test=False,
                api_key=api_keys['real']['order']['key'],
                api_secret=api_keys['real']['order']['secret']
            )
        else:
            # default provider == 'bitmex'
            self.ws = BitmexWsClient(
                test=False,
                api_key=api_keys['real']['order']['key'],
                api_secret=api_keys['real']['order']['secret']
            )

        self.ws.sig_auth_success.connect(self.slt_ws_subscribe)
        self.ws.start()

    def slt_ws_subscribe(self):
        # web socket client connected with auth
        self.ws.subscribe('trade:XBTUSD',
                          'tradeBin1m:XBTUSD',
                          'orderBookL2:XBTUSD')

    def is_same_time(self, t_axis):
        last = int(self.series['time_axis'][-1])
        return 0 if int(t_axis) == last else 1 if int(t_axis) >= last else -1

    def get_model(self, option):
        provider = option['provider']
        symbol = option['symbol']
        return self.master_data[provider]['price'][symbol]

    def create_chart_model(self, idx: str, data_type: str):
        provider, symbol = idx.split(':')
        data = self.master_data[provider]['price'][symbol][data_type]
        model = ChartModel(data, data_len=self.data_len,
                           idx=idx, store=self, ws=self.ws)
        self.chart_models.append(model)
        self.ws.sig_message.connect(model.slt_ws_message)
        return model


class ChartModel(QObject):
    def __init__(self, data, data_len, idx, store, ws):
        QObject.__init__(self)
        self.provider, self.symbol = idx.split(':')
        self.data = data
        self.data_len = data_len  # 100,000
        self.store = store
        self.ws: WsClient = ws

        self.view_width = 640
        self.view_height = 480

        self.chart_models = []
        self.time_axis_model = TimeAxisModel(self)

    def get_data(self):
        return self.data

    def get_store(self):
        return self.store

    def set_size(self, size: QSize):
        self.view_width = size.width()
        self.view_height = size.height()

    def create_model(self, md_type):
        if md_type == 'candle':
            model = CandleModel(self, self.time_axis_model)
            self.chart_models.append(model)
            return model
        elif md_type == 'line':
            model = LineModel(self, self.time_axis_model)
            self.chart_models.append(model)
            return model

    def create_time(self):
        return self.time_axis_model

    def slt_ws_message(self, msg):
        j = self.ws.json()

        if j.get('table') == 'trade':
            items = j.get('data')

            for data in items:
                if self.data['close'][-1] == data['price']:
                    return

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
                    opn = self.data['open'][-1]  # 6410
                    low = self.data['low'][-1]  # 6400
                    high = self.data['high'][-1]  # 6460

                    low = low if close > low else close
                    high = close if close > high else high

                    d = {
                        'time_axis': t_axis,
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

                    self.update_data(d)

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

                    self.append_data(d)
                    self.update_X_TIME()

    def is_same_time(self, t_axis):
        last = int(self.data['time_axis'][-1])
        return 0 if int(t_axis) == last else 1 if int(t_axis) >= last else -1

    def update_data(self, data):
        for i in ['close', 'open', 'low', 'high']:
            self.data[i][-1] = data[i]

        self.sig_update_point.emit(data)


class TimeAxisModel(QObject):
    DEFAULT_X_RANGE = 1000
    AXIS_TYPE = 'time'
    X_TIME = (time.time() // 60) * 50  # (sec // 60s) * marker_gap -> scaled min

    def __init__(self, c_model):
        QObject.__init__(self)

        self.c_model = c_model
        self.series = c_model.get_data()
        self.store = c_model.get_store()

        self.x_pos = 0
        self.x_range = self.DEFAULT_X_RANGE
        self.x_range_prev = self.DEFAULT_X_RANGE
        self.x_ratio = self.view_width / self.x_range
        self.x_time_pos = self.X_TIME
        self.x_time_gap = 60

        self.marker_gap = 50

        self.minutes = [
            1, 2, 3, 5, 10, 15, 30,  # 1m, 2m, 3m, 5m, 10m, 30m,
            60, 120, 180, 240, 360, 480, 720,  # 1h, 2h, 3h, 4h, 6h, 8h, 12h,
            1440, 2880, 5760,  # 1d, 2d, 4d,
            10080, 20160, 40320,  # 1w, 2w, 4w,
        ]
        self.minute_pos = 7  # default 1h
        self.months = [
            '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]

        self.init_axis_data()

    def init_axis_data(self):
        ts = self.series['timestamp'].astype(np.int64)
        self.series['time_axis'] = vec.ts_to_axis(ts, 60)
        self.series['time_axis_scaled'] = vec.mult(self.series['time_axis'],
                                                   self.marker_gap)

    def change_axis(self, pos, rng):
        chart = self.c_model

        # limit pos
        # -> 640 + (-430) = 210 > 50 * 4
        if chart.view_width + self.x_pos > self.marker_gap * 10:
            # change pos
            self.x_pos += pos

        # limit rng
        # -> 1000 + n > 1000
        if self.x_range + rng > self.DEFAULT_X_RANGE:
            # change x_range
            self.x_range += rng

        self.change_ratio(chart.view_width / self.x_range)

    def change_ratio(self, ratio):
        self.x_ratio = ratio

    def current_x_range(self) -> int:
        return cache_x_range(self.x_pos,
                             self.x_range,
                             self.marker_gap)  # (num1 + num2) // num3

    def current_x_pos(self) -> int:
        return cache_x_pos(self.x_pos, self.marker_gap)  # num1 // num2

    def calc_marker(self, axis_data):
        start = axis_data[0]  # min
        remain = start % self.minutes[self.minute_pos]
        self.x_time_pos = (start - remain) * self.marker_gap
        self.x_time_gap = self.minutes[self.minute_pos] * self.marker_gap
        self.set_time_gap(self.x_time_gap * self.x_ratio)

    def set_time_gap(self, gap):
        if 0 <= self.minute_pos < len(self.minutes):
            if 0 < gap < 75:
                self.minute_pos = self.minute_pos + 1
            elif 150 < gap:
                self.minute_pos = self.minute_pos - 1

    def get_month(self, m):
        return self.months[m]

    def get_minute(self):
        return self.minutes[self.minute_pos]

    def get_rectx(self):
        return self.X_TIME - self.x_pos - self.x_range


class BaseChart(QObject):
    INT_MAX = sys.maxsize // 10 ** 11 * 10

    def __init__(self, c_model: ChartModel, axis_model: TimeAxisModel):
        QObject.__init__(self)

        self.c_model = c_model
        self.series = c_model.get_data()
        self.store = c_model.get_store()

        self.x_axis = axis_model

    def change_x(self, pos, rng):
        self.x_axis.change_axis(pos, rng)


class LineModel(BaseChart):
    CHART_TYPE = 'line'

    def __init__(self, c_model, axis_model=None):
        BaseChart.__init__(self, c_model, axis_model)

    def slt_ws_message(self, j):
        pass


class CandleModel(BaseChart):
    CHART_TYPE = 'candle'
    Y_VAL = 0  # (sec // 60s) * marker_gap -> scaled min

    sig_add_point = pyqtSignal(dict)
    sig_update_point = pyqtSignal(dict)

    def __init__(self, c_model: ChartModel, axis_model: TimeAxisModel):
        BaseChart.__init__(self, c_model, axis_model)

        self.y_range = 100
        self.y_ratio = self.view_height / self.y_range  # 480 / 100 = 4.8
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
            self.print_data['r_' + i] = vec.sub(self.INT_MAX, self.series[i])

        return self.current_data()

    def current_data(self, indi=None):
        chart = self.c_model
        x_axis = self.x_axis

        if not indi:
            s = -x_axis.current_x_range()
            p = x_axis.current_x_pos()
            e = -p if 0 < p else None

            if 0 < -s < chart.data_len:
                self.c_data = self._create_data(s, e)

            if e - s > 0:
                x_axis.calc_marker(self.c_data['time_axis'])

                rh = self.c_data['r_high']
                rl = self.c_data['r_low']
                self.Y_VAL = np.min(rh)  # min value
                remain = self.Y_VAL % self.y_val_gap  # 9875421 % 50
                self.y_val_pos = (self.Y_VAL - remain)  # first y grid
                self.y_range = np.max(rl) - self.Y_VAL  # min value
                self.y_ratio = self.view_height / self.y_range
                self.set_y_gap(self.y_val_gap * self.y_ratio)  # y gap 50 * 4.8

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

        return {
            'time_axis_scaled': self.series['time_axis_scaled'][start: end],
            'time_axis': self.series['time_axis'][start: end],
            'high': self.series['high'][start: end],
            'r_high': self.series['r_high'][start: end],
            'low': self.series['low'][start: end],
            'r_low': self.series['r_low'][start: end],
            'close': self.series['close'][start: end],
            'r_close': self.series['r_close'][start: end],
            'open': self.series['open'][start: end],
            'r_open': self.series['r_open'][start: end],
            'len': len(self.series['r_open'][start: end])
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
            self.series['r_' + i][-1] = data['r_' + i]
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
            self.series['r_' + i] = np.append(
                self.series['r_' + i], data['r_open']
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
