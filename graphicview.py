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
        
        self.unrealAsset = None
        self.position = None
        self.width = width
        self.height = height
        
        self.selected_edge = None
        self.click_pos = self.click_rect = None
        
        
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
        
        self.click_pos = event.pos()
        rect = self.rect()
        if abs(rect.left() - self.click_pos.x()) < 5:
            self.selected_edge = 'left'
        elif abs(rect.right() - self.click_pos.x()) < 5:
            self.selected_edge = 'right'
        elif abs(rect.top() - self.click_pos.y()) < 5:
            self.selected_edge = 'top'
        elif abs(rect.bottom() - self.click_pos.y()) < 5:
            self.selected_edge = 'bottom'
        else:
            self.selected_edge = None
        self.click_pos = event.pos()
        self.click_rect = rect
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Stores the current position (while checking if within boundaries) and calls the mouseMoveEvent
        
        Args:
            event (QMouseEvent): The qt event
        """
        pos = event.pos()
        x_diff = pos.x() - self.click_pos.x()
        y_diff = pos.y() - self.click_pos.y()

        # Start with the rectangle as it was when clicked.
        rect = QRectF(self.click_rect)

        # Then adjust by the distance the mouse moved.
        if self.selected_edge is None:
            rect.translate(x_diff, y_diff)
        elif self.selected_edge == 'top':
            rect.adjust(0, y_diff, 0, 0)
        elif self.selected_edge == 'left':
            rect.adjust(x_diff, 0, 0, 0)
        elif self.selected_edge == 'bottom':
            rect.adjust(0, 0, 0, y_diff)
        elif self.selected_edge == 'right':
            rect.adjust(0, 0, x_diff, 0)

        scene_rect = self.scene().sceneRect()
        view_left = scene_rect.left()
        view_top = scene_rect.top()
        view_right = scene_rect.right()
        view_bottom = scene_rect.bottom()

        # Next, check if the rectangle has been dragged out of bounds.
        if rect.top() < view_top:
            if self.selected_edge is None:
                rect.translate(0, view_top-rect.top())
            else:
                rect.setTop(view_top)
        if rect.left() < view_left:
            if self.selected_edge is None:
                rect.translate(view_left-rect.left(), 0)
            else:
                rect.setLeft(view_left)
        if view_bottom < rect.bottom():
            if self.selected_edge is None:
                rect.translate(0, view_bottom - rect.bottom())
            else:
                rect.setBottom(view_bottom)
        if view_right < rect.right():
            if self.selected_edge is None:
                rect.translate(view_right - rect.right(), 0)
            else:
                rect.setRight(view_right)

        # Also check if the rectangle has been dragged inside out.
        if rect.width() < 5:
            if self.selected_edge == 'left':
                rect.setLeft(rect.right() - 5)
            else:
                rect.setRight(rect.left() + 5)
        if rect.height() < 5:
            if self.selected_edge == 'top':
                rect.setTop(rect.bottom() - 5)
            else:
                rect.setBottom(rect.top() + 5)

        # Finally, update the rect that is now guaranteed to stay in bounds.
        self.setRect(rect)
        
    def mouseReleaseEvent(self, event):
        """Calls the mouseReleaseEvent, resets variables, and moves its Unreal counterpart
        
        Args:
            event (QMouseEvent): The qt event
        """
        super().mouseReleaseEvent(event)
        self.handlePositioning()
        
        # apply the change to the item to its Unreal engine counterpart
        rect = QRectF(self.rect())
        
        print("self.position is {},{}".format(rect.x(), rect.y()))
        newLocation = unreal.Vector(rect.x(), rect.y(), 0)
        # oldUnrealLocation = self.unrealAsset.get_actor_location()
        # newUnrealX = oldUnrealLocation.x + self.pos().x() - self.mousePressPos.x()
        # newUnrealY = oldUnrealLocation.y + self.pos().y() - self.mousePressPos.y()
        # newLocation = unreal.Vector(newUnrealX, newUnrealY, 0)
        if self.unrealAsset:
            # no need to sweep or teleport, since we are just placing actors
            self.unrealAsset.set_actor_location(newLocation, False, False)
    
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
        if self.gridCreated: # only add the item if the grid has been created
            if shape == 'circle':
                asset = SphereItem(0, 0, width, height)
            else:
                asset = SquareItem(0, 0, width, height)
            
            self.scene.addItem(asset)
            self.scene.setSceneRect(0, 0, self.gridWidth, self.gridHeight)
            return asset
        else:
            # we don't necessarily need a grid to add an item, but if this were to happen then boundaries could not be set
            print("Must create a grid before adding assets")
            return
        