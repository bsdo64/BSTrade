from PyQt5 import QtCore
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneWheelEvent


class ChartScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)

    def sceneRectChanged(self, rect: QtCore.QRectF):
        pass

    def wheelEvent(self, event: 'QGraphicsSceneWheelEvent'):
        # print('event.pos() : \t\t', event.pos())
        # print('event.scenePos() : \t', event.scenePos()) # mouse point in scene
        # print('self.sceneRect() : \t', self.sceneRect())
        super().wheelEvent(event)
