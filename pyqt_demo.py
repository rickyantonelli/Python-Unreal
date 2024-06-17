from PySide6.QtWidgets import *
import unreal

def main():
    app = QApplication([])
    window = QWidget()
    
    label = QLabel(window)
    label.setText("Wassup")
    
    window.show()
    app.exec()

if __name__ == '__main__':
    main()