import unreal
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QThread

import graphicview   
import unreallibrary
        
class GridWidget(QWidget):
    """A QWidget to display a 2D grid that reflects items into the 3D space of the current Unreal Engine map"""
    def __init__(self):
        super().__init__()
        self.view = graphicview.GridGraphicsView()
        self.UEL = unreallibrary.UnrealLibrary()
        
        self.addCubeButton = QPushButton("Add Cube")
        self.addSphereButton = QPushButton("Add Sphere")
        
        self.vertLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()
        self.vertLayout.addWidget(self.view)
        self.buttonLayout.addWidget(self.addCubeButton)
        self.buttonLayout.addWidget(self.addSphereButton)
        self.vertLayout.addLayout(self.buttonLayout)
        self.setLayout(self.vertLayout)
        
        self.addCubeButton.pressed.connect(lambda: self.addItem('square'))
        self.addSphereButton.pressed.connect(lambda: self.addItem('circle'))
        
    def addItem(self, itemShape='square'):
        """Adds an item to the grid (square or circle), and an Unreal Engine asset (cube or sphere)
        
        Args:
            itemShape (str): The shape that we want to pass in
        """
        item = self.view.addItem(itemShape, 0, 0, 25, 25)
        unrealActor = self.UEL.spawnActor(itemShape, x=0, y=0)
        item.unrealAsset = unrealActor


# TODO: Normally we would use if __name__ == '__main__':
# but this blocks the widget from running in Unreal, for now we'll leave it out
app = None
if not QApplication.instance():
    app = QApplication(sys.argv)
gridWidget = GridWidget()
gridWidget.view.createGrid(20, 1600, 600)
gridWidget.show()

# parent widget to unreal
unreal.parent_external_window_to_slate(gridWidget.winId())