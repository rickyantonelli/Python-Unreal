import unreal

from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPolygonF, QCursor, QAction
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QMenu, QGraphicsLineItem

from unreallibrary import UnrealLibrary

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
    
    def __init__(self, x, y, width, height, unrealActor=None, label=None, unrealPath=None):
        """Init's the SquareItem, sets necessary flags and properties"""
        QGraphicsRectItem.__init__(self, QRectF(0, 0, width, height))
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)
        self.setBrush(QBrush(Qt.GlobalColor.blue))
        self.setPen(QPen(Qt.GlobalColor.black))
        self.setZValue(1) # so that the item is always layered ahead of grid lines
        
        self.offset = QPointF(0, 0)
        self.UEL = UnrealLibrary()
        
        self.handles = {}
        
        self.width = width
        self.height = height
        
        self.selectedEdge = None
        self.clickPos = self.clickRect = None
        self.setRectPos(x, y)
        self.handlePositioning()
        
        self.actorLabel = label
        
        # sphere item 
        if not isinstance(self, SphereItem):
            if unrealActor:
                # if an asset is passed in, that means we are copying
                self.unrealActor = self.UEL.copyActor(unrealActor, self.actorLabel)
                self.unrealActor.set_actor_location(unreal.Vector(x+(width/2), y+(height/2), 0), False, False)
            else:
                # set x and y to 12.5 since we are now using the center of the QRectF
                # and our grid starts at (0,0) in the top left
                # TODO: should just be the center of the rect not +12.5
                self.unrealActor = self.UEL.spawnActor('square', x+(width/2), y+(height/2), self.actorLabel, unrealPath)
        
    def setRectPos(self, x, y):
        rect = QRectF(self.rect())
        rect.translate(x, y)
        self.setRect(rect)
        
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
        
        self.width = rect.width()
        self.height = rect.height()
        
        if self.unrealActor:
            # reflect the position change in unreal engine
            # no need to sweep or teleport, since we are just placing actors
            self.unrealActor.set_actor_location(newLocation, False, False)
            
            # on resizing, reflect the scale update in Unreal 
            oldActorScale = self.unrealActor.get_actor_scale3d()
            xFactor = rect.width() / self.clickRect.width()
            yFactor = rect.height() / self.clickRect.height()
            # lets expose the zFactor because in the future we'll like to allow for this to be changeable
            zFactor = 1
            
            newXScale = oldActorScale.x * xFactor
            newYScale = oldActorScale.y * yFactor
            newZScale = oldActorScale.z * zFactor
            if newXScale != 1 or newYScale != 1 or newZScale != 1:
                # only apply updates to unreal if we need to (there is a scale change)
                self.unrealActor.set_actor_scale3d(unreal.Vector(newXScale, newYScale, newZScale))
    
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
        
    #TODO: We should move context menu stuff to the view
    def displayContextMenu(self, event):
        """Generates a QMenu and adds actions to it
        
        Args:
            event (QMouseEvent): The qt event
        """
        contextMenu = QMenu()
        deleteAction = QAction("Delete Item", contextMenu)
        deleteAction.triggered.connect(self.deleteItem)
        contextMenu.addAction(deleteAction)
        contextMenu.exec(event.screenPos())
        
    def deleteItem(self):
        """Removes this item from the GridGraphicsView and deletes its Unreal counterpart"""
        if self.unrealActor:
            self.UEL.ELL.destroy_actor(self.unrealActor)
        if self.scene():
            self.scene().removeItem(self)
      
