from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHBoxLayout, QMessageBox, QLineEdit, QFormLayout,
                             QHeaderView, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont
from services.fournisseur_service import get_fournisseurs, create_fournisseur
import datetime


class FournisseursWidget(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Fournisseurs")
        self.resize(800, 500)
        self.setup_ui()
        self.load_fournisseurs()
        self.setup_animations()

    def setup_ui(self):
        # Style global
        self.setStyleSheet("""
            QDialog {
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

        # En-tête
        header = QHBoxLayout()

        title = QLabel("GESTION DES FOURNISSEURS")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Tableau des fournisseurs
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nom", "Type", "Téléphone", "NINEA"])
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

        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        self.table.setGraphicsEffect(shadow)

        layout.addWidget(self.table)

        # Formulaire d'ajout avec style amélioré
        form_container = QVBoxLayout()

        form_title = QLabel("Ajouter un nouveau fournisseur")
        form_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-top: 10px;
            }
        """)
        form_container.addWidget(form_title)

        # Style commun pour les QLineEdit
        line_edit_style = """
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """

        # Style pour les labels du formulaire
        label_style = """
            QLabel {
                font-weight: 500;
                color: #34495e;
            }
        """

        # Disposition du formulaire en grid
        form_layout = QFormLayout()
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(10)

        self.nom_input = QLineEdit()
        self.nom_input.setStyleSheet(line_edit_style)
        self.nom_input.setPlaceholderText("Nom du fournisseur")

        self.type_input = QLineEdit()
        self.type_input.setStyleSheet(line_edit_style)
        self.type_input.setPlaceholderText("Type de fournisseur")

        self.tel_input = QLineEdit()
        self.tel_input.setStyleSheet(line_edit_style)
        self.tel_input.setPlaceholderText("Numéro de téléphone")

        self.ninea_input = QLineEdit()
        self.ninea_input.setStyleSheet(line_edit_style)
        self.ninea_input.setPlaceholderText("Numéro NINEA")

        # Ajout des champs au formulaire
        nom_label = QLabel("Nom:")
        nom_label.setStyleSheet(label_style)
        form_layout.addRow(nom_label, self.nom_input)

        type_label = QLabel("Type:")
        type_label.setStyleSheet(label_style)
        form_layout.addRow(type_label, self.type_input)

        tel_label = QLabel("Téléphone:")
        tel_label.setStyleSheet(label_style)
        form_layout.addRow(tel_label, self.tel_input)

        ninea_label = QLabel("NINEA:")
        ninea_label.setStyleSheet(label_style)
        form_layout.addRow(ninea_label, self.ninea_input)

        form_container.addLayout(form_layout)

        # Boutons d'action
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)

        # Bouton ajouter
        self.ajouter_btn = QPushButton("➕ Ajouter Fournisseur")
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
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.ajouter_btn.setCursor(Qt.PointingHandCursor)
        self.ajouter_btn.clicked.connect(self.ajouter_fournisseur)
        self.ajouter_btn.setToolTip("Enregistrer ce nouveau fournisseur")

        # Bouton effacer
        self.clear_btn = QPushButton("🗑️ Effacer")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
        """)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_form)
        self.clear_btn.setToolTip("Vider les champs du formulaire")

        buttons_layout.addWidget(self.ajouter_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()

        form_container.addLayout(buttons_layout)
        layout.addLayout(form_container)

        # Barre de statut
        status_bar = QHBoxLayout()

        # Date de dernière mise à jour
        self.update_label = QLabel(f"Dernière mise à jour: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
        self.update_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        status_bar.addWidget(self.update_label)

        status_bar.addStretch()

        # Bouton rafraîchir
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

    def load_fournisseurs(self):
        result = get_fournisseurs()
        if result["success"]:
            fournisseurs = result["data"]
            self.table.setRowCount(len(fournisseurs))
            for i, f in enumerate(fournisseurs):
                self.table.setItem(i, 0, QTableWidgetItem(f["nom"]))
                self.table.setItem(i, 1, QTableWidgetItem(f["type"]))
                self.table.setItem(i, 2, QTableWidgetItem(f["telephone"]))
                self.table.setItem(i, 3, QTableWidgetItem(f["ninea"]))

            # Mettre à jour le compteur
            self.update_label.setText(
                f"Dernière mise à jour: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} • {len(fournisseurs)} fournisseur(s)")
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
        self.load_fournisseurs()

        # Animation de rafraîchissement
        anim = QPropertyAnimation(self.table, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0.5)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def clear_form(self):
        self.nom_input.clear()
        self.type_input.clear()
        self.tel_input.clear()
        self.ninea_input.clear()

    def ajouter_fournisseur(self):
        # Validation basique
        if not self.nom_input.text() or not self.type_input.text():
            self.show_error_message("Champs requis", "Le nom et le type de fournisseur sont obligatoires.")
            return

        data = {
            "nom": self.nom_input.text(),
            "type": self.type_input.text(),
            "telephone": self.tel_input.text(),
            "ninea": self.ninea_input.text(),
            "email": "contact@fournisseur.sn",  # Placeholder
            "adresse": "Adresse fictive",  # Placeholder
            "numero_rc": "RC12345"  # Placeholder
        }

        result = create_fournisseur(data)
        if result["success"]:
            self.show_success_message("Succès", "Le fournisseur a été ajouté avec succès!")
            self.clear_form()
            self.refresh_data()
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