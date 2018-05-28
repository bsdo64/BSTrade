from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QDockWidget

from source_clients.bitmexwsclient import BitmexWsClient


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ws = BitmexWsClient(test=True)

        self.setup_ui()

    def setup_ui(self):
        self.resize(1024, 768)
        self.setObjectName("MainWindow")
        self.setWindowTitle("BSTrade")

        center = QTextEdit()
        center.setMinimumSize(200, 480)
        self.setCentralWidget(center)

        self.setupDockWidgets()

    def setupDockWidgets(self):
        dock1 = QDockWidget()
        dock1.setMinimumWidth(200)
        dock1.setMinimumHeight(100)
        dock1.setWindowTitle("Right dock")
        self.addDockWidget(Qt.RightDockWidgetArea, dock1)

        dock2 = QDockWidget()
        dock2.setMinimumWidth(200)
        dock2.setMinimumHeight(100)
        dock2.setWindowTitle("Left dock")
        self.addDockWidget(Qt.LeftDockWidgetArea, dock2)
