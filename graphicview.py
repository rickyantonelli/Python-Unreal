import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QCursor, QAction
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QMenu

class SquareItem(QGraphicsRectItem):
    """The parent class for draggable items and also the base class for squares/cubes, which handles mouse events and updating the Unreal assets"""
    
    topLeft = 'topleft'
    topMiddle = 'top'
    topRight = 'topright'
    middleLeft = 'left'
    middleRight = 'right'
    bottomLeft = 'bottomleft'
    bottomMiddle = 'bottom'
    bottomRight = 'bottomright'
    
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
        
        self.unrealAsset = None
        self.position = None
        self.width = width
        self.height = height
        
        self.selectedEdge = None
        self.clickPos = self.clickRect = None
        
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
    
    # def boundingRect(self):
    #     """Takes the bounding rect and returns it with the extra margins and space in mind
        
    #     Returns:
    #         The adjusted rect
    #     """
    #     o = self.resizeMargin + self.resizeSpace
    #     return self.rect().adjusted(-o, -o, o, o)
    
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
        if event.button() == Qt.MouseButton.RightButton:
            self.displayContextMenu(event)
        else:
            self.selectedEdge = self.handleAt(event.pos())
            self.clickPos = event.pos()
            self.clickRect = self.rect()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Stores the current position (while checking if within boundaries) and calls the mouseMoveEvent
        
        Args:
            event (QMouseEvent): The qt event
        """
        pos = event.pos()
        xDiff = pos.x() - self.clickPos.x()
        yDiff = pos.y() - self.clickPos.y()

        # get the rectangle as it was when clicked
        rect = QRectF(self.clickRect)

        # if the mouse is not on an edge, then we move the object (translate)
        # if it is on an edge, then we resize (adjust)
        if self.selectedEdge is None:
            rect.translate(xDiff, yDiff)
        elif self.selectedEdge == 'top':
            rect.adjust(0, yDiff, 0, 0)
        elif self.selectedEdge == 'left':
            rect.adjust(xDiff, 0, 0, 0)
        elif self.selectedEdge == 'bottom':
            rect.adjust(0, 0, 0, yDiff)
        elif self.selectedEdge == 'right':
            rect.adjust(0, 0, xDiff, 0)
        elif self.selectedEdge == 'topleft':
            rect.adjust(xDiff, yDiff, 0, 0)
        elif self.selectedEdge == 'topright':
            rect.adjust(0, yDiff, xDiff, 0)
        elif self.selectedEdge == 'bottomleft':
            rect.adjust(xDiff, 0, 0, yDiff)
        elif self.selectedEdge == 'bottomright':
            rect.adjust(0, 0, xDiff, yDiff)

        # this section ensures that we do not drag the rect outside of our boundaries
        # we have set the sceneRect() to be that of the grid boundary
        sceneRect = self.scene().sceneRect()
        viewLeft = sceneRect.left()
        viewTop = sceneRect.top()
        viewRight = sceneRect.right()
        viewBottom = sceneRect.bottom()

        # if we reach an edge, then update the translation to be clamped at the edge that we hit
        # this is much smoother than just not moving when you hit an edge, as movement can still be done on the valid axis
        if rect.top() < viewTop:
            if self.selectedEdge is None:
                rect.translate(0, viewTop-rect.top())
            else:
                rect.setTop(viewTop)
        if rect.left() < viewLeft:
            if self.selectedEdge is None:
                rect.translate(viewLeft-rect.left(), 0)
            else:
                rect.setLeft(viewLeft)
        if viewBottom < rect.bottom():
            if self.selectedEdge is None:
                rect.translate(0, viewBottom - rect.bottom())
            else:
                rect.setBottom(viewBottom)
        if viewRight < rect.right():
            if self.selectedEdge is None:
                rect.translate(viewRight - rect.right(), 0)
            else:
                rect.setRight(viewRight)

        # lastly, make sure that we aren't resizing into a negative amount
        # without this we could drag all the way backwards into itself
        if rect.width() < 5:
            if self.selectedEdge == 'left':
                rect.setLeft(rect.right() - 5)
            else:
                rect.setRight(rect.left() + 5)
        if rect.height() < 5:
            if self.selectedEdge == 'top':
                rect.setTop(rect.bottom() - 5)
            else:
                rect.setBottom(rect.top() + 5)

        # set the rect with our updates, recalculate positioning for cursors with new rect shape
        self.setRect(rect)
        self.handlePositioning()
        
    def mouseReleaseEvent(self, event):
        """Calls the mouseReleaseEvent, resets variables, and moves its Unreal counterpart
        
        Args:
            event (QMouseEvent): The qt event
        """
        super().mouseReleaseEvent(event)
        
        # apply the change to the item to its Unreal engine counterpart
        rect = QRectF(self.rect())
        
        # take the center() of the rect as the point
        # if we do not take the center(), then resizing will not change position in Unreal in the way we'd like
        print("new position is {},{}".format(rect.center().x(), rect.center().y()))
        newLocation = unreal.Vector(rect.center().x(), rect.center().y(), 0)
        
        if self.unrealAsset:
            # reflect the position change in unreal engine
            # no need to sweep or teleport, since we are just placing actors
            self.unrealAsset.set_actor_location(newLocation, False, False)
            
            # on resizing, reflect the scale update in Unreal 
            oldActorScale = self.unrealAsset.get_actor_scale3d()
            xFactor = rect.width() / self.clickRect.width()
            yFactor = rect.height() / self.clickRect.height()
            # lets expose the zFactor because in the future we'll like to allow for this to be changeable
            zFactor = 1
            
            newXScale = oldActorScale.x * xFactor
            newYScale = oldActorScale.y * yFactor
            newZScale = oldActorScale.z * zFactor
            if newXScale != 1 or newYScale != 1 or newZScale != 1:
                # only apply updates to unreal if we need to (there is a scale change)
                self.unrealAsset.set_actor_scale3d(unreal.Vector(newXScale, newYScale, newZScale))
    
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
        
    def displayContextMenu(self, event):
        contextMenu = QMenu()
        deleteAction = QAction("Delete Item", contextMenu)
        deleteAction.triggered.connect(self.deleteItem)
        contextMenu.addAction(deleteAction)
        contextMenu.exec(event.screenPos())
        
    def deleteItem(self):
        self.UEL.ELL.destroy_actor(self.unrealAsset)
        if self.scene():
            self.scene().removeItem(self)
      
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
        # self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
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
        
    def addItem(self, shape='square', width=15, height=15):
        """Adds an item to the to the GridGraphicsView
        
        Each item is represented by a 2D shape, and represents a 3D shape that it generates in the Unreal Engine scene
        
        Args:
            posX (float): The x position that the item should be set at
            posY (float): The y position that the item should be set at
            width (float): The width of the item's shape
            height (float): The height of the item's shape
        """
        print("width is {}".format(width))
        print("height is {}".format(height))
        if self.gridCreated: # only add the item if the grid has been created
            if shape == 'circle':
                asset = SphereItem(0, 0, width, height)
            else:
                asset = SquareItem(0, 0, width, height)
            
            self.scene.addItem(asset)
            self.scene.setSceneRect(0, 0, self.gridWidth, self.gridHeight)
            
            #TODO: Allow for passing in of x and y coordinates, which will then translate the rect to those coordinates after creation
            return asset
        else:
            # we don't necessarily need a grid to add an item, but if this were to happen then boundaries could not be set
            print("Must create a grid before adding assets")
            return
        