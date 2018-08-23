import typing
import numba as nb
import numpy as np

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QPainterPath, QColor, QKeyEvent
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem, \
    QGraphicsSceneWheelEvent

from BSTrade.Data.Models import CandleModel
from BSTrade.util.fn import attach_timer
from BSTrade.util.thread import Thread


@nb.jit(nogil=True, cache=True, fastmath=True)
def draw_path(data, p_list: list):
    new_path = QPainterPath()
    for i in np.arange(data['close'].shape[0]):
        new_path.moveTo(data['time_axis_scaled'][i], data['r_high'][i])
        new_path.lineTo(data['time_axis_scaled'][i], data['r_low'][i])

    p_list.append(new_path)


@nb.jit(nogil=True, cache=True, fastmath=True)
def draw_rect(data, p_list: list):
    new_path = QPainterPath()
    new_path.setFillRule(Qt.WindingFill)
    for i in np.arange(data['close'].shape[0]):
        new_path.addRect(
            data['time_axis_scaled'][i] - 15,  # x
            data['r_open'][i],  # y
            30,  # width
            data['open'][i] - data['close'][i],  # height
        )

    p_list.append(new_path)


class CandleStick(QGraphicsItem):
    def __init__(self, model: CandleModel, view, parent=None):
        QGraphicsItem.__init__(self, parent)
        self.model = model
        self.view = view
        self.data_x_range = self.model.current_x_range()  # 2 <
        self.init_draw = False
        self.init_len = 0

        self.plus_line_path = []
        self.minus_line_path = []
        self.plus_bar_path = []
        self.minus_bar_path = []

        self.thread = Thread()
        self.make_path()

        self.model.sig_add_point.connect(self.slt_add_point)
        self.model.sig_update_point.connect(self.slt_update_point)

    def paint(self,
              painter: QtGui.QPainter,
              option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...):

        # Set level of detail
        # print(option.levelOfDetailFromTransform(painter.worldTransform()))

        r = self.model.current_x_range()
        p = self.model.current_x_pos()

        if self.init_len > 0:

            path_len = len(self.plus_bar_path)
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
                    path2 = QPainterPath()
                    path3 = QPainterPath()
                    path4 = QPainterPath()

                    try:
                        for i in range(s, e):
                            path.addPath(self.plus_line_path[i])
                            path2.addPath(self.minus_line_path[i])
                            path3.addPath(self.plus_bar_path[i])
                            path4.addPath(self.minus_bar_path[i])
                    except IndexError as err:
                        print(err)

                    # draw plus line
                    pen.setColor(QColor("#496856"))
                    painter.setPen(pen)
                    painter.drawPath(path)

                    # draw minus line
                    pen.setColor(QColor("#6F3541"))
                    painter.setPen(pen)
                    painter.drawPath(path2)

                    # draw plus bar
                    painter.fillPath(path3, QColor('#7BB888'))

                    # draw minus bar
                    painter.fillPath(path4, QColor('#CC4E5C'))

                    painter.restore()
                else:
                    painter.save()
                    pen = QPen()
                    pen.setCosmetic(True)
                    pen.setColor(QColor(Qt.white))
                    painter.setPen(pen)

                    path = QPainterPath()
                    path2 = QPainterPath()

                    try:
                        for i in range(s, e):
                            path.addPath(self.plus_line_path[i])
                            path2.addPath(self.minus_line_path[i])
                    except IndexError as err:
                        print(err)

                    painter.drawPath(path)
                    painter.drawPath(path2)
                    painter.restore()

    def wheelEvent(self, event: 'QGraphicsSceneWheelEvent'):
        super().wheelEvent(event)
        self.make_path()

    def make_path(self):
        if len(self.plus_bar_path) == 0:
            df = self.model.c_data
            if 'len' in df:
                print('draw new initial path')
                self.init_len = df['len']
                self.save_path(df)

                self.init_draw = True

        else:
            if self.model.current_x_range() > self.data_x_range:  # 3 > 2
                print('draw next path')

                last = self.data_x_range
                nxt = self.model.x_range_prev
                self.data_x_range += nxt  # 2 += 500

                next_df = self.model.prev_data(d_s=last, d_len=nxt)

                self.save_path(next_df)

    def save_path(self, df):

        plus_cond = df['close'] > df['open']
        plus_df = {}
        for i in df:
            if i != 'len':
                plus_df[i] = df[i][plus_cond]

        minus_df = {}
        for i in df:
            if i != 'len':
                minus_df[i] = df[i][np.invert(plus_cond)]

        self.create_in_thread(draw_path,
                              plus_df,
                              self.plus_line_path)
        self.create_in_thread(draw_path,
                              minus_df,
                              self.minus_line_path)

        self.create_in_thread(draw_rect,
                              plus_df,
                              self.plus_bar_path)
        self.create_in_thread(draw_rect,
                              minus_df,
                              self.minus_bar_path)

    def create_in_thread(self, fn, *args):
        w = self.thread.make_worker(fn, *args)
        w.sig.finished.connect(self.update)
        self.thread.start(w)

    def slt_update_point(self, data):
        """
        Bar :
            p1(p5)         p4
              +-----------+
              |           |
              |           |
              +-----------+
            p2             p3

            p1 - p4 = close
            p2 - p3 = open

        Line :
            s1
             +
             |
             |
             +
            s2

            s1 = high
            s2 = low
        """
        if not len(self.plus_bar_path) and not len(self.minus_bar_path):
            return

        if data['plus_cond']:
            bar = self.plus_bar_path[0]
            bar2 = self.minus_bar_path[0]
            line = self.plus_line_path[0]
            line_to = data['r_high']
            up = data['r_close']
            down = data['r_open']

        else:
            bar = self.minus_bar_path[0]
            bar2 = self.plus_bar_path[0]
            line = self.minus_line_path[0]
            line_to = data['r_low']
            up = data['r_open']
            down = data['r_close']

        bar_count = bar.elementCount()
        line_count = line.elementCount()

        self.hide_marker(bar2, data)

        bar.setElementPositionAt(bar_count - 1,
                                 data['time_axis_scaled'] - 15, up)
        bar.setElementPositionAt(bar_count - 4,
                                 data['time_axis_scaled'] + 15, up)
        bar.setElementPositionAt(bar_count - 2,
                                 data['time_axis_scaled'] - 15, down)
        bar.setElementPositionAt(bar_count - 3,
                                 data['time_axis_scaled'] + 15, down)
        bar.setElementPositionAt(bar_count - 5,
                                 data['time_axis_scaled'] - 15, up)

        s1 = line.elementAt(line_count - 1)
        if s1.type == QPainterPath.MoveToElement:
            line.lineTo(data['time_axis_scaled'], line_to)
        elif s1.type == QPainterPath.LineToElement:
            line.setElementPositionAt(line_count - 1,
                                      data['time_axis_scaled'],
                                      data['r_high'])
            line.setElementPositionAt(line_count - 2,
                                      data['time_axis_scaled'],
                                      data['r_low'])

        self.update()

    def hide_marker(self, bar2, data):
        bar2_count = bar2.elementCount()

        """
        path can't subtract, so set height to 0
         
        Bar : 
            m1(m5)         m4
              +-----------+
              |           |
              |           |
              +-----------+
            m2             m3

            m1 - m4 = open
            m2 - m3 = close
        """

        bar2.setElementPositionAt(bar2_count - 1,
                                  data['time_axis_scaled'] - 15,
                                  data['r_open'])
        bar2.setElementPositionAt(bar2_count - 4,
                                  data['time_axis_scaled'] + 15,
                                  data['r_open'])
        bar2.setElementPositionAt(bar2_count - 2,
                                  data['time_axis_scaled'] - 15,
                                  data['r_open'])
        bar2.setElementPositionAt(bar2_count - 3,
                                  data['time_axis_scaled'] + 15,
                                  data['r_open'])
        bar2.setElementPositionAt(bar2_count - 5,
                                  data['time_axis_scaled'] - 15,
                                  data['r_open'])

    def slt_add_point(self, data):
        if not len(self.plus_line_path):
            return

        self.add_new_marker(self.plus_bar_path[0],
                            self.plus_line_path[0],
                            data)

        self.add_new_marker(self.minus_bar_path[0],
                            self.minus_line_path[0],
                            data)

        self.update()

    def add_new_marker(self, bar, line, data):
        bar.addRect(
            data['time_axis_scaled'] - 15,  # x
            data['r_open'],  # y
            30,  # width
            0,  # height
        )

        line.moveTo(data['time_axis_scaled'], data['r_high'])

    def boundingRect(self):
        return self.view.rect


attach_timer(CandleStick, limit=10)
