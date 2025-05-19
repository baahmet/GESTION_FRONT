from PyQt5.QtWidgets import QWidget, QVBoxLayout
from ui.main_layout import MainLayout

class DashboardWidget(QWidget):
    """
    Ce widget charge le MainLayout après connexion.
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Charger le MainLayout en lui passant la référence du main_window (pour déconnexion)
        self.main_layout = MainLayout(self.main_window)
        layout.addWidget(self.main_layout)

        self.setLayout(layout)
