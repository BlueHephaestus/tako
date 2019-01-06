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

        #Create GraphicsScene and GraphicsView of it
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.viewport().installEventFilter(self)

        #Add view to the layout
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.view)

        #Load and add the current pixmap
        self.pixmap = QPixmap('yang.png')
        self.scene.addPixmap(self.pixmap)

        #Modifiable attributes to determine what's being drawn
        #self.selection = QGraphicsRectItem(QRectF(0,0,0,0))
        #self.scene.addItem(self.selection)

        self.color = SELECTION_RECT_FILL_COLOR #For now it's just one color

        #Current tool being used to make selections in our image
        #self.tool = RECT_SELECT
        self.tool = LASSO_SELECT

        #Drawing Attributes for the Canvas
        self.painter = QPainter()

        #Show our widget
        self.show()

    def render_selection(self, selection, polygon=False):
        """
        Updates the current displayed selection shape
            on the canvas to be the given selection.
        """

        #Always remove anything other than our pixmap when re-rendering
        while len(self.scene.items()) > 1:
            self.scene.removeItem(self.scene.items()[0])

        #Add new selection 
        if polygon:
            #They have a special method for this we have to use to add them
            self.scene.addPolygon(selection)

        else:
            self.scene.addItem(selection)



    def eventFilter(self, source, event):
        if source is self.view.viewport():

            #Selection events are dependent on the current selection tool

            #Users select a rectangle portion
            if self.tool == RECT_SELECT:

                if (event.type() == QEvent.MouseButtonPress):

                    #Initialize selection rectangle with this
                    self.select_start = QPoint(event.x(), event.y())
                    self.select_rect = QRect(QPoint(event.x(), event.y()), QPoint(event.x(), event.y()))

                    #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
                    #   so that we lock on to areas in these step sizes to allow easier rectangle selection.
                    self.outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)

                    #Render it
                    self.render_selection(self.outline_rect)

                elif (event.type() == QEvent.MouseMove):

                    #Get new rectangle from our initial select_rect point to this point
                    self.select_rect = get_rectangle_from_points(self.select_start, QPoint(event.x(), event.y()))

                    #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
                    #   so that we lock on to areas in these step sizes to allow easier rectangle selection.
                    self.outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)

                    #Render it
                    self.render_selection(self.outline_rect)

                elif (event.type() == QEvent.MouseButtonRelease):
                    #Get new rectangle from our initial select_rect point to this point
                    self.select_rect = get_rectangle_from_points(self.select_start, QPoint(event.x(), event.y()))

                    #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
                    #   so that we lock on to areas in these step sizes to allow easier rectangle selection.
                    outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)

                    #Render it
                    self.render_selection(self.outline_rect)

            #Users select an arbitrary region of the image which is then approximated by win_h x win_w windows
            elif self.tool == LASSO_SELECT:
                if (event.type() == QEvent.MouseButtonPress):

                    #Initialize selection polygon with this
                    self.select_start = QPoint(event.x(), event.y())
                    self.select_polygon = QPolygonF([self.select_start])

                    #Render it
                    self.render_selection(self.select_polygon, polygon=True)

                elif (event.type() == QEvent.MouseMove):

                    #Append this new point to the polygon selection
                    self.select_polygon.append(QPoint(event.x(), event.y()))

                    #Render it
                    self.render_selection(self.select_polygon, polygon=True)

                elif (event.type() == QEvent.MouseButtonRelease):
                    """
                    Our polygon is now complete, we now approximate 
                        the area encompassed by it with rectangles of 
                        shape win_h x win_w and render these in its place.
                    """
                    self.select_rect_group = approximate_polygon(self.select_polygon, self.h, self.w, self.win_h, self.win_w)

                    #Render the approximation
                    self.render_selection(self.select_rect_group)

                    
                    

        return False

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


GUI(None, 10, 10)


