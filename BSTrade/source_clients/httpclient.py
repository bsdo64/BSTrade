import json

from PyQt5.QtCore import QUrl, pyqtSignal, QObject, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class HttpClient(QObject):
    sig_ended = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.request = QNetworkRequest()
        self.request.setRawHeader(b"accept", b"application/json")
        self.request.setRawHeader(b'user-agent',
                                  b'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, '
                                  b'like Gecko) Chrome/66.0.3359.139 Safari/537.36')

        self._ended = True
        self._reply = None
        self._text = b''
        self._string = ''
        self._status_code = None
        self._json = None
        self._headers = None

        self._connect_to_slot()

    def reply(self):
        return self._reply

    def json(self):
        return self._json

    def status(self):
        return self._status_code

    def text(self):
        return self._string

    def headers(self):
        return self._headers

    def content_type(self):
        content_type = self._headers['content-type']
        if 'text/html' in content_type:
            return 'html'
        elif 'test/plain' in content_type:
            return 'text'
        elif 'application/json' in content_type:
            return 'json'

    def _save_header(self, raw_headers):
        h = {}
        for t in raw_headers:
            h.update({str.lower(bytes(t[0]).decode()): bytes(t[1]).decode()})

        self._headers = h

    def set_header(self, header):
        """
        header must consist of strings of dict

        :param header: dict
        """
        if isinstance(header, dict):
            for k in header:
                self.request.setRawHeader(k.encode(), header[k].encode())

    def get(self, url: str, header=None):
        """
        Get http request

        :param url:
        :param header:
        """
        self.request.setUrl(QUrl(url))
        self.set_header(header)
        self.network_manager.get(self.request)

    def post(self, url: str, header: list(tuple())=None, data: bytes=None):
        self.request.setUrl(QUrl(url))
        self.set_header(header)
        self.network_manager.post(self.request, data)

    def put(self, url: str, header: list(tuple())=None, data: bytes=None):
        self.request.setUrl(QUrl(url))
        self.set_header(header)
        self.network_manager.put(self.request, data)

    def delete(self, url: str, header: list(tuple())=None):
        self.request.setUrl(QUrl(url))
        self.set_header(header)
        self.network_manager.deleteResource(self.request)

    def _connect_to_slot(self):
        self.network_manager.finished.connect(self.slot_reply_finished)

    def slot_reply_finished(self, data: QNetworkReply):

        self._reply = data
        self._text = data.readAll()
        self._string = bytes(self._text).decode()
        self._status_code = data.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        self._save_header(data.rawHeaderPairs())

        if self.content_type() == 'json':
            if len(self._string):
                self._json = json.loads(self._string)
        else:
            self._json = None

        if self._status_code >= 400:
            print(self._string)

        self.sig_ended.emit(True)
        data.deleteLater()
