from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene


class ChartAxisView(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setFixedWidth(56)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # self.setFrameStyle(QFrame.NoFrame)
        # self.setStyleSheet("""
        #     QGraphicsView { border: 1px solid black }
        # """)

        scene = QGraphicsScene()
        scene.addSimpleText('nice!!')
        self.text = scene.addText('hello')

        scene.addText('world')
        self.setScene(scene)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        trans = self.text.transform()
        trans.translate(11, 11)

        print()
        print(trans.m11(), trans.m12(), trans.m13())
        print(trans.m21(), trans.m22(), trans.m23())
        print(trans.m31(), trans.m22(), trans.m33())
        print()
        super().mouseMoveEvent(event)
