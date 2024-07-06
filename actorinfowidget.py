import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QCursor, QAction
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QMenu, QWidget

class InfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        
    # TODO: Widget that displays info on the selected item
    # Name (changeable) and that's it for now