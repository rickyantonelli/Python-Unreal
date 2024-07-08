import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QSlider

class InfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.nameLabel = QLineEdit()
        self.thumbnailLabel = QLabel()
        
        self.gridView = None
        # if self.gridView:
        #     self.gridView.scene.selectionChanged(self.updateInfo)
        
        self.zScaleSlider = QSlider(Qt.Horizontal)
        self.zScaleSlider.setRange(0.01, 10)
        self.zScaleSlider.setValue(1)
        
        self.zScaleSlider.valueChanged.connect(self.zScaleSliderUpdate)
        
        self.vertLayout = QVBoxLayout(self)
        self.vertLayout.addWidget(self.nameLabel)
        self.vertLayout.addWidget(self.zScaleSlider)
        self.setLayout(self.vertLayout)
        
    
    def zScaleSliderUpdate(self):
        if self.gridView and self.gridView.scene.selectedItems():
            selectedItemAsset = self.gridView.scene.selectedItems()[0].unrealAsset
            selectedItemAsset.set_actor_scale3d(unreal.Vector(selectedItemAsset.get_actor_scale3d().x, selectedItemAsset.get_actor_scale3d().y, self.zScaleSlider.value()))
        
    
    def updateInfo(self):
        print("updating")
        if self.gridView and self.gridView.scene.selectedItems():
            selectedItem = self.gridView.scene.selectedItems()[0]
            selectedName = selectedItem.unrealAsset.get_actor_label()
            self.zScaleSlider.setValue(selectedItem.unrealAsset.get_actor_scale3d().z)
            self.nameLabel.setText(selectedName)
        
    # TODO: Widget that displays info on the selected item
    # Name (changeable) and that's it for now
    # It seems that a lot of thumbnail generation is deprecated with Unreal's API, so we'll leave it out for now