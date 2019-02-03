import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from config import * 

def get_rectangle_from_points(p1, p2):
    x1, y1 = p1.x(), p1.y()
    x2, y2 = p2.x(), p2.y()
    #Get the top-left and bot-right points for the rectangle defined by the two points.
    #We do this by handling the 4 different orientations possible.
    if x1 <= x2 and y1 <= y2:
        """
        1
         \
          2
        """
        return QRect(QPoint(x1, y1), QPoint(x2, y2))

    elif x1 > x2 and y1 <= y2:
        """
          1
         /
        2 
        """
        return QRect(QPoint(x2, y1), QPoint(x1, y2))
    elif x1 <= x2 and y1 > y2:
        """
          2
         /
        1 
        """
        return QRect(QPoint(x1, y2), QPoint(x2, y1))

    elif x1 > x2 and y1 > y2:
        """
        2
         \
          1
        """
        return QRect(QPoint(x2, y2), QPoint(x1, y1))

def get_outline_rect(rect, step_h, step_w):
    """
    Get a new qt rectangle made entirely of smaller rectangles of size step_hxstep_w 
        which outlines the area encompassed by the given rectangle.

    Luckily, this is easily done with a simple modular arithmetic formula I came up with.
    """
    x1,y1,x2,y2 = rect.getCoords()

    """
    Handle edge case when x1 == x2 and x1 % step_w == 0,
        or y1 == y2 and y1 % step_h == 0, which resulted
        in outline_x1 == outline_x2 or outline_y1 == outline_y2,
        respectively.

    We add a small epsilon factor to break the cases causing it
        without ever feasibly breaking the cases that don't.
    """
    x2+=EPSILON
    y2+=EPSILON

    outline_x1 = np.floor(x1/step_w)*step_w 
    outline_y1 = np.floor(y1/step_h)*step_h
    outline_x2 = np.ceil(x2/step_w)*step_w
    outline_y2 = np.ceil(y2/step_h)*step_h


    return QGraphicsRectItem(QRectF(QPointF(outline_x1, outline_y1), QPointF(outline_x2, outline_y2)))

