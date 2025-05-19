from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QHBoxLayout, QFileDialog, QMessageBox, QGraphicsDropShadowEffect,
    QComboBox, QLineEdit
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QBrush
import datetime

from services.rapport_service import get_rapports, generer_rapport, telecharger_rapport, update_rapport, delete_rapport
from ui.modules.rapport_form_dialog import RapportFormDialog
from services.auth_service import AuthService


class RapportsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = AuthService.get_user_role()
        self.rapports = []
        self.filtered_rapports = []
        self.setup_ui_style()
        self.init_ui()
        self.load_rapports()
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

        title = QLabel("GESTION DES RAPPORTS")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header.addWidget(title)

        header.addStretch()

        # Bouton Générer un rapport (visible seulement pour comptable)
        self.create_btn = QPushButton("📊 Générer un rapport")
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
        self.create_btn.clicked.connect(self.open_form_dialog)
        self.create_btn.setToolTip("Générer un nouveau rapport")
        if self.user_role !="comptable":
            self.create_btn.setVisible(False)
        header.addWidget(self.create_btn)

        layout.addLayout(header)

        # Barre de filtres
        filter_bar = QHBoxLayout()

        # Filtre par type
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous les types", "tous")
        self.type_filter.addItem("PDF", "pdf")
        self.type_filter.addItem("EXCEL", "excel")
        self.type_filter.setStyleSheet("""
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
        self.type_filter.currentIndexChanged.connect(self.apply_filters)
        filter_bar.addWidget(QLabel("Type:"))
        filter_bar.addWidget(self.type_filter)

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
        self.results_label = QLabel("0 rapports")
        self.results_label.setStyleSheet("color: #7f8c8d;")
        filter_bar.addWidget(self.results_label)

        layout.addLayout(filter_bar)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Période", "Type", "Fichier", "Généré par", "Statut", "Actions"])
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

        # Barre de statut
        status_bar = QHBoxLayout()
        self.update_label = QLabel(f"Dernière mise à jour: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
        self.update_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        status_bar.addWidget(self.update_label)

        status_bar.addStretch()

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

    def load_rapports(self):
        result = get_rapports()
        if result["success"]:
            self.rapports = result["data"]
            self.filtered_rapports = self.rapports
            self.apply_filters()
        else:
            self.show_error_message("Erreur", result["message"])

    def apply_filters(self):
        type_filter = self.type_filter.currentData()
        search_text = self.search_input.text().lower()

        self.filtered_rapports = []
        for rapport in self.rapports:
            if type_filter != "tous" and rapport["type"] != type_filter:
                continue

            searchable_text = (
                    rapport["periode"].lower() +
                    rapport["type"].lower() +
                    (rapport.get("nom_fichier", "") or "").lower() +
                    (rapport.get("genere_par_nom", "") or "").lower()
            )

            if search_text and search_text not in searchable_text:
                continue

            self.filtered_rapports.append(rapport)

        self.update_table()
        self.results_label.setText(f"{len(self.filtered_rapports)} rapport(s) trouvé(s)")

    def update_table(self):
        self.table.setRowCount(len(self.filtered_rapports))

        for i, rapport in enumerate(self.filtered_rapports):
            # Période
            periode_item = QTableWidgetItem(rapport.get("periode", ""))
            self.table.setItem(i, 0, periode_item)

            # Type
            type_item = QTableWidgetItem(rapport.get("type", "").upper())
            self.table.setItem(i, 1, type_item)

            # Fichier
            fichier_item = QTableWidgetItem(rapport.get("nom_fichier", "Non généré"))
            self.table.setItem(i, 2, fichier_item)

            # Généré par
            genere_par_item = QTableWidgetItem(rapport.get("genere_par_nom", "Inconnu"))
            self.table.setItem(i, 3, genere_par_item)

            # Statut
            statut_item = QTableWidgetItem("Disponible" if rapport.get("nom_fichier") else "Non généré")
            statut_item.setTextAlignment(Qt.AlignCenter)
            if rapport.get("nom_fichier"):
                statut_item.setForeground(QBrush(QColor("#27ae60")))
            else:
                statut_item.setForeground(QBrush(QColor("#e74c3c")))
            self.table.setItem(i, 4, statut_item)

            # Actions
            action_widget = self.create_action_widget(rapport)
            self.table.setCellWidget(i, 5, action_widget)

            # Alternance des couleurs de ligne
            if i % 2 == 0:
                for j in range(self.table.columnCount()):
                    if self.table.item(i, j):
                        self.table.item(i, j).setBackground(QColor("#f8f9fa"))

    def create_action_widget(self, rapport):
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 0, 5, 0)
        action_layout.setSpacing(8)

        # Bouton Télécharger (visible si rapport disponible)
        if rapport.get("nom_fichier"):
            download_btn = QPushButton("⬇ Télécharger")
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                    min-width: 100px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                QPushButton:pressed {
                    background-color: #1f618d;
                }
            """)
            download_btn.setToolTip("Télécharger ce rapport")
            download_btn.setCursor(Qt.PointingHandCursor)
            download_btn.clicked.connect(lambda: self.telecharger_rapport(rapport["id"]))
            action_layout.addWidget(download_btn)

        # Boutons Modifier/Supprimer (seulement pour comptable)
        if self.user_role == "comptable":
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
            """)
            modifier_btn.setToolTip("Modifier ce rapport")
            modifier_btn.setCursor(Qt.PointingHandCursor)
            modifier_btn.clicked.connect(lambda: self.modifier_rapport(rapport))
            action_layout.addWidget(modifier_btn)

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
            supprimer_btn.setToolTip("Supprimer ce rapport")
            supprimer_btn.setCursor(Qt.PointingHandCursor)
            supprimer_btn.clicked.connect(lambda: self.supprimer_rapport(rapport["id"]))
            action_layout.addWidget(supprimer_btn)

        action_layout.addStretch()
        return action_widget

    def setup_animations(self):
        self.anim = QPropertyAnimation(self.table, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def refresh_data(self):
        self.load_rapports()
        self.update_label.setText(f"Dernière mise à jour: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")

        anim = QPropertyAnimation(self.table, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0.5)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()

    def open_form_dialog(self):
        dialog = RapportFormDialog(self)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "Le rapport a été généré avec succès!")

    def modifier_rapport(self, rapport):
        dialog = RapportFormDialog(self, rapport)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "Le rapport a été modifié avec succès!")

    def supprimer_rapport(self, rapport_id):
        confirm = self.show_confirmation_dialog(
            "Confirmation de suppression",
            "Voulez-vous vraiment supprimer ce rapport ?",
            "Cette action est irréversible."
        )
        if confirm == QMessageBox.Yes:
            result = delete_rapport(rapport_id)
            if result["success"]:
                self.show_success_message("Succès", "Le rapport a été supprimé avec succès!")
                self.refresh_data()
            else:
                self.show_error_message("Erreur", result["message"])

    def telecharger_rapport(self, rapport_id):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer le rapport",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        if path:
            result = telecharger_rapport(rapport_id, path)
            if result["success"]:
                self.show_success_message("Succès", "Rapport téléchargé avec succès!")
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