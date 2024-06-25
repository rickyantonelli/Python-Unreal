import unreal
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout

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
        item = self.view.addAsset('square', 0, 0, 15, 15)
        unrealActor = self.UEL.spawnActor()
        item.unrealAsset = unrealActor
        
    def addSphere(self):
        self.view.addAsset('circle', 20, 20, 15, 15)

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = QMainWindow()
    window.setWindowTitle("Unreal Blockout Widget")
    gridWidget = GridWidget()
    window.setCentralWidget(gridWidget)
    
    gridWidget.view.createGrid(20, 800, 600)
    
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()