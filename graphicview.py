import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QMainWindow, QGraphicsRectItem, QGraphicsPolygonItem

class DraggableItem:
    """The parent class for draggable items, which handles mouse events and updating the Unreal assets"""
    def initDraggable(self):
        """Sets the necessary properties for the item and declares more"""
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.offset = QPointF(0, 0)
        self.unrealAsset = None
        self.UEL = unreallibrary.UnrealLibrary()
        self.boundary = None
        self.position = None

    def mousePressEvent(self, event):
        """Stores the original position and calls the mousePressEvent
        
        Args:
            event (QMouseEvent): The qt event
        """
        self.offset = event.pos()
        if isinstance(super(), QGraphicsItem):
            super().mouseReleaseEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Retrieves the current position and applies it to its Unreal counterpart, and calls the mouseReleaseEvent
        
        Args:
            event (QMouseEvent): The qt event
        """
        print("self.position is {},{}".format(self.position.x(), self.position.y()))
        newLocation = unreal.Vector(self.position.x(), self.position.y(), 0)
        if self.unrealAsset:
            # no need to sweep or teleport, since we are just placing actors
            self.unrealAsset.set_actor_location(newLocation, False, False)
        if isinstance(super(), QGraphicsItem):
            super().mouseReleaseEvent(event)
        
    def mouseMoveEvent(self, event):
        """Stores the current position (while checking if within boundaries) and calls the mouseMoveEvent
        
        Args:
            event (QMouseEvent): The qt event
        """
        self.position = event.scenePos() - self.offset
        if self.boundary:
            # check if the mouse location is within the boundaries that we set
            # if it isnt then just set the position to the boundary
            newX = max(self.boundary.left(), min(self.position.x(), self.boundary.right() - self.boundingRect().width()))
            newY = max(self.boundary.top(), min(self.position.y(), self.boundary.bottom() - self.boundingRect().height()))
            self.position = QPointF(newX, newY)
        # set the location of the item to the new position
        self.setPos(self.position.x(), self.position.y())
        if isinstance(super(), QGraphicsItem):
            super().mouseReleaseEvent(event)
            
    def setBoundary(self, rect):
        """Sets the boundary for the item, to ensure that it cannot be dragged out of the grid
        
        Args:
            rect (QRect): The grid's boundary
        """
        self.boundary = rect
        
class DraggableSquare(QGraphicsRectItem, DraggableItem):
    """A QGraphicsRectItem to be displayed in the grid, which inherits DraggableItem to handle mouse events and Unreal Assets
    
    Attributes:
        x (float): The starting x position on the grid
        y (float): The starting y position on the grid
        width (float): The width of the rectangle
        height (float): The height of the rectangle
    """
    def __init__(self, x, y, width, height):
        QGraphicsRectItem.__init__(self, QRectF(0, 0, width, height))
        """Init's the QGraphicsRectItem and sets necessities while also inheriting DraggableItem's initialization"""
        self.initDraggable()
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(x, y)
        
    def mouseReleaseEvent(self, event):
        """Calls the parent DraggableItem class's mouseReleaseEvent"""
        DraggableItem.mouseReleaseEvent(self, event)
        
    def mouseMoveEvent(self, event):
        """Calls the parent DraggableItem class's mouseMoveEvent"""
        DraggableItem.mouseMoveEvent(self, event)
    
    def mousePressEvent(self, event):
        """Calls the parent DraggableItem class's mousePressEvent"""
        DraggableItem.mousePressEvent(self, event)
        
class DraggableEllipse(QGraphicsEllipseItem, DraggableItem):
    """A QGraphicsEllipseItem to be displayed in the grid, which inherits DraggableItem to handle mouse events and Unreal Assets
    
    Attributes:
        x (float): The starting x position on the grid
        y (float): The starting y position on the grid
        width (float): The width of the ellipse
        height (float): The height of the ellipse
    """
    # TODO: this should never not be a circle, so we should just take in one param for width and height to avoid confusion
    def __init__(self, x, y, width, height):
        """Init's the QGraphicsEllipseItem and sets necessities while also inheriting DraggableItem's initialization"""
        QGraphicsEllipseItem.__init__(self, QRectF(0, 0, width, height))
        self.initDraggable()
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(x, y)
        
    def mouseReleaseEvent(self, event):
        """Calls the parent DraggableItem class's mouseReleaseEvent"""
        DraggableItem.mouseReleaseEvent(self, event)
        
    def mouseMoveEvent(self, event):
        """Calls the parent DraggableItem class's mouseMoveEvent"""
        DraggableItem.mouseMoveEvent(self, event)
    
    def mousePressEvent(self, event):
        """Calls the parent DraggableItem class's mousePressEvent"""
        DraggableItem.mousePressEvent(self, event)

class GridGraphicsView(QGraphicsView):
    """A QGraphicsView that takes in shapes as items in a 2D space, to represent a 3D space in Unreal Engine"""
    def __init__(self):
        """Init's GridGraphicsView and sets the scene"""
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.gridWidth = None
        self.gridHeight = None
        self.gridCreated = False
        

    def createGrid(self, step=20, width=800, height=600):
        """Creates the grid in the graphics view and adds grid lines
        
        Args:
            step (int): The step for each grid line
            width (int): The width of the grid
            height (int): The height of the grid
        """
        # lines are light grey for now, can add a colorpicker if we want to add the flexibility
        lightGray = QColor(211, 211, 211)
        
        # TODO: Give some flexibility to the grid - for example maybe just lines at the end as an option
        
        # make this `+ 1` so that we add a line to the edges
        for x in range(0, width + 1, step):
            self.scene.addLine(x, 0, x, height, QPen(lightGray))
        for y in range(0, height + 1, step):
            self.scene.addLine(0, y, width, y, QPen(lightGray))
        
        # this "grid" does not actually create a grid, but rather sets the lines for an area
        # and establishes boundaries for that area
        # we store gridWidth and gridHeight so that we can set the boundary for an item when we create it
        self.gridWidth = width
        self.gridHeight = height
        self.gridCreated = True
        
    def addItem(self, shape='square', posX=0, posY=0, width=15, height=15):
        """Adds an item to the to the GridGraphicsView
        
        Each item is represented by a 2D shape, and represents a 3D shape that it generates in the Unreal Engine scene
        
        Args:
            posX (float): The x position that the item should be set at
            posY (float): The y position that the item should be set at
            width (float): The width of the item's shape
            height (float): The height of the item's shape
        """
        
        if self.gridCreated: # only add the item if the grid has been created
            if shape == 'circle':
                asset = DraggableEllipse(posX, posY, width, height)
            else:
                asset = DraggableSquare(posX, posY, width, height)
            
            # set the boundary for the item, so that the shape can not be dragged outside the grid
            asset.setBoundary(QRectF(0, 0, self.gridWidth, self.gridHeight))
            
            self.scene.addItem(asset)
            return asset
        else:
            # we don't necessarily need a grid to add an item, but if this were to happen then boundaries could not be set
            print("Must create a grid before adding assets")
            return
        