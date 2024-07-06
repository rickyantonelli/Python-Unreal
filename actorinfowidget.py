import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit

class InfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.nameLabel = QLineEdit()
        self.thumbnailLabel = QLabel()
        
        self.vertLayout = QVBoxLayout(self)
        self.vertLayout.addWidget(self.nameLabel)
        self.setLayout(self.vertLayout)
        
        self.gridView = None
        # if self.gridView:
        #     self.gridView.scene.selectionChanged(self.updateInfo)
        
    def updateInfo(self):
        print("updating")
        if self.gridView and self.gridView.scene.selectedItems():
            selectedItem = self.gridView.scene.selectedItems()[0]
            selectedName = selectedItem.unrealAsset.get_actor_label()
            self.nameLabel.setText(selectedName)
        
    # TODO: Widget that displays info on the selected item
    # Name (changeable) and that's it for now
    # It seems that a lot of thumbnail generation is deprecated with Unreal's API, so we'll leave it out for now