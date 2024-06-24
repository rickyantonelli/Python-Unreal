import sys
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QMainWindow

class DraggableAsset(QGraphicsEllipseItem):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setAcceptHoverEvents(True)
        self.offset = QPointF(0, 0)

    def mousePressEvent(self, event):
        self.offset = event.pos()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        print("newPos is {},{}".format(event.pos().x(), event.pos().y()))
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        newPos = event.scenePos() - self.offset
        self.setPos(newPos.x(), newPos.y())
        super().mouseMoveEvent(event)

class GridGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

    def createGrid(self, size, width, height):
        lightGray = QColor(211, 211, 211)
        for x in range(0, width, size):
            self.scene.addLine(x, 0, x, height, QPen(lightGray))
        for y in range(0, height, size):
            self.scene.addLine(0, y, width, y, QPen(lightGray))
        
    def addAsset(self, posX, posY, width, height):
        asset = DraggableAsset(posX, posY, width, height)
        self.scene.addItem(asset)