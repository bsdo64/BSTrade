from PyQt5.QtWidgets import QMainWindow, QTextEdit


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setup_ui()

    def setup_ui(self):
        self.setCentralWidget(QTextEdit())
