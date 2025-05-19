from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox, QFormLayout
from services.budget_service import update_budget

class ModifierBudgetDialog(QDialog):
    """
    Boîte de dialogue pour modifier un budget actif.
    Champs modifiables : exercice (si non utilisé), montant total (si pas déjà engagé).
    """
    def __init__(self, budget, parent=None):
        super().__init__(parent)
        self.budget = budget
        self.setWindowTitle("✏️ Modifier le budget")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Champ exercice
        self.exercice_input = QLineEdit(self.budget["exercice"])
        self.exercice_input.setPlaceholderText("Ex : 2024-2025")

        # Champ montant total
        self.montant_input = QLineEdit(str(self.budget["montant_total"]))
        self.montant_input.setPlaceholderText("Montant total du budget")

        form.addRow("Exercice :", self.exercice_input)
        form.addRow("Montant total (FCFA) :", self.montant_input)

        layout.addLayout(form)

        self.save_btn = QPushButton("💾 Enregistrer")
        self.save_btn.setStyleSheet("background-color: #00796b; color: white; padding: 8px;")
        self.save_btn.clicked.connect(self.valider_modification)
        layout.addWidget(self.save_btn)

        if self.budget["statut"] == "cloture":
            self.exercice_input.setDisabled(True)
            self.montant_input.setDisabled(True)
            self.save_btn.setDisabled(True)
            QMessageBox.warning(self, "Budget clôturé", "Ce budget est clôturé et ne peut pas être modifié.")

    def valider_modification(self):
        exercice = self.exercice_input.text().strip()
        try:
            montant_total = float(self.montant_input.text())
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Le montant doit être un nombre valide.")
            return

        montant_deja_utilise = self.budget["montant_total"] - self.budget["montant_disponible"]
        if montant_total < montant_deja_utilise:
            QMessageBox.warning(
                self, "Montant insuffisant",
                f"Impossible de fixer un montant total inférieur au montant déjà engagé ({montant_deja_utilise:.0f} F)."
            )
            return

        data = {
            "exercice": exercice,
            "montant_total": montant_total
        }

        response = update_budget(self.budget["id"], data)
        if response["success"]:
            QMessageBox.information(self, "Succès", "Budget mis à jour avec succès.")
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", response["message"])
