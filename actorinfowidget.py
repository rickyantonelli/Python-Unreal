import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint, QRect
from PySide6.QtGui import QPen, QPainter, QFont, QIntValidator
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QSlider, QStyle

class InfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.nameLabel = QLineEdit()
        self.thumbnailLabel = QLabel()
        
        self.gridView = None
        
        # set up a slider that updates the z scale (which we dont see in the 2D view)
        self.zScaleSlider = ZSlider()
        self.zScaleSlider.valueChanged.connect(self.zScaleSliderUpdate)
        
        # simple QLineEdit next to the slider to indicate the value
        self.zSliderValue = QLineEdit()
        self.zSliderValue.setText(str(self.zScaleSlider.value()/100))
        self.zSliderValue.setFixedWidth(50)
        self.zSliderValue.setAlignment(Qt.AlignCenter)
        self.zSliderValue.returnPressed.connect(self.zSliderValueUpdate)
        
        validator = QIntValidator(self.zScaleSlider.minimum(), self.zScaleSlider.maximum())
        self.zSliderValue.setValidator(validator)
        
        self.vertLayout = QVBoxLayout(self)
        self.vertLayout.addWidget(self.nameLabel)
        
        
        self.sliderLayout = QHBoxLayout()
        self.sliderLayout.addWidget(self.zScaleSlider)
        self.sliderLayout.addWidget(self.zSliderValue)
        
        self.vertLayout.addLayout(self.sliderLayout)
        
        self.setLayout(self.vertLayout)
        
    def zScaleSliderUpdate(self):
        if self.gridView and self.gridView.scene.selectedItems():
            selectedItemAsset = self.gridView.scene.selectedItems()[0].unrealAsset
            selectedItemAsset.set_actor_scale3d(unreal.Vector(selectedItemAsset.get_actor_scale3d().x, selectedItemAsset.get_actor_scale3d().y, self.zScaleSlider.value()/100))
            self.zSliderValue.setText(str(self.zScaleSlider.value()/100))
            
    def zSliderValueUpdate(self):
        self.zScaleSlider.setValue(int(self.zSliderValue.text())*100)
    
    def updateInfo(self):
        print("updating")
        if self.gridView and self.gridView.scene.selectedItems():
            selectedItem = self.gridView.scene.selectedItems()[0]
            selectedName = selectedItem.unrealAsset.get_actor_label()
            self.zScaleSlider.setValue(selectedItem.unrealAsset.get_actor_scale3d().z*100)
            self.nameLabel.setText(selectedName)
        
    # TODO: Widget that displays info on the selected item
    # Name (changeable) and that's it for now
    # It seems that a lot of thumbnail generation is deprecated with Unreal's API, so we'll leave it out for now
    
    
class ZSlider(QSlider):
    def __init__(self):
        super().__init__()
        
        self.setOrientation(Qt.Horizontal)
        self.setMinimum(1)
        self.setMaximum(1000)
        self.setValue(25)
        self.setTickInterval(1000)
        self.setSingleStep(1)
        
        # overriding the stylesheet in unreal_stylesheet
        self.setStyleSheet("""
            QSlider {
            border: 1px solid #353535;
            border-radius: 3px; }
            QSlider:horizontal {
                height: 18px; }
            QSlider:vertical {
                width: 18px; }
            QSlider::groove {
                border: 1px solid #151515;
                background: #151515;
                border-radius: 3px; }
                QSlider::groove:horizontal {
                height: 16px; }
                QSlider::groove:vertical {
                width: 16px; }
            QSlider::handle {
                background: #353535;
                border-radius: 3px; }
                QSlider::handle:hover {
                background: #575757; }
                QSlider::handle:horizontal {
                width: 20px; }
                QSlider::handle:vertical {
                height: 30px; }
        """)
         