def approximate_polygon(polygon, img_h, img_w, step_h, step_w):
    """
    We approximate the area encompassed by our QPolygonF
        with rectangles of shape step_h x step_w, and
        we obtain the list of approximate rectangles via iterating
        through each rectangle on the image and checking
        if it's center is inside the polygon.

    We add these all to a QGraphicsItemGroup, and return that.
    """
    #Ensure int data types
    img_h, img_w, step_h, step_w = int(img_h), int(img_w), int(step_h), int(step_w)

    #Create group
    rects = QGraphicsItemGroup()
    #Iterate through centers
    for i in range(int(step_h//2), img_h, step_h):
        for j in range(int(step_w//2), img_w, step_w):

            #Check if center is inside polygon
            if polygon.containsPoint(QPointF(j, i), Qt.OddEvenFill):

                #Get the rectangle at this position
                rect = QGraphicsRectItem(QRectF(QPointF(j-step_w//2, i-step_h//2), QPointF(j+step_w//2, i+step_h//2)))

                #Append to our item group
                rects.addToGroup(rect)

    return rects


def relative_coordinates(view, x, y):
    """
    Gets the x and y coordinates, relative 
        to the given graphicsview scroll position(s).
    """
    scroll_x = view.horizontalScrollBar().value()
    scroll_y = view.verticalScrollBar().value()

    return (scroll_x + x, scroll_y + y)


class ToolButton():
    """
    Creates a button corresponding to the given tool,
        allowing the user to change their currently selected 
        tool to this tool id on pushing this button.
    """
    def __init__(self, parent, icon_fname, tool_id, x, y, w=TOOLBAR_MIN_ITEM_WIDTH, h=TOOLBAR_MAX_ITEM_HEIGHT):
        self.w, self.h = w, h
        self.tool_id = tool_id

        #These callback methods are forced to be staticmethods with no args in PyQt,
        #   so we define it inside the __init__ method
        def on_click():
            #Initialize our callback function for when this button is pressed

            #Change parent active tool to this tool_id
            parent.canvas.tool = tool_id

            #Change other tool button states to not checked
            #   (only way to change check state is with toggle())
            for tool_button in parent.tool_buttons:
                if tool_button.button.isChecked():
                    tool_button.button.toggle()

            #Change this button state to checked
            if not self.button.isChecked():
                self.button.toggle()

        self.button = QPushButton('', parent)
        self.button.resize(self.w, self.h)
        self.button.move(x, y)
        self.button.setIcon(QIcon(icon_fname))
        self.button.setIconSize(QSize(self.w, self.h))
        self.button.clicked.connect(on_click)
        self.button.setCheckable(True)

        #If we already have initialized the tool value to this tool_id, toggle this button.
        if parent.canvas.tool == tool_id:
            self.button.toggle()

    #Add our supporting function for enabling/disabling the button this class wraps around
    def setEnabled(self, condition):
        self.button.setEnabled(condition)





class ToolSlider():
    """
    Creates a slider with the given specifications,
        to be linked to various parameters in the GUI
        to be changed via movements of the slider.
    """
    def __init__(self, parent, slider_name, x, y, w=TOOLBAR_MAX_ITEM_WIDTH, h=TOOLBAR_MAX_ITEM_HEIGHT):
        self.w, self.h = w, h

        label = QLabel(slider_name, parent)
        label.setAlignment(Qt.AlignCenter)
        label.resize(self.w, TOOLBAR_MIN_ITEM_HEIGHT)
        label.move(x, y)

        slider = QSlider(Qt.Horizontal, parent)
        slider.resize(self.w, self.h)
        slider.move(x, y)

class LabelButton():
    """
    Creates a button corresponding to the given label,
        allowing the user to change their currently selected 
        label to this label on pushing this button.
    """
    def __init__(self, parent, label_id, label_name, x, y, w=TOOLBAR_MAX_ITEM_WIDTH, h=TOOLBAR_MAX_ITEM_HEIGHT):
        self.w, self.h = w, h

        #These callback methods are forced to be staticmethods with no args in PyQt,
        #   so we define it inside the __init__ method
        def on_click():
            #Initialize our callback function for when this button is pressed

            #Change parent active label to this label_id
            parent.canvas.label = label_id

            #Change other label button states to not checked
            #   (only way to change check state is with toggle())
            for label_button in parent.label_buttons:
                if label_button.button.isChecked():
                    label_button.button.toggle()

            #Change this button state to checked
            if not self.button.isChecked():
                self.button.toggle()

        self.button = QPushButton(label_name, parent)
        self.button.resize(self.w, self.h)
        self.button.move(x, y)
        self.button.clicked.connect(on_click)
        self.button.setCheckable(True)

        #If we already have initialized the label value to this label_id, toggle this button.
        if parent.canvas.label == label_id:
            self.button.toggle()

        """
        The only way I could find to set a background color for a pyqt button,
           despite how much I don't like using this method since it
           requires we basically add CSS code.
        """
        self.button.setStyleSheet("background-color: {}".format(LABEL_COLORS[label_id]))

class ImageNavigator():
    """
    Creates a display for the current image out of how many are remaining,
        surrounded by left and right arrows to allow the user to
        navigate to the previous and next image, respectively.
    """
    def __init__(self, parent, x, y, w=TOOLBAR_MAX_ITEM_WIDTH, h=TOOLBAR_MAX_ITEM_HEIGHT):
        self.w, self.h = w, h

        self.button_w = self.w*IMAGE_NAVIGATOR_BUTTON_WIDTH_PERC
        self.label_w = self.w*IMAGE_NAVIGATOR_LABEL_WIDTH_PERC

        #Left / Previous Image Button
        button = QPushButton('Prev', parent)
        button.resize(self.w*IMAGE_NAVIGATOR_BUTTON_WIDTH_PERC, self.h)
        button.move(x, y)

        x += self.button_w

        #Label
        label = QLabel("Image 4/9", parent)
        label.setAlignment(Qt.AlignCenter)
        label.resize(self.w*IMAGE_NAVIGATOR_LABEL_WIDTH_PERC, self.h)
        label.move(x, y)

        x += self.label_w

        #Right / Next Image Button
        button = QPushButton('Next', parent)
        button.resize(self.w*IMAGE_NAVIGATOR_BUTTON_WIDTH_PERC, self.h)
        button.move(x, y)

        x += self.button_w

class StatsPanel():
    """
    Create a text panel to display several statistics about the ongoing session.
    """
    def __init__(self, parent, x, y, win_h, win_w, w=TOOLBAR_MAX_ITEM_WIDTH, h=TOOLBAR_MAX_ITEM_HEIGHT):
        self.w, self.h = w, h

        #Label
        label = QLabel("Classification Size: {}x{} pixels\nUsername: N/A".format(win_h,win_w), parent)
        label.setAlignment(Qt.AlignCenter)
        label.resize(self.w, self.h)
        label.move(x, y)

class QuitButton():
    """
    Creates a quit button, to end the session.
    """
    def __init__(self, parent, x, y, w=TOOLBAR_MAX_ITEM_WIDTH, h=TOOLBAR_MAX_ITEM_HEIGHT):
        self.w, self.h = w, h
        button = QPushButton("Quit Session", parent)
        button.resize(self.w, self.h)
        button.move(x, y)


















