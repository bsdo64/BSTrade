import time

from PyQt5.QtCore import QUrl, QUrlQuery, QObject, pyqtSignal

from BSTrade.Api.auth import bitmex
from BSTrade.Data.const import Provider, HttpEndPointType as EndPoint


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

    if prov == Provider.BITMEX:
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

    elif prov == Provider.UPBIT:
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

    elif prov == Provider.COINONE:
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

    elif prov == Provider.BINANCE:
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


def serialize_result(prov, h_method, params, result):
    res = {
        'provider': prov,
        'endpoint': h_method,
        'params': params
    }

    if prov == Provider.BITMEX:
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
                    "symbol": "string",
                    "rootSymbol": "string",
                    "state": "string",
                    "typ": "string",
                    "listing": "2018-09-11T14:55:46.798Z",
                    "front": "2018-09-11T14:55:46.798Z",
                    "expiry": "2018-09-11T14:55:46.798Z",
                    "settle": "2018-09-11T14:55:46.798Z",
                    "relistInterval": "2018-09-11T14:55:46.798Z",
                    "inverseLeg": "string",
                    "sellLeg": "string",
                    "buyLeg": "string",
                    "optionStrikePcnt": 0,
                    "optionStrikeRound": 0,
                    "optionStrikePrice": 0,
                    "optionMultiplier": 0,
                    "positionCurrency": "string",
                    "underlying": "string",
                    "quoteCurrency": "string",
                    "underlyingSymbol": "string",
                    "reference": "string",
                    "referenceSymbol": "string",
                    "calcInterval": "2018-09-11T14:55:46.799Z",
                    "publishInterval": "2018-09-11T14:55:46.799Z",
                    "publishTime": "2018-09-11T14:55:46.799Z",
                    "maxOrderQty": 0,
                    "maxPrice": 0,
                    "lotSize": 0,
                    "tickSize": 0,
                    "multiplier": 0,
                    "settlCurrency": "string",
                    "underlyingToPositionMultiplier": 0,
                    "underlyingToSettleMultiplier": 0,
                    "quoteToSettleMultiplier": 0,
                    "isQuanto": true,
                    "isInverse": true,
                    "initMargin": 0,
                    "maintMargin": 0,
                    "riskLimit": 0,
                    "riskStep": 0,
                    "limit": 0,
                    "capped": true,
                    "taxed": true,
                    "deleverage": true,
                    "makerFee": 0,
                    "takerFee": 0,
                    "settlementFee": 0,
                    "insuranceFee": 0,
                    "fundingBaseSymbol": "string",
                    "fundingQuoteSymbol": "string",
                    "fundingPremiumSymbol": "string",
                    "fundingTimestamp": "2018-09-11T14:55:46.800Z",
                    "fundingInterval": "2018-09-11T14:55:46.800Z",
                    "fundingRate": 0,
                    "indicativeFundingRate": 0,
                    "rebalanceTimestamp": "2018-09-11T14:55:46.800Z",
                    "rebalanceInterval": "2018-09-11T14:55:46.800Z",
                    "openingTimestamp": "2018-09-11T14:55:46.800Z",
                    "closingTimestamp": "2018-09-11T14:55:46.800Z",
                    "sessionInterval": "2018-09-11T14:55:46.800Z",
                    "prevClosePrice": 0,
                    "limitDownPrice": 0,
                    "limitUpPrice": 0,
                    "bankruptLimitDownPrice": 0,
                    "bankruptLimitUpPrice": 0,
                    "prevTotalVolume": 0,
                    "totalVolume": 0,
                    "volume": 0,
                    "volume24h": 0,
                    "prevTotalTurnover": 0,
                    "totalTurnover": 0,
                    "turnover": 0,
                    "turnover24h": 0,
                    "homeNotional24h": 0,
                    "foreignNotional24h": 0,
                    "prevPrice24h": 0,
                    "vwap": 0,
                    "highPrice": 0,
                    "lowPrice": 0,
                    "lastPrice": 0,
                    "lastPriceProtected": 0,
                    "lastTickDirection": "string",
                    "lastChangePcnt": 0,
                    "bidPrice": 0,
                    "midPrice": 0,
                    "askPrice": 0,
                    "impactBidPrice": 0,
                    "impactMidPrice": 0,
                    "impactAskPrice": 0,
                    "hasLiquidity": true,
                    "openInterest": 0,
                    "openValue": 0,
                    "fairMethod": "string",
                    "fairBasisRate": 0,
                    "fairBasis": 0,
                    "fairPrice": 0,
                    "markMethod": "string",
                    "markPrice": 0,
                    "indicativeTaxRate": 0,
                    "indicativeSettlePrice": 0,
                    "optionUnderlyingPrice": 0,
                    "settledPrice": 0,
                    "timestamp": "2018-09-11T14:55:46.801Z"
                }
            ]
            """
            res['data'] = [{
                'symbol': item['symbol'],
                'state': item['state'],
                'pair': item['quoteCurrency'],
                'tickSize': item['tickSize'],
                'makerFee': item['makerFee'],
                'takerFee': item['takerFee'],
                'timestamp': item['timestamp'],
            } for item in result]

        elif h_method == EndPoint.get_ticker:
            pass
    elif prov == Provider.UPBIT:
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
    elif prov == Provider.COINONE:
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

    elif prov == Provider.BINANCE:
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