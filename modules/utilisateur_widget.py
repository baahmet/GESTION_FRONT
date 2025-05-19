from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QHeaderView, QGraphicsDropShadowEffect, QLabel
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QBrush

from ui.modules.utilisateur_form_dialog import UtilisateurFormDialog
from services.utilisateur_service import get_utilisateurs, delete_utilisateur
from services.auth_service import AuthService


class UtilisateursWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = AuthService.get_user_role()
        self.setup_ui_style()
        self.init_ui()
        self.load_utilisateurs()
        self.setup_animations()

    def setup_ui_style(self):
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

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()

        title = QLabel("GESTION DES UTILISATEURS")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header.addWidget(title)

        header.addStretch()

        # Bouton Ajouter
        self.create_btn = QPushButton("➕ Ajouter un Utilisateur")
        self.create_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.clicked.connect(self.open_create_dialog)
        self.create_btn.setToolTip("Ajouter un nouvel utilisateur")

        # Désactiver si pas admin
        if self.user_role != "comptable":
            self.create_btn.setEnabled(False)

        header.addWidget(self.create_btn)

        layout.addLayout(header)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Nom", "Email", "Rôle", "Date création", "Actions"])
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

        # Configuration du tableau
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        self.table.setGraphicsEffect(shadow)

        layout.addWidget(self.table)

    def load_utilisateurs(self):
        # Animation de chargement
        self.start_loading_animation()

        result = get_utilisateurs()

        if result["success"]:
            utilisateurs = result["data"]
            self.table.setRowCount(len(utilisateurs))

            for i, utilisateur in enumerate(utilisateurs):
                # Nom
                nom_item = QTableWidgetItem(utilisateur["nom"])
                self.table.setItem(i, 0, nom_item)

                # Email
                email_item = QTableWidgetItem(utilisateur["email"])
                self.table.setItem(i, 1, email_item)

                # Rôle
                role = utilisateur["role"].capitalize()
                role_item = QTableWidgetItem(role)

                # Colorer selon le rôle
                if role == "Comptable":
                    role_item.setForeground(QBrush(QColor("#3498db")))
                elif role == "Directeur":
                    role_item.setForeground(QBrush(QColor("#27ae60")))
                elif role == "CSA":
                    role_item.setForeground(QBrush(QColor("#9b59b6")))

                self.table.setItem(i, 2, role_item)

                # Date création
                date_item = QTableWidgetItem(utilisateur["date_creation"][:19])
                date_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 3, date_item)

                # Actions
                action_widget = self.create_action_widget(utilisateur)
                self.table.setCellWidget(i, 4, action_widget)

                # Alternance des couleurs de ligne
                if i % 2 == 0:
                    for j in range(self.table.columnCount()):
                        if self.table.item(i, j):
                            self.table.item(i, j).setBackground(QColor("#f8f9fa"))
        else:
            self.show_error_message("Erreur", result["message"])

        # Fin de l'animation de chargement
        self.stop_loading_animation()

    def create_action_widget(self, utilisateur):
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 0, 5, 0)
        action_layout.setSpacing(8)

        # Bouton Modifier
        modifier_btn = QPushButton("✏️ Modifier")
        modifier_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
                min-width: 80px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e67e22;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        modifier_btn.setToolTip("Modifier cet utilisateur")
        modifier_btn.setCursor(Qt.PointingHandCursor)
        modifier_btn.clicked.connect(lambda _, u=utilisateur: self.open_edit_dialog(u))

        # Désactiver si pas admin
        if self.user_role == "comptable" and "directeur" and "csa":
            modifier_btn.setVisible(False)

        action_layout.addWidget(modifier_btn)

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
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        supprimer_btn.setToolTip("Supprimer cet utilisateur")
        supprimer_btn.setCursor(Qt.PointingHandCursor)
        supprimer_btn.clicked.connect(lambda _, u_id=utilisateur["id"]: self.supprimer_utilisateur(u_id))

        # Désactiver si pas admin ou si c'est le compte actuel
        if self.user_role != "comptable" or utilisateur["id"] == AuthService.user_data.get("id"):
            supprimer_btn.setEnabled(False)

        action_layout.addWidget(supprimer_btn)

        action_layout.addStretch()
        return action_widget

    def start_loading_animation(self):
        self.create_btn.setEnabled(False)
        self.create_btn.setText("⏳ Chargement...")

        self.loading_anim = QPropertyAnimation(self.table, b"windowOpacity")
        self.loading_anim.setDuration(300)
        self.loading_anim.setStartValue(1)
        self.loading_anim.setEndValue(0.5)
        self.loading_anim.start()

    def stop_loading_animation(self):
        self.create_btn.setEnabled(self.user_role == "comptable")
        self.create_btn.setText("➕ Ajouter un Utilisateur")

        self.loading_anim.setDirection(self.loading_anim.Backward)
        self.loading_anim.start()

    def setup_animations(self):
        # Animation d'apparition du tableau
        self.anim = QPropertyAnimation(self.table, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def open_create_dialog(self):
        dialog = UtilisateurFormDialog(self)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.load_utilisateurs()
            self.show_success_message("Succès", "Utilisateur créé avec succès!")

    def open_edit_dialog(self, utilisateur):
        dialog = UtilisateurFormDialog(self, utilisateur_data=utilisateur)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.load_utilisateurs()
            self.show_success_message("Succès", "Utilisateur modifié avec succès!")

    def supprimer_utilisateur(self, utilisateur_id):
        reply = self.show_confirmation_dialog(
            "Confirmation de suppression",
            "Voulez-vous vraiment supprimer cet utilisateur ?",
            "Cette action est irréversible."
        )
        if reply == QMessageBox.Yes:
            result = delete_utilisateur(utilisateur_id)
            if result["success"]:
                self.show_success_message("Succès", "Utilisateur supprimé avec succès!")
                self.load_utilisateurs()
            else:
                self.show_error_message("Erreur", result["message"])

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