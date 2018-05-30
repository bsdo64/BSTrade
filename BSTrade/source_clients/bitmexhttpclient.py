import json
import time
from PyQt5.QtCore import QUrl, QUrlQuery
from .httpclient import HttpClient
from .auth import bitmex


class BitmexHttpClient(HttpClient):

    def __init__(self, test=False, api_key=None, api_secret=None):
        super().__init__()
        if test:
            self.base_uri = "https://testnet.bitmex.com/api/v1"
        else:
            self.base_uri = "https://www.bitmex.com/api/v1"

        self.test = test
        self.api_key = api_key
        self.api_secret = api_secret

        self.rate_limit = None

        # api - endpoints
        self.Announcement = Announcement(self)
        self.ApiKey = ApiKey(self)
        self.Chat = Chat(self)
        self.Execution = Execution(self)
        self.Funding = Funding(self)
        self.Instrument = Instrument(self)
        self.Insurance = Insurance(self)
        self.Leaderboard = Leaderboard(self)
        self.Liquidation = Liquidation(self)
        self.Notification = Notification(self)
        self.Order = Order(self)
        self.OrderBook = OrderBook(self)
        self.Position = Position(self)
        self.Quote = Quote(self)
        self.Schema = Schema(self)
        self.Settlement = Settlement(self)
        self.Stats = Stats(self)
        self.Trade = Trade(self)
        self.User = User(self)

    def xstr(self, obj):
        if obj is None:
            return None
        else:
            return str(obj)

    def clean_tuple(self, l):
        return [t for t in l if t[1]]

    def make_q_url(self, endpoint, query=None, data=None):
        if query is None:
            query = []
        if data is None:
            data = []

        query = self.clean_tuple(query)
        data = self.clean_tuple(data)

        qurl = QUrl(endpoint)
        query_url = QUrlQuery()
        query_url.setQueryItems(query or data)

        if data:
            return qurl, query_url
        else:
            qurl.setQuery(query_url)
            return qurl

    def make_auth_header(self, qurl, data='', method=None):
        header = {}

        if not self.api_key and not self.api_secret:
            return header

        if method:
            verb = method

            if method == 'PUT':
                header.update({'content-type': 'application/x-www-form-urlencoded'})
        else:
            verb = 'GET'

        url = qurl.path() + '?' + qurl.query(QUrl.FullyDecoded)
        expires = int(round(time.time()) + 5)

        sign = bitmex.generate_signature(self.api_secret, verb, url, expires, data)
        header.update({
            'api-expires': str(expires),
            'api-key': self.api_key,
            'api-signature': sign
        })
        return header

    def get_base_uri(self):
        url = self.base_uri
        qurl = QUrl(url)

        self.request.setUrl(qurl)
        self.network_manager.get(self.request)


