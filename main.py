import unreal
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QThread

import graphicview   
import unreallibrary
        
class GridWidget(QWidget):
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
        
        self.addCubeButton.pressed.connect(self.addCube)
        self.addSphereButton.pressed.connect(self.addSphere)
        
    def addCube(self):
        item = self.view.addAsset('square', 0, 0, 25, 25)
        unrealActor = self.UEL.spawnActor('cube')
        item.unrealAsset = unrealActor
        
    def addSphere(self):
        item = self.view.addAsset('circle', 0, 0, 25, 25)
        unrealActor = self.UEL.spawnActor('sphere')
        item.unrealAsset = unrealActor


# TODO: Normally we would use if __name__ == '__main__':
# but this blocks the widget from running in Unreal, for now we'll leave it out
app = None
if not QApplication.instance():
    app = QApplication(sys.argv)
gridWidget = GridWidget()
gridWidget.view.createGrid(20, 800, 600)
gridWidget.show()
unreal.parent_external_window_to_slate(gridWidget.winId())