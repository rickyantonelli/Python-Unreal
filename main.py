import unreal
import sys
import unreal_stylesheet

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QThread, Qt

from actorinfowidget import InfoWidget
from graphicview import GridGraphicsView
from unreallibrary import UnrealLibrary
        
class GridWidget(QWidget):
    """A QWidget to display a 2D grid that reflects items into the 3D space of the current Unreal Engine map"""
    def __init__(self):
        super().__init__()
        self.view = GridGraphicsView()
        self.UEL = UnrealLibrary()
        
        self.addCubeButton = QPushButton("Add Cube")
        self.addSphereButton = QPushButton("Add Sphere")
        self.infoWidget = InfoWidget()
        self.infoWidget.gridView = self.view
        self.view.scene.selectionChanged.connect(self.infoWidget.updateInfo)
        
        self.mainLayout = QHBoxLayout(self)
        
        self.vertLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.vertLayout.addWidget(self.view)
        self.buttonLayout.addWidget(self.addCubeButton)
        self.buttonLayout.addWidget(self.addSphereButton)
        self.vertLayout.addLayout(self.buttonLayout)
        self.mainLayout.addLayout(self.vertLayout)
        self.mainLayout.addWidget(self.infoWidget)
        
        self.setLayout(self.mainLayout)
        self.mainLayout.setStretch(0, 4)
        self.mainLayout.setStretch(1, 1)
        
        self.addCubeButton.pressed.connect(lambda x = 'square': self.addItem(x))
        self.addSphereButton.pressed.connect(lambda x = 'circle':self.addItem(x))
        
    def addItem(self, itemShape='square'):
        """Adds an item to the grid (square or circle), and an Unreal Engine asset (cube or sphere)
        
        Args:
            itemShape (str): The shape that we want to pass in
        """
        self.view.addItem(itemShape, 25, 25)
        # unrealActor = self.UEL.spawnActor(itemShape, x=12.5, y=12.5)
        # item.unrealAsset = unrealActor


# TODO: Normally we would use if __name__ == '__main__':
# but this blocks the widget from running in Unreal, for now we'll leave it out
app = None
if not QApplication.instance():
    app = QApplication(sys.argv)

# applies a qt stylesheet to make widgets look native to Unreal
# https://github.com/leixingyu/unrealStylesheet
unreal_stylesheet.setup()

gridWidget = GridWidget()
gridWidget.view.createGrid(20, 1200, 600)
gridWidget.show()

# parent widget to unreal
unreal.parent_external_window_to_slate(gridWidget.winId())