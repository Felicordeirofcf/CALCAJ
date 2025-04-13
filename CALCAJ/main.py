import sys
from PySide6.QtWidgets import QApplication
from ui_mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("MinhaEmpresa")
    app.setApplicationName("CalculadoraJudicial")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
