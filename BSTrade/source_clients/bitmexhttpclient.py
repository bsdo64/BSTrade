import time
from PyQt5.QtCore import QUrl, QUrlQuery
from .httpclient import HttpClient
from .auth import bitmex

secret = '0LC7T3jzS9M9Dk0Ce1sbUmKmg5rZ_sd352gYeLtCUtu6apzb'
key = 'hImUSySfSitmsaSrYv4IKecu'


class Announcement:
    def __init__(self, client):
        self.client = client
        self.endpoint = self.client.base_uri + '/announcement'

    def get(self, columns=None):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('columns', columns)
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_urgent(self):
        c = self.client
        qurl = c.make_q_url(self.endpoint + '/urgent')
        header = c.make_auth_header(qurl)

        c.get(qurl.toString(QUrl.FullyEncoded), header)


class ApiKey:
    def __init__(self, client):
        self.client = client
        self.endpoint = self.client.base_uri + '/apiKey'

    def get(self, reverse=False):
        c = self.client
        qurl = c.make_q_url(self.endpoint, query=[
            ('reverse', str(reverse))
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Chat:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/chat'

    def get(self, count: float = None, start: float = None,
            reverse: bool = True, channel_id: float = None):
        c = self.client
        qurl = c.make_q_url(self.url, query=[
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('channelID', channel_id)
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def post(self, message, channel_id: float = 1.0):
        c = self.client
        qurl, post_data = c.make_q_url(self.url, data=[
            ('message', message),
            ('channelID', str(channel_id))
        ])

        data = post_data.query().encode()
        header = c.make_auth_header(qurl, data=data)
        c.post(qurl.toString(QUrl.FullyEncoded), header, data)

    def get_channels(self):
        c = self.client
        qurl = c.make_q_url(self.url + '/channels')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_connected(self):
        c = self.client
        qurl = c.make_q_url(self.url + '/connected')

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Execution:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/execution'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: float = None, start: float = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.url, query=[
            ('symbol', symbol),
            ('filter', json_filter),
            ('columns', columns),
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('startTime', start_time),
            ('endTime', end_time),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_trade_history(self, symbol: str, json_filter: str = None, columns: str = None,
                          count: float = None, start: float = None, reverse: bool = False,
                          start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.url + '/tradeHistory', query=[
            ('symbol', symbol),
            ('filter', json_filter),
            ('columns', columns),
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('startTime', start_time),
            ('endTime', end_time),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Funding:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/funding'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: float = None, start: float = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.url, query=[
            ('symbol', symbol),
            ('filter', json_filter),
            ('columns', columns),
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('startTime', start_time),
            ('endTime', end_time),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Instrument:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/instrument'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: float = None, start: float = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.url, query=[
            ('symbol', symbol),
            ('filter', json_filter),
            ('columns', columns),
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('startTime', start_time),
            ('endTime', end_time),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_active(self):
        pass

    def get_active_and_indices(self):
        pass

    def get_active_intervals(self):
        pass

    def get_composite_index(self):
        pass

    def get_indices(self):
        pass


class Insurance:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/insurance'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: float = None, start: float = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.url, query=[
            ('symbol', symbol),
            ('filter', json_filter),
            ('columns', columns),
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('startTime', start_time),
            ('endTime', end_time),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Leaderboard:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/leaderboard'

    def get(self, method='notional'):
        c = self.client
        qurl = c.make_q_url(self.url, query=[
            ('method', method),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def get_name(self):
        c = self.client
        qurl = c.make_q_url(self.url)

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Liquidation:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/liquidation'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: float = None, start: float = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.url, query=[
            ('symbol', symbol),
            ('filter', json_filter),
            ('columns', columns),
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('startTime', start_time),
            ('endTime', end_time),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Notification:
    def __init__(self):
        pass

    def get(self):
        pass


class Order:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/order'

    def get(self, symbol: str, json_filter: str = None, columns: str = None,
            count: float = None, start: float = None, reverse: bool = False,
            start_time=None, end_time=None):
        c = self.client
        qurl = c.make_q_url(self.url, query=[
            ('symbol', symbol),
            ('filter', json_filter),
            ('columns', columns),
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('startTime', start_time),
            ('endTime', end_time),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)

    def put(self):
        pass

    def post(self):
        pass

    def delete(self):
        pass

    def delete_all(self):
        pass

    def put_bulk(self):
        pass

    def post_bulk(self):
        pass

    def post_cancel_all_after(self):
        pass

    def post_close_position(self):
        pass


class OrderBook:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/orderBook'

    def get_l2(self, symbol: str, depth: float= 25.0):
        c = self.client
        qurl = c.make_q_url(self.url + '/L2', query=[
            ('symbol', symbol),
            ('depth', depth),
        ])

        header = c.make_auth_header(qurl)
        c.get(qurl.toString(QUrl.FullyEncoded), header)


class Position:
    def __init__(self):
        pass

    def get(self):
        pass

    def post_isolate(self):
        pass

    def post_leverage(self):
        pass

    def post_risk_limit(self):
        pass

    def post_transfer_margin(self):
        pass


class Quote:
    def __init__(self):
        pass

    def get(self):
        pass

    def get_bucketed(self):
        pass


class Schema:
    def __init__(self):
        pass

    def get(self):
        pass

    def get_websocket_help(self):
        pass


class Settlement:
    def __init__(self):
        pass

    def get(self):
        pass


class Stats:
    def __init__(self):
        pass

    def get(self):
        pass

    def get_history(self):
        pass

    def get_history_usd(self):
        pass


class Trade:
    def __init__(self):
        pass

    def get(self):
        pass

    def get_bucketed(self):
        pass


class User:
    def __init__(self):
        pass

    def get(self):
        pass

    def put(self):
        pass

    def get_affiliate_status(self):
        pass

    def post_cancel_withdrawal(self):
        pass

    def get_check_referral_code(self):
        pass

    def get_commission(self):
        pass

    def post_confirm_email(self):
        pass

    def post_confirm_enable_tfa(self):
        pass

    def post_confirm_withdrawal(self):
        pass

    def get_deposit_address(self):
        pass

    def post_disable_tfa(self):
        pass

    def post_logout(self):
        pass

    def post_logout_all(self):
        pass

    def get_margin(self):
        pass

    def get_min_withdrawal_fee(self):
        pass

    def post_preference(self):
        pass

    def post_request_enable_tfa(self):
        pass

    def post_request_withdrawal(self):
        pass

    def get_wallet(self):
        pass

    def get_wallet_history(self):
        pass

    def get_wallet_summary(self):
        pass


class BitmexHttpClient(HttpClient):

    def __init__(self, test=False, api_key=None, api_secret=None):
        super().__init__()
        self.base_uri = "https://www.bitmex.com/api/v1"
        self.test = test
        self.api_key = api_key
        self.api_secret = api_secret

        # api - endpoints
        self.Announcement = Announcement(self)
        self.ApiKey = ApiKey(self)
        self.Chat = Chat(self)

    def make_q_url(self, endpoint, query=None, data=None):
        if query is None:
            query = []

        qurl = QUrl(endpoint)
        q = QUrlQuery()
        q.setQueryItems(query)
        qurl.setQuery(q)

        if data:
            post_data = QUrlQuery()
            post_data.setQueryItems(data)

            return qurl, post_data
        else:
            return qurl

    def make_auth_header(self, qurl, data=''):
        if data:
            verb = 'POST'
        else:
            verb = 'GET'

        url = qurl.path() + '?' + qurl.query(QUrl.FullyDecoded)
        expires = int(round(time.time()) + 5)

        sign = bitmex.generate_signature(secret, verb, url, expires, data)
        header = {
            'api-expires': str(expires),
            'api-key': key,
            'api-signature': sign
        }
        return header

    def get_base_uri(self):
        url = self.base_uri
        qurl = QUrl(url)

        self.request.setUrl(qurl)
        self.network_manager.get(self.request)
