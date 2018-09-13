from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

from BSTrade.Data.source import bs_req
from BSTrade.Data.const import Provider, HttpEndPointType


class OrderBook:
    def __init__(self, provider, symbol):
        self.symbol = symbol
        self.provider = provider
        self.timestamp = None
        self.book = []


class Trade:
    def __init__(self, provider, symbol):
        self.symbol = symbol
        self.provider = provider
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

    def update(self, bin_size, data):
        self.data[bin_size] = data

    def add_old(self, bin_size, data):
        self.data[bin_size].append(data)

    def add_new(self, data):
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

    def request_sync_candle(self):
        param = {
            'binSize': '1m',
            'symbol': self.name,
            'count': 500,
            'start': 0,
            'reverse': True
        }

        def calc(p):
            p['start'] += 500
            return p, p['start'] < 500 * 20

        bs_req.loop.set_calc(calc)
        bs_req.loop.set_prov(self.provider)
        bs_req.loop.set_param(param)
        bs_req.loop.sig.finished.connect(self.loop_finish)
        bs_req.loop.start()

    def loop_finish(self, data):
        bs_req.loop.sig.finished.disconnect(self.loop_finish)
        print(len(data))


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


if __name__ == '__main__':
    app = QApplication([])
    s = Symbol({'symbol': 'XBTUSD', 'state': 'Open'}, Provider.BITMEX)
    bs_req.get_candles(Provider.BITMEX, {'binSize': '1m'})
    s.request_sync_candle()
    bs_req.get_candles(Provider.BITMEX, {'binSize': '1m'})
    bs_req.get_candles(Provider.BITMEX, {'binSize': '1m'})
    bs_req.get_candles(Provider.BITMEX, {'binSize': '1m'})
    bs_req.get_candles(Provider.BITMEX, {'binSize': '1m'})


    app.exec()