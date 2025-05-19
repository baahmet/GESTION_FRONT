# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui.login_widget import LoginWidget
from ui.code2fa_widget import Code2FAWidget
from ui.dashboard_widget import DashboardWidget

class MainApp(QMainWindow):
    """
    Fenêtre principale de l'application.
    Utilise un QStackedWidget pour gérer les vues de façon fluide et sans fenêtres multiples.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Budgétaire - UFR SET")
        self.resize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5faff;
            }
        """)

        # Stack central contenant toutes les vues principales
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Initialisation des widgets (vues)
        self.login_widget = LoginWidget(self)
        self.code2fa_widget = Code2FAWidget(self)
        self.dashboard_widget = DashboardWidget(self)

        # Ajout des widgets dans la pile
        self.stack.addWidget(self.login_widget)        # index 0
        self.stack.addWidget(self.code2fa_widget)      # index 1
        self.stack.addWidget(self.dashboard_widget)    # index 2

        # Lancement sur la page de connexion
        self.stack.setCurrentIndex(0)

    def navigate_to(self, index):
        """
        Méthode pour changer de vue via l'index dans la pile
        """
        self.stack.setCurrentIndex(index)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
