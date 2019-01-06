import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
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

            #Check if center i,j is inside polygon
            if polygon.containsPoint(QPointF(j, i), Qt.OddEvenFill):

                #Get the rectangle at this position
                rect = QGraphicsRectItem(QRectF(QPointF(j-step_w//2, i-step_h//2), QPointF(j+step_w//2, i+step_w//2)))

                #Append to our item group
                rects.addToGroup(rect)

    return rects

























