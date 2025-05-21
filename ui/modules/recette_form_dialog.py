from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QDateEdit,
                             QFileDialog, QComboBox, QFormLayout, QGroupBox,
                             QSpacerItem, QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap
import os

from services.budget_service import get_budgets
from services.recette_service import create_recette, update_recette


class StyledLineEdit(QLineEdit):
    """LineEdit personnalisé avec un style amélioré"""

    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border: 1px solid #aaa;
            }
        """)


class RecetteFormDialog(QDialog):
    """
    Dialogue pour l'ajout d'une nouvelle recette avec style amélioré
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._setup_ui()
        self._apply_styles()

    def _init_ui(self):
        """Initialise les paramètres de base de l'interface"""
        self.setWindowTitle("Nouvelle Recette")
        self.resize(500, 500)
        self.setMinimumSize(450, 450)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

    def _setup_ui(self):
        """Configure les éléments de l'interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # En-tête
        self._create_header(main_layout)

        # Diviseur
        self._add_divider(main_layout)

        # Groupe de champs pour les informations principales
        main_group = self._create_group_box("Informations de la Recette")
        main_layout.addWidget(main_group)
        form_layout = QFormLayout(main_group)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Configuration des champs
        self._setup_budget_field(form_layout)
        self._setup_source_field(form_layout)
        self._setup_type_field(form_layout)
        self._setup_montant_field(form_layout)
        self._setup_date_field(form_layout)
        self._setup_justificatif_field(form_layout)

        # Élément d'espacement
        main_layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Boutons d'action
        self._create_action_buttons(main_layout)

        self.setLayout(main_layout)

    def _create_header(self, layout):
        """Crée l'en-tête du formulaire"""
        header_layout = QHBoxLayout()

        # Titre
        title = QLabel("NOUVELLE RECETTE")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        # Icône (optionnelle)
        icon_path = os.path.join("icons", "income.png")
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
            header_layout.addWidget(icon_label)

        layout.addLayout(header_layout)

    def _add_divider(self, layout):
        """Ajoute une ligne de séparation"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #dcdde1; max-height: 1px;")
        layout.addWidget(line)

    def _create_group_box(self, title):
        """Crée un groupe de champs stylisé"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2980b9;
            }
        """)
        return group

    def _create_label(self, text):
        """Crée un label stylisé pour les champs de formulaire"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #34495e;
            }
        """)
        if text.endswith("*"):
            label.setStyleSheet("""
                QLabel {
                    font-size: 10pt;
                    color: #34495e;
                    font-weight: bold;
                }
            """)
        return label

    def _setup_budget_field(self, layout):
        """Configure le champ budget"""
        self.budget_input = QComboBox()
        self.budget_input.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
                min-height: 30px;
            }
            QComboBox:hover {
                border: 1px solid #aaa;
            }
            QComboBox:focus {
                border: 1px solid #3498db;
            }
        """)

        budgets = get_budgets()
        if budgets["success"]:
            self.budget_mapping = {f"{b['exercice']} ({b['montant_disponible']:,.0f} F)": b['id'] for b in
                                   budgets["data"]}
            self.budget_input.addItems(self.budget_mapping.keys())
        else:
            self.budget_input.addItem("Aucun budget trouvé")
            self.budget_mapping = {}

        layout.addRow(self._create_label("Budget associé *"), self.budget_input)

    def _setup_source_field(self, layout):
        """Configure le champ source"""
        self.source_input = StyledLineEdit("Ex: Subvention")
        layout.addRow(self._create_label("Source *"), self.source_input)

    def _setup_type_field(self, layout):
        """Configure le champ type"""
        self.type_input = StyledLineEdit("Ex: Cotisation, Don, etc.")
        layout.addRow(self._create_label("Type *"), self.type_input)

    def _setup_montant_field(self, layout):
        """Configure le champ montant"""
        self.montant_input = StyledLineEdit("Ex: 1500000")
        layout.addRow(self._create_label("Montant (F CFA) *"), self.montant_input)

    def _setup_date_field(self, layout):
        """Configure le champ date"""
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
                min-height: 30px;
            }
            QDateEdit:hover {
                border: 1px solid #aaa;
            }
            QDateEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        layout.addRow(self._create_label("Date *"), self.date_input)

    def _setup_justificatif_field(self, layout):
        """Configure le champ justificatif"""
        justificatif_layout = QHBoxLayout()
        self.justificatif_path = QLineEdit()
        self.justificatif_path.setReadOnly(True)
        self.justificatif_path.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
            }
        """)

        browse_button = QPushButton("📎 Parcourir...")
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #d6dbdf;
            }
        """)
        browse_button.clicked.connect(self._handle_file_browse)

        justificatif_layout.addWidget(self.justificatif_path)
        justificatif_layout.addWidget(browse_button)

        layout.addRow(self._create_label("Justificatif"), justificatif_layout)

    def _create_action_buttons(self, layout):
        """Configure les boutons d'action"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Bouton Annuler
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #d6dbdf;
            }
            QPushButton:pressed {
                background-color: #cbd0d3;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        # Bouton Enregistrer
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setMinimumWidth(150)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        save_btn.clicked.connect(self._handle_save)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def _apply_styles(self):
        """Applique des styles globaux à la fenêtre"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

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
            self._show_error_message("Veuillez remplir tous les champs obligatoires (*)")
            return

        try:
            montant = float(montant_str)
            if montant <= 0:
                raise ValueError
        except ValueError:
            self._show_error_message("Le montant doit être un nombre positif")
            return

        # Récupération du budget sélectionné
        budget_label = self.budget_input.currentText()
        budget_id = self.budget_mapping.get(budget_label)

        if not budget_id:
            self._show_error_message("Veuillez sélectionner un budget valide")
            return

        data = {
            "budget": budget_id,
            "source": source,
            "type": type_recette,
            "montant": montant,
            "date": date
        }

        # Envoi des données
        result = create_recette(data, justificatif if justificatif else None)
        if result["success"]:
            self._show_success_message("Recette ajoutée avec succès")
            self.accept()
        else:
            self._show_error_message(result.get("message", "Erreur inconnue"))

    def _show_error_message(self, message):
        """Affiche un message d'erreur stylisé"""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle("Erreur")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 10pt;
            }
            QLabel {
                color: #e74c3c;
                font-weight: bold;
                min-width: 250px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        error_box.exec_()

    def _show_success_message(self, message):
        """Affiche un message de succès stylisé"""
        success_box = QMessageBox(self)
        success_box.setIcon(QMessageBox.Information)
        success_box.setWindowTitle("Succès")
        success_box.setText(message)
        success_box.setStandardButtons(QMessageBox.Ok)
        success_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 10pt;
            }
            QLabel {
                color: #27ae60;
                font-weight: bold;
                min-width: 250px;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        success_box.exec_()


class ModifierRecetteDialog(QDialog):
    """
    Dialogue pour la modification d'une recette existante avec style amélioré
    """

    def __init__(self, recette, parent=None):
        super().__init__(parent)
        self.recette = recette
        self.justificatif_path = None
        self._init_ui()
        self._setup_ui()
        self._apply_styles()

    def _init_ui(self):
        """Initialise les paramètres de base de l'interface"""
        self.setWindowTitle(f"Modifier Recette: {self.recette.get('source', '')}")
        self.resize(500, 500)
        self.setMinimumSize(450, 450)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

    def _setup_ui(self):
        """Configure les éléments de l'interface"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # En-tête
        self._create_header(main_layout)

        # Diviseur
        self._add_divider(main_layout)

        # Groupe de champs pour les informations principales
        main_group = self._create_group_box("Informations de la Recette")
        main_layout.addWidget(main_group)
        form_layout = QFormLayout(main_group)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Configuration des champs
        self._setup_form_fields(form_layout)

        # Élément d'espacement
        main_layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Boutons d'action
        self._create_action_buttons(main_layout)

        self.setLayout(main_layout)

    def _create_header(self, layout):
        """Crée l'en-tête du formulaire"""
        header_layout = QHBoxLayout()

        # Titre
        title = QLabel(f"MODIFICATION RECETTE: {self.recette.get('source', '').upper()}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        # Icône (optionnelle)
        icon_path = os.path.join("icons", "income.png")
        if os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
            header_layout.addWidget(icon_label)

        layout.addLayout(header_layout)

    def _add_divider(self, layout):
        """Ajoute une ligne de séparation"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #dcdde1; max-height: 1px;")
        layout.addWidget(line)

    def _create_group_box(self, title):
        """Crée un groupe de champs stylisé"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2980b9;
            }
        """)
        return group

    def _create_label(self, text):
        """Crée un label stylisé pour les champs de formulaire"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #34495e;
            }
        """)
        if text.endswith("*"):
            label.setStyleSheet("""
                QLabel {
                    font-size: 10pt;
                    color: #34495e;
                    font-weight: bold;
                }
            """)
        return label

    def _setup_form_fields(self, layout):
        """Configure les champs du formulaire"""
        # Champ source
        self.source_input = StyledLineEdit()
        self.source_input.setText(self.recette.get('source', ''))
        layout.addRow(self._create_label("Source *"), self.source_input)

        # Champ type
        self.type_input = StyledLineEdit()
        self.type_input.setText(self.recette.get('type', ''))
        layout.addRow(self._create_label("Type *"), self.type_input)

        # Champ montant
        self.montant_input = StyledLineEdit()
        self.montant_input.setText(str(self.recette.get('montant', '')))
        layout.addRow(self._create_label("Montant (F CFA) *"), self.montant_input)

        # Champ date
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.fromString(self.recette.get('date', ''), "yyyy-MM-dd"))
        self.date_input.setCalendarPopup(True)
        self.date_input.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
                min-height: 30px;
            }
            QDateEdit:hover {
                border: 1px solid #aaa;
            }
            QDateEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        layout.addRow(self._create_label("Date *"), self.date_input)

        # Champ justificatif
        justificatif_layout = QHBoxLayout()
        self.justificatif_path = QLineEdit()
        self.justificatif_path.setReadOnly(True)
        self.justificatif_path.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
            }
        """)

        browse_button = QPushButton("📎 Parcourir...")
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #d6dbdf;
            }
        """)
        browse_button.clicked.connect(self._handle_justificatif_selection)

        justificatif_layout.addWidget(self.justificatif_path)
        justificatif_layout.addWidget(browse_button)

        layout.addRow(self._create_label("Justificatif"), justificatif_layout)

    def _create_action_buttons(self, layout):
        """Configure les boutons d'action"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Bouton Annuler
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #d6dbdf;
            }
            QPushButton:pressed {
                background-color: #cbd0d3;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        # Bouton Enregistrer
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setMinimumWidth(150)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        save_btn.clicked.connect(self._handle_save)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def _apply_styles(self):
        """Applique des styles globaux à la fenêtre"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

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
            self.justificatif_path.setText(os.path.basename(path))

    def _handle_save(self):
        """Gère l'enregistrement des modifications"""
        # Validation des données
        source = self.source_input.text().strip()
        type_recette = self.type_input.text().strip()
        montant_str = self.montant_input.text().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if not all([source, type_recette, montant_str]):
            self._show_error_message("Veuillez remplir tous les champs obligatoires (*)")
            return

        try:
            montant = float(montant_str)
            if montant <= 0:
                raise ValueError
        except ValueError:
            self._show_error_message("Le montant doit être un nombre positif")
            return

        data = {
            "source": source,
            "type": type_recette,
            "montant": montant,
            "date": date
        }

        # Envoi des données
        result = update_recette(
            self.recette["id"],
            data,
            self.justificatif_path if self.justificatif_path else None
        )

        if result["success"]:
            self._show_success_message("Recette modifiée avec succès")
            self.accept()
        else:
            self._show_error_message(result.get("message", "Erreur inconnue"))

    def _show_error_message(self, message):
        """Affiche un message d'erreur stylisé"""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle("Erreur")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 10pt;
            }
            QLabel {
                color: #e74c3c;
                font-weight: bold;
                min-width: 250px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        error_box.exec_()

    def _show_success_message(self, message):
        """Affiche un message de succès stylisé"""
        success_box = QMessageBox(self)
        success_box.setIcon(QMessageBox.Information)
        success_box.setWindowTitle("Succès")
        success_box.setText(message)
        success_box.setStandardButtons(QMessageBox.Ok)
        success_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 10pt;
            }
            QLabel {
                color: #27ae60;
                font-weight: bold;
                min-width: 250px;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        success_box.exec_()