class Announcement:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/announcement'

    def get(self, columns=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('columns', c.xstr(columns))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_urgent(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/urgent')
        header = c.make_auth_header(qurl)

        c.get(qurl.toString(QUrl.FullyEncoded), header)


class ApiKey:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/apiKey'

    def get(self, reverse=False):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('reverse', c.xstr(reverse))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Chat:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/chat'

    def get(self, count: int = 100, start: int = 0,
            reverse: bool = True, channel_id: float = None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('channelID', c.xstr(channel_id))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def post(self, message, channel_id: float = 1.0):
        c = self.client
        qurl, post_data = c.make_q_url(self.endpoint, data=[
            ('message', c.xstr(message)),
            ('channelID', c.xstr(channel_id))
        ])

        data = post_data.query().encode()
        header = c.make_auth_header(qurl, data=data, method='POST')
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def get_channels(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/channels')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_connected(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/connected')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Execution:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/execution'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_trade_history(self, symbol: str, json_filter: str = None, columns: str = None,
                          count: int = None, start: int = None, reverse: bool = False,
                          start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/tradeHistory', query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Funding:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/funding'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Instrument:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/instrument'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_active(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/active')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_active_and_indices(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/activeAndIndices')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_active_intervals(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/activeIntervals')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_composite_index(self, symbol: str = '.XBT', json_filter: str = None, columns: str = None,
                            count: int = None, start: int = None, reverse: bool = False,
                            start_time=None, end_time=None, account: int = None):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/compositeIndex', query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
            ('account', c.xstr(account)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_indices(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/indices')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Insurance:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/insurance'

    def get(self, symbol: str = '', json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Leaderboard:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/leaderboard'

    def get(self, method='notional'):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('method', c.xstr(method)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_name(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/name')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Liquidation:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/liquidation'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Notification:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/notification'

    def get(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint)

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Order:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/order'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def put(self, order_id: str = None, orig_cl_ord_id: str = None, cl_ord_id: str = None,
            simple_order_qty: float = None, order_qty: float = None, simple_leaves_qty: float = None,
            leaves_qty: float = None, price: float = None, stop_px: float = None,
            peg_offset_value: float = None, text: str = None):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint, data=[
            ('orderID', c.xstr(order_id)),
            ('origClOrdID', c.xstr(orig_cl_ord_id)),
            ('clOrdID', c.xstr(cl_ord_id)),
            ('simpleOrderQty', c.xstr(simple_order_qty)),
            ('orderQty', c.xstr(order_qty)),
            ('simpleLeavesQty', c.xstr(simple_leaves_qty)),
            ('leavesQty', c.xstr(leaves_qty)),
            ('price', c.xstr(price)),
            ('stopPx', c.xstr(stop_px)),
            ('pegOffsetValue', c.xstr(peg_offset_value)),
            ('text', c.xstr(text)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='PUT', data=data)
        c.put(qurl.toString(QUrl.FullyEncoded), header, data)

    def post(self, symbol, side: str = None, simple_order_qty: float = None,
             order_qty: float = None, price: float = None, display_qty: float = None,
             stop_px: float = None, cl_ord_id: str = None, cl_ord_link_id: str = None,
             peg_offset_value: float = None, peg_price_type: str = None, ord_type: str = None,
             time_in_force: str = None, exe_inst: str = None, contingency_type: str = None,
             text: str = None):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint, data=[
            ('symbol', c.xstr(symbol)),
            ('side', c.xstr(side)),
            ('simpleOrderQty', c.xstr(simple_order_qty)),
            ('orderQty', c.xstr(order_qty)),
            ('price', c.xstr(price)),
            ('displayQty', c.xstr(display_qty)),
            ('stopPx', c.xstr(stop_px)),
            ('clOrdID', c.xstr(cl_ord_id)),
            ('clOrdLinkID', c.xstr(cl_ord_link_id)),
            ('pegOffsetValue', c.xstr(peg_offset_value)),
            ('pegPriceType', c.xstr(peg_price_type)),
            ('ordType', c.xstr(ord_type)),
            ('timeInForce', c.xstr(time_in_force)),
            ('exeInst', c.xstr(exe_inst)),
            ('contingencyType', c.xstr(contingency_type)),
            ('text', c.xstr(text)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def delete(self, order_id: str = None, cl_ord_id: str = None, text: str = None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('orderID', c.xstr(order_id)),
            ('clOrdID', c.xstr(cl_ord_id)),
            ('text', c.xstr(text)),
        ])

        header = c.make_auth_header(qurl, method='DELETE')
        c.delete(qurl.toString(QUrl.FullyEncoded), header)

    def delete_all(self, symbol=None, json_filter=None, text=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/all', query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('text', c.xstr(text)),
        ])

        header = c.make_auth_header(qurl, method='DELETE')
        c.delete(qurl.toString(QUrl.FullyEncoded), header)

    def put_bulk(self, orders: list):
        """
        :param orders:

        json.dumps([
            {"orderID":order_id","price":2433.5,"orderQty":147,"side":"Sell"},
            {"orderID":order_id","price":2433.5,"orderQty":147,"side":"Sell"},
        ])
        """
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/bulk', data=[
            ('orders', c.xstr(json.dumps(orders))),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='PUT', data=data)
        c.put(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_bulk(self, orders: list):
        """
        :param orders:

        json.dumps([
            {"symbol":"XBTUSD","price":2433.5,"orderQty":147,"side":"Sell"},
            {"symbol":"XBTUSD","price":2433.5,"orderQty":147,"side":"Sell"},
        ])
        """
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/bulk', data=[
            ('orders', c.xstr(json.dumps(orders))),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_cancel_all_after(self, timeout):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/cancelAllAfter', data=[
            ('timeout', c.xstr(timeout)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)


class OrderBook:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/orderBook'

    def get_l2(self, symbol: str, depth: float = 25.0):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/L2', query=[
            ('symbol', c.xstr(symbol)),
            ('depth', c.xstr(depth)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Position:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/position'

    def get(self, json_filter=None, columns=None, count=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def post_isolate(self, symbol: str, enabled: bool = True):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/isolate', data=[
            ('symbol', c.xstr(symbol)),
            ('enabled', c.xstr(str(enabled).lower())),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_leverage(self, symbol: str, leverage: float):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/leverage', data=[
            ('symbol', c.xstr(symbol)),
            ('leverage', c.xstr(leverage)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_risk_limit(self, symbol: str, risk_limit: float):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/riskLimit', data=[
            ('symbol', c.xstr(symbol)),
            ('riskLimit', c.xstr(risk_limit)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_transfer_margin(self, symbol, amount):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/transferMargin', data=[
            ('symbol', c.xstr(symbol)),
            ('amount', c.xstr(amount)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)


class Quote:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/quote'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_bucketed(self, bin_size: str, symbol: str, json_filter: str = None,
                     columns: str = None, count: int = None, start: int = None,
                     reverse: bool = False, start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/bucketed', query=[
            ('binSize', c.xstr(bin_size)),
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Schema:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/schema'

    def get(self, model: str = None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('model', c.xstr(model)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_websocket_help(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/websocketHelp')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Settlement:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/settlement'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Stats:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/stats'

    def get(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint)

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_history(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/history')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_history_usd(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/historyUSD')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Trade:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/trade'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: int = None, start: int = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_bucketed(self, bin_size: str, partial: bool = False,
                     symbol: str = None, json_filter: str = None, columns: str = None,
                     count: int = None, start: int = None, reverse: bool = False,
                     start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/bucketed', query=[
            ('binSize', c.xstr(bin_size)),
            ('partial', c.xstr(partial)),
            ('symbol', c.xstr(symbol)),
            ('filter', c.xstr(json_filter)),
            ('columns', c.xstr(columns)),
            ('count', c.xstr(count)),
            ('start', c.xstr(start)),
            ('reverse', c.xstr(reverse)),
            ('startTime', c.xstr(start_time)),
            ('endTime', c.xstr(end_time)),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class User:
    def __init__(self, client: BitmexHttpClient):
        self.client = client
        self.endpoint = self.client.base_uri + '/user'

    def get(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint)

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def put(self, firstname: str = None, lastname: str = None, old_password: str = None,
            new_password: str = None, new_password_confirm: str = None, username: str = None,
            country: str = None, pgp_pub_key: str = None):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint, data=[
            ('firstname', c.xstr(firstname)),
            ('lastname', c.xstr(lastname)),
            ('oldPassword', c.xstr(old_password)),
            ('newPassword', c.xstr(new_password)),
            ('newPasswordConfirm', c.xstr(new_password_confirm)),
            ('username', c.xstr(username)),
            ('country', c.xstr(country)),
            ('pgpPubKey', c.xstr(pgp_pub_key)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='PUT', data=data)
        c.put(qurl.toString(QUrl.FullyEncoded), header, data)

    def get_affiliate_status(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/affiliateStatus')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def post_cancel_withdrawal(self, token):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/affiliateStatus', data=[
            ('token', c.xstr(token))
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def get_check_referral_code(self, referral_code: str = None):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/checkReferralCode', query=[
            ('referralCode', c.xstr(referral_code))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_commission(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/commission')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def post_confirm_email(self, token):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/confirmEmail', data=[
            ('token', c.xstr(token))
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_confirm_enable_tfa(self, token, auth_type: str = None):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/confirmEnableTFA', data=[
            ('token', c.xstr(token)),
            ('type', c.xstr(auth_type))
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_confirm_withdrawal(self, token):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/confirmWithdrawal', data=[
            ('token', c.xstr(token)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def get_deposit_address(self, currency: str = 'XBt'):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/depositAddress', query=[
            ('currency', c.xstr(currency))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def post_disable_tfa(self, token, auth_type: str = None):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/disableTFA', data=[
            ('token', c.xstr(token)),
            ('type', c.xstr(auth_type))
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_logout(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/logout')

        header = c.make_auth_header(qurl, method='POST')
        c.post(qurl.toString(QUrl.FullyEncoded), header)

    def post_logout_all(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/logoutAll')

        header = c.make_auth_header(qurl, method='POST')
        c.post(qurl.toString(QUrl.FullyEncoded), header)

    def get_margin(self, currency: str = 'XBt'):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/margin', query=[
            ('currency', c.xstr(currency))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_min_withdrawal_fee(self, currency: str = 'XBt'):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/minWithdrawalFee', query=[
            ('currency', c.xstr(currency))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def post_preferences(self, prefs: str, overwrite: bool = None):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/preferences', data=[
            ('prefs', c.xstr(prefs)),
            ('overwrite', c.xstr(overwrite))
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_request_enable_tfa(self, auth_type: str = None):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/requestEnableTFA', data=[
            ('type', c.xstr(auth_type)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def post_request_withdrawal(self, currency, amount, address,
                                fee: float = None, otp_token: str = None):
        c = self.client
        qurl, data = c.make_q_url(self.endpoint + '/requestWithdrawal', data=[
            ('currency', c.xstr(currency)),
            ('amount', c.xstr(amount)),
            ('address', c.xstr(address)),
            ('otpToken', c.xstr(otp_token)),
            ('fee', c.xstr(fee)),
        ])

        data = data.query().encode()
        header = c.make_auth_header(qurl, method='POST', data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def get_wallet(self, currency: str = 'XBt'):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/wallet', query=[
            ('currency', c.xstr(currency))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_wallet_history(self, currency: str = 'XBt'):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/walletHistory', query=[
            ('currency', c.xstr(currency))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_wallet_summary(self, currency: str = 'XBt'):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/walletSummary', query=[
            ('currency', c.xstr(currency))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)
