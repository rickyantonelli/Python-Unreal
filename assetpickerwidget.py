import unreal
import unreallibrary
from PySide6.QtCore import Qt, QPointF, QRectF, QPoint, QRect
from PySide6.QtGui import QPen, QPainter, QFont, QIntValidator
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QLineEdit

from unreallibrary import UnrealLibrary

class AssetPicker(QWidget):
    def __init__(self, gridView):
        """ Init's UnrealLibrary and initializes the necessary libraries"""
        super().__init__()
        self.UEL = UnrealLibrary()
        self.assetPath = None
        self.unrealAsset = None
        self.gridView = gridView
        
        self.assetPickerButton = QPushButton("Pick Asset")
        self.spawnAssetButton = QPushButton("Spawn Asset")
        self.spawnAssetButton.setDisabled(True)
        
        self.assetLineEdit = QLineEdit()
        self.assetLineEdit.setDisabled(True)
        self.assetLineEdit.setReadOnly(True)
        
        self.assetPickerButton.pressed.connect(self.pickAsset)
        self.spawnAssetButton.pressed.connect(self.spawnActor)
        
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.assetLineEdit)
        self.mainLayout.addWidget(self.assetPickerButton)
        self.mainLayout.addWidget(self.spawnAssetButton)
        
    def pickAsset(self):
        contentDir = self.UEL.EUL.get_current_content_browser_path()
        
        dialog = QFileDialog(self, "Content Browser", contentDir)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.Detail)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        
        if dialog.exec() == QFileDialog.Accepted:
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.assetPath = selected_files[0].split("Content/")[1]
                
                self.spawnAssetButton.setEnabled(True)
                self.assetLineEdit.setEnabled(True)
                assetName = self.assetPath.split("/")[-1].split(".")[0]
                self.assetLineEdit.setText(assetName)
                
    def spawnActor(self):
        # self.gridView.addItem(assetPath=self.assetPath)
        pass
                
            