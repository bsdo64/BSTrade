import numpy

import pandas as pd

from PyQt5.QtCore import pyqtSignal, QObject

from BSTrade.Data.instruments import markets
from BSTrade.Lib.BSChart.Model import ChartModel
from .const import Provider
from .reader import DataReader


class Trade:
    def __init__(self, store):
        self.store = store


class Candle:
    def __init__(self, store: 'Store'):
        self.store = store
        self.cache = store.cache
        self.reader = store.reader

    def init_data(self):
        for prov in Provider:
            for symbol in self.cache[prov]['symbol']:
                self.cache[prov]['symbol'][symbol]['candle'] = {
                    item: {
                        i: numpy.array([

                        ]) for i in ['close', 'open', 'low', 'high',
                                     'timestamp']
                    } for item in ['1m', '5m', '15m', '30m']
                }

    def request(self, provider, symbol, bin_size):
        self.reader.request({
            'provider': provider,
            'symbol': symbol,
            'data_type': 'candle',
            'params': {'bin_size': bin_size, 'symbol': symbol, 'count': 500},
        })

    def sync_api(self, provider, symbol, bin_size):
        self.reader.request({
            'provider': provider,
            'symbol': symbol,
            'data_type': 'candle',
            'params': {'bin_size': bin_size, 'symbol': symbol, 'count': 500},
        })

    def set_cache(self, data):
        provider = data['provider']
        symbol = data['symbol']
        bin_size = data['bin_size']

        self.cache[provider]['symbol'][symbol]['candle'][bin_size] = data

    def get_cache(self, provider, symbol, bin_size):
        return self.cache[provider]['symbol'][symbol]['candle'][bin_size]

    def update_last(self, provider, symbol, bin_size, ohlc):
        candle = self.cache[provider]['symbol'][symbol]['candle']
        for i in ['open', 'close', 'low', 'high']:
            candle[bin_size][i][-1] = ohlc[i]


class Api:
    def __init__(self, parent):
        self._store = Store(parent)

        # Public
        self.Candle = Candle(self._store)
        self.Trade = Trade(self._store)
        self.Symbol = Symbol(self._store)
        self.OrderBook = OrderBook(self._store)
        self.Stats = Stats(self._store)

        # Private
        self.User = User(self._store)
        self.Order = Order(self._store)
        self.Account = Account(self._store)
        self.Wallet = Wallet(self._store)

        # System
        self.App = App(self._store)

        self.Candle.init_data()
        self.Trade.init_data()
        self.Symbol.init_data()
        self.OrderBook.init_data()
        self.Stats.init_data()
        self.User.init_data()
        self.Order.init_data()
        self.Account.init_data()
        self.Wallet.init_data()
        self.App.init_data()

    @property
    def store(self):
        return self._store


class Store(QObject):
    sig_init = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config
        self.cache = {
            prov: {
                'provider': prov,
                'symbol': {
                    symbol: {} for symbol in markets[prov]
                }
            } for prov in Provider,
        }

        self.chart_models = {}
        self.reader = DataReader()
        self.writer = DataWriter()

        self.reader.sig_http_finish.connect(self.slt_http_finish)
        self.reader.sig_ws_finish.connect(self.slt_ws_finish)

    def app_data(self, *args):
        d = self.cache
        for i in args:
            d = d.get(i, {})

        return d

    def provider_data(self, provider, *args):

        d = self.cache.get(provider, {})
        for i in args:
            d = d.get(i, {})

        return d

    def trade_data(self, option):
        provider = option['provider']
        symbol = option['symbol']
        bin_size = option['bin_size']
        return self.cache[provider]['symbol'][symbol]['candle'][bin_size]

    def do_request_http(self):
        self.reader.request({
            'provider': Provider.BITMEX,
            'client': 'http',
            'endpoint': ['get', 'trade', 'bucketed'],
            'params': {'bin_size': '1m', 'symbol': 'XBTUSD', 'count': 500},
            'symbol': 'XBTUSD',
            'option': {}
        })

    def do_request_ws(self):
        self.reader.request_ws({
            'client': Provider.BITMEX,
            'subscribe': ['trade:XBTUSD',
                          'tradeBin1m:XBTUSD',
                          'orderBookL2:XBTUSD']
        })

    def slt_http_finish(self, data: dict):
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

        self.cache[provider] = {
            'symbol': {
                symbol: {
                    data_type: np_data
                },
            }
        }
        self.data_len = len(data['data'])
        self.sig_init.emit()

    def slt_ws_finish(self, data):
        pass

    def create_chart_model(self, idx: str, data_type: str):
        provider, symbol = idx.split(':')
        try:
            data = self.cache[provider]['symbol'][symbol][data_type]
        except KeyError:
            data = {}

        model = ChartModel(idx=idx, store=self, ws=self.ws)
        self.chart_models[model.ID] = model
        return model
