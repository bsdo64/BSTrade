from PyQt5.QtCore import pyqtSignal, QObject

from BSTrade.Data.source import bs_req
from .const import Provider, HttpEndPointType


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
    def __init__(self, provider, symbol):
        self.symbol = symbol
        self.provider = provider
        self.model = 'candle'
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
    def __init__(self, symbol, provider):
        self.provider = provider
        self.name = symbol['symbol']
        self.state = symbol['state']
        self.code = symbol['symbol']

        self.Candle = Candle(provider, symbol)
        # self.Trade = Trade(reader)
        # self.Orderbook = OrderBook(reader)
        # self.Stat = Stat(reader)
        # self.Indicators = Indicators(reader)

    def new_candle(self, bin_size):
        # self.reader.r.request({
        #     'symbol': self.symbol,
        #     'model': 'candle',
        #     'params': {
        #         'bin_size': bin_size,
        #         'symbol': self.symbol,
        #         'count': 500
        #     },
        # })

        self.sig.new_candle.emit()


class StockMarket(object):
    """
    Market Info : KOSPI, KOSDAQ, NASDAQ
    """
    pass


class MarketSig(QObject):
    symbol_updated = pyqtSignal(object)


class CryptoMarket(object):
    sig = MarketSig()
    """
    Market Info : Bitmex, Upbit, Binance
    """
    def __init__(self, provider):
        self.market_type = 'crypto'
        self.provider = provider
        # self.reader = DataReader(provider)

        self.symbols = {}

    def symbol(self, symbol: str):
        return self.symbols[symbol]

    def update(self):
        bs_req.sig.finished.connect(self.on_update)
        bs_req.get_symbols(self.provider, {'count': 500})

    def on_update(self, res):
        if res['endpoint'] == HttpEndPointType.get_symbols:
            symbols = res['data']
            self.symbols = {
                symb['symbol']: Symbol(symb, self.provider)
                for symb in symbols
            }

            self.sig.symbol_updated.emit(self)
            bs_req.sig.finished.disconnect(self.on_update)


class Store(QObject):
    sig_init = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.markets = {prov: CryptoMarket(prov) for prov in Provider}
        self.chart_models = {}

    def market(self, provider) -> CryptoMarket:
        return self.markets[provider]

    # def slt_http_finish(self, data: dict):
    #     df: pd.DataFrame = data['data']
    #     provider = data['provider']
    #     symbol = data['symbol']
    #     data_type = data['data_type']
    #
    #     """
    #     Structure :
    #     data = {
    #         'provider': self.provider,
    #         'symbol': self.instrument,
    #         'data_type': 'tradebin1m',
    #         'data': self.r.df
    #     }
    #     """
    #
    #     if hasattr(df, 'timestamp'):
    #         df['timestamp_str'] = df['timestamp']
    #         df['timestamp'] = df['timestamp'].astype('datetime64')
    #
    #     np_data = {key: df[key].values for key in df.keys()}
    #
    #     self.markets[provider] = {
    #         'symbol': {
    #             symbol: {
    #                 data_type: np_data
    #             },
    #         }
    #     }
    #     self.data_len = len(data['data'])
    #     self.sig_init.emit()
    #
    # def slt_ws_finish(self, data):
    #     pass
    #
    # def create_chart_model(self, idx: str, data_type: str):
    #     provider, symbol = idx.split(':')
    #     try:
    #         data = self.markets[provider]['symbol'][symbol][data_type]
    #     except KeyError:
    #         data = {}
    #
    #     model = ChartModel(idx=idx, store=self, ws=self.ws)
    #     self.chart_models[model.ID] = model
    #     return model
