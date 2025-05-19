from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, QComboBox,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont
from services.commande_service import get_commandes, delete_commande, valider_commande
from ui.modules.commande_form_dialog import CommandeFormDialog
from ui.modules.fournisseurs_widget import FournisseursWidget
from services.auth_service import AuthService
import datetime


class CommandesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = AuthService.get_user_role()
        self.commandes = []
        self.filtered_commandes = []
        self.setup_ui()
        self.load_commandes()
        self.setup_animations()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QToolTip {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()

        title = QLabel("GESTION DES COMMANDES")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header.addWidget(title)

        header.addStretch()

        # Boutons d'action
        btn_layout = QHBoxLayout()

        # Bouton Nouvelle Commande
        self.ajouter_btn = QPushButton("➕ Nouvelle Commande")
        self.ajouter_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.ajouter_btn.setCursor(Qt.PointingHandCursor)
        self.ajouter_btn.clicked.connect(self.open_form)
        self.ajouter_btn.setToolTip("Ajouter une nouvelle commande")
        btn_layout.addWidget(self.ajouter_btn)

        # Bouton Gérer Fournisseurs
        self.fournisseur_btn = QPushButton("🏢 Gérer Fournisseurs")
        self.fournisseur_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.fournisseur_btn.setCursor(Qt.PointingHandCursor)
        self.fournisseur_btn.clicked.connect(self.open_fournisseurs)
        self.fournisseur_btn.setToolTip("Gérer la liste des fournisseurs")
        btn_layout.addWidget(self.fournisseur_btn)

        # Si l'utilisateur n'est pas comptable, désactiver les boutons
        if self.user_role != "comptable":
            self.ajouter_btn.setVisible(False)
            self.fournisseur_btn.setVisible(False)

        header.addLayout(btn_layout)
        layout.addLayout(header)

        # Ajout d'une barre de filtres
        filter_bar = QHBoxLayout()

        # Filtre par statut
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous les statuts", "tous")
        self.status_filter.addItem("En attente", "en_attente")
        self.status_filter.addItem("Validée", "validee")
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        self.status_filter.currentIndexChanged.connect(self.apply_filters)
        filter_bar.addWidget(QLabel("Statut:"))
        filter_bar.addWidget(self.status_filter)

        # Filtre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.apply_filters)
        filter_bar.addWidget(QLabel("Recherche:"))
        filter_bar.addWidget(self.search_input)

        filter_bar.addStretch()

        # Affichage du nombre de résultats
        self.results_label = QLabel("0 commandes")
        self.results_label.setStyleSheet("color: #7f8c8d;")
        filter_bar.addWidget(self.results_label)

        layout.addLayout(filter_bar)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Réf", "Désignation", "Ligne", "Montant", "Statut", "Actions"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                gridline-color: #ecf0f1;
                font-size: 13px;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #e0f2fe;
                color: #2c3e50;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        # Ajouter un effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        self.table.setGraphicsEffect(shadow)

        layout.addWidget(self.table)

        # Ajout d'une barre de statut
        status_bar = QHBoxLayout()

        # Date de dernière mise à jour
        self.update_label = QLabel(f"Dernière mise à jour: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
        self.update_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        status_bar.addWidget(self.update_label)

        status_bar.addStretch()

        # Bouton de rafraîchissement
        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d5dbdb;
            }
        """)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_data)
        status_bar.addWidget(refresh_btn)

        layout.addLayout(status_bar)

    def load_commandes(self):
        result = get_commandes()
        if result["success"]:
            self.commandes = result["data"]
            self.filtered_commandes = self.commandes
            self.apply_filters()
        else:
            self.show_error_message("Erreur", result["message"])

    def apply_filters(self):
        # Récupérer les valeurs des filtres
        status_filter = self.status_filter.currentData()
        search_text = self.search_input.text().lower()

        # Filtrer les commandes
        self.filtered_commandes = []
        for commande in self.commandes:
            # Filtre par statut
            if status_filter != "tous" and commande["statut"] != status_filter:
                continue

            # Filtre par texte de recherche
            searchable_text = (
                    commande["reference"].lower() +
                    commande["designation"].lower() +
                    str(commande["ligne_budgetaire"]) +
                    str(commande["total"]) +
                    commande["statut"].lower()
            )

            if search_text and search_text not in searchable_text:
                continue

            self.filtered_commandes.append(commande)

        # Mettre à jour le tableau
        self.update_table()

        # Mettre à jour le compteur de résultats
        self.results_label.setText(f"{len(self.filtered_commandes)} commande(s) trouvée(s)")

    def update_table(self):
        self.table.setRowCount(len(self.filtered_commandes))

        for i, cmd in enumerate(self.filtered_commandes):
            # Référence
            ref_item = QTableWidgetItem(cmd["reference"])
            self.table.setItem(i, 0, ref_item)

            # Désignation
            designation_item = QTableWidgetItem(cmd["designation"])
            self.table.setItem(i, 1, designation_item)

            # Ligne budgétaire
            ligne_item = QTableWidgetItem(str(cmd["ligne_budgetaire"]))
            self.table.setItem(i, 2, ligne_item)

            # Montant (aligné à droite)
            montant_item = QTableWidgetItem(f"{cmd['total']:,} F")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 3, montant_item)

            # Statut avec couleur
            statut_item = QTableWidgetItem(cmd["statut"].replace("_", " ").capitalize())

            # Coloration selon le statut
            if cmd["statut"] == "en_attente":
                statut_item.setForeground(QColor("#f39c12"))
            elif cmd["statut"] == "validee":
                statut_item.setForeground(QColor("#27ae60"))

            self.table.setItem(i, 4, statut_item)

            # Actions
            action_widget = self.create_action_widget(cmd)
            self.table.setCellWidget(i, 5, action_widget)

    def create_action_widget(self, cmd):
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 0, 5, 0)
        action_layout.setSpacing(8)

        # N'afficher les boutons d'action que si l'utilisateur est comptable
        if self.user_role == "comptable" and cmd["statut"] == "en_attente":
            # Bouton Valider
            valider_btn = QPushButton("✅ Valider")
            valider_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                    min-width: 80px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2ecc71;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                QPushButton:pressed {
                    background-color: #219653;
                }
            """)
            valider_btn.setToolTip("Valider cette commande")
            valider_btn.setCursor(Qt.PointingHandCursor)
            valider_btn.clicked.connect(lambda _, id=cmd["id"]: self.valider_commande(id))
            action_layout.addWidget(valider_btn)

            # Bouton Supprimer
            supprimer_btn = QPushButton("🗑 Supprimer")
            supprimer_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                    min-width: 80px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                QPushButton:pressed {
                    background-color: #922b21;
                }
            """)
            supprimer_btn.setToolTip("Supprimer cette commande")
            supprimer_btn.setCursor(Qt.PointingHandCursor)
            supprimer_btn.clicked.connect(lambda _, id=cmd["id"]: self.supprimer_commande(id))
            action_layout.addWidget(supprimer_btn)
        elif cmd["statut"] == "validee":
            # Afficher un indicateur visuel pour les commandes validées
            status_label = QLabel("✅ Validée")
            status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            action_layout.addWidget(status_label)
        else:
            # Pour les autres utilisateurs ou les commandes déjà validées
            if self.user_role != "comptable":
                status_label = QLabel("🔒 Accès en lecture seule")
                status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
                action_layout.addWidget(status_label)

        action_layout.addStretch()
        return action_widget

    def open_form(self):
        dialog = CommandeFormDialog(self)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "La commande a été créée avec succès!")

    def open_fournisseurs(self):
        dialog = FournisseursWidget()
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        dialog.exec_()
        # Rafraîchir au cas où des modifications de fournisseurs affecteraient les commandes
        self.refresh_data()

    def valider_commande(self, commande_id):
        confirm = self.show_confirmation_dialog(
            "Validation de commande",
            "Voulez-vous valider cette commande ?",
            "Une fois validée, la commande ne pourra plus être modifiée."
        )
        if confirm == QMessageBox.Yes:
            result = valider_commande(commande_id, "validee")
            if result["success"]:
                self.show_success_message("Succès", "La commande a été validée avec succès!")
                self.refresh_data()
            else:
                self.show_error_message("Erreur", result["message"])

    def supprimer_commande(self, commande_id):
        confirm = self.show_confirmation_dialog(
            "Confirmation de suppression",
            "Voulez-vous vraiment supprimer cette commande ?",
            "Cette action est irréversible."
        )
        if confirm == QMessageBox.Yes:
            result = delete_commande(commande_id)
            if result["success"]:
                self.show_success_message("Succès", "La commande a été supprimée avec succès!")
                self.refresh_data()
            else:
                self.show_error_message("Erreur", result["message"])

    def setup_animations(self):
        # Animation d'apparition du tableau
        self.anim = QPropertyAnimation(self.table, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def refresh_data(self):
        self.load_commandes()
        self.update_label.setText(f"Dernière mise à jour: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Animation de rafraîchissement
        anim = QPropertyAnimation(self.table, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0.5)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def show_error_message(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #e74c3c;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
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
                background-color: white;
            }
            QMessageBox QLabel {
                color: #27ae60;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        msg.exec_()

    def show_confirmation_dialog(self, title, question, details=""):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(title)
        msg.setText(question)
        if details:
            msg.setInformativeText(details)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                min-width: 60px;
            }
            QMessageBox QPushButton[text="Yes"], 
            QMessageBox QPushButton[text="Oui"] {
                background-color: #27ae60;
                color: white;
            }
            QMessageBox QPushButton[text="Yes"]:hover, 
            QMessageBox QPushButton[text="Oui"]:hover {
                background-color: #2ecc71;
            }
            QMessageBox QPushButton[text="No"], 
            QMessageBox QPushButton[text="Non"] {
                background-color: #e74c3c;
                color: white;
            }
            QMessageBox QPushButton[text="No"]:hover, 
            QMessageBox QPushButton[text="Non"]:hover {
                background-color: #c0392b;
            }
        """)
        return msg.exec_()