from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QDateEdit,
                             QFileDialog, QComboBox)
from PyQt5.QtCore import Qt, QDate

from services.budget_service import get_budgets
from services.recette_service import create_recette, update_recette
import os


class RecetteFormDialog(QDialog):
    """
    Dialogue pour l'ajout d'une nouvelle recette
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Ajouter une Recette")
        self.setMinimumSize(400, 350)

        # Layout principal
        main_layout = QVBoxLayout()

        # Champs de formulaire
        self._setup_budget_field(main_layout)
        self._setup_source_field(main_layout)
        self._setup_type_field(main_layout)
        self._setup_montant_field(main_layout)
        self._setup_date_field(main_layout)
        self._setup_justificatif_field(main_layout)

        # Boutons d'action
        self._setup_action_buttons(main_layout)

        self.setLayout(main_layout)

    def _setup_budget_field(self, layout):
        """Configure le champ budget"""
        self.budget_input = QComboBox()
        budgets = get_budgets()
        if budgets["success"]:
            self.budget_mapping = {f"{b['exercice']} ({b['montant_disponible']:,.0f} F)": b['id'] for b in
                                   budgets["data"]}
            self.budget_input.addItems(self.budget_mapping.keys())
        else:
            self.budget_input.addItem("Aucun budget trouvé")
            self.budget_mapping = {}

        layout.addWidget(QLabel("Budget associé:"))
        layout.addWidget(self.budget_input)


    def _setup_source_field(self, layout):
        """Configure le champ source"""
        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("Ex: Subvention")
        layout.addWidget(QLabel("Source de la recette:"))
        layout.addWidget(self.source_input)

    def _setup_type_field(self, layout):
        """Configure le champ type"""
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Ex: Cotisation, Don, etc.")
        layout.addWidget(QLabel("Type de recette:"))
        layout.addWidget(self.type_input)

    def _setup_montant_field(self, layout):
        """Configure le champ montant"""
        self.montant_input = QLineEdit()
        self.montant_input.setPlaceholderText("Ex: 1500000")
        layout.addWidget(QLabel("Montant (F CFA):"))
        layout.addWidget(self.montant_input)

    def _setup_date_field(self, layout):
        """Configure le champ date"""
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        layout.addWidget(QLabel("Date de la recette:"))
        layout.addWidget(self.date_input)

    def _setup_justificatif_field(self, layout):
        """Configure le champ justificatif"""
        justificatif_layout = QHBoxLayout()
        self.justificatif_path = QLineEdit()
        self.justificatif_path.setReadOnly(True)

        browse_button = QPushButton("📎 Parcourir...")
        browse_button.clicked.connect(self._handle_file_browse)

        justificatif_layout.addWidget(self.justificatif_path)
        justificatif_layout.addWidget(browse_button)

        layout.addWidget(QLabel("Justificatif (facultatif):"))
        layout.addLayout(justificatif_layout)

    def _setup_action_buttons(self, layout):
        """Configure les boutons d'action"""
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("✅ Enregistrer")
        save_btn.clicked.connect(self._handle_save)

        cancel_btn = QPushButton("❌ Annuler")
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

    def _handle_file_browse(self):
        """Ouvre le dialogue de sélection de fichier"""
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un fichier justificatif",
            "",
            "PDF / Images (*.pdf *.png *.jpg *.jpeg)"
        )
        if fichier:
            self.justificatif_path.setText(fichier)

    def _handle_save(self):

        """Gère l'enregistrement de la recette"""

        # Validation des données

        source = self.source_input.text().strip()
        type_recette = self.type_input.text().strip()
        montant_str = self.montant_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        justificatif = self.justificatif_path.text()

        if not all([source, type_recette, montant_str]):
            QMessageBox.warning(
                self,
                "Champs requis",
                "Veuillez remplir tous les champs obligatoires."
            )
            return

        try:
            montant = float(montant_str)
            if montant <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self,
                "Montant invalide",
                "Le montant doit être un nombre positif."
            )
            return

        # Récupération du budget sélectionné
        budget_label = self.budget_input.currentText()
        budget_id = self.budget_mapping.get(budget_label)

        if not budget_id:
            QMessageBox.warning(self, "Budget requis", "Veuillez sélectionner un budget valide.")
            return

        data = {
            "budget": budget_id,
            "source": source,
            "type": type_recette,
            "montant": montant,
            "date": date
        }

        # Envoi des données
        result = create_recette(data)
        if result["success"]:
            QMessageBox.information(
                self,
                "Succès",
                "Recette ajoutée avec succès."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                result["message"]
            )


class ModifierRecetteDialog(QDialog):
    """
    Dialogue pour la modification d'une recette existante
    """

    def __init__(self, recette, parent=None):
        super().__init__(parent)
        self.recette = recette
        self.justificatif_path = None
        self._setup_ui()

    def _setup_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Modifier une recette")
        layout = QVBoxLayout(self)

        # Configuration des champs
        self._setup_form_fields(layout)

        # Configuration des boutons
        self._setup_buttons(layout)

    def _setup_form_fields(self, layout):
        """Configure les champs du formulaire"""
        # Champ source
        self.source_input = QLineEdit(self.recette['source'])
        layout.addWidget(QLabel("Source"))
        layout.addWidget(self.source_input)

        # Champ type
        self.type_input = QLineEdit(self.recette['type'])
        layout.addWidget(QLabel("Type"))
        layout.addWidget(self.type_input)

        # Champ montant
        self.montant_input = QLineEdit(str(self.recette['montant']))
        layout.addWidget(QLabel("Montant"))
        layout.addWidget(self.montant_input)

        # Champ date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.fromString(self.recette['date'], "yyyy-MM-dd"))
        layout.addWidget(QLabel("Date"))
        layout.addWidget(self.date_input)

        # Bouton justificatif
        self.justificatif_button = QPushButton("Choisir justificatif")
        self.justificatif_button.clicked.connect(self._handle_justificatif_selection)

    def _setup_buttons(self, layout):
        """Configure les boutons d'action"""
        save_button = QPushButton("Enregistrer")
        save_button.clicked.connect(self._handle_save)
        layout.addWidget(save_button)

    def _handle_justificatif_selection(self):
        """Gère la sélection du justificatif"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un fichier",
            "",
            "Fichiers PDF/Images (*.pdf *.png *.jpg *.jpeg)"
        )
        if path:
            self.justificatif_path = path

    def _handle_save(self):
        """Gère l'enregistrement des modifications"""
        data = {
            "source": self.source_input.text(),
            "type": self.type_input.text(),
            "montant": self.montant_input.text(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
        }

        result = update_recette(
            self.recette["id"],
            data,
            self.justificatif_path
        )

        if result["success"]:
            QMessageBox.information(
                self,
                "Succès",
                result["message"]
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                result["message"]
            )