from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class http_client:
    def __init__(self):
        self.network_manager = QNetworkAccessManager()

        self.connect_to_slot()

    def get(self, url: str):
        self.network_manager.get(QNetworkRequest(QUrl(url)))

    def connect_to_slot(self):
        self.network_manager.finished.connect(self.slot_reply_finished)

    def slot_reply_finished(self, data: QNetworkReply):
        pass