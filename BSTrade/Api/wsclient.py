import ujson as json

from PyQt5.QtCore import QObject, QUrl, pyqtSignal
from PyQt5.QtWebSockets import QWebSocket

from BSTrade.util.fn import attach_timer


class WsClient(QObject):
    sig_message = pyqtSignal(object)
    sig_connected = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.websocket = QWebSocket()

        self._connected = False
        self._auth = False
        self._data = None

        self.websocket.connected.connect(self.slot_connected)
        self.websocket.disconnected.connect(self.slot_disconnected)
        self.websocket.textMessageReceived.connect(self.slot_message_received)
        self.websocket.error.connect(self.slot_error)

    def is_connected(self):
        return self._connected

    def set_data(self, data):
        self._data = data

    def data(self):
        return self._data

    def json(self):
        try:
            j = json.loads(self.data())
        except ValueError as e:
            j = {}

        return j

    def send(self, data):
        if isinstance(data, dict):
            d = json.dumps(data)
        else:
            d = str(data)

        self.websocket.sendTextMessage(d)

    def open(self, url):
        self.websocket.open(QUrl(url))

    def close(self):
        self.websocket.close()

    def slot_connected(self):
        self._connected = True
        self.sig_connected.emit()

    def slot_disconnected(self):
        self._connected = False

    def slot_message_received(self, message: str):
        self.set_data(message)
        self.sig_message.emit(self)

    def slot_error(self, error_code):
        print("error code: {}".format(error_code))
        print(self.websocket.errorString())


attach_timer(WsClient)