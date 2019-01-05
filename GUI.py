import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from config import *
from gui_base import *


class GUI():

    def __init__(self, dataset, win_h, win_w):
        app = QApplication([])
        screen = QDesktopWidget().screenGeometry()
        screen_h, screen_w = screen.height(), screen.width()

        toolbar = Toolbar(dataset, screen_h, screen_w, win_h, win_w)
        canvas = Canvas(dataset, screen_h, screen_w, win_h, win_w)
        app.exec_()


class Canvas(QWidget):

    def __init__(self, dataset, screen_h, screen_w, win_h, win_w):
        super(Canvas, self).__init__()
        self.dataset = dataset
        self.win_h = win_h
        self.win_w = win_w

        #Compute size of our canvas relative to screen dimensions
        self.h = CANVAS_SCREEN_HEIGHT_PERCENTAGE*screen_h
        self.w = CANVAS_SCREEN_WIDTH_PERCENTAGE*screen_w
        self.y = CANVAS_SCREEN_Y_HEIGHT_PERCENTAGE*screen_h

        #Width of toolbar + padding we gave our canvas on the y-axis
        self.x = TOOLBAR_SCREEN_WIDTH_PERCENTAGE*screen_w + \
                 TOOLBAR_SCREEN_Y_HEIGHT_PERCENTAGE*screen_h + \
                 CANVAS_SCREEN_Y_HEIGHT_PERCENTAGE*screen_h 

        self.setWindowTitle("| Canvas |")
        self.setGeometry(self.x,self.y,self.w,self.h)

        #Load Image
        self.pixmap = QPixmap('yang.png')
        #self.pixmap.fill(QColor("transparent"))
        #Create Label, add Image to Label
        """
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)

        #Create ScrollArea, add Label to ScrollArea
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.label)
        #scroll.setWidget(self.overlay)

        """
        #Create Layout, add ScrollArea to Layout
        self.layout = QVBoxLayout(self)
        #self.layout.addWidget(self.scroll)

        """
        self.canvas = QWidget(parent=self)
        self.canvas.move(0,0)
        self.canvas.resize(self.w, self.h)
        #self.canvas.setWindowFlags(Qt.FramelessWindowHint)
        #self.canvas.setAttribute(Qt.WA_TranslucentBackground)
        self.layout.addWidget(self.canvas)
        """

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.layout.addWidget(self.view)

        self.scene.addPixmap(self.pixmap)

        #Create Overlay
        #self.overlay = Overlay(self, self.dataset, self.height(), self.width(), self.win_h, self.win_w)

        #Modifiable attributes to determine what's being drawn
        self.rects = QGraphicsItemGroup()
        self.rect = QRect(0,0,0,0)

        #For now it's just one color
        self.color = SELECTION_RECT_FILL_COLOR

        #Drawing Attributes for the Canvas
        self.painter = QPainter()

        #Show our widget
        self.show()

        """
        def paintEvent(self, event):
        print(event.type())
        self.scene.clear()
        self.scene.addRect(QRectF(QRect(400,400,1000,1000)), brush=self.color)
        print("asdf")
        """
        """
        #Paint the given active shape
        self.painter.begin(self.canvas)

        self.painter.fillRect(QRect(0,0,500,500), self.color)

        self.painter.setPen(self.color)
        self.painter.setBrush(self.color)
        self.painter.drawRect(self.rect)
        self.painter.fillRect(self.rect, self.color)
        #self.label.setPixmap(self.pixmap)

        self.painter.end()
        """

    def mousePressEvent(self, event):

        #Initialize selection rectangle with this
        self.select_start = QPoint(event.x(), event.y())
        self.select_rect = QRect(QPoint(event.x(), event.y()), QPoint(event.x(), event.y()))

        #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
        #   so that we lock on to areas in these step sizes to allow easier rectangle selection.

        #Get a rectangle outline with this rect/point as both top-left and bot-right of the rectangle and draw it
        outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)
        
        self.rect = outline_rect
        self.scene.addRect(QRectF(QRect(400,400,1000,1000)), brush=self.color)

        #self.update()

    def mouseMoveEvent(self, event):
        #Update Selection Rectangle

        #Get new rectangle from our initial select_rect point to this point
        self.select_rect = get_rectangle_from_points(self.select_start, QPoint(event.x(), event.y()))

        #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
        #   so that we lock on to areas in these step sizes to allow easier rectangle selection.
        outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)

        self.rect = outline_rect
        self.update()

        """
        #Delete old selection rectangle and draw new one with this new rectangle outline
        self.canvas.delete("selection")
        self.canvas.create_rectangle(outline_rect_x1, outline_rect_y1, outline_rect_x2, outline_rect_y2, fill='', outline="darkRed", width=2, tags="selection")
        """

    def mouseReleaseEvent(self, event):
        #Get new rectangle from our initial select_rect point to this point
        self.select_rect = get_rectangle_from_points(self.select_start, QPoint(event.x(), event.y()))

        #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
        #   so that we lock on to areas in these step sizes to allow easier rectangle selection.
        outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)

        self.rect = outline_rect
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
            sys.exit()


class Overlay(QGraphicsView):
    def __init__(self, parent, dataset, h, w, win_h, win_w):
        super(Overlay, self).__init__(parent)
        self.parent = parent
        self.dataset = dataset
        self.h = h
        self.w = w
        self.win_h = win_h
        self.win_w = win_w

        #Initialize as Translucent Background
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        #Initialize position and size
        self.move(0,0)
        self.resize(w, h)

        #Show this overlay now that we're ready
        self.show()

        #Drawing Attributes for the Canvas
        self.painter = QPainter()

        #Modifiable attributes to determine what's being drawn
        self.rect = QRect(0,0,0,0)

        #For now it's just one color
        self.color = SELECTION_RECT_FILL_COLOR



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
            sys.exit()


class Toolbar(QWidget):
    def __init__(self, dataset, screen_h, screen_w, win_h, win_w):
        super(Toolbar, self).__init__()
        self.dataset = dataset

        #Compute size of our toolbar relative to screen dimensions
        self.h = TOOLBAR_SCREEN_HEIGHT_PERCENTAGE*screen_h
        self.w = TOOLBAR_SCREEN_WIDTH_PERCENTAGE*screen_w
        self.y = TOOLBAR_SCREEN_Y_HEIGHT_PERCENTAGE*screen_h 
        self.x = self.y#Same padding as y

        self.setWindowTitle("| Toolbar |")
        self.setGeometry(self.x,self.y,self.w,self.h)

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
            sys.exit()


GUI(-1, 10, 10)


