from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
                             QDoubleSpinBox, QDateEdit, QTextEdit, QPushButton,
                             QFileDialog, QMessageBox, QLabel)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
import os

from services.budget_service import get_budgets
from services.demande_depense_service import get_demandes_depense
from services.depense_service import create_depense, update_depense
from services.ligne_budgetaire_service import get_lignes_by_budget


class DepenseFormDialog(QDialog):
    def __init__(self, parent=None, depense_data=None):
        super().__init__(parent)
        self.depense_data = depense_data
        self.justificatif_path = None
        self.setup_ui()
        self.load_initial_data()

    def setup_ui(self):
        self.setWindowTitle("📝 " + ("Modifier Dépense" if self.depense_data else "Nouvelle Dépense"))
        self.setFixedSize(500, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                padding: 8px;
                border-radius: 4px;
                min-width: 100px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Header
        header = QLabel("FORMULAIRE DE DÉPENSE")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #0078d7;
                padding-bottom: 5px;
                border-bottom: 2px solid #0078d7;
            }
        """)
        self.layout.addWidget(header)

        # Formulaire
        self.form_layout = QFormLayout()
        self.form_layout.setVerticalSpacing(15)
        self.form_layout.setHorizontalSpacing(10)

        self.setup_form_fields()
        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

        # Bouton Valider
        self.submit_btn = QPushButton("💾 Enregistrer")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.submit_btn.clicked.connect(self.submit)
        self.layout.addWidget(self.submit_btn)

    def setup_form_fields(self):
        # Ligne Budgétaire
        self.ligne_combo = QComboBox()
        self.ligne_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.form_layout.addRow("Ligne Budgétaire:", self.ligne_combo)

        # Demande liée
        self.demande_combo = QComboBox()
        self.demande_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.form_layout.addRow("Demande liée:", self.demande_combo)

        # Date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet("padding: 8px;")
        self.form_layout.addRow("Date:", self.date_input)

        # Type
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Ex: Achat fournitures")
        self.type_input.setStyleSheet("padding: 8px;")
        self.form_layout.addRow("Type:", self.type_input)

        # Catégorie
        self.categorie_input = QLineEdit()
        self.categorie_input.setPlaceholderText("Ex: Fonctionnement")
        self.categorie_input.setStyleSheet("padding: 8px;")
        self.form_layout.addRow("Catégorie:", self.categorie_input)

        # Montant
        self.montant_input = QDoubleSpinBox()
        self.montant_input.setPrefix("💰 ")
        self.montant_input.setSuffix(" FCFA")
        self.montant_input.setMaximum(1_000_000_000)
        self.montant_input.setStyleSheet("padding: 8px;")
        self.form_layout.addRow("Montant:", self.montant_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Détails de la dépense...")
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-height: 80px;
            }
        """)
        self.form_layout.addRow("Description:", self.description_input)

        # Justificatif
        self.justificatif_btn = QPushButton("📄 Sélectionner un justificatif")
        self.justificatif_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.justificatif_btn.clicked.connect(self.select_justificatif)
        self.form_layout.addRow("Justificatif:", self.justificatif_btn)

        self.justificatif_label = QLabel("Aucun fichier sélectionné")
        self.justificatif_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.form_layout.addRow("", self.justificatif_label)

    def load_initial_data(self):
        # Charger les budgets
        budgets = get_budgets().get("data", [])
        budget_en_cours = next((b for b in budgets if b.get("statut") == "en_cours"), None)

        if not budget_en_cours:
            self.show_error("Aucun budget actif", "Aucun budget en cours trouvé.")
            self.reject()
            return

        self.budget_id = budget_en_cours.get("id")

        # Charger les lignes budgétaires
        lignes = get_lignes_by_budget(self.budget_id).get("data", [])
        self.lignes_mapping = {l.get("article"): l.get("id") for l in lignes if l.get("budget") == self.budget_id}
        self.ligne_combo.addItems(self.lignes_mapping.keys())

        # Charger les demandes approuvées
        demandes_result = get_demandes_depense()
        self.demandes_map = {}

        if demandes_result.get("success"):
            self.demandes_map = {
                f"{d.get('motif')} ({d.get('montant_estime', 0)} F)": d.get("id")
                for d in demandes_result.get("data", [])
                if d.get("statut") == "approuvée"
            }
            self.demande_combo.addItems(self.demandes_map.keys())
        else:
            self.demande_combo.addItem("Aucune demande disponible")

        # Pré-remplir en mode modification
        if self.depense_data:
            self.prefill_form()

    def prefill_form(self):
        data = self.depense_data
        self.date_input.setDate(QDate.fromString(data.get("date", ""), "yyyy-MM-dd"))
        self.type_input.setText(data.get("type_depense", ""))
        self.categorie_input.setText(data.get("categorie", ""))
        self.montant_input.setValue(float(data.get("montant", 0)))
        self.description_input.setPlainText(data.get("description", ""))

        # Sélectionner la ligne budgétaire
        ligne_id = data.get("ligne_budgetaire")
        for article, l_id in self.lignes_mapping.items():
            if l_id == ligne_id:
                self.ligne_combo.setCurrentText(article)
                break

        # Sélectionner la demande liée
        demande_id = data.get("demande")
        for label, d_id in self.demandes_map.items():
            if d_id == demande_id:
                self.demande_combo.setCurrentText(label)
                break

    def select_justificatif(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un justificatif",
            "",
            "Fichiers PDF (*.pdf);;Images (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.justificatif_path = file_path
            filename = os.path.basename(file_path)
            self.justificatif_btn.setText("✅ Justificatif sélectionné")
            self.justificatif_label.setText(f"Fichier: {filename}")
            self.justificatif_label.setToolTip(file_path)

    def submit(self):
        # Validation des champs obligatoires
        if not self.type_input.text().strip():
            self.show_error("Champ manquant", "Le type de dépense est obligatoire.")
            return

        if self.montant_input.value() <= 0:
            self.show_error("Montant invalide", "Le montant doit être supérieur à zéro.")
            return

        # Préparation des données
        demande_label = self.demande_combo.currentText()
        data = {
            "budget": self.budget_id,
            "ligne_budgetaire": self.lignes_mapping.get(self.ligne_combo.currentText()),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "type_depense": self.type_input.text().strip(),
            "categorie": self.categorie_input.text().strip(),
            "montant": self.montant_input.value(),
            "description": self.description_input.toPlainText().strip(),
            "demande": self.demandes_map.get(demande_label),
        }

        # Gestion du fichier justificatif
        files = {}
        if self.justificatif_path:
            try:
                files["justificatif"] = open(self.justificatif_path, "rb")
            except Exception as e:
                self.show_error("Erreur fichier", f"Impossible d'ouvrir le fichier: {str(e)}")
                return

        # Envoi des données
        try:
            if self.depense_data:
                result = update_depense(self.depense_data["id"], data, files)
            else:
                result = create_depense(data, files)

            if result.get("success"):
                self.show_success("Succès", "Dépense enregistrée avec succès!")
                self.accept()
            else:
                self.show_error("Erreur", result.get("message", "Erreur inconnue"))

        except Exception as e:
            self.show_error("Erreur", f"Erreur lors de l'envoi: {str(e)}")
        finally:
            if 'files' in locals() and files.get("justificatif"):
                files["justificatif"].close()

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