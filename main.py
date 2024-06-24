from PyQt6.QtWidgets import *
import qgraphicsview   

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D Grid")
        self.setGeometry(100, 100, 800, 600)
        self.view = qgraphicsview.GridGraphicsView()
        self.setCentralWidget(self.view)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.view.createGrid(20, 800, 600)
    window.view.addAsset(0, 0, 15, 15)
    window.view.addAsset(20, 20, 15, 15)
    
    window.show()
    sys.exit(app.exec())