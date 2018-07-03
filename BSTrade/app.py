from PyQt5.QtCore import QObject
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication
import sys
from widgets import MainWindow

import resources


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')

        self.app.setStyleSheet("""
                    QTextEdit {
                        background: #191d26;
                        color: #D8D8D8;
                    }
                """)

        self.window = MainWindow()
        self.window.show()

        self.start()

    def start(self):
        sys.exit(self.app.exec_())

