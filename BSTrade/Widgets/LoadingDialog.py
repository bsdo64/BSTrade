from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QDesktopWidget


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.text = QLabel("Loading...")
        hbox = QHBoxLayout()
        hbox.addWidget(self.text)
        self.setLayout(hbox)

        self.setModal(True)
        self.setWindowModality(Qt.NonModal)

        self.setWindowFlags(self.windowFlags() | Qt.Tool)

        r = QDesktopWidget().availableGeometry()
        self.move(
            (r.width() - r.x()) / 2,
            (r.height() - r.y()) / 2
        )
