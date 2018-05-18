from PyQt5.QtCore import QUrl, pyqtSignal, QObject, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class HttpClient(QObject):
    sig_reply = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.request = QNetworkRequest()
        self.request.setRawHeader(b"accept", b"application/json")
        self.request.setRawHeader(b'user-agent',
                                  b'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, '
                                  b'like Gecko) Chrome/66.0.3359.139 Safari/537.36')
        self._connect_to_slot()

    def set_header(self, header):
        """
        header must consist of strings of dict

        :param header: dict
        :return: None
        """
        if isinstance(header, dict):
            for k in header:
                self.request.setRawHeader(k.encode(), header[k].encode())

    def get(self, url: str, header=None):
        """
        Get http request

        :param url:
        :param header:
        :return:
        """
        self.request.setUrl(QUrl(url))
        self.set_header(header)
        self.network_manager.get(self.request)

    def _connect_to_slot(self):
        self.network_manager.finished.connect(self.slot_reply_finished)

    def slot_reply_finished(self, data: QNetworkReply):
        print(data.attribute(QNetworkRequest.HttpStatusCodeAttribute))
        s = data.readAll()
        d = bytes(s).decode()
        self.sig_reply.emit(d)

