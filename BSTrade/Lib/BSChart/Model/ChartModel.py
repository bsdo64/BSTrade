import ciso8601

import numpy as np
from PyQt5.QtCore import QObject, QSize

from BSTrade.Api.wsclient import WsClient
from .PlotModel import LineModel, CandleModel
from .TimeAxisModel import TimeAxisModel


class ChartModel(QObject):
    def __init__(self, data, data_len, idx, store, ws):
        super().__init__()
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