class SphereItem(SquareItem):
    """Sphere class that inherits from SquareItem but paints an ellipse to represent the sphere in Unreal Engine"""
    def __init__(self, x, y, width, height, unrealActor=None, label=None, unrealPath=None):
        """Init's SphereItem"""
        super().__init__(x, y, width, height, unrealActor, label, unrealPath)
        if unrealActor:
                # if an asset is passed in, that means we are copying
                self.unrealActor = self.UEL.copyActor(unrealActor, self.actorLabel)
                self.unrealActor.set_actor_location(unreal.Vector(x+(width/2), y+(height/2), 0), False, False)
        else:
            # set x and y to 12.5 since we are now using the center of the QRectF
            # and our grid starts at (0,0) in the top left
            # TODO: should just be the center of the rect not +12.5
            self.unrealActor = self.UEL.spawnActor('circle', x+(width/2), y+(height/2), self.actorLabel)
        
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
        self.gridWidth = 1200
        self.gridHeight = 600
        self.gridCreated = False
        self.UEL = UnrealLibrary()
        
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.scene.setSceneRect(0, 0, self.gridWidth, self.gridHeight)
        self.scene.selectionChanged.connect(self.changeUnrealSelection)
        
        self.canSpawnItemOnPress = True
        self.copiedItems = None
        self.step = None
        self.numItems = 0
        self.zoom = 0.5
        self.scale(self.zoom, self.zoom)
        
        self.createGrid(20, self.gridWidth, self.gridHeight)
        
    def createGrid(self, step=20, width=800, height=600, zoom = None):
        """Creates the grid in the graphics view and adds grid lines
        
        Args:
            step (int): The step for each grid line
            width (int): The width of the grid
            height (int): The height of the grid
        """
        if not zoom:
            zoom = self.zoom
        
        self.gridWidth = width / zoom
        self.gridHeight = height / zoom
        self.step = step
        
        # lines are light grey for now, can add a colorpicker if we want to add the flexibility
        lightGray = QColor(211, 211, 211)
        
        # TODO: Give some flexibility to the grid - for example maybe just lines at the end as an option
        
        # make this `+ 1` so that we add a line to the edges
        for x in range(0, int(self.gridWidth) + 1, step):
            self.scene.addLine(x, 0, x, int(self.gridHeight), QPen(lightGray))
        for y in range(0, int(self.gridHeight) + 1, step):
            self.scene.addLine(0, y, int(self.gridWidth), y, QPen(lightGray))
        
        # this "grid" does not actually create a grid, but rather sets the lines for an area
        # and establishes boundaries for that area
        # we store gridWidth and gridHeight so that we can set the boundary for an item when we create it
        self.gridCreated = True
        
        self.scene.setSceneRect(0, 0, self.gridWidth, self.gridHeight)
        
    def addItem(self, shape='square', width=15, height=15, x=0, y=0, assetPath=None):
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
        label = "BlockoutActor{}".format(self.numItems) if self.numItems > 0 else "BlockoutActor"
        if self.gridCreated: # only add the item if the grid has been created
            if shape == 'circle':
                asset = SphereItem(x, y, width, height, None, label, assetPath)
            else:
                asset = SquareItem(x, y, width, height, None, label, assetPath)
            
            self.scene.addItem(asset)
            self.numItems += 1
    
            return asset
        else:
            # we don't necessarily need a grid to add an item, but if this were to happen then boundaries could not be set
            # so we'll just print rather than raising an exception
            print("Must create a grid before adding assets")
            return
    
    def keyPressEvent(self, event):
        """ Handles key press hot keys and also calls the parent keyPressEvent()
        
        Hotkeys:
            Quick spawning (F): Creates a cube item at the given mouse location
            Copy Items (ctrl+c): Copies the selected items and stores them in self.copiedItems
            Paste Items (ctrl+v): Pastes the selected items at the cursors location
                - NOTE: Pasting multiple items will put them all at the cursor location
                    In the future we can make the pasting be an offset, so that we keep the shape of the multi-copy
        """
        # quick spawn items (cubes for now, allow to be set by the user later)
        if self.canSpawnItemOnPress and event.key() == Qt.Key_F:
            cursorPos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            self.addItem('square', 25, 25, cursorPos.x(), cursorPos.y())
            self.canSpawnItemOnPress = False
            
        # copy selected items
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            if self.scene.selectedItems():
                self.copiedItems = self.scene.selectedItems()
        
        # paste selected items
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            self.pasteItems(self.copiedItems)
        super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
        """ Handles key releasing so that quick spawn cant be held down + calls keyReleaseEvent()"""
        if event.key() == Qt.Key_F:
            self.canSpawnItemOnPress = True
        super().keyReleaseEvent(event)
        
    def pasteItems(self, items):
        """ Pastes the items into the gridview at the mouse cursor's position
        
        Args:
            items (list): List of items to paste into the view
            
        """
        if not items:
            return
        
        for item in items:
            width = item.width
            height = item.height
            cursorPos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
            unrealActor = item.unrealActor
            if isinstance(item, SphereItem):
                asset = SphereItem(cursorPos.x(), cursorPos.y(), width, height, unrealActor, self.chosenAssetPath)
                self.scene.addItem(asset)
            else:
                asset = SquareItem(cursorPos.x(), cursorPos.y(), width, height, unrealActor, self.chosenAssetPath)
                self.scene.addItem(asset)
                
    def changeUnrealSelection(self):
        """Reflects the selection change of the GridGraphicsView and selects those Unreal Engine counterparts"""
        unrealActors = []
        
        for item in self.scene.selectedItems():
            unrealActors.append(item.unrealActor)
            
        self.UEL.selectActors(unrealActors)
        
    def clearSceneLines(self):
        """Clears all the lines in the grid by deleting the QGraphicsLineItems"""
        for item in self.scene.items():
            if isinstance(item, QGraphicsLineItem):
                self.scene.removeItem(item)
    
    def updateViewScale(self, newZoom):
        """Updates the scale of the GridGraphicsView based on the new zoom
        
        Args:
            newZoom (float): The new zoom for the grid
        """
        # before implementing the new zoom, we must first revert the old zoom
        # this is especially needed for scale(), as there is no base scale stored
        # so applying a new zoom scale without reverting would scale onto the zoomed scale, which quickly breaks everything
        self.gridWidth = self.gridWidth * self.zoom
        self.gridHeight = self.gridHeight * self.zoom
        self.scale(1/self.zoom, 1/self.zoom)
        
        # now update to the new zoom
        self.zoom = newZoom
        self.scale(newZoom, newZoom)
        self.clearSceneLines()
        self.createGrid(self.step, self.gridWidth, self.gridHeight)
        
         