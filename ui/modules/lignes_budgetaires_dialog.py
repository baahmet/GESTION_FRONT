from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QBrush
from services.ligne_budgetaire_service import get_lignes_by_budget, create_ligne_budgetaire


class LigneBudgetaireDialog(QDialog):
    def __init__(self, budget, parent=None):
        super().__init__(parent)
        self.budget = budget
        self.setup_ui()
        self.load_lignes()

    def setup_ui(self):
        self.setWindowTitle(f"Lignes budgétaires - {self.budget['exercice']}")
        self.setFixedSize(700, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel(f"LIGNES BUDGÉTAIRES - EXERCICE {self.budget['exercice']}")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }
        """)
        layout.addWidget(header)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Article, Montant, % du budget
        self.table.setHorizontalHeaderLabels(["Nom de la ligne", "Montant alloué", "% du budget"])
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

        # Configuration technique
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addWidget(self.table)

        # Bouton Ajouter
        add_btn = QPushButton("➕ Ajouter une ligne budgétaire")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                font-weight: 500;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        add_btn.clicked.connect(self.ajouter_ligne)
        layout.addWidget(add_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def load_lignes(self):
        result = get_lignes_by_budget(self.budget['id'])
        if result['success']:
            lignes = result['data']
            self.table.setRowCount(len(lignes))

            total = sum(l['montant_alloue'] for l in lignes)

            for i, ligne in enumerate(lignes):
                # Article
                self.table.setItem(i, 0, QTableWidgetItem(ligne['article']))

                # Montant (formaté et aligné à droite)
                montant_item = QTableWidgetItem(f"{ligne['montant_alloue']:,.2f} F")
                montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(i, 1, montant_item)

                # Pourcentage du budget total
                if total > 0:
                    percent = (ligne['montant_alloue'] / total) * 100
                    percent_item = QTableWidgetItem(f"{percent:.1f}%")
                    percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                    # Couleur en fonction du pourcentage
                    if percent > 30:
                        percent_item.setForeground(QBrush(QColor("#e74c3c")))
                    elif percent > 15:
                        percent_item.setForeground(QBrush(QColor("#f39c12")))
                    else:
                        percent_item.setForeground(QBrush(QColor("#27ae60")))

                    self.table.setItem(i, 2, percent_item)

                # Alternance des couleurs de ligne
                if i % 2 == 0:
                    for j in range(self.table.columnCount()):
                        if self.table.item(i, j):
                            self.table.item(i, j).setBackground(QColor("#f8f9fa"))
                        else:
                            self.show_error("Erreur", result['message'])

    def ajouter_ligne(self):
        # Boîte de dialogue pour l'article
        article, ok = QInputDialog.getText(
            self,
            "Nouvelle ligne budgétaire",
            "Nom de l'article :",
            text="Nouvel article"
        )
        if not ok or not article.strip():
            return

        # Boîte de dialogue pour le montant
        montant, ok = QInputDialog.getDouble(
            self,
            "Montant alloué",
            f"Montant alloué pour '{article}' :",
            value=1000.00,
            min=0.01,
            max=self.budget['montant_disponible'],
            decimals=2
        )
        if not ok:
            return

        data = {
            "article": article.strip(),
            "montant_alloue": montant,
            "budget": self.budget['id']
        }

        result = create_ligne_budgetaire(data, budget_disponible=self.budget['montant_disponible'])

        if result['success']:
            self.load_lignes()
        else:
            self.show_error("Erreur", result['message'])

    def show_error(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #e74c3c;
            }
        """)
        msg.exec_()