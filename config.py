from PyQt5.QtGui import QColor

NPY_IMAGE_DIR = "data/images"
NPY_CLASSIFICATION_DIR = "data/classifications"
IMAGE_MAX_GB = 1.0#Maximum allowed size of a viewable image, in GB.

#TOOLBAR_SCREEN_HEIGHT_PERCENTAGE = .925
TOOLBAR_SCREEN_HEIGHT_PERCENTAGE = .70
TOOLBAR_SCREEN_WIDTH_PERCENTAGE = .13
TOOLBAR_SCREEN_Y_HEIGHT_PERCENTAGE = 0.0375

#CANVAS_SCREEN_HEIGHT_PERCENTAGE = .925
CANVAS_SCREEN_HEIGHT_PERCENTAGE = .70
CANVAS_SCREEN_WIDTH_PERCENTAGE = .80
CANVAS_SCREEN_Y_HEIGHT_PERCENTAGE = 0.0375 

SELECTION_RECT_FILL_COLOR = QColor(255, 0, 0, 255)

EPSILON = 1e-7

RECT_SELECT = 0
LASSO_SELECT = 1
