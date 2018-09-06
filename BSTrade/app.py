import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from BSTrade.Process import Coins
from BSTrade.Widgets.Main import Main
import multiprocessing as mp


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = Main()

        self.setup_ui()

    def setup_ui(self):
        self.app.setStyle('Fusion')
        self.app.setStyleSheet("""
            QPlainTextEdit {
                background: #191d26;
                color: #D8D8D8;
            }
        """)

        self.window.show()

        p = mp.Process(target=Coins.request, args=())
        p.start()

        # p.join()

    def start(self):
        sys.exit(self.app.exec_())
