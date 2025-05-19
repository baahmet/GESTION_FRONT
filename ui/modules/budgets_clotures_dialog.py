from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFont
from services.budget_service import get_budgets


class BudgetsCloturesDialog(QDialog):
    """
    Dialogue affichant les budgets clôturés avec un design moderne
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_budgets()

    def setup_ui(self):
        self.setWindowTitle("📂 Archives des Budgets Clôturés")
        self.setMinimumSize(800, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("ARCHIVES DES BUDGETS CLÔTURÉS")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 10px;
                border-bottom: 2px solid #7f8c8d;
            }
        """)
        layout.addWidget(header)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Exercice", "Montant total", "Disponible", "Utilisé", "Date clôture"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                gridline-color: #ecf0f1;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        # Configuration
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addWidget(self.table)

        # Footer
        footer = QLabel("Les budgets clôturés sont en lecture seule")
        footer.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-style: italic;
                font-size: 12px;
            }
        """)
        layout.addWidget(footer, alignment=Qt.AlignRight)

    def load_budgets(self):
        """Charge et affiche les budgets clôturés avec mise en forme"""
        result = get_budgets()
        if result["success"]:
            budgets = [b for b in result["data"] if b["statut"] == "cloture"]
            self.table.setRowCount(len(budgets))

            for row, budget in enumerate(budgets):
                # Exercice
                self.table.setItem(row, 0, QTableWidgetItem(budget["exercice"]))

                # Montant total (formaté)
                total_item = QTableWidgetItem(f"{budget['montant_total']:,.0f} F")
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 1, total_item)

                # Montant disponible
                dispo = budget['montant_disponible']
                dispo_item = QTableWidgetItem(f"{dispo:,.0f} F")
                dispo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(row, 2, dispo_item)

                # Montant utilisé (calculé)
                utilise = budget['montant_total'] - dispo
                utilise_item = QTableWidgetItem(f"{utilise:,.0f} F")
                utilise_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                # Couleur selon l'utilisation
                if dispo == 0:
                    utilise_item.setForeground(QBrush(QColor("#e74c3c")))  # Rouge si tout utilisé
                elif dispo / budget['montant_total'] > 0.5:
                    utilise_item.setForeground(QBrush(QColor("#f39c12")))  # Orange si >50% restant
                else:
                    utilise_item.setForeground(QBrush(QColor("#27ae60")))  # Vert sinon

                self.table.setItem(row, 3, utilise_item)

                # Date
                date_item = QTableWidgetItem(budget["date_creation"].split("T")[0])
                self.table.setItem(row, 4, date_item)

                # Alternance des couleurs de ligne
                if row % 2 == 0:
                    for col in range(self.table.columnCount()):
                        if self.table.item(row, col):
                            self.table.item(row, col).setBackground(QColor("#f8f9fa"))