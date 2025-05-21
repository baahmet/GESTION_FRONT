from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout,
    QGroupBox, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QMargins
from PyQt5.QtGui import QColor, QLinearGradient, QPalette, QFont
from services.budget_service import get_budgets, cloturer_budget, delete_budget
from services.auth_service import AuthService
from ui.modules.budget_form_dialog import BudgetFormDialog
from ui.modules.lignes_budgetaires_dialog import LigneBudgetaireDialog
from ui.modules.budgets_clotures_dialog import BudgetsCloturesDialog
from ui.modules.modifier_budget_dialog import ModifierBudgetDialog
from ui.modules.budget_dashboard_widget import BudgetDashboardWidget


class BudgetsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = AuthService.get_user_role()
        self.init_ui()
        self.load_budgets()
        self.setup_animations()

    def init_ui(self):
        # Layout principal sans marges supplémentaires pour bien s'adapter au conteneur parent
        self.layout_principal = QVBoxLayout()
        self.layout_principal.setContentsMargins(15, 5, 15,
                                                 15)  # Réduire les marges pour éviter les doublons avec MainLayout
        self.layout_principal.setSpacing(12)  # Espacement réduit
        self.setLayout(self.layout_principal)

        # Widget principal pour un meilleur style
        main_content = QWidget()
        main_content.setStyleSheet("""
            background-color: #f5f7fa;
            border-radius: 8px;
        """)
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(20, 15, 20, 20)

        # Titre de section - plus petit car le titre principal est déjà dans la navbar
        section_title = QLabel("Gestion des Budgets")
        section_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #003366;
            padding-bottom: 5px;
            border-bottom: 2px solid #1e88e5;
        """)
        main_layout.addWidget(section_title)

        # Conteneur pour les actions - Style moderne
        actions_container = QWidget()
        actions_container.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            padding: 10px;
        """)

        # Effet d'ombre pour le conteneur
        container_shadow = QGraphicsDropShadowEffect()
        container_shadow.setBlurRadius(10)
        container_shadow.setColor(QColor(0, 0, 0, 40))
        container_shadow.setOffset(0, 3)
        actions_container.setGraphicsEffect(container_shadow)

        # Layout pour les boutons d'action
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(10, 10, 10, 10)
        actions_layout.setSpacing(12)

        # Boutons d'action avec icônes et styles modernes
        buttons = [
            ("✏️ Modifier", "#FFA000", self.ouvrir_dialogue_modification),
            ("⏹ Clôturer", "#C62828", self.cloturer_budget),
            ("🗑 Supprimer", "#B71C1C", self.supprimer_budget),
            ("📊 Lignes", "#1976D2", self.ouvrir_lignes_budgetaires)
        ]

        for text, color, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-weight: 600;
                    min-width: 100px;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 20)};
                }}
                QPushButton:disabled {{
                    background-color: #cccccc;
                    color: #666666;
                }}
            """)
            btn.clicked.connect(callback)
            actions_layout.addWidget(btn)

            # Stocker les boutons pour référence ultérieure
            if "Modifier" in text:
                self.modifier_button = btn
            elif "Clôturer" in text:
                self.cloturer_button = btn
            elif "Supprimer" in text:
                self.supprimer_button = btn
            elif "Lignes" in text:
                self.lignes_button = btn

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        actions_layout.addItem(spacer)
        main_layout.addWidget(actions_container)

        # 🔒 Désactiver actions pour Directeur & CSA
        if self.user_role in ["directeur", "csa"]:
            self.modifier_button.setVisible(False)
            self.cloturer_button.setVisible(False)
            self.supprimer_button.setVisible(False)
            self.lignes_button.setVisible(False)

        # Container pour les boutons de création et archives
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(10)

        # Bouton Créer Budget avec effet de survol élégant
        self.creer_button = QPushButton("➕ CRÉER UN BUDGET")
        self.creer_button.setStyleSheet("""
            QPushButton {
                background-color: #388e3c;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                letter-spacing: 0.5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2e7d32;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
            QPushButton:disabled {
                background-color: #a5d6a7;
                color: #e8f5e9;
            }
        """)
        self.creer_button.clicked.connect(self.creer_budget)
        buttons_layout.addWidget(self.creer_button)

        if self.user_role in ["directeur", "csa"]:
            self.creer_button.setVisible(False)

        # Bouton budgets clôturés avec style moderne
        clotures_btn = QPushButton("📚 ARCHIVES")
        clotures_btn.setStyleSheet("""
            QPushButton {
                background-color: #004080;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #002966;
            }
        """)
        clotures_btn.clicked.connect(self.afficher_budgets_clotures)
        buttons_layout.addWidget(clotures_btn)

        # Spacer pour aligner les boutons à gauche
        buttons_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        main_layout.addWidget(buttons_container)

        # Groupe budget en cours avec style élégant
        self.budget_actif_group = QGroupBox("BUDGET ACTIF")
        self.budget_actif_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #003366;
                border: 1px solid #0078d7;
                border-radius: 8px;
                padding-top: 12px;
                margin-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }
        """)

        # Ombre pour le groupe
        group_shadow = QGraphicsDropShadowEffect()
        group_shadow.setBlurRadius(8)
        group_shadow.setColor(QColor(0, 120, 215, 70))
        group_shadow.setOffset(0, 2)
        self.budget_actif_group.setGraphicsEffect(group_shadow)

        self.budget_actif_layout = QVBoxLayout(self.budget_actif_group)
        self.budget_actif_layout.setContentsMargins(15, 20, 15, 15)
        self.budget_actif_layout.setSpacing(10)
        main_layout.addWidget(self.budget_actif_group)
        self.budget_actif_group.hide()

        # Ajouter le contenu principal au layout
        self.layout_principal.addWidget(main_content)

    def darken_color(self, hex_color, percent=10):
        """Assombrit une couleur hexadécimale"""
        color = QColor(hex_color)
        return color.darker(100 + percent).name()

    def setup_animations(self):
        # Animation de fondu pour l'apparition des éléments
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.start()

    def load_budgets(self):
        # Animation de chargement
        loading_animation = QPropertyAnimation(self, b"windowOpacity")
        loading_animation.setDuration(200)
        loading_animation.setStartValue(1)
        loading_animation.setEndValue(0.7)
        loading_animation.start()

        result = get_budgets()

        loading_animation.setDirection(loading_animation.Backward)
        loading_animation.start()

        if result["success"]:
            self.budgets = result["data"]
            actif = next((b for b in self.budgets if b["statut"] == "en_cours"), None)
            self.budget_actif = actif

            if actif:
                self.show_budget_resume(actif)
            else:
                self.budget_actif_group.hide()
        else:
            QMessageBox.critical(self, "Erreur", result["message"])

    def show_budget_resume(self, budget):
        # Effet de transition
        if self.budget_actif_group.isVisible():
            hide_animation = QPropertyAnimation(self.budget_actif_group, b"windowOpacity")
            hide_animation.setDuration(200)
            hide_animation.setStartValue(1)
            hide_animation.setEndValue(0)
            hide_animation.finished.connect(lambda: self.update_budget_display(budget))
            hide_animation.start()
        else:
            self.update_budget_display(budget)
            show_animation = QPropertyAnimation(self.budget_actif_group, b"windowOpacity")
            show_animation.setDuration(300)
            show_animation.setStartValue(0)
            show_animation.setEndValue(1)
            show_animation.start()
    def update_budget_display(self, budget):
        # Nettoyer l'affichage existant
        while self.budget_actif_group.layout().count():
            item = self.budget_actif_group.layout().takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Données backend déjà calculées
        total = budget['montant_total']
        dispo = budget['montant_disponible']
        montant_total_recettes = budget['montant_total_recettes']
        montant_total_depenses = budget['montant_total_depenses_validees']
        # Calcul du montant global (initial + recettes)
        montant_global = total + montant_total_recettes

        # Sécurité division
        utilise = montant_total_depenses
        pourcentage_utilise = (utilise / montant_global) * 100 if montant_global > 0 else 0


        # Layout container
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        # Colonne gauche
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Colonne droite
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        # Style labels
        label_style = """
            font-size: 13px;
            padding: 6px 10px;
            border-radius: 4px;
            background-color: #f5f7fa;
            margin: 1px 0;
        """

        # Infos affichées
        left_layout.addWidget(QLabel(f"🏛  EXERCICE: <b><span style='color:#0078D7;'>{budget['exercice']}</span></b>"))
        left_layout.addWidget(QLabel(f"💰  TOTAL: <b><span style='color:#4CAF50;'>{total:,.0f} F</span></b>"))
        right_layout.addWidget(QLabel(f"💵  DISPONIBLE: <b><span style='color:#2196F3;'>{dispo:,.0f} F</span></b>"))
        right_layout.addWidget(QLabel(
            f"🛒  UTILISÉ: <b><span style='color:#FF9800;'>{utilise:,.0f} F</span> ({pourcentage_utilise:.1f}%)</b>"))

        statut_color = "#4CAF50" if budget['statut'] == 'en_cours' else "#F44336"
        left_layout.addWidget(QLabel(
            f"📊  STATUT: <b><span style='color:{statut_color};'>{budget['statut'].upper().replace('_', ' ')}</span></b>"))

        # Organiser colonnes
        info_layout.addWidget(left_column)
        info_layout.addWidget(right_column)

        # Ajouter au groupe
        self.budget_actif_group.layout().addWidget(info_container)

        # Espacement et dashboard
        self.budget_actif_group.layout().addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        dashboard = BudgetDashboardWidget(budget)
        self.budget_actif_group.layout().addWidget(dashboard)

        self.budget_actif_group.show()

    def ouvrir_dialogue_modification(self):
        if not self.budget_actif:
            self.show_error_message("Aucun budget actif", "Aucun budget en cours sélectionné.")
            return

        dialog = ModifierBudgetDialog(self.budget_actif, self)
        if dialog.exec_():
            self.load_budgets()

    def cloturer_budget(self):
        if not self.budget_actif:
            self.show_error_message("Aucun budget actif", "Aucun budget en cours sélectionné.")
            return

        exercice = self.budget_actif.get("exercice", "cet exercice")
        reply = self.show_confirmation_dialog(
            "Confirmation de clôture",
            f"Voulez-vous vraiment clôturer le budget {exercice} ?",
            "Cette action est irréversible. Vous pourrez toujours consulter le budget dans les archives."
        )

        if reply == QMessageBox.Yes:
            response = cloturer_budget(self.budget_actif.get("id"))
            if response["success"]:
                self.show_success_message("Succès", response["message"])
                self.load_budgets()
            else:
                self.show_error_message("Erreur", response["message"])

    def supprimer_budget(self):
        if not self.budget_actif:
            self.show_error_message("Aucun budget actif", "Aucun budget en cours sélectionné.")
            return

        exercice = self.budget_actif.get("exercice", "cet exercice")
        reply = self.show_confirmation_dialog(
            "Confirmation de suppression",
            f"Êtes-vous sûr de vouloir supprimer le budget {exercice} ?",
            "Cette action supprimera définitivement toutes les données associées à ce budget."
        )

        if reply == QMessageBox.Yes:
            response = delete_budget(self.budget_actif.get("id"))
            if response["success"]:
                self.show_success_message("Succès", "Budget supprimé avec succès.")
                self.load_budgets()
            else:
                self.show_error_message("Erreur", response["message"])

    def ouvrir_lignes_budgetaires(self):
        if not self.budget_actif:
            self.show_error_message("Aucun budget actif", "Aucun budget en cours sélectionné.")
            return

        dialog = LigneBudgetaireDialog(self.budget_actif, self)
        dialog.exec_()

    def afficher_budgets_clotures(self):
        dialog = BudgetsCloturesDialog(self)
        dialog.exec_()

    def creer_budget(self):
        dialog = BudgetFormDialog(self)
        if dialog.exec_():
            self.load_budgets()

    def show_error_message(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 13px;
            }
            QMessageBox QLabel {
                color: #721c24;
            }
            QMessageBox QPushButton {
                padding: 5px 15px;
                border-radius: 4px;
                background-color: #f1f1f1;
            }
        """)
        msg.exec_()

    def show_success_message(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 13px;
            }
            QMessageBox QLabel {
                color: #155724;
            }
            QMessageBox QPushButton {
                padding: 5px 15px;
                border-radius: 4px;
                background-color: #f1f1f1;
            }
        """)
        msg.exec_()

    def show_confirmation_dialog(self, title, question, details):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(title)
        msg.setText(question)
        msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f8f9fa;
                font-size: 13px;
            }
            QMessageBox QLabel {
                color: #004085;
            }
            QMessageBox QPushButton[text="Yes"] {
                background-color: #dc3545;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QMessageBox QPushButton[text="Oui"] {
                background-color: #dc3545;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QMessageBox QPushButton[text="No"] {
                background-color: #f8f9fa;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QMessageBox QPushButton[text="Non"] {
                background-color: #f8f9fa;
                padding: 5px 15px;
                border-radius: 4px;
            }
        """)
        return msg.exec_()