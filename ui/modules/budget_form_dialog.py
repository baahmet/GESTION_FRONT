from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFormLayout, QMessageBox, QDoubleSpinBox, QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIntValidator
from services.budget_service import create_budget
from services.auth_service import AuthService
from datetime import datetime


class BudgetFormDialog(QDialog):
    """
    Formulaire moderne pour la création d'un nouveau budget
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("➕ Nouveau Budget")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("CRÉATION D'UN NOUVEAU BUDGET")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #0078d7;
                padding-bottom: 5px;
                border-bottom: 2px solid #0078d7;
            }
        """)
        layout.addWidget(header)

        # Formulaire
        form = QFormLayout()
        form.setVerticalSpacing(15)
        form.setHorizontalSpacing(10)

        # Champ Exercice
        current_year = datetime.now().year
        self.exercice_input = QLineEdit(f"{current_year}-{current_year + 1}")
        self.exercice_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        form.addRow("Exercice budgétaire:", self.exercice_input)

        # Champ Montant
        self.montant_input = QDoubleSpinBox()
        self.montant_input.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.montant_input.setRange(1000, 1_000_000_000)
        self.montant_input.setPrefix("💰 ")
        self.montant_input.setSuffix(" FCFA")
        self.montant_input.setSingleStep(100000)
        self.montant_input.setValue(5000000)
        self.montant_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        form.addRow("Montant total:", self.montant_input)

        layout.addLayout(form)
        layout.addStretch()

        # Boutons
        btn_container = QFrame()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        save_btn.clicked.connect(self.submit)
        btn_layout.addWidget(save_btn)

        layout.addWidget(btn_container)

        self.setLayout(layout)

    def submit(self):
        exercice = self.exercice_input.text().strip()
        montant = self.montant_input.value()

        if not exercice:
            self.show_error("Champ requis", "L'exercice budgétaire est obligatoire")
            return

        if montant <= 0:
            self.show_error("Montant invalide", "Le montant doit être supérieur à zéro")
            return

        data = {
            "exercice": exercice,
            "montant_total": montant,
            "montant_disponible": montant,
            "comptable": AuthService.user_data.get("id")
        }

        result = create_budget(data)
        if result["success"]:
            self.show_success("Succès", result["message"])
            self.accept()
        else:
            self.show_error("Erreur", result["message"])

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

    def show_success(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #27ae60;
            }
        """)
        msg.exec_()