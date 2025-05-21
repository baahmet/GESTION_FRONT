from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QPushButton, QMessageBox, QLabel, QGroupBox, QHBoxLayout,
    QSpacerItem, QSizePolicy, QFrame, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPixmap
import os

from services.commande_service import create_commande
from services.ligne_budgetaire_service import get_lignes_by_budget
from services.fournisseur_service import get_fournisseurs
from services.budget_service import get_budgets


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


class StyledComboBox(QComboBox):
    """ComboBox personnalisé avec un style amélioré"""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
            }
            QComboBox:hover {
                border: 1px solid #aaa;
            }
            QComboBox:focus {
                border: 1px solid #3498db;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #ccc;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
        """)


class StyledSpinBox(QSpinBox):
    """SpinBox personnalisé avec un style amélioré"""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
            }
            QSpinBox:hover {
                border: 1px solid #aaa;
            }
            QSpinBox:focus {
                border: 1px solid #3498db;
            }
        """)


class StyledDoubleSpinBox(QDoubleSpinBox):
    """DoubleSpinBox personnalisé avec un style amélioré"""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(30)
        self.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px 10px;
                background-color: #fafafa;
                color: #333;
                font-size: 10pt;
            }
            QDoubleSpinBox:hover {
                border: 1px solid #aaa;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #3498db;
            }
        """)


class CommandeFormDialog(QDialog):
    """
    Dialogue pour la création de nouvelles commandes avec style amélioré
    Gère la sélection des lignes budgétaires et fournisseurs
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.budget_id = None
        self.lignes_mapping = {}
        self.fournisseurs_mapping = {}
        self._init_ui()
        self._setup_ui()
        self._apply_styles()

    def _init_ui(self):
        """Initialise les paramètres de base de l'interface"""
        self.setWindowTitle("Nouvelle Commande")
        self.resize(600, 600)
        self.setMinimumSize(550, 550)
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

        # Vérification du budget actif
        if not self._check_active_budget():
            return

        # Groupe de champs pour les informations de base
        base_group = self._create_group_box("Informations de Base")
        base_layout = QFormLayout(base_group)
        base_layout.setSpacing(12)
        base_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(base_group)

        # Configuration des champs de base
        self._setup_budget_fields(base_layout)
        self._setup_supplier_fields(base_layout)

        # Groupe de champs pour les détails de la commande
        details_group = self._create_group_box("Détails de la Commande")
        details_layout = QFormLayout(details_group)
        details_layout.setSpacing(12)
        details_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(details_group)

        # Configuration des champs de détails
        self._setup_order_details(details_layout)

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
        title = QLabel("NOUVELLE COMMANDE")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        # Icône (optionnelle)
        icon_path = os.path.join("icons", "order.png")
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

    def _check_active_budget(self):
        """Vérifie qu'un budget est actif"""
        budgets = get_budgets().get("data", [])
        active_budget = next(
            (b for b in budgets if b.get("statut") == "en_cours"),
            None
        )

        if not active_budget:
            self._show_error_message(
                "Aucun budget actif",
                "Aucun budget n'est actuellement en cours.\n"
                "Veuillez créer ou activer un budget avant de passer une commande."
            )
            self.reject()
            return False

        self.budget_id = active_budget["id"]
        return True

    def _setup_budget_fields(self, layout):
        """Configure les champs liés au budget"""
        response = get_lignes_by_budget(self.budget_id)
        lignes = response.get("data", [])

        self.ligne_combo = StyledComboBox()

        # Create mapping with proper error handling
        self.lignes_mapping = {}
        for l in lignes:
            try:
                article = l.get("article", "Sans nom")
                reste = l.get("reste", "N/A")
                display_text = f"{article} (Reste: {reste:,.0f} CFA)" if isinstance(reste, (int, float)) else article
                self.lignes_mapping[display_text] = l["id"]
            except KeyError as e:
                print(f"Missing expected key in line data: {e}")
                continue

        if not self.lignes_mapping:
            self._show_error_message(
                "Aucune ligne budgétaire",
                "Aucune ligne budgétaire valide disponible pour ce budget.\n"
                "Veuillez vérifier les données des lignes budgétaires."
            )
            self.reject()
            return

        self.ligne_combo.addItems(self.lignes_mapping.keys())
        layout.addRow(self._create_label("Ligne Budgétaire *"), self.ligne_combo)

    def _setup_supplier_fields(self, layout):
        """Configure les champs liés aux fournisseurs"""
        fournisseurs = get_fournisseurs().get("data", [])

        self.fournisseur_combo = StyledComboBox()
        self.fournisseurs_mapping = {f["nom"]: f["id"] for f in fournisseurs}

        if not self.fournisseurs_mapping:
            self._show_error_message(
                "Aucun fournisseur",
                "Aucun fournisseur enregistré.\n"
                "Veuillez d'abord créer des fournisseurs."
            )
            self.reject()
            return

        self.fournisseur_combo.addItems(self.fournisseurs_mapping.keys())
        layout.addRow(self._create_label("Fournisseur *"), self.fournisseur_combo)

    def _setup_order_details(self, layout):
        """Configure les détails de la commande"""
        # Référence
        self.reference_input = StyledLineEdit()
        self.reference_input.setPlaceholderText("Réf. interne ou bon de commande")
        layout.addRow(self._create_label("Référence *"), self.reference_input)

        # Désignation
        self.designation_input = StyledLineEdit()
        self.designation_input.setPlaceholderText("Description détaillée de l'article")
        layout.addRow(self._create_label("Désignation *"), self.designation_input)

        # Date
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
        layout.addRow(self._create_label("Date"), self.date_input)

        # Quantité
        self.quantite_input = StyledSpinBox()
        self.quantite_input.setMinimum(1)
        self.quantite_input.setMaximum(9999)
        layout.addRow(self._create_label("Quantité *"), self.quantite_input)

        # Prix unitaire
        self.prix_input = StyledDoubleSpinBox()
        self.prix_input.setRange(0, 1_000_000_000)
        self.prix_input.setPrefix("CFA ")
        self.prix_input.setDecimals(2)
        layout.addRow(self._create_label("Prix Unitaire *"), self.prix_input)

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
        save_btn = QPushButton("💾 Enregistrer la Commande")
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
        save_btn.clicked.connect(self._handle_submit)

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

    def _validate_form(self):
        """Valide les données du formulaire"""
        required_fields = {
            "Référence": self.reference_input.text().strip(),
            "Désignation": self.designation_input.text().strip()
        }

        for field, value in required_fields.items():
            if not value:
                self._show_error_message("Champ manquant", f"Le champ '{field}' est obligatoire.")
                return False

        if self.prix_input.value() <= 0:
            self._show_error_message("Prix invalide", "Le prix unitaire doit être supérieur à 0.")
            return False

        return True

    def _prepare_order_data(self):
        """Prépare les données de la commande pour l'API"""
        return {
            "ligne_budgetaire": self.lignes_mapping[self.ligne_combo.currentText()],
            "fournisseur": self.fournisseurs_mapping[self.fournisseur_combo.currentText()],
            "reference": self.reference_input.text().strip(),
            "designation": self.designation_input.text().strip(),
            "quantite": self.quantite_input.value(),
            "prix_unitaire": self.prix_input.value(),
            "date": self.date_input.date().toString("yyyy-MM-dd")
        }

    def _handle_submit(self):
        """Gère la soumission du formulaire"""
        if not self._validate_form():
            return

        order_data = self._prepare_order_data()
        result = create_commande(order_data)

        if result.get("success"):
            self._show_success_message("Succès", "La commande a été enregistrée avec succès!")
            self.accept()
        else:
            self._show_error_message("Erreur", result.get("message", "Une erreur inconnue est survenue"))

    def _show_error_message(self, title, message):
        """Affiche un message d'erreur stylisé"""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle(title)
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

    def _show_success_message(self, title, message):
        """Affiche un message de succès stylisé"""
        success_box = QMessageBox(self)
        success_box.setIcon(QMessageBox.Information)
        success_box.setWindowTitle(title)
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