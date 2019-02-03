import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from config import *
from gui_base import *
from Dataset import *


class GUI():

    def __init__(self, dataset, win_h, win_w):
        app = QApplication([])
        screen = QDesktopWidget().screenGeometry()
        screen_h, screen_w = screen.height(), screen.width()

        canvas = Canvas(dataset, screen_h, screen_w, win_h, win_w)
        toolbar = Toolbar(dataset, canvas, screen_h, screen_w, win_h, win_w)
        app.installEventFilter(canvas)
        sys.exit(app.exec_())


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

        self.color = SELECTION_RECT_FILL_COLOR #For now it's just one color

        self.pencil_rects = QGraphicsItemGroup()

        #Current tool being used to make selections in our image (defaults to RECT_SELECT)
        self.tool = RECT_SELECT

        #Current label to fill in those selections with (defaults to first)
        self.label = 0

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

                elif (event.type() == QEvent.MouseMove and event.buttons() != Qt.NoButton):

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

                elif (event.type() == QEvent.MouseMove and event.buttons() != Qt.NoButton):

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

            #Users can select around the given cursor wherever they drag the pencil, with this selection area depending on pencil_size
            elif self.tool == PENCIL:

                if (event.type() == QEvent.MouseMove):
                    #This tool begins doing things immediately, in order to
                    #   show the selection area around the cursor as they move it
                    self.pencil_rects = QGraphicsItemGroup()
                    r = 6
                    rsqrd = r**2
                    cx,cy = relative_coordinates(self.view, event.x(), event.y())
                    #Round cx and cy to be the center of whatever window they're in atm
                    cx = np.floor(cx/self.win_w)*self.win_w + self.win_w//2
                    cy = np.floor(cy/self.win_h)*self.win_h + self.win_h//2

                    #Iterate through outer boundary rectangle for our circle
                    for x in range(-r,r+1):
                        for y in range(-r,r+1):
                            if x**2 + y**2 <= rsqrd:
                                #Point at these cords should have a rect, get the coordinates for the rect
                                #Convert the relative cords to the absolute ones
                                px = cx + x*self.win_w
                                py = cy + y*self.win_h
                                rect = QGraphicsRectItem(QRectF(QPointF(px-self.win_w//2, py-self.win_h//2), QPointF(px+self.win_w//2, py+self.win_h//2)))
                                self.pencil_rects.addToGroup(rect)
                    self.render_selection(self.pencil_rects)


                    """
                    for x,rectx in enumerate(range(max(self.win_w//2, cx-r), min(self.img_w, cx+r), self.win_w):
                        for y,recty in enumerate(range(max(0, cy-r), min(self.img_h, cy+r), self.win_h):
                            if x**2 + y**2 <= rsqrd:
                                pencil_rects.addToGroup(
                    """

                    """
                    for radius in range(1,3):

                        r2 = radius**2;

                        addrect = lambda x,y: self.pencil_rects.addToGroup(get_outline_rect(QRect(QPoint(x,y),QPoint(x,y)), self.win_h, self.win_w))
                        addrect(cx, cy + radius*self.win_h);
                        addrect(cx, cy - radius*self.win_h);
                        addrect(cx + radius*self.win_w, cy);
                        addrect(cx - radius*self.win_w, cy);

                        x = 1;
                        y = int(np.sqrt(r2 - 1) + 0.5);
                        while (x < y): 
                            addrect(cx + x*self.win_w, cy + y*self.win_h);
                            addrect(cx + x*self.win_w, cy - y*self.win_h);
                            addrect(cx - x*self.win_w, cy + y*self.win_h);
                            addrect(cx - x*self.win_w, cy - y*self.win_h);
                            addrect(cx + y*self.win_h, cy + x*self.win_w);
                            addrect(cx + y*self.win_h, cy - x*self.win_w);
                            addrect(cx - y*self.win_h, cy + x*self.win_w);
                            addrect(cx - y*self.win_h, cy - x*self.win_w);
                            x += 1;
                            y = int(np.sqrt(r2 - x**2) + 0.5);

                        if (x == y) :
                            addrect(cx + x*self.win_w, cy + y*self.win_h);
                            addrect(cx + x*self.win_w, cy - y*self.win_h);
                            addrect(cx - x*self.win_w, cy + y*self.win_h);
                            addrect(cx - x*self.win_w, cy - y*self.win_h);

                    self.render_selection(self.pencil_rects)
                    self.pencil_rects = QGraphicsItemGroup()
                    """
                    
                    

                if (event.type() == QEvent.MouseButtonPress):

                    print("Press")
                    #Initialize selection polygon with this
                    x,y = relative_coordinates(self.view, event.x(), event.y())


                    x,y = relative_coordinates(self.view, event.x(), event.y())

                elif (event.type() == QEvent.MouseButtonRelease):
                    print("Release")
                    


                    
                    

        return False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
            sys.exit()


class Toolbar(QWidget):
    def __init__(self, dataset, canvas, screen_h, screen_w, win_h, win_w):
        super(Toolbar, self).__init__()
        self.dataset = dataset
        self.canvas = canvas

        self.win_h = win_h
        self.win_w = win_w

        self.h = TOOLBAR_HEIGHT
        self.w = TOOLBAR_WIDTH
        self.y = TOOLBAR_Y
        self.x = TOOLBAR_X

        self.setWindowTitle("| Toolbar |")
        self.setGeometry(self.x,self.y,self.w,self.h)

        #All buttons on the toolbar
        self.tool_buttons = []
        self.label_buttons = []

        #Add toolbar button items

        #Pointers for easy positioning of elements
        item_x, item_y = TOOLBAR_PADDING, TOOLBAR_PADDING

        #Rectangle Selection Tool
        rect_select = ToolButton(self, RECT_SELECT_ICON_FNAME, RECT_SELECT, item_x, item_y)
        self.tool_buttons.append(rect_select)
        item_x += rect_select.w + TOOLBAR_PADDING

        #Lasso Selection Tool
        lasso_select = ToolButton(self, LASSO_SELECT_ICON_FNAME, LASSO_SELECT, item_x, item_y)
        self.tool_buttons.append(lasso_select)
        item_x += lasso_select.w + TOOLBAR_PADDING

        #Pencil Tool
        pencil = ToolButton(self, PENCIL_ICON_FNAME, PENCIL, item_x, item_y)
        pencil.button.setEnabled(False)
        item_x += pencil.w + TOOLBAR_PADDING

        #Eraser Tool
        eraser = ToolButton(self, ERASER_ICON_FNAME, ERASER, item_x, item_y)
        eraser.button.setEnabled(False)
        item_x += eraser.w + TOOLBAR_PADDING

        #Reset for next row
        item_x = TOOLBAR_PADDING
        item_y += rect_select.h + TOOLBAR_PADDING

        #Add initial toolbar slider items
        pencil_size = ToolSlider(self, "Pencil Size (N/A)", item_x, item_y)
        item_y += pencil_size.h

        eraser_size = ToolSlider(self, "Eraser Size (N/A)", item_x, item_y)
        item_y += eraser_size.h

        #Add toolbar label buttons
        for label_id, label in enumerate(self.dataset.labels):
            label_button = LabelButton(self, label_id, label, item_x, item_y)
            self.label_buttons.append(label_button)
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
        stats_panel = StatsPanel(self, item_x, item_y, self.win_h, self.win_w)
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

GUI(Dataset("testinput/", "testoutput/", "testlabels.txt", False), 10, 10)
#GUI(None, 100, 50)


