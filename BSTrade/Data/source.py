import inspect
import time
from pprint import pprint
from typing import Dict

from PyQt5.QtCore import QUrl, QUrlQuery
from PyQt5.QtWidgets import QApplication

from BSTrade.Api import HttpClient
from BSTrade.Api.auth import bitmex
from BSTrade.Api.wsclient import WsClient
from BSTrade.Data.const import Provider, HttpEndPointType as EndPoint
from BSTrade.util.fn import attach_timer


def xstr(obj, require=None):
    if obj is None:
        if require:
            raise ValueError('required value is not filled')

        return None
    elif isinstance(obj, bool):
        return str(obj).lower()
    else:
        return str(obj)


def make_params(prov, h_method, params=None, method='GET'):
    if params is None:
        params = {}

    if prov == Provider.BITMEX:
        base = "https://www.bitmex.com/api/v1"

        if h_method == EndPoint.exchange_status:
            pass

        elif h_method == EndPoint.candles:
            pass

        elif h_method == EndPoint.symbols:
            url = base + '/instrument'
            q = [(
                tup[0], xstr(params.get(tup[0]), tup[1])
            ) for tup in [
                ('symbol', False),
                ('filter', False),
                ('columns', False),
                ('count', False),
                ('start', False),
                ('reverse', False),
                ('startTime', False),
                ('endTime', False),
            ]]

            qurl = QUrl(url)
            qs = QUrlQuery()
            qs.setQueryItems(q)

            if method == 'GET':
                qurl.setQuery(qs)

            return qurl, qs.query().encode()

        elif h_method == EndPoint.orderbook:
            pass

        elif h_method == EndPoint.ticker:
            pass

    elif prov == Provider.UPBIT:
        base = "https://api.upbit.com/v1"

        if h_method == EndPoint.exchange_status:
            pass

        elif h_method == EndPoint.candles:
            pass

        elif h_method == EndPoint.symbols:
            pass

        elif h_method == EndPoint.orderbook:
            pass

        elif h_method == EndPoint.ticker:
            pass

    elif prov == Provider.COINONE:
        base = 'https://api.coinone.co.kr/'

        if h_method == EndPoint.exchange_status:
            pass

        elif h_method == EndPoint.candles:
            pass

        elif h_method == EndPoint.symbols:
            url = base + '/ticker_utc'
            q = [(
                tup[0], xstr(params.get(tup[0]), tup[1])
            ) for tup in [
                ('currency', False)
            ]]

            qurl = QUrl(url)
            qs = QUrlQuery()
            qs.setQueryItems(q)

            if method == 'GET':
                qurl.setQuery(qs)

            return qurl, qs.query().encode()

        elif h_method == EndPoint.orderbook:
            pass

        elif h_method == EndPoint.ticker:
            pass

def make_auth_header(prov, qurl, data=None, method='GET'):
    if prov == Provider.BITMEX:
        api_key = bitmex.api_keys['real']['order']['key']
        api_secret = bitmex.api_keys['real']['order']['secret']
        expires = int(round(time.time()) + 5)
        header = {}

        if not api_key or not api_secret:
            return header

        if method == 'PUT':
            header.update({
                'content-type': 'application/x-www-form-urlencoded'
            })

        sign = bitmex.generate_signature(
            api_secret,
            method,
            qurl.path() + '?' + qurl.query(QUrl.FullyDecoded),
            expires,
            data or ''
        )
        header.update({
            'api-expires': str(expires),
            'api-key': api_key,
            'api-signature': sign
        })
        return header

    elif prov == Provider.UPBIT:
        pass

    elif prov == Provider.COINONE:
        pass


class RateLimiter:
    def __init__(self, prov):
        self.provider = prov
        self.rate = 300
        self.per = 300
        self.allowance = self.rate
        self.last_check = time.time()
        self.reply = []

    def add(self, res):
        self.reply.append(res)

    def abort_all(self):
        for i in self.reply:
            try:
                i.close()
                i.abort()
                i.deleteLater()
            except BaseException as e:
                print(e)

        self.reply = []

    def remove_one(self, res):
        self.reply.pop(self.reply.index(res))

    def res_one(self):
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        self.allowance += int(time_passed * (self.rate / self.per))

        if self.allowance > self.rate:
            self.allowance = self.rate
        elif self.allowance < 1:
            print('no', self.allowance)
        else:
            print('ok', self.allowance)
            self.allowance -= 1


class BSreq:

    def __init__(self):
        self.provider = Provider
        self.http = HttpClient()
        self.ws: Dict[Provider, WsClient] = {
            prov: WsClient() for prov in Provider
        }
        self.limiter: Dict[Provider, RateLimiter] = {
            prov: RateLimiter(prov) for prov in Provider
        }

        self.http.sig_ended.connect(self.res)

    def exchange_status(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)
        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.set_property(res, prov, h_method, params)

    def candles(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)
        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.set_property(res, prov, h_method, params)

    def symbols(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)
        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.limiter[prov].add(res)
        self.set_property(res, prov, h_method, params)

    def orderbook(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)
        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
        self.set_property(res, prov, h_method, params)

    def ticker(self, prov: Provider, params=None):
        method = 'GET'
        h_method = EndPoint[inspect.currentframe().f_code.co_name]
        qurl, _ = make_params(prov, h_method, params)
        auth_header = make_auth_header(prov, qurl, method=method)
        res = self.http.get(qurl.toString(QUrl.FullyEncoded), auth_header)
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
            pprint(self.http.headers())
            self.limiter[prov].res_one()
            self.limiter[prov].remove_one(data)


bs_req = BSreq()
attach_timer(BSreq)

if __name__ == '__main__':

    app = QApplication([])

    for i in range(100):
        bs_req.symbols(Provider.BITMEX, {'count': 500, 'column': 'symbol'})

    # bs_req.symbols(Provider.COINONE, {'currency': 'all'})

    app.exec()
