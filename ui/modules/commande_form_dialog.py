from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QMessageBox
)
from PyQt5.QtCore import QDate
from services.commande_service import create_commande
from services.ligne_budgetaire_service import get_lignes_by_budget
from services.fournisseur_service import get_fournisseurs
from services.budget_service import get_budgets


class CommandeFormDialog(QDialog):
    """
    Dialogue pour la création de nouvelles commandes
    Gère la sélection des lignes budgétaires et fournisseurs
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.budget_id = None
        self.lignes_mapping = {}
        self.fournisseurs_mapping = {}
        self._init_ui()
        self._setup_ui()

    def _init_ui(self):
        """Initialise les paramètres de base de l'interface"""
        self.setWindowTitle("Nouvelle Commande")
        self.resize(500, 400)
        self.setMinimumSize(500, 400)

    def _setup_ui(self):
        """Configure les éléments de l'interface"""
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Vérification du budget actif
        if not self._check_active_budget():
            return

        # Configuration des champs
        self._setup_budget_fields(form_layout)
        self._setup_supplier_fields(form_layout)
        self._setup_order_details(form_layout)

        main_layout.addLayout(form_layout)
        self._setup_submit_button(main_layout)

    def _check_active_budget(self):
        """Vérifie qu'un budget est actif"""
        budgets = get_budgets().get("data", [])
        active_budget = next(
            (b for b in budgets if b.get("statut") == "en_cours"),
            None
        )

        if not active_budget:
            QMessageBox.warning(
                self,
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

        self.ligne_combo = QComboBox()

        # Create mapping with proper error handling
        self.lignes_mapping = {}
        for l in lignes:
            try:
                article = l.get("article", "Sans nom")
                reste = l.get("reste", "N/A")  # Use default if 'reste' doesn't exist
                display_text = f"{article} (Reste: {reste} CFA)" if reste != "N/A" else article
                self.lignes_mapping[display_text] = l["id"]
            except KeyError as e:
                print(f"Missing expected key in line data: {e}")
                continue

        if not self.lignes_mapping:
            QMessageBox.warning(
                self,
                "Aucune ligne budgétaire",
                "Aucune ligne budgétaire valide disponible pour ce budget.\n"
                "Veuillez vérifier les données des lignes budgétaires."
            )
            self.reject()
            return

        self.ligne_combo.addItems(self.lignes_mapping.keys())
        layout.addRow("Ligne Budgétaire *", self.ligne_combo)
    def _setup_supplier_fields(self, layout):
        """Configure les champs liés aux fournisseurs"""
        fournisseurs = get_fournisseurs().get("data", [])

        self.fournisseur_combo = QComboBox()
        self.fournisseurs_mapping = {f["nom"]: f["id"] for f in fournisseurs}

        if not self.fournisseurs_mapping:
            QMessageBox.warning(
                self,
                "Aucun fournisseur",
                "Aucun fournisseur enregistré.\n"
                "Veuillez d'abord créer des fournisseurs."
            )
            self.reject()
            return

        self.fournisseur_combo.addItems(self.fournisseurs_mapping.keys())
        layout.addRow("Fournisseur *", self.fournisseur_combo)

    def _setup_order_details(self, layout):
        """Configure les détails de la commande"""
        # Référence
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Réf. interne ou bon de commande")
        layout.addRow("Référence *", self.reference_input)

        # Désignation
        self.designation_input = QLineEdit()
        self.designation_input.setPlaceholderText("Description détaillée de l'article")
        layout.addRow("Désignation *", self.designation_input)

        # Quantité
        self.quantite_input = QSpinBox()
        self.quantite_input.setMinimum(1)
        self.quantite_input.setMaximum(9999)
        layout.addRow("Quantité *", self.quantite_input)

        # Prix unitaire
        self.prix_input = QDoubleSpinBox()
        self.prix_input.setRange(0, 1_000_000_000)
        self.prix_input.setPrefix("CFA ")
        self.prix_input.setDecimals(2)
        layout.addRow("Prix Unitaire *", self.prix_input)

    def _setup_submit_button(self, layout):
        """Configure le bouton de soumission"""
        self.submit_btn = QPushButton("💾 Enregistrer la Commande")
        self.submit_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.submit_btn.clicked.connect(self._handle_submit)
        layout.addWidget(self.submit_btn)

    def _validate_form(self):
        """Valide les données du formulaire"""
        required_fields = {
            "Référence": self.reference_input.text().strip(),
            "Désignation": self.designation_input.text().strip()
        }

        for field, value in required_fields.items():
            if not value:
                QMessageBox.warning(
                    self,
                    "Champ manquant",
                    f"Le champ '{field}' est obligatoire."
                )
                return False

        if self.prix_input.value() <= 0:
            QMessageBox.warning(
                self,
                "Prix invalide",
                "Le prix unitaire doit être supérieur à 0."
            )
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
            "date": QDate.currentDate().toString("yyyy-MM-dd")
        }

    def _handle_submit(self):
        """Gère la soumission du formulaire"""
        if not self._validate_form():
            return

        order_data = self._prepare_order_data()
        result = create_commande(order_data)

        if result.get("success"):
            QMessageBox.information(
                self,
                "Succès",
                "La commande a été enregistrée avec succès!"
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Erreur",
                result.get("message", "Une erreur inconnue est survenue")
            )