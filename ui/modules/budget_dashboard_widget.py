from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class BudgetDashboardWidget(QWidget):
    def __init__(self, budget_data, parent=None):
        super().__init__(parent)
        self.budget_data = budget_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        montant_total = self.budget_data['montant_total']
        montant_disponible = self.budget_data['montant_disponible']
        montant_total_recettes = self.budget_data['montant_total_recettes']
        montant_total_depenses = self.budget_data['montant_total_depenses_validees']

        # Calcul du montant global (initial + recettes)
        montant_global = montant_total + montant_total_recettes

        # Sécurité division
        utilise = montant_total_depenses
        pourcentage_utilise = (utilise / montant_global) * 100 if montant_global > 0 else 0

        # Synthèse
        resume_group = QGroupBox("Synthèse Globale")
        resume_layout = QVBoxLayout(resume_group)

        resume_layout.addWidget(QLabel(f"💼 Montant initial : <b>{montant_total:,.0f} F</b>"))
        resume_layout.addWidget(QLabel(f"💰 Recettes cumulées : <b>{montant_total_recettes:,.0f} F</b>"))
        resume_layout.addWidget(QLabel(f"💸 Dépenses validées : <b>{montant_total_depenses:,.0f} F</b>"))
        resume_layout.addWidget(QLabel(f"📈 Solde disponible : <b>{montant_disponible:,.0f} F</b>"))
        resume_layout.addWidget(QLabel(f"🛒 Utilisé : <b>{pourcentage_utilise:.1f}%</b>"))

        layout.addWidget(resume_group)

        # --- Graphique ---
        fig, ax = plt.subplots(figsize=(4, 4))
        labels = ['Disponible', 'Dépenses validées']
        values = [montant_disponible, montant_total_depenses]
        colors = ['#4caf50', '#f44336']

        # Sécurité anti négatif
        safe_values = [max(0, v) for v in values]
        if sum(safe_values) == 0:
            safe_values = [1, 0]  # Placeholder visuel

        ax.pie(safe_values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')
        ax.set_title("Répartition du budget")

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
