from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox
)
from services.fournisseur_service import (
    create_fournisseur,
    update_fournisseur,
    get_fournisseurs
)


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

    def _init_ui(self):
        """Initialise les paramètres de base de l'interface"""
        self.setWindowTitle("Gestion Fournisseur")
        self.resize(400, 250)
        self.setMinimumSize(400, 250)

    def _setup_ui(self):
        """Configure les éléments de l'interface"""
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Création des champs de formulaire
        self._create_form_fields(form_layout)
        main_layout.addLayout(form_layout)

        # Bouton de soumission
        self._create_submit_button(main_layout)

        self.setLayout(main_layout)

        # Si mode édition, charger les données
        if self.fournisseur:
            self._load_fournisseur_data()

    def _create_form_fields(self, layout):
        """Crée et ajoute les champs du formulaire"""
        self.nom_input = QLineEdit()
        self.type_input = QLineEdit()
        self.adresse_input = QLineEdit()
        self.email_input = QLineEdit()
        self.tel_input = QLineEdit()
        self.rc_input = QLineEdit()
        self.ninea_input = QLineEdit()

        # Configuration des placeholders
        self._set_placeholders()

        # Ajout des champs au layout
        layout.addRow("Nom *", self.nom_input)
        layout.addRow("Type *", self.type_input)
        layout.addRow("Adresse", self.adresse_input)
        layout.addRow("Email", self.email_input)
        layout.addRow("Téléphone *", self.tel_input)
        layout.addRow("N° RC", self.rc_input)
        layout.addRow("NINEA", self.ninea_input)

    def _set_placeholders(self):
        """Définit les textes d'aide pour les champs"""
        self.nom_input.setPlaceholderText("Nom complet du fournisseur")
        self.type_input.setPlaceholderText("Type de produits/services")
        self.adresse_input.setPlaceholderText("Adresse physique")
        self.email_input.setPlaceholderText("contact@exemple.com")
        self.tel_input.setPlaceholderText("77 123 45 67")
        self.rc_input.setPlaceholderText("Numéro de registre du commerce")
        self.ninea_input.setPlaceholderText("Identifiant fiscal")

    def _create_submit_button(self, layout):
        """Crée le bouton de soumission"""
        submit_btn = QPushButton("💾 Enregistrer")
        submit_btn.setStyleSheet("font-weight: bold;")
        submit_btn.clicked.connect(self._handle_submit)
        layout.addWidget(submit_btn)

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
                QMessageBox.warning(
                    self,
                    "Champ requis",
                    f"Le champ {field} est obligatoire"
                )
                return False

        return True

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
            if self.fournisseur:
                result = update_fournisseur(self.fournisseur["id"], data)
            else:
                result = create_fournisseur(data)

            self._process_submission_result(result)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur technique",
                f"Une erreur est survenue: {str(e)}"
            )

    def _process_submission_result(self, result):
        """Traite le résultat de la soumission"""
        if result["success"]:
            QMessageBox.information(
                self,
                "Succès",
                "Fournisseur enregistré avec succès!"
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                result.get("message", "Erreur inconnue")
            )