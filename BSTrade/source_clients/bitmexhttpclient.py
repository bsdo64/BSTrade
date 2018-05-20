import pprint
import time
import urllib.parse
from PyQt5.QtCore import QUrl, pyqtSignal, QObject, Qt, QUrlQuery
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from .httpclient import HttpClient
from .auth import bitmex

secret = '0LC7T3jzS9M9Dk0Ce1sbUmKmg5rZ_sd352gYeLtCUtu6apzb'
key = 'hImUSySfSitmsaSrYv4IKecu'


class Announcement:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/announcement'

    def get(self, columns=None):
        c = self.client
        qurl = QUrl(self.url)
        q = QUrlQuery()
        q.setQueryItems([
            ('columns', columns)
        ])
        qurl.setQuery(q)

        c.request.setUrl(qurl)
        c.network_manager.get(c.request)

    def get_urgent(self):
        c = self.client
        url = self.url + '/urgent'
        qurl = QUrl(url)

        c.request.setUrl(qurl)
        c.network_manager.get(c.request)


class ApiKey:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/apiKey'

    def get(self, reverse=False):
        c = self.client
        qurl = QUrl(self.url)
        q = QUrlQuery()
        q.setQueryItems([
            ('reverse', str(reverse))
        ])
        qurl.setQuery(q)

        verb = 'GET'
        url = qurl.path() + '?' + q.query()
        expires = int(round(time.time()) + 5)
        data = ''

        sign = bitmex.generate_signature(secret, verb, url, expires, data)

        c.set_header({
            'api-expires': str(expires),
            'api-key': key,
            'api-signature': sign
        })
        c.request.setUrl(qurl)
        c.network_manager.get(c.request)


class Chat:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/chat'

    def get(self, count: float=None, start: float=None, reverse: bool=True, channelID: float=None):
        c = self.client
        qurl = QUrl(self.url)
        q = QUrlQuery()
        q.setQueryItems([
            ('count', count),
            ('start', start),
            ('reverse', str(reverse)),
            ('channelID', channelID)
        ])
        qurl.setQuery(q)

        verb = 'GET'
        url = qurl.path() + '?' + q.query()
        expires = int(round(time.time()) + 5)
        data = ''

        sign = bitmex.generate_signature(secret, verb, url, expires, data)

        c.set_header({
            'api-expires': str(expires),
            'api-key': key,
            'api-signature': sign
        })
        c.request.setUrl(qurl)
        c.network_manager.get(c.request)

    def post(self, message, channelID: float=1.0):
        c = self.client
        qurl = QUrl(self.url)
        query = QUrlQuery()
        query.setQueryItems([
            ('message', message),
            ('channelID', str(channelID))
        ])

        verb = 'POST'
        url = qurl.path()
        expires = int(round(time.time()) + 5)
        data = query.query().encode()

        sign = bitmex.generate_signature(secret, verb, url, expires, data)

        c.set_header({
            'content-type': 'application/x-www-form-urlencoded',
            'api-expires': str(expires),
            'api-key': key,
            'api-signature': sign
        })

        c.request.setUrl(qurl)
        c.network_manager.post(c.request, data)


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

    def get_base_uri(self):
        url = self.base_uri
        qurl = QUrl(url)

        self.request.setUrl(qurl)
        self.network_manager.get(self.request)
