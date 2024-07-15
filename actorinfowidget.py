import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint, QRect
from PySide6.QtGui import QPen, QPainter, QFont, QIntValidator
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QSlider, QStyle

class InfoWidget(QWidget):
    def __init__(self, gridView):
        super().__init__()
        self.nameLabel = QLabel("Name:")
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setReadOnly(True)

        self.gridView = gridView
        
        # set up a slider that updates the z scale (which we dont see in the 2D view)
        self.zoomSlider = ZSlider()
        self.zoomSlider.setMinimum(0)
        self.zoomSlider.setMaximum(200)
        self.zoomSlider.setValue(self.gridView.zoom * 100)
        self.zoomSlider.setTickInterval(100)
        self.zoomSlider.setSingleStep(1)
        self.zoomSlider.valueChanged.connect(self.zoomSliderUpdate)
        
        # simple QLineEdit next to the slider to indicate the value
        self.zoomValue = QLineEdit()
        self.zoomValue.setText(str(self.zoomSlider.value()/100))
        self.zoomValue.setFixedWidth(50)
        self.zoomValue.setAlignment(Qt.AlignCenter)
        self.zoomValue.returnPressed.connect(self.zoomSliderValueUpdate)
        zoomSliderValidator = QIntValidator(self.zoomSlider.minimum(), self.zoomSlider.maximum())
        self.zoomValue.setValidator(zoomSliderValidator)
        
        
        # set up a slider that updates the z scale (which we dont see in the 2D view)
        self.zScaleSlider = ZSlider()
        self.zScaleSlider.valueChanged.connect(self.zScaleSliderUpdate)
        self.zScaleSlider.setMinimum(1)
        self.zScaleSlider.setMaximum(1000)
        self.zScaleSlider.setValue(25)
        self.zScaleSlider.setTickInterval(1000)
        self.zScaleSlider.setSingleStep(1)
        
        # simple QLineEdit next to the slider to indicate the value
        self.zSliderValue = QLineEdit()
        self.zSliderValue.setText(str(self.zScaleSlider.value()/100))
        self.zSliderValue.setFixedWidth(50)
        self.zSliderValue.setAlignment(Qt.AlignCenter)
        self.zSliderValue.returnPressed.connect(self.zSliderValueUpdate)
        zSliderValidator = QIntValidator(self.zScaleSlider.minimum(), self.zScaleSlider.maximum())
        self.zSliderValue.setValidator(zSliderValidator)
        
        self.zoomSliderLayout = QHBoxLayout()
        self.zoomSliderLabel = QLabel("Grid Zoom:")
        self.zoomSliderLayout.addWidget(self.zoomSliderLabel)
        self.zoomSliderLayout.addWidget(self.zoomSlider)
        self.zoomSliderLayout.addWidget(self.zoomValue)
        
        self.nameLayout = QHBoxLayout()
        self.nameLayout.addWidget(self.nameLabel)
        self.nameLayout.addWidget(self.nameLineEdit)
              
        self.zSliderLayout = QHBoxLayout()
        self.zSliderLabel = QLabel("Z-Scale:")
        self.zSliderLayout.addWidget(self.zSliderLabel)
        self.zSliderLayout.addWidget(self.zScaleSlider)
        self.zSliderLayout.addWidget(self.zSliderValue)
        
        self.vertLayout = QVBoxLayout(self)
        self.vertLayout.addLayout(self.zoomSliderLayout)
        self.vertLayout.addLayout(self.nameLayout)
        self.vertLayout.addLayout(self.zSliderLayout)
        
        self.setLayout(self.vertLayout)
        
    def zScaleSliderUpdate(self):
        if self.gridView.scene.selectedItems():
            selectedItemAsset = self.gridView.scene.selectedItems()[0].unrealActor
            selectedItemAsset.set_actor_scale3d(unreal.Vector(selectedItemAsset.get_actor_scale3d().x, selectedItemAsset.get_actor_scale3d().y, self.zScaleSlider.value()/100))
            self.zSliderValue.setText(str(self.zScaleSlider.value()/100))
            
    def zoomSliderUpdate(self):
        self.gridView.updateViewScale(self.zoomSlider.value()/100)
        self.zoomValue.setText(str(self.zoomSlider.value()/100))
            
    def zSliderValueUpdate(self):
        self.zScaleSlider.setValue(int(self.zSliderValue.text())*100)
        
    def zoomSliderValueUpdate(self):
        self.zoomSlider.setValue(int(self.zoomValue.text())*100)
    
    def updateInfo(self):
        print("updating")
        if self.gridView and self.gridView.scene.selectedItems():
            selectedItem = self.gridView.scene.selectedItems()[0]
            selectedName = selectedItem.unrealActor.get_actor_label()
            self.zScaleSlider.setValue(selectedItem.unrealActor.get_actor_scale3d().z*100)
            self.nameLineEdit.setText(selectedName)
        
    # TODO: Widget that displays info on the selected item
    # Name (changeable) and that's it for now
    # It seems that a lot of thumbnail generation is deprecated with Unreal's API, so we'll leave it out for now
    
    
class ZSlider(QSlider):
    def __init__(self):
        super().__init__()
        
        self.setOrientation(Qt.Horizontal)
        
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
                width: 15px; }
                QSlider::handle:vertical {
                height: 30px; }
        """)
         