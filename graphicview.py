import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QCursor
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem, QMainWindow, QGraphicsRectItem, QGraphicsPolygonItem

class SquareItem(QGraphicsRectItem):
    """The parent class for draggable items and also the base class for squares/cubes, which handles mouse events and updating the Unreal assets"""
    
    topLeft = 1
    topMiddle = 2
    topRight = 3
    middleLeft = 4
    middleRight = 5
    bottomLeft = 6
    bottomMiddle = 7
    bottomRight = 8
    
    resizeMargin = +10
    resizeSpace = -4
    
    # store the different cursors we'll use for resizing
    resizeCursors = {
        topLeft: Qt.SizeFDiagCursor,
        topMiddle: Qt.SizeVerCursor,
        topRight: Qt.SizeBDiagCursor,
        middleLeft: Qt.SizeHorCursor,
        middleRight: Qt.SizeHorCursor,
        bottomLeft: Qt.SizeBDiagCursor,
        bottomMiddle: Qt.SizeVerCursor,
        bottomRight: Qt.SizeFDiagCursor,
    }
    
    def __init__(self, x, y, width, height):
        """Init's the SquareItem, sets necessary flags and properties"""
        QGraphicsRectItem.__init__(self, QRectF(0, 0, width, height))
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setPos(x, y)
        
        self.offset = QPointF(0, 0)
        self.UEL = unreallibrary.UnrealLibrary()
        
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        
        self.unrealAsset = None
        self.boundary = None
        self.position = None
        self.width = width
        self.height = height
        
        self.handlePositioning()
        
    def handleAt(self, point):
        """Checks the given point to see whether it lands in any of the QRectFs for resizing, returns none if not
        
        Args:
            point (QPoint): The point that the mouse is at when the event is triggered
            
        Returns:
            The number related to the resizing direction, or None if not a resize
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None    
        
    def handlePositioning(self):
        """Sets the QRectFs that are needed to provide the proper cursor and set up resizing"""
        size = self.resizeMargin
        bound = self.boundingRect()
        
        # apply the sections that a mouse point would qualify for resizing
        self.handles[self.topLeft]      = QRectF(bound.left(), bound.top(), size, size)
        self.handles[self.topMiddle]    = QRectF(bound.center().x() - size / 2, bound.top(), size, size)
        self.handles[self.topRight]     = QRectF(bound.right() - size, bound.top(), size, size)
        self.handles[self.middleLeft]   = QRectF(bound.left(), bound.center().y() - size / 2, size, size)
        self.handles[self.middleRight]  = QRectF(bound.right() - size, bound.center().y() - size / 2, size, size)
        self.handles[self.bottomLeft]   = QRectF(bound.left(), bound.bottom() - size, size, size)
        self.handles[self.bottomMiddle] = QRectF(bound.center().x() - size / 2, bound.bottom() - size, size, size)
        self.handles[self.bottomRight]  = QRectF(bound.right() - size, bound.bottom() - size, size, size)

    def mousePressEvent(self, event):
        """Checks if the click qualifies for resizing or moving, then stores the rect and positions + calls the mousePressEvent
        
        Args:
            event (QMouseEvent): The qt event
        """
        # retrieve what type of point this is
        self.offset = event.pos()
        self.handleSelected = self.handleAt(event.pos())
        self.mousePressPos = event.pos()
        if self.handleSelected:
            self.mousePressRect = self.boundingRect()
            
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Stores the current position (while checking if within boundaries) and calls the mouseMoveEvent
        
        Args:
            event (QMouseEvent): The qt event
        """
        self.position = event.scenePos() - self.offset
        if self.handleSelected:
            self.resizeItem(event.pos())
        else:       
            # Only call super if the move event stays within the boundary
            if self.position.x() < self.boundary.left() or self.position.x() + self.boundingRect().width() > self.boundary.right():
                return
            if self.position.y() < self.boundary.top() or self.position.y() + self.boundingRect().height() > self.boundary.bottom():
                return
            super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Calls the mouseReleaseEvent, resets variables, and moves its Unreal counterpart
        
        Args:
            event (QMouseEvent): The qt event
        """
        super().mouseReleaseEvent(event)
        
        # apply the change to the item to its Unreal engine counterpart
        
        if self.position:
            print("self.position is {},{}".format(self.position.x(), self.position.y()))
            newLocation = unreal.Vector(self.position.x(), self.position.y(), 0)
            # oldUnrealLocation = self.unrealAsset.get_actor_location()
            # newUnrealX = oldUnrealLocation.x + self.pos().x() - self.mousePressPos.x()
            # newUnrealY = oldUnrealLocation.y + self.pos().y() - self.mousePressPos.y()
            # newLocation = unreal.Vector(newUnrealX, newUnrealY, 0)
            if self.unrealAsset:
                # no need to sweep or teleport, since we are just placing actors
                self.unrealAsset.set_actor_location(newLocation, False, False)
        
        # since we're releasing, reset these variables to None
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()
                
    def hoverMoveEvent(self, event):
        """Gets the cursor type and applies the hoverMoveEvent"""
        handle = self.handleAt(event.pos())
        cursor = Qt.ArrowCursor if handle is None else self.resizeCursors[handle]
        self.setCursor(cursor)
        super().hoverMoveEvent(event)
            
    def hoverLeaveEvent(self, event):
        """Resets the cursor type back to the ArrowCursor and applies the hoverLeaveEvent"""
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)
        
    # def boundingRect(self):
    #     """Takes the bounding rect and returns it with the extra margins and space in mind
        
    #     Returns:
    #         The adjusted rect
    #     """
    #     o = self.resizeMargin + self.resizeSpace
    #     return self.rect().adjusted(-o, -o, o, o)
            
    def setBoundary(self, rect):
        """Sets the boundary for the item, to ensure that it cannot be dragged out of the grid
        
        Args:
            rect (QRect): The grid's boundary
        """
        self.boundary = rect
    
    # resizing referenced from https://stackoverflow.com/questions/34429632/resize-a-qgraphicsitem-with-the-mouse
    def resizeItem(self, pos):
        """Resizes the item based on where the cursor was pulled from
        
            Ex: If pulled from the bottom middle down, will be resized only vertically but not horizontally
        """
        offset = self.resizeMargin + self.resizeSpace
        boundingRect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)
        
        self.prepareGeometryChange()
        
        if self.handleSelected == self.topLeft:
            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + pos.x() - self.mousePressPos.x()
            toY = fromY + pos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setTop(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)
        elif self.handleSelected == self.topMiddle:
            fromY = self.mousePressRect.top()
            toY = fromY + pos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setTop(toY)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)
        elif self.handleSelected == self.topRight:
            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + pos.x() - self.mousePressPos.x()
            toY = fromY + pos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setTop(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)
        elif self.handleSelected == self.middleLeft:
            fromX = self.mousePressRect.left()
            toX = fromX + pos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setLeft(toX)
            rect.setLeft(boundingRect.left() + offset)
            self.setRect(rect)
        elif self.handleSelected == self.middleRight:
            fromX = self.mousePressRect.right()
            toX = fromX + pos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setRight(toX)
            rect.setRight(boundingRect.right() - offset)
            self.setRect(rect)
        elif self.handleSelected == self.bottomLeft:
            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + pos.x() - self.mousePressPos.x()
            toY = fromY + pos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setBottom(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)
        elif self.handleSelected == self.bottomMiddle:
            fromY = self.mousePressRect.bottom()
            toY = fromY + pos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setBottom(toY)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)
        elif self.handleSelected == self.bottomRight:
            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + pos.x() - self.mousePressPos.x()
            toY = fromY + pos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setBottom(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        self.handlePositioning()
        
class SphereItem(SquareItem):
    """Sphere class that inherits from SquareItem but paints an ellipse to represent the sphere in Unreal Engine"""
    def __init__(self, x, y, width, height):
        """Init's SphereItem"""
        super().__init__(x, y, width, height)
        
    def paint(self, painter, option, widget):
        """Sets the brush and pen for the sphere, and draws an ellipse to represent a sphere"""
        painter.setBrush(QBrush(Qt.GlobalColor.blue))
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawEllipse(self.rect())

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
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.scene.setSceneRect(0, 0, 1200, 600)
        
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
        
    def addItem(self, shape='square', width=15, height=15, posX=None, posY=None):
        """Adds an item to the to the GridGraphicsView
        
        Each item is represented by a 2D shape, and represents a 3D shape that it generates in the Unreal Engine scene
        
        Args:
            posX (float): The x position that the item should be set at
            posY (float): The y position that the item should be set at
            width (float): The width of the item's shape
            height (float): The height of the item's shape
        """
        if not posX:
            x = (self.gridWidth - width) / 2
        else:
            x = posX
        if not posY:
            y = (self.gridHeight - height) / 2
        else:
            y = posY
            
        print("x is {}".format(x))
        print("y is {}".format(y))
        if self.gridCreated: # only add the item if the grid has been created
            if shape == 'circle':
                asset = SphereItem(x, y, width, height)
            else:
                asset = SquareItem(x, y, width, height)
            
            # set the boundary for the item, so that the shape can not be dragged outside the grid
            asset.setBoundary(QRectF(0, 0, self.gridWidth, self.gridHeight))
            
            self.scene.addItem(asset)
            return asset
        else:
            # we don't necessarily need a grid to add an item, but if this were to happen then boundaries could not be set
            print("Must create a grid before adding assets")
            return
        