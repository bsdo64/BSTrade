import time

from PyQt5.QtCore import QUrl, QUrlQuery, QObject, pyqtSignal

from BSTrade.Api.auth import bitmex
from BSTrade.Data.const import Exchange, HttpEndPointType as EndPoint


class ReqLooperSig(QObject):
    finished = pyqtSignal(object)


class ReqLooper:
    sig = ReqLooperSig()

    def __init__(self, req):
        self.req = req
        self.prov = None
        self.param = None
        self.calc = None

        self.r = []

    def set_prov(self, prov):
        self.prov = prov

    def set_param(self, param):
        self.param = param

    def set_calc(self, f):
        """
        def calc(p):
            p['start'] += 500
            return p, p['start'] < 500 * 20

        f = calc
        """
        self.calc = f

    def start(self):
        self.req.sig.finished.connect(self.req_loop)
        self.req.get_candles(self.prov, self.param)

    def clear(self):
        self.r = []
        self.calc = None
        self.param = None
        self.prov = None

        self.req.sig.finished.disconnect(self.req_loop)

    def req_loop(self, data):
        self.r.append(data)
        param, cond = self.calc(self.param)
        self.param = param
        if cond:
            self.req.get_candles(self.prov, self.param)
        else:
            self.sig.finished.emit(self.r)
            self.clear()


class RateLimiter:
    def __init__(self, prov):
        self.provider = prov
        self.rate = 300
        self.per = 300
        self.allowance = self.rate
        self.last_check = None
        self.reply = []

    def current(self):
        return self.allowance

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

        if self.last_check is None:
            self.last_check = current

        time_passed = current - self.last_check
        self.last_check = current
        self.allowance += time_passed * (self.rate / self.per)

        if self.allowance > self.rate:
            self.allowance = self.rate
            print(self.provider.name, 'rate-limit : ', self.allowance)
        elif self.allowance < 1.0:
            print(self.provider.name,
                  'request canceled. rate-limit : ', self.allowance)
        else:
            self.allowance -= 1.0
            print(self.provider.name, 'rate-limit : ', self.allowance)


def xstr(obj, require=None):
    if obj is None:
        if require:
            raise ValueError('required value is not filled')

        return None
    elif isinstance(obj, bool):
        return str(obj).lower()
    else:
        return str(obj)


def make_url(url, q, method):
    qurl = QUrl(url)
    qs = QUrlQuery()
    qs.setQueryItems(q)

    if method == 'GET':
        qurl.setQuery(qs)

    return qurl, qs.query().encode()


def make_params(prov, h_method, params=None, method='GET'):
    if params is None:
        params = {}

    if prov == Exchange.BITMEX:
        base = "https://www.bitmex.com/api/v1"

        if h_method == EndPoint.get_exchange_status:
            pass

        elif h_method == EndPoint.get_candles:
            url = base + '/trade/bucketed'
            q = [(
                tup[0], xstr(params.get(tup[0]), tup[1])
            ) for tup in [
                ('binSize', True),
                ('symbol', False),
                ('filter', False),
                ('columns', False),
                ('count', False),
                ('start', False),
                ('reverse', False),
                ('startTime', False),
                ('endTime', False),
            ]]

            return make_url(url, q, method)

        elif h_method == EndPoint.get_symbols:
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

            return make_url(url, q, method)

        elif h_method == EndPoint.get_orderbook:
            pass

        elif h_method == EndPoint.get_ticker:
            pass

    elif prov == Exchange.UPBIT:
        base = "https://api.upbit.com/v1"

        if h_method == EndPoint.get_exchange_status:
            pass

        elif h_method == EndPoint.get_candles:
            pass

        elif h_method == EndPoint.get_symbols:
            pass

        elif h_method == EndPoint.get_orderbook:
            pass

        elif h_method == EndPoint.get_ticker:
            pass

    elif prov == Exchange.COINONE:
        base = 'https://api.coinone.co.kr/'

        if h_method == EndPoint.get_exchange_status:
            pass

        elif h_method == EndPoint.get_candles:
            pass

        elif h_method == EndPoint.get_symbols:
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

            return make_url(url, q, method)

        elif h_method == EndPoint.get_orderbook:
            pass

        elif h_method == EndPoint.get_ticker:
            pass

    elif prov == Exchange.BINANCE:
        base = 'https://api.binance.com/api/v1'

        if h_method == EndPoint.get_exchange_status:
            pass

        elif h_method == EndPoint.get_candles:
            pass

        elif h_method == EndPoint.get_symbols:
            url = base + '/exchangeInfo'
            q = []

            qurl = QUrl(url)
            qs = QUrlQuery()
            qs.setQueryItems(q)

            if method == 'GET':
                qurl.setQuery(qs)

            return make_url(url, q, method)

        elif h_method == EndPoint.get_orderbook:
            pass

        elif h_method == EndPoint.get_ticker:
            pass


