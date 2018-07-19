from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem


class SceneRectItem(QGraphicsItem):
    def __init__(self, parent=None):
        QGraphicsItem.__init__(self, parent)

    def paint(self, painter: QtGui.QPainter,
              option: 'QStyleOptionGraphicsItem',
              widget: QWidget = ...):

        scene = self.scene()
        rect = scene.sceneRect()

        painter.save()
        pen = QPen()
        pen.setCosmetic(True)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.drawRect(rect)
        painter.restore()

    def boundingRect(self):
        return QRectF(0, 0, 100, 100)