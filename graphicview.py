import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QMainWindow, QGraphicsRectItem, QGraphicsPolygonItem

class DraggableItem:
    def initDraggable(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.offset = QPointF(0, 0)
        self.unrealAsset = None
        self.UEL = unreallibrary.UnrealLibrary()
        self.boundary = None
        self.position = None

    def mousePressEvent(self, event):
        self.offset = event.pos()
        if isinstance(super(), QGraphicsItem):
            super().mouseReleaseEvent(event)
        
    def mouseReleaseEvent(self, event):
        print("self.position is {},{}".format(self.position.x(), self.position.y()))
        newLocation = unreal.Vector(self.position.x(), self.position.y(), 0)
        if self.unrealAsset:
            self.unrealAsset.set_actor_location(newLocation, False, False)
        if isinstance(super(), QGraphicsItem):
            super().mouseReleaseEvent(event)
        
    def mouseMoveEvent(self, event):
        # TODO: Currently can drag this off screen
        self.position = event.scenePos() - self.offset
        if self.boundary:
            newX = max(self.boundary.left(), min(self.position.x(), self.boundary.right() - self.boundingRect().width()))
            newY = max(self.boundary.top(), min(self.position.y(), self.boundary.bottom() - self.boundingRect().height()))
            self.position = QPointF(newX, newY)
        self.setPos(self.position.x(), self.position.y())
        if isinstance(super(), QGraphicsItem):
            super().mouseReleaseEvent(event)
            
    def setBoundary(self, rect):
        self.boundary = rect
        
class DraggableSquare(QGraphicsRectItem, DraggableItem):
    def __init__(self, x, y, width, height):
        QGraphicsRectItem.__init__(self, QRectF(0, 0, width, height))
        self.initDraggable()
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(x, y)
        self._drag_start_pos = QPointF()
        
    def mouseReleaseEvent(self, event):
        DraggableItem.mouseReleaseEvent(self, event)
        
    def mouseMoveEvent(self, event):
        DraggableItem.mouseMoveEvent(self, event)
    
    def mousePressEvent(self, event):
        DraggableItem.mousePressEvent(self, event)
        
class DraggableEllipse(QGraphicsEllipseItem, DraggableItem):
    def __init__(self, x, y, width, height):
        QGraphicsEllipseItem.__init__(self, QRectF(0, 0, width, height))
        self.initDraggable()
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(x, y)
        
    def mouseReleaseEvent(self, event):
        DraggableItem.mouseReleaseEvent(self, event)
        
    def mouseMoveEvent(self, event):
        DraggableItem.mouseMoveEvent(self, event)
    
    def mousePressEvent(self, event):
        DraggableItem.mousePressEvent(self, event)

class GridGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.gridWidth = None
        self.gridHeight = None
        self.gridCreated = False
        

    def createGrid(self, size=20, width=800, height=600):
        lightGray = QColor(211, 211, 211)
        for x in range(0, width + 1, size):
            self.scene.addLine(x, 0, x, height, QPen(lightGray))
        for y in range(0, height + 1, size):
            self.scene.addLine(0, y, width, y, QPen(lightGray))
            
        self.gridWidth = width
        self.gridHeight = height
        self.gridCreated = True
        
    def addAsset(self, shape='square', posX=0, posY=0, width=15, height=15):
        if self.gridCreated:
            if shape == 'circle':
                asset = DraggableEllipse(posX, posY, width, height)
            else:
                asset = DraggableSquare(posX, posY, width, height)
            
            asset.setBoundary(QRectF(0, 0, self.gridWidth, self.gridHeight))
            
            self.scene.addItem(asset)
            return asset
        else:
            print("Must create a grid before adding assets")
            return
        