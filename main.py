import unreal
import sys
import unreal_stylesheet

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog
from PySide6.QtCore import Qt

from actorinfowidget import InfoWidget
from graphicview import GridGraphicsView
from unreallibrary import UnrealLibrary
from assetpickerwidget import AssetPicker
        
class GridWidget(QWidget):
    """A QWidget to display a 2D grid that reflects items into the 3D space of the current Unreal Engine map"""
    def __init__(self):
        super().__init__()
        self.view = GridGraphicsView()
        self.UEL = UnrealLibrary()
        
        self.assetPath = None
        
        self.addCubeButton = QPushButton("Add Cube")
        self.addSphereButton = QPushButton("Add Sphere")
        self.assetPickerWidget = AssetPicker(self.view)
        self.infoWidget = InfoWidget(self.view)
        self.infoWidget.gridView = self.view
        self.view.scene.selectionChanged.connect(self.infoWidget.updateInfo)
        
        self.mainLayout = QHBoxLayout(self)
        
        self.vertLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.rightLayout = QVBoxLayout()
        
        self.vertLayout.addWidget(self.view)
        self.buttonLayout.addWidget(self.addCubeButton)
        self.buttonLayout.addWidget(self.addSphereButton)
        self.vertLayout.addLayout(self.buttonLayout)
        self.rightLayout.addWidget(self.infoWidget)
        self.rightLayout.addWidget(self.assetPickerWidget)
        
        self.mainLayout.addLayout(self.vertLayout)
        self.mainLayout.addLayout(self.rightLayout)
        self.mainLayout.setStretch(0, 4)
        self.mainLayout.setStretch(1, 1)
        self.setLayout(self.mainLayout)
        
        self.addCubeButton.pressed.connect(lambda x = 'square': self.addItem(x))
        self.addSphereButton.pressed.connect(lambda x = 'circle':self.addItem(x))
        
        
        self.resize(1540, 660)
        
    def resizeEvent(self, event):
        print(self.size())
        super().resizeEvent(event)
        
    def addItem(self, itemShape='square'):
        """Adds an item to the grid (square or circle), and an Unreal Engine asset (cube or sphere)
        
        Args:
            itemShape (str): The shape that we want to pass in
        """
        self.view.addItem(itemShape, 25, 25)

# TODO: Normally we would use if __name__ == '__main__':
# but this blocks the widget from running in Unreal, for now we'll leave it out
app = None
if not QApplication.instance():
    app = QApplication(sys.argv)

# applies a qt stylesheet to make widgets look native to Unreal
# https://github.com/leixingyu/unrealStylesheet
unreal_stylesheet.setup()

gridWidget = GridWidget()
gridWidget.setWindowTitle("QuickBlock")
gridWidget.show()

# parent widget to unreal
unreal.parent_external_window_to_slate(gridWidget.winId())