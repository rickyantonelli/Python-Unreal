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
        self.zoomSlider.setMinimum(1)
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
        self.zSlider = ZSlider()
        self.zSlider.valueChanged.connect(self.zSliderUpdate)
        self.zSlider.setMinimum(1)
        self.zSlider.setMaximum(1000)
        self.zSlider.setValue(25)
        self.zSlider.setTickInterval(1000)
        self.zSlider.setSingleStep(1)
        
        # simple QLineEdit next to the slider to indicate the value
        self.zValue = QLineEdit()
        self.zValue.setText(str(self.zSlider.value()/100))
        self.zValue.setFixedWidth(50)
        self.zValue.setAlignment(Qt.AlignCenter)
        self.zValue.returnPressed.connect(self.zValueUpdate)
        zSliderValidator = QIntValidator(self.zSlider.minimum(), self.zSlider.maximum())
        self.zValue.setValidator(zSliderValidator)
        
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
        self.zSliderLayout.addWidget(self.zSlider)
        self.zSliderLayout.addWidget(self.zValue)
        
        self.vertLayout = QVBoxLayout(self)
        self.vertLayout.addLayout(self.zoomSliderLayout)
        self.vertLayout.addLayout(self.nameLayout)
        self.vertLayout.addLayout(self.zSliderLayout)
        
        self.setLayout(self.vertLayout)
        
    def zSliderUpdate(self):
        """Updates the Unreal Engine z-scale for the selected items and the QLineEdit that displays the value of the zSlider
        Since this is a 2D grid, the z-axis is obviously not a factor. But we want to give the user the ability to very losely set the z-height
        
        """
        if self.gridView.scene.selectedItems():
            for item in self.gridView.scene.selectedItems():
                selectedItemAsset = item.unrealActor
                selectedItemAsset.set_actor_scale3d(unreal.Vector(selectedItemAsset.get_actor_scale3d().x, selectedItemAsset.get_actor_scale3d().y, self.zSlider.value()/100))
                self.zValue.setText(str(self.zSlider.value()/100))
            
    def zoomSliderUpdate(self):
        """Updates the grid zoom and the QLineEdit that displays the value of the zoomSlider"""
        self.gridView.updateViewScale(self.zoomSlider.value()/100)
        self.zoomValue.setText(str(self.zoomSlider.value()/100))
            
    def zValueUpdate(self):
        """Updates the zSlider when the zValue is updated with a validated amount"""
        self.zSlider.setValue(int(self.zValue.text())*100)
        
    def zoomSliderValueUpdate(self):
        """Updates the zoomSlider when the zoomValue is updated with a validated amount"""
        self.zoomSlider.setValue(int(self.zoomValue.text())*100)
    
    def updateInfo(self):
        """Updates the widget based on the selected item"""
        if self.gridView and self.gridView.scene.selectedItems():
            if len(self.gridView.scene.selectedItems()) > 1:
                # if we have more than one item selected, set some base values
                # we want to keep these around though because we allow for z-scale updates with multi-select
                self.zSlider.setValue(100)
                self.nameLineEdit.setText("Multiple items selected")
            else:
                selectedItem = self.gridView.scene.selectedItems()[0]
                selectedName = selectedItem.unrealActor.get_actor_label()
                self.zSlider.setValue(selectedItem.unrealActor.get_actor_scale3d().z*100)
                self.nameLineEdit.setText(selectedName)    
    
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
         