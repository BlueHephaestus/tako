import numpy as np
from PyQt5.QtCore import *

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
    outline_x1 = np.floor(x1/step_w)*step_w 
    outline_y1 = np.floor(y1/step_h)*step_h
    outline_x2 = np.ceil(x2/step_w)*step_w
    outline_y2 = np.ceil(y2/step_h)*step_h

    return QRect(QPoint(outline_x1, outline_y1), QPoint(outline_x2, outline_y2))
