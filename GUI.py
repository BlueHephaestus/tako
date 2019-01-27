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

        self.h = CANVAS_HEIGHT
        self.w = CANVAS_WIDTH
        self.y = CANVAS_Y
        self.x = CANVAS_X

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
        self.img_h, self.img_w = self.pixmap.height(), self.pixmap.width()
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

    def relative_coordinates(view, event):
        """
        Gets the relative coordinates of the x and y 
            position of this event, relative to the
            given graphicsview scroll position(s).
        """
        x = event.x()
        y = event.y()
        scroll_x = view.horizontalScrollBar().value()
        scroll_y = view.verticalScrollBar().value()

        return (scroll_x + x, scroll_y + y)




    def eventFilter(self, source, event):
        if source is self.view.viewport():

            #Selection events are dependent on the current selection tool

            #Users select a rectangle portion
            if self.tool == RECT_SELECT:

                if (event.type() == QEvent.MouseButtonPress):

                    #Initialize selection rectangle with this
                    x,y = relative_coordinates(self.view, event.x(), event.y())
                    self.select_start = QPoint(x,y)
                    self.select_rect = QRect(QPoint(x,y), QPoint(x,y))

                    #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
                    #   so that we lock on to areas in these step sizes to allow easier rectangle selection.
                    self.outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)

                    #Render it
                    self.render_selection(self.outline_rect)

                elif (event.type() == QEvent.MouseMove):

                    #Get new rectangle from our initial select_rect point to this point
                    x,y = relative_coordinates(self.view, event.x(), event.y())
                    self.select_rect = get_rectangle_from_points(self.select_start, QPoint(x,y))

                    #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
                    #   so that we lock on to areas in these step sizes to allow easier rectangle selection.
                    self.outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)

                    #Render it
                    self.render_selection(self.outline_rect)

                elif (event.type() == QEvent.MouseButtonRelease):
                    #Get new rectangle from our initial select_rect point to this point
                    x,y = relative_coordinates(self.view, event.x(), event.y())
                    self.select_rect = get_rectangle_from_points(self.select_start, QPoint(x,y))

                    #Our rectangle selections can only be made up of small rectangles of size win_h x win_w
                    #   so that we lock on to areas in these step sizes to allow easier rectangle selection.
                    outline_rect = get_outline_rect(self.select_rect, self.win_h, self.win_w)

                    #Render it
                    self.render_selection(self.outline_rect)

            #Users select an arbitrary region of the image which is then approximated by win_h x win_w windows
            elif self.tool == LASSO_SELECT:
                if (event.type() == QEvent.MouseButtonPress):

                    #Initialize selection polygon with this
                    x,y = relative_coordinates(self.view, event.x(), event.y())
                    self.select_start = QPoint(x,y)
                    self.select_polygon = QPolygonF([self.select_start])

                    #Render it
                    self.render_selection(self.select_polygon, polygon=True)

                elif (event.type() == QEvent.MouseMove):

                    #Append this new point to the polygon selection
                    x,y = relative_coordinates(self.view, event.x(), event.y())
                    self.select_polygon.append(QPoint(x,y))

                    #Render it
                    self.render_selection(self.select_polygon, polygon=True)

                elif (event.type() == QEvent.MouseButtonRelease):
                    """
                    Our polygon is now complete, we now approximate 
                        the area encompassed by it with rectangles of 
                        shape win_h x win_w and render these in its place.
                    """
                    self.select_rect_group = approximate_polygon(self.select_polygon, self.img_h, self.img_w, self.win_h, self.win_w)

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
        ####TEMPORARY
        self.labels = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]

        self.h = TOOLBAR_HEIGHT
        self.w = TOOLBAR_WIDTH
        self.y = TOOLBAR_Y
        self.x = TOOLBAR_X

        self.setWindowTitle("| Toolbar |")
        self.setGeometry(self.x,self.y,self.w,self.h)

        #Add toolbar button items

        #Pointers for easy positioning of elements
        item_x, item_y = TOOLBAR_PADDING, TOOLBAR_PADDING

        #Rectangle Selection Tool
        rect_select = ToolButton(self, RECT_SELECT_ICON_FNAME, item_x, item_y)
        item_x += rect_select.w + TOOLBAR_PADDING

        #Lasso Selection Tool
        lasso_select = ToolButton(self, LASSO_SELECT_ICON_FNAME, item_x, item_y)
        item_x += lasso_select.w + TOOLBAR_PADDING

        #Pencil Tool
        pencil = ToolButton(self, PENCIL_ICON_FNAME, item_x, item_y)
        item_x += pencil.w + TOOLBAR_PADDING

        #Eraser Tool
        eraser = ToolButton(self, ERASER_ICON_FNAME, item_x, item_y)
        item_x += eraser.w + TOOLBAR_PADDING

        #Reset for next row
        item_x = TOOLBAR_PADDING
        item_y += rect_select.h + TOOLBAR_PADDING

        #Add initial toolbar slider items
        pencil_size = ToolSlider(self, "Pencil Size", item_x, item_y)
        item_y += pencil_size.h

        eraser_size = ToolSlider(self, "Eraser Size", item_x, item_y)
        item_y += eraser_size.h

        #Add toolbar label buttons
        for i, label in enumerate(self.labels):
            label_button = LabelButton(self, i, label, item_x, item_y)
            item_y += label_button.h
        item_y += TOOLBAR_PADDING

        #Add remaining toolbar slider items
        label_transparency = ToolSlider(self, "Label Transparency", item_x, item_y)
        item_y += label_transparency.h

        zoom_factor = ToolSlider(self, "Zoom Factor", item_x, item_y)
        item_y += zoom_factor.h 
        
        #Add Image Navigation
        image_nav = ImageNavigator(self, item_x, item_y)
        item_y += image_nav.h 

        #Add Stats Panel
        stats_panel = StatsPanel(self, item_x, item_y)
        item_y += stats_panel.h 

        #Add Quit Button
        quit_button = QuitButton(self, item_x, item_y)


        
        


        """
        tsticon2 = QIcon("lasso_selection_tool_icon.png")
        self.button2 = QPushButton(tsticon2, '', self)
        self.button2.resize(50,50)
        self.button2.move(70,10)
        self.button2.setIcon(tsticon2)
        self.button2.setIconSize(QSize(40, 40))   
        """
        #self.button.initStyleOption(select_tool_style)
        #self.button.setIconSize(QSize(50,50))

        #self.button.clicked.connect(self.handleButton)
        #layout = QVBoxLayout(self)
        #layout.addWidget(self.button)

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
            sys.exit() 
#GUI(None, 10, 10)
GUI(None, 100, 50)


