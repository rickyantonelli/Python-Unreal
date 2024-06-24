from PyQt6.QtWidgets import *
import graphicview   
        
class GridWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.view = graphicview.GridGraphicsView()
        
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
        print('adding cube')
        self.view.addAsset('square', 0, 0, 15, 15)
        
    def addSphere(self):
        gridWidget.view.addAsset('circle', 20, 20, 15, 15)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Unreal Blockout Widget")
    gridWidget = GridWidget()
    window.setCentralWidget(gridWidget)
    
    gridWidget.view.createGrid(20, 800, 600)
    gridWidget.view.addAsset('square', 0, 0, 15, 15)
    gridWidget.view.addAsset('circle', 20, 20, 15, 15)
    
    window.show()
    sys.exit(app.exec())