import inspect
from typing import Dict

from PyQt5.QtCore import QUrl, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication

from BSTrade.Api import HttpClient
from BSTrade.Api.wsclient import WsClient
from BSTrade.Data.const import Provider, HttpEndPointType as EndPoint
from BSTrade.Data.http_helper import RateLimiter, make_params, \
    make_auth_header, serialize_result
from BSTrade.util.fn import attach_timer


class BSWsSig(QObject):
    subscribed = pyqtSignal(dict)
    auth_success = pyqtSignal()


class BSWs:
    sig = BSWsSig()

    def __init__(self):
        self.client: Dict[Provider, WsClient] = {}
        self._subscribe = {}

    def start_all(self):
        """
        Must start outer of __init__
        It won't start in __init__

        :return:
        """
        for prov in Provider:
            self._subscribe[prov] = set()
            client = self.client[prov] = WsClient()
            client.sig_connected.connect(self.on_connected)
            client.sig_message.connect(self.on_message)
            client.open('wss://www.bitmex.com/realtime')  # start ws

    def ping(self, prov):
        self.client[prov].send('ping')

    def auth(self, prov):
        pass

    def subscribes(self, prov) -> set:
        return self._subscribe[prov]

    def subscribe(self, prov):
        pass

    def unsubscribe(self, prov):
        pass

    def on_connected(self):
        print('connected')

    def on_message(self, client):
        print(client)


class BSReqSig(QObject):
    finished = pyqtSignal(object)


class BSReq:
    sig = BSReqSig()

    def __init__(self):
        self.provider = Provider
        self.http = HttpClient()
        self.limiter: Dict[Provider, RateLimiter] = {
            prov: RateLimiter(prov) for prov in Provider
        }

        self.http.sig_ended.connect(self.res)

    def get_exchange_status(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)

        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.limiter[prov].add(res)
        self.set_property(res, prov, h_method, params)

    def get_candles(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)

        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.limiter[prov].add(res)
        self.set_property(res, prov, h_method, params)

    def get_symbols(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)

        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.limiter[prov].add(res)
        self.set_property(res, prov, h_method, params)

    def get_orderbook(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)

        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.limiter[prov].add(res)
        self.set_property(res, prov, h_method, params)

    def get_ticker(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)

        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.limiter[prov].add(res)
        self.set_property(res, prov, h_method, params)

    def set_property(self, res, prov, h_method, params):
        res.setProperty('prov', prov)
        res.setProperty('h_method', h_method)
        res.setProperty('params', params)

    def res(self, data):
        prov = data.property('prov')
        h_method = data.property('h_method')
        params = data.property('params')

        if self.http.status() != 200:
            print('abort all')
            self.limiter[prov].abort_all()

        elif self.http.status() == 200:
            self.limiter[prov].res_one()
            self.limiter[prov].remove_one(data)

            self.sig.finished.emit(serialize_result(
                prov, h_method, params, self.http.json()
            ))


bs_ws = BSWs()
bs_req = BSReq()
attach_timer(BSReq)

if __name__ == '__main__':

    app = QApplication([])

    def result(res):
        """
        res = {
            'provider': prov,
            'endpoint': h_method,
            'params': params,
            'data': result
        }
        :param res:
        :return:
        """
        print(bs_req.limiter[Provider.BITMEX].current())
        print(len(res))
        # bs_req.get_candles(Provider.BITMEX, {'count': 500, 'binSize': '1m'})

    bs_ws.start_all()

    bs_req.sig.finished.connect(result)
    bs_req.get_candles(Provider.BITMEX, {
        'count': 500,
        'binSize': '1m',
        'reverse': True,
        'symbol': 'XBTUSD'
    })
    # bs_req.get_symbols(Provider.COINONE, {'currency': 'all'})

    app.exec()
