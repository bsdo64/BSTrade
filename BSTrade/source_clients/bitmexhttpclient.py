from PyQt5.QtCore import QUrl, pyqtSignal, QObject, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from .httpclient import HttpClient
from .auth import bitmex


class Announcement:
    def __init__(self, client):
        self.client = client
        self.url = self.client.base_uri + '/announcement'

    def get(self, columns=None):
        c = self.client
        qurl = QUrl(self.url)
        if columns:
            qurl.setQuery('columns={}'.format(columns))
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
        qurl.setQuery('reverse={}'.format(str(reverse).lower()))
        c.request.setUrl(qurl)
        c.network_manager.get(c.request)

    def get_urgent(self):
        c = self.client
        url = self.url + '/urgent'
        qurl = QUrl(url)

        c.request.setUrl(qurl)
        c.network_manager.get(c.request)


class BitmexHttpClient(HttpClient):

    def __init__(self, test=False, api_key=None, api_secret=None):
        super().__init__()
        self.base_uri = "https://www.bitmex.com/api/v1"
        self.test = test
        self.api_key = api_key
        self.api_secret = api_secret
        self.Announcement = Announcement(self)
        self.ApiKey = ApiKey(self)

    def get_base_uri(self):
        url = self.base_uri
        qurl = QUrl(url)

        self.request.setUrl(qurl)
        self.network_manager.get(self.request)
