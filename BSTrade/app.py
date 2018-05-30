from PyQt5.QtWidgets import QApplication
import sys
from forms import MainWindow
from source_clients.bitmexwsclient import BitmexWsClient

if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyleSheet("""
            QLabel {
                background: black;
                color: white;
            }
        """)

    window = MainWindow()
    window.show()

    app.exec()
