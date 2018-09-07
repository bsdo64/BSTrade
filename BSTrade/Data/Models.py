import numpy

import pandas as pd

from PyQt5.QtCore import pyqtSignal, QObject

from BSTrade.Data.instruments import markets
from BSTrade.Lib.BSChart.Model import ChartModel
from .const import Provider
from .reader import DataReader


class Api:
    def __init__(self, parent):
        self._store: Store = Store(parent)

        # Public
        # self.Candle = Candle(self._store)
        # self.Trade = Trade(self._store)
        # self.Symbol = Symbol(self._store)
        # self.OrderBook = OrderBook(self._store)
        # self.Stats = Stats(self._store)
        #
        # # Private
        # self.User = User(self._store)
        # self.Order = Order(self._store)
        # self.Account = Account(self._store)
        # self.Wallet = Wallet(self._store)
        #
        # # System
        # self.App = App(self._store)
        #
        # self.Candle.init_data()
        # self.Trade.init_data()
        # self.Symbol.init_data()
        # self.OrderBook.init_data()
        # self.Stats.init_data()
        # self.User.init_data()
        # self.Order.init_data()
        # self.Account.init_data()
        # self.Wallet.init_data()
        # self.App.init_data()

    @property
    def store(self) -> 'Store':
        return self._store


class OrderBook:
    def __init__(self, symbol):
        self.symbol = symbol
        self.timestamp = None
        self.book = []


class Trade:
    def __init__(self, symbol):
        self.symbol = symbol
        self.trades = []


class Candle(object):
    def __init__(self, reader):
        self.model = 'candle'
        self.reader = reader
        """
        {
            'open': float, 
            'close': float, 
            'high': float, 
            'low': float,
            'timestamp': datetime
        }
        """
        self.data = {
            '1m': [],
            '5m': [],
            '10m': []
        }

    def ohlc(self, bin_size):
        return self.data[bin_size]

    def new(self, bin_size, data):
        self.data[bin_size] = data

    def add(self, bin_size, data):
        self.data[bin_size].append(data)

    def update_last(self, data):
        bin_size = data['bin_size']

        for i in ['open', 'close', 'low', 'high']:
            self.data[bin_size][-1][i] = data[i]


class SymbolSig(QObject):
    new_candle = pyqtSignal(object)


class Symbol(object):
    sig = SymbolSig()
    """
    Symbol Info : bitmex-XBTUSD, upbit-KRW-BTC, ....
    """
    def __init__(self, symbol: str, reader: DataReader):
        self.name = symbol
        self.reader = reader
        self.symbol = symbol
        self.code = symbol

        self.Candle = Candle(reader)
        self.Trade = Trade(reader)
        self.Orderbook = OrderBook(reader)
        # self.Stat = Stat(reader)
        # self.Indicators = Indicators(reader)

    def new_candle(self, bin_size):
        self.reader.r.request({
            'symbol': self.symbol,
            'model': 'candle',
            'params': {
                'bin_size': bin_size,
                'symbol': self.symbol,
                'count': 500
            },
        })

        self.sig.new_candle.emit()


class StockMarket(object):
    """
    Market Info : KOSPI, KOSDAQ, NASDAQ
    """
    pass


class CryptoMarket(object):
    """
    Market Info : Bitmex, Upbit, Binance
    """
    def __init__(self, provider):
        self.market_type = 'crypto'
        self.provider = provider
        self.reader = DataReader(provider)
        self.symbols = {
            symb: Symbol(symb, self.reader) for symb in markets[provider]
        }

    def symbol(self, symbol: str):
        return self.symbols[symbol]


class Store(QObject):
    sig_init = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config
        self.markets = {
            Provider.BITMEX: CryptoMarket(Provider.BITMEX),
            Provider.UPBIT: CryptoMarket(Provider.UPBIT)
        }
        self.chart_models = {}

    def market(self, provider):
        return self.markets[provider]

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

        self.markets[provider] = {
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
            data = self.markets[provider]['symbol'][symbol][data_type]
        except KeyError:
            data = {}

        model = ChartModel(idx=idx, store=self, ws=self.ws)
        self.chart_models[model.ID] = model
        return model
