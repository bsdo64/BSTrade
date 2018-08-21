import numpy as np
from PyQt5.QtGui import QPainter, QPen, QPainterPath, QColor
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem

from BSTrade.Data.Models import ChartModel


class Line(QGraphicsItem):
    def __init__(self, model, view, indi, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.model:ChartModel = model
        self.view = view
        self.indi = indi
        self.data_x_range = self.model.current_x_range()  # 2 <
        self.init_draw = False
        self.init_len = 0

        self.line_path = []

        self.make_path()

    def paint(self,
              painter: QPainter,
              option: QStyleOptionGraphicsItem,
              widget=None):

        r = self.model.current_x_range()
        p = self.model.current_x_pos()

        if self.init_len > 0:

            path_len = len(self.line_path)
            prev = self.model.x_range_prev

            s = (p - self.init_len) // prev + 1 if p > self.init_len else 0
            e = (r - self.init_len) // prev + 2
            e = e - 1 if path_len < e else e  # 1 > 2

            # print("range : [{},{}]".format(s, e))

            if 0 < path_len:

                if e - s < 5:
                    painter.save()
                    pen = QPen()
                    pen.setCosmetic(True)
                    painter.setPen(pen)

                    path = QPainterPath()

                    try:
                        for i in range(s, e):
                            path.addPath(self.line_path[i])
                    except IndexError as err:
                        print(err)

                    # draw plus line
                    pen.setColor(QColor("#496856"))
                    painter.setPen(pen)
                    painter.drawPath(path)

                    painter.restore()

    def make_path(self):
        if len(self.line_path) == 0:
            df = self.model.create_indicator(self.indi)
            if 'len' in df and df['len'] > 0:
                print('draw new initial path')
                self.init_len = df['len']
                self.save_path(df)

                self.init_draw = True

    def save_path(self, df):
        line_df = {}
        for i in df:
            if i != 'len':
                line_df[i] = df[i]

        new_path = QPainterPath()
        new_path.moveTo(line_df['time_axis_scaled'][0],
                        line_df['r_' + self.indi][0])
        for i in np.arange(line_df[self.indi].shape[0]):
            new_path.lineTo(line_df['time_axis_scaled'][i], line_df['r_' + self.indi][i])

        self.line_path.append(new_path)

    def boundingRect(self):
        return self.view.rect