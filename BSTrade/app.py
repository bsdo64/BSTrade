import sys
from typing import List

from PyQt5.QtWidgets import QApplication

from BSTrade.Process import Coins
from BSTrade.Widgets.Main import Main
import multiprocessing as mp


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.db = None
        self.window = Main(self.db)
        self.process: List[mp.Process] = []

        self.add_sub_process()
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

    def add_sub_process(self):
        self.process.append(mp.Process(target=Coins.request, args=()))

        self.start_sub_process()

    def start_sub_process(self):
        for p in self.process:
            p.start()

        # p.join()

    def terminate_sub_process(self):
        for p in self.process:
            p.terminate()

    def start(self):
        self.app.exec_()
        self.terminate_sub_process()
