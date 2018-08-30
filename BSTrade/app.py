import sys

from PyQt5.QtWidgets import QApplication
from BSTrade.Widgets.Main import Main


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

    def start(self):
        sys.exit(self.app.exec_())
