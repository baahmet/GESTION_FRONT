from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QLabel, QGroupBox, QHBoxLayout, QSpacerItem,
    QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
import os


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


class FournisseurFormDialog(QDialog):
    """
    Dialogue pour la création et modification de fournisseurs
    Gère à la fois l'ajout et l'édition grâce au paramètre fournisseur optionnel
    """

    def __init__(self, parent=None, fournisseur=None):
        super().__init__(parent)
        self.fournisseur = fournisseur
        self._init_ui()
        self._setup_ui()
        self._apply_styles()

    def _init_ui(self):
        """Initialise les paramètres de base de l'interface"""
        mode = "Modification" if self.fournisseur else "Nouveau"
        self.setWindowTitle(f"{mode} Fournisseur")
        self.resize(500, 500)
        self.setMinimumSize(450, 450)

        # Configuration de base de la fenêtre
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

        # Groupe de champs pour les informations générales
        general_group = self._create_group_box("Informations Générales")
        general_layout = QFormLayout(general_group)
        general_layout.setSpacing(12)
        general_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(general_group)

        # Création des champs principaux
        self._create_main_fields(general_layout)

        # Groupe de champs pour les informations administratives
        admin_group = self._create_group_box("Informations Administratives")
        admin_layout = QFormLayout(admin_group)
        admin_layout.setSpacing(12)
        admin_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addWidget(admin_group)

        # Création des champs administratifs
        self._create_admin_fields(admin_layout)

        # Élément d'espacement
        main_layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Boutons d'action
        self._create_action_buttons(main_layout)

        self.setLayout(main_layout)

        # Si mode édition, charger les données
        if self.fournisseur:
            self._load_fournisseur_data()

    def _create_header(self, layout):
        """Crée l'en-tête du formulaire"""
        header_layout = QHBoxLayout()

        # Titre
        title = QLabel(
            "FOURNISSEUR" if not self.fournisseur else f"FOURNISSEUR: {self.fournisseur.get('nom', '')}"
        )
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        # Icône (on pourrait ajouter une icône ici si disponible)
        icon_path = os.path.join("icons", "supplier.png")
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

    def _create_main_fields(self, layout):
        """Crée les champs principaux du formulaire"""
        self.nom_input = StyledLineEdit("Nom complet du fournisseur")
        self.type_input = StyledLineEdit("Type de produits/services")
        self.adresse_input = StyledLineEdit("Adresse physique")
        self.email_input = StyledLineEdit("contact@exemple.com")
        self.tel_input = StyledLineEdit("77 123 45 67")

        # Ajout des champs obligatoires avec indication visuelle
        layout.addRow(self._create_label("Nom *"), self.nom_input)
        layout.addRow(self._create_label("Type *"), self.type_input)
        layout.addRow(self._create_label("Adresse"), self.adresse_input)
        layout.addRow(self._create_label("Email"), self.email_input)
        layout.addRow(self._create_label("Téléphone *"), self.tel_input)

    def _create_admin_fields(self, layout):
        """Crée les champs administratifs du formulaire"""
        self.rc_input = StyledLineEdit("Numéro de registre du commerce")
        self.ninea_input = StyledLineEdit("Identifiant fiscal")

        layout.addRow(self._create_label("N° RC"), self.rc_input)
        layout.addRow(self._create_label("NINEA"), self.ninea_input)

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

    def _create_action_buttons(self, layout):
        """Crée les boutons d'action"""
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

    def _load_fournisseur_data(self):
        """Remplit les champs avec les données du fournisseur existant"""
        self.nom_input.setText(self.fournisseur.get("nom", ""))
        self.type_input.setText(self.fournisseur.get("type", ""))
        self.adresse_input.setText(self.fournisseur.get("adresse", ""))
        self.email_input.setText(self.fournisseur.get("email", ""))
        self.tel_input.setText(self.fournisseur.get("telephone", ""))
        self.rc_input.setText(self.fournisseur.get("numero_rc", ""))
        self.ninea_input.setText(self.fournisseur.get("ninea", ""))

    def _validate_form(self):
        """Valide les données du formulaire"""
        required_fields = {
            "Nom": self.nom_input.text().strip(),
            "Type": self.type_input.text().strip(),
            "Téléphone": self.tel_input.text().strip()
        }

        for field, value in required_fields.items():
            if not value:
                self._show_error_message(f"Le champ {field} est obligatoire")
                return False

        return True

    def _show_error_message(self, message):
        """Affiche un message d'erreur stylisé"""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowTitle("Champ requis")
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

    def _prepare_data(self):
        """Prépare les données pour l'envoi"""
        return {
            "nom": self.nom_input.text().strip(),
            "type": self.type_input.text().strip(),
            "adresse": self.adresse_input.text().strip(),
            "email": self.email_input.text().strip(),
            "telephone": self.tel_input.text().strip(),
            "numero_rc": self.rc_input.text().strip(),
            "ninea": self.ninea_input.text().strip(),
        }

    def _handle_submit(self):
        """Gère la soumission du formulaire"""
        if not self._validate_form():
            return

        data = self._prepare_data()

        try:
            from services.fournisseur_service import create_fournisseur, update_fournisseur

            if self.fournisseur:
                result = update_fournisseur(self.fournisseur["id"], data)
            else:
                result = create_fournisseur(data)

            self._process_submission_result(result)

        except Exception as e:
            self._show_technical_error(str(e))

    def _show_technical_error(self, message):
        """Affiche une erreur technique stylisée"""
        error_box = QMessageBox(self)
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Erreur technique")
        error_box.setText(f"Une erreur est survenue:")
        error_box.setInformativeText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 10pt;
            }
            QLabel {
                color: #c0392b;
                min-width: 300px;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        error_box.exec_()

    def _process_submission_result(self, result):
        """Traite le résultat de la soumission"""
        if result["success"]:
            success_box = QMessageBox(self)
            success_box.setIcon(QMessageBox.Information)
            success_box.setWindowTitle("Succès")
            success_box.setText("Fournisseur enregistré avec succès!")
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
            self.accept()
        else:
            self._show_technical_error(result.get("message", "Erreur inconnue"))