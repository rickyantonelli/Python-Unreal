import sys
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QMainWindow, QGraphicsRectItem, QGraphicsPolygonItem

class DraggableItem:
    def initDraggable(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.offset = QPointF(0, 0)
        self.unrealAsset = None

    def mousePressEvent(self, event):
        self.offset = event.pos()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        print("newPos is {},{}".format(event.pos().x(), event.pos().y()))
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        # TODO: Currently can drag this off screen
        newPos = event.scenePos() - self.offset
        self.setPos(newPos.x(), newPos.y())
        super().mouseMoveEvent(event)
        
class DraggableSquare(QGraphicsRectItem, DraggableItem):
    def __init__(self, x, y, width, height):
        QGraphicsRectItem.__init__(self, QRectF(0, 0, width, height))
        self.initDraggable()
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(x, y)
        
class DraggableEllipse(QGraphicsEllipseItem, DraggableItem):
    def __init__(self, x, y, width, height):
        QGraphicsEllipseItem.__init__(self, QRectF(0, 0, width, height))
        self.initDraggable()
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(x, y)

class GridGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

    def createGrid(self, size=20, width=800, height=600):
        lightGray = QColor(211, 211, 211)
        for x in range(0, width, size):
            self.scene.addLine(x, 0, x, height, QPen(lightGray))
        for y in range(0, height, size):
            self.scene.addLine(0, y, width, y, QPen(lightGray))
        
    def addAsset(self, shape='square', posX=0, posY=0, width=15, height=15):
        if shape == 'circle':
            asset = DraggableEllipse(posX, posY, width, height)
        else:
            asset = DraggableSquare(posX, posY, width, height)
            
        self.scene.addItem(asset)
        return asset
        