def make_auth_header(prov, qurl, data=None, method='GET'):
    if prov == Exchange.BITMEX:
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

    elif prov == Exchange.UPBIT:
        pass

    elif prov == Exchange.COINONE:
        pass


def serialize_result(prov, h_method, params, result):
    res = {
        'provider': prov,
        'endpoint': h_method,
        'params': params
    }

    if prov == Exchange.BITMEX:
        if h_method == EndPoint.get_candles:
            """
            [
                {
                    "timestamp": "2018-09-11T14:55:47.264Z",
                    "symbol": "string",
                    "open": 0,
                    "high": 0,
                    "low": 0,
                    "close": 0,
                    "trades": 0,
                    "volume": 0,
                    "vwap": 0,
                    "lastSize": 0,
                    "turnover": 0,
                    "homeNotional": 0,
                    "foreignNotional": 0
                }
            ]
            """
            res['data'] = [{
                'timestamp': item['timestamp'],
                'symbol': item['symbol'],
                'open': item['open'],
                'high': item['high'],
                'low': item['low'],
                'close': item['close'],
                'trades': item['trades'],
                'volume': item['volume'],
            } for item in result]

        elif h_method == EndPoint.get_exchange_status:
            pass
        elif h_method == EndPoint.get_orderbook:
            pass
        elif h_method == EndPoint.get_symbols:
            """
            [
                  {
                    "symbol": "XBTUSD",
                    "rootSymbol": "XBT",
                    "state": "Open",
                    "typ": "FFWCSX",
                    "listing": "2016-05-13T12:00:00.000Z",
                    "front": "2016-05-13T12:00:00.000Z",
                    "positionCurrency": "USD",
                    "underlying": "XBT",
                    "quoteCurrency": "USD",
                    "underlyingSymbol": "XBT=",
                    "reference": "BMEX",
                    "referenceSymbol": ".BXBT",
                    "calcInterval": null,
                    "publishInterval": null,
                    "publishTime": null,
                    "maxOrderQty": 10000000,
                    "maxPrice": 1000000,
                    "lotSize": 1,
                    "tickSize": 0.5,
                    "multiplier": -100000000,
                    "settlCurrency": "XBt",
                    "underlyingToPositionMultiplier": null,
                    "underlyingToSettleMultiplier": -100000000,
                    "quoteToSettleMultiplier": null,
                    "isQuanto": false,
                    "isInverse": true,
                    "initMargin": 0.01,
                    "maintMargin": 0.005,
                    "riskLimit": 20000000000,
                    "riskStep": 10000000000,
                    "limit": null,
                    "capped": false,
                    "taxed": true,
                    "deleverage": true,
                    "makerFee": -0.00025,
                    "takerFee": 0.00075,
                    "fundingBaseSymbol": ".XBTBON8H",
                    "fundingQuoteSymbol": ".USDBON8H",
                    "fundingPremiumSymbol": ".XBTUSDPI8H",
                    "fundingTimestamp": "2018-09-18T04:00:00.000Z",
                    "fundingInterval": "2000-01-01T08:00:00.000Z",
                    "fundingRate": 0.000003,
                    "indicativeFundingRate": -0.000048,
                    "openingTimestamp": "2018-09-18T00:00:00.000Z",
                    "closingTimestamp": "2018-09-18T02:00:00.000Z",
                    "sessionInterval": "2000-01-01T02:00:00.000Z",
                    "prevClosePrice": 6471.83,
                    "prevTotalVolume": 813753649323,
                    "totalVolume": 813824946364,
                    "volume": 71297041,
                    "volume24h": 2569320995,
                    "prevTotalTurnover": 11042062528776500,
                    "totalTurnover": 11043204886146680,
                    "turnover": 1142357370181,
                    "turnover24h": 40483916962693,
                    "homeNotional24h": 404839.1696269308,
                    "foreignNotional24h": 2569320995,
                    "prevPrice24h": 6514.5,
                    "vwap": 6346.7885,
                    "highPrice": 6515,
                    "lowPrice": 6201,
                    "lastPrice": 6246.5,
                    "lastPriceProtected": 6246.5,
                    "lastTickDirection": "ZeroMinusTick",
                    "lastChangePcnt": -0.0411,
                    "bidPrice": 6246.5,
                    "midPrice": 6246.75,
                    "askPrice": 6247,
                    "impactBidPrice": 6246.4864,
                    "impactMidPrice": 6246.75,
                    "impactAskPrice": 6246.8766,
                    "hasLiquidity": true,
                    "openInterest": 748483419,
                    "openValue": 11976483187419,
                    "fairMethod": "FundingRate",
                    "fairBasisRate": 0.003285,
                    "fairBasis": 0,
                    "fairPrice": 6249.58,
                    "markMethod": "FairPrice",
                    "markPrice": 6249.58,
                    "indicativeSettlePrice": 6249.58,
                    "timestamp": "2018-09-18T01:59:30.000Z"
                }

            ]
            
            {
                'symbol',
                'totalVolume',
                'volume',
                'totalTurnover',
                'turnover',
                'openInterest',
                'openValue',
                'timestamp',
                'indicativeSettlePrice',
                'fairPrice',
                'markPrice',
                'lastPrice',
                'lastTickDirection',
                'lastChangePcnt',
                'lastPriceProtected',
                'prevPrice24h',
                'volume24h',
                'turnover24h',
                'homeNotional24h',
                'foreignNotional24h',
                'indicativeFundingRate',
                'bidPrice',
                'midPrice',
                'askPrice',
                'impactBidPrice',
                'impactMidPrice',
                'impactAskPrice',
                'vwap' 
            }
            """
            res['data'] = result

        elif h_method == EndPoint.get_ticker:
            pass
    elif prov == Exchange.UPBIT:
        if h_method == EndPoint.get_candles:
            pass
        elif h_method == EndPoint.get_exchange_status:
            pass
        elif h_method == EndPoint.get_orderbook:
            pass
        elif h_method == EndPoint.get_symbols:
            pass
        elif h_method == EndPoint.get_ticker:
            pass
    elif prov == Exchange.COINONE:
        if h_method == EndPoint.get_candles:
            pass
        elif h_method == EndPoint.get_exchange_status:
            pass
        elif h_method == EndPoint.get_orderbook:
            pass
        elif h_method == EndPoint.get_symbols:
            """
            {
                "ltc": {
                    "volume": "4796.0612",
                    "last": "60300",
                    "yesterday_last": "62450",
                    "yesterday_low": "61550",
                    "high": "62950",
                    "currency": "ltc",
                    "low": "60050",
                    "yesterday_first": "63600",
                    "yesterday_volume": "0.0000",
                    "yesterday_high": "65250",
                    "first": "62450"
                },
            }
            """
            res['data'] = [{
                'symbol': k,
                'state': 'Open',
                'pair': 'KRW',
                'tickSize': None,
                'timestamp': None
            } for k, v in result.items()]

        elif h_method == EndPoint.get_ticker:
            pass

    elif prov == Exchange.BINANCE:
        if h_method == EndPoint.get_candles:
            pass
        elif h_method == EndPoint.get_exchange_status:
            pass
        elif h_method == EndPoint.get_orderbook:
            pass
        elif h_method == EndPoint.get_symbols:
            """
            {
              "timezone": "UTC",
              "serverTime": 1508631584636,
              "rateLimits": [{
                  "rateLimitType": "REQUESTS_WEIGHT",
                  "interval": "MINUTE",
                  "limit": 1200
                },
                {
                  "rateLimitType": "ORDERS",
                  "interval": "SECOND",
                  "limit": 10
                },
                {
                  "rateLimitType": "ORDERS",
                  "interval": "DAY",
                  "limit": 100000
                }
              ],
              "exchangeFilters": [],
              "symbols": [{
                "symbol": "ETHBTC",
                "status": "TRADING",
                "baseAsset": "ETH",
                "baseAssetPrecision": 8,
                "quoteAsset": "BTC",
                "quotePrecision": 8,
                "orderTypes": ["LIMIT", "MARKET"],
                "icebergAllowed": false,
                "filters": [{
                  "filterType": "PRICE_FILTER",
                  "minPrice": "0.00000100",
                  "maxPrice": "100000.00000000",
                  "tickSize": "0.00000100"
                }, {
                  "filterType": "LOT_SIZE",
                  "minQty": "0.00100000",
                  "maxQty": "100000.00000000",
                  "stepSize": "0.00100000"
                }, {
                  "filterType": "MIN_NOTIONAL",
                  "minNotional": "0.00100000"
                }]
              }]
            }
            """

            res['data'] = [{
                'symbol': item['symbol'],
                'state': item['status'],
                'pair': item['quoteAsset'],
                'tickSize': item['filters'][0].get('tickSize'),
                'timestamp': result['serverTime']
            } for item in result['symbols']]

        elif h_method == EndPoint.get_ticker:
            pass

    return res