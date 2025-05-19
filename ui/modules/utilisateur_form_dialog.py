from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox
)
from services.utilisateur_service import register_utilisateur, update_utilisateur


class UtilisateurFormDialog(QDialog):
    """Boîte de dialogue pour la création ou modification d'utilisateurs."""

    def __init__(self, parent=None, utilisateur_data=None):
        """Initialise la boîte de dialogue du formulaire utilisateur.

        Args:
            parent: Widget parent
            utilisateur_data (dict, optional): Données de l'utilisateur pour modification
        """
        super().__init__(parent)
        self.utilisateur_data = utilisateur_data
        self.setWindowTitle("Modifier Utilisateur" if utilisateur_data else "Créer Utilisateur")
        self.init_ui()

    def init_ui(self):
        """Configure l'interface utilisateur du formulaire."""
        # Configuration du layout principal
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Champ Nom
        self.nom_input = QLineEdit()
        form_layout.addRow("Nom :", self.nom_input)

        # Champ Email
        self.email_input = QLineEdit()
        form_layout.addRow("Email :", self.email_input)

        # Liste déroulante pour le rôle
        self.role_combo = QComboBox()
        self.role_combo.addItems(["comptable", "directeur", "csa"])
        form_layout.addRow("Rôle :", self.role_combo)

        # Champ mot de passe (uniquement en création)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if not self.utilisateur_data:
            form_layout.addRow("Mot de passe :", self.password_input)

        # Préremplissage des champs en mode modification
        if self.utilisateur_data:
            self.nom_input.setText(self.utilisateur_data["nom"])
            self.email_input.setText(self.utilisateur_data["email"])
            self.role_combo.setCurrentText(self.utilisateur_data["role"])

        # Bouton de soumission
        self.submit_btn = QPushButton(
            "Modifier" if self.utilisateur_data else "Créer"
        )
        self.submit_btn.clicked.connect(self.submit)

        # Finalisation du layout
        layout.addLayout(form_layout)
        layout.addWidget(self.submit_btn)

    def submit(self):
        """Traite la soumission du formulaire."""
        # Récupération des valeurs du formulaire
        nom = self.nom_input.text()
        email = self.email_input.text()
        role = self.role_combo.currentText()
        password = self.password_input.text()

        # Validation des champs obligatoires
        if not nom or not email:
            QMessageBox.warning(
                self,
                "Champs requis",
                "Veuillez remplir tous les champs."
            )
            return

        # Préparation des données
        data = {
            "nom": nom,
            "email": email,
            "role": role
        }

        # Ajout du mot de passe uniquement en création
        if not self.utilisateur_data and password:
            data["mot_de_passe"] = password

        # Exécution de l'opération appropriée (création ou modification)
        if self.utilisateur_data:
            result = update_utilisateur(self.utilisateur_data["id"], data)
        else:
            result = register_utilisateur(data)

        # Gestion du résultat
        if result["success"]:
            QMessageBox.information(
                self,
                "Succès",
                "Opération réalisée avec succès."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                result["message"]
            )