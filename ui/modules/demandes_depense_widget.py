from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QWidget, QLineEdit,
                             QComboBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont
from services.auth_service import AuthService
from services.demande_depense_service import get_demandes_depense, create_demande_depense, valider_demande_depense, \
    delete_demande_depense
from ui.modules.demande_depense_form_dialog import DemandeDepenseFormDialog
import datetime


class DemandesDepenseWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_role = AuthService.get_user_role()
        self.setWindowTitle("Demandes de Dépense")
        self.resize(800, 500)
        self.demandes = []
        self.filtered_demandes = []
        self.setup_ui()
        self.load_demandes()
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

        title = QLabel("GESTION DES DEMANDES DE DÉPENSE")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header.addWidget(title)

        header.addStretch()

        # Bouton principal pour ajouter
        self.create_btn = QPushButton("➕ Nouvelle demande")
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
        """)
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.clicked.connect(self.open_form_dialog)
        self.create_btn.setToolTip("Ajouter une nouvelle demande de dépense")
        header.addWidget(self.create_btn)

        # Si CSA ou Directeur → désactiver création
        if self.user_role in ["csa", "directeur"]:
            self.create_btn.setEnabled(False)
            self.create_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: 500;
                    font-size: 13px;
                }
            """)

        layout.addLayout(header)

        # Ajout d'une barre de filtres
        filter_bar = QHBoxLayout()

        # Filtre par statut
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous les statuts", "tous")
        self.status_filter.addItem("En attente", "en_attente")
        self.status_filter.addItem("Approuvée", "approuvée")
        self.status_filter.addItem("Refusée", "refusée")
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
        self.results_label = QLabel("0 demandes")
        self.results_label.setStyleSheet("color: #7f8c8d;")
        filter_bar.addWidget(self.results_label)

        layout.addLayout(filter_bar)

        # Tableau des demandes
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Motif", "Montant estimé", "Statut", "Demandeur", "Actions"])
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

    def setup_animations(self):
        # Animation d'apparition du tableau
        self.anim = QPropertyAnimation(self.table, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def load_demandes(self):
        result = get_demandes_depense()
        if result["success"]:
            self.demandes = result["data"]
            self.filtered_demandes = self.demandes
            self.apply_filters()
        else:
            self.show_error_message("Erreur", result["message"])

    def apply_filters(self):
        # Récupérer les valeurs des filtres
        status_filter = self.status_filter.currentData()
        search_text = self.search_input.text().lower()

        # Filtrer les demandes
        self.filtered_demandes = []
        for demande in self.demandes:
            # Filtre par statut
            if status_filter != "tous" and demande["statut"] != status_filter:
                continue

            # Filtre par texte de recherche
            searchable_text = (
                    demande["motif"].lower() +
                    str(demande["montant_estime"]) +
                    demande["statut"].lower() +
                    demande["utilisateur_nom"].lower()
            )

            if search_text and search_text not in searchable_text:
                continue

            self.filtered_demandes.append(demande)

        # Mettre à jour le tableau
        self.update_table()

        # Mettre à jour le compteur de résultats
        self.results_label.setText(f"{len(self.filtered_demandes)} demande(s) trouvée(s)")

    def update_table(self):
        self.table.setRowCount(len(self.filtered_demandes))

        for i, demande in enumerate(self.filtered_demandes):
            # Motif
            motif_item = QTableWidgetItem(demande["motif"])
            self.table.setItem(i, 0, motif_item)

            # Montant (aligné à droite)
            montant_item = QTableWidgetItem(f"{demande['montant_estime']:,} F")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 1, montant_item)

            # Statut avec couleur
            statut_item = QTableWidgetItem(demande["statut"].capitalize())

            # Coloration selon le statut
            if demande["statut"] == "en_attente":
                statut_item.setForeground(QColor("#f39c12"))
            elif demande["statut"] == "approuvée":
                statut_item.setForeground(QColor("#27ae60"))
            elif demande["statut"] == "refusée":
                statut_item.setForeground(QColor("#e74c3c"))

            self.table.setItem(i, 2, statut_item)

            # Utilisateur
            user_item = QTableWidgetItem(demande["utilisateur_nom"])
            self.table.setItem(i, 3, user_item)

            # Actions
            action_widget = self.create_action_widget(demande)
            self.table.setCellWidget(i, 4, action_widget)

    def create_action_widget(self, demande):
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 0, 5, 0)
        action_layout.setSpacing(8)

        if demande["statut"] == "en_attente":
            # Directeur : Valider / Refuser
            if self.user_role == "directeur":
                btn_valider = QPushButton("✅ Valider")
                btn_valider.setStyleSheet("""
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
                btn_valider.setToolTip("Approuver cette demande")
                btn_valider.setCursor(Qt.PointingHandCursor)
                btn_valider.clicked.connect(lambda _, d_id=demande["id"]: self.valider_demande(d_id, True))
                action_layout.addWidget(btn_valider)

                btn_refuser = QPushButton("❌ Refuser")
                btn_refuser.setStyleSheet("""
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
                btn_refuser.setToolTip("Refuser cette demande")
                btn_refuser.setCursor(Qt.PointingHandCursor)
                btn_refuser.clicked.connect(lambda _, d_id=demande["id"]: self.valider_demande(d_id, False))
                action_layout.addWidget(btn_refuser)

            # Comptable : Modifier / Supprimer
            if self.user_role == "comptable":
                btn_modifier = QPushButton("✏️ Modifier")
                btn_modifier.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-size: 12px;
                        min-width: 80px;
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
                btn_modifier.setToolTip("Modifier cette demande")
                btn_modifier.setCursor(Qt.PointingHandCursor)
                btn_modifier.clicked.connect(lambda _, d_id=demande["id"]: self.modifier_demande(d_id))
                action_layout.addWidget(btn_modifier)

                btn_supprimer = QPushButton("🗑 Supprimer")
                btn_supprimer.setStyleSheet("""
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
                btn_supprimer.setToolTip("Supprimer cette demande")
                btn_supprimer.setCursor(Qt.PointingHandCursor)
                btn_supprimer.clicked.connect(lambda _, d_id=demande["id"]: self.supprimer_demande(d_id))
                action_layout.addWidget(btn_supprimer)
        else:
            # Si la demande n'est pas en attente, afficher un statut visuel
            status_text = "Approuvée" if demande["statut"] == "approuvée" else "Refusée"
            status_color = "#27ae60" if demande["statut"] == "approuvée" else "#e74c3c"
            status_icon = "✅" if demande["statut"] == "approuvée" else "❌"

            status_label = QLabel(f"{status_icon} {status_text}")
            status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
            action_layout.addWidget(status_label)

        action_layout.addStretch()
        return action_widget

    def open_form_dialog(self):
        dialog = DemandeDepenseFormDialog(self)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "La demande a été créée avec succès!")

    def valider_demande(self, demande_id, valider):
        statut = "approuvée" if valider else "refusée"
        result = valider_demande_depense(demande_id, statut)
        if result["success"]:
            self.show_success_message("Succès", f"La demande a été {statut} avec succès!")
            self.refresh_data()
        else:
            self.show_error_message("Erreur", result["message"])

    def modifier_demande(self, demande_id):
        dialog = DemandeDepenseFormDialog(self, demande_id=demande_id)
        dialog.setWindowTitle("Modifier une demande")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "La demande a été modifiée avec succès!")

    def supprimer_demande(self, demande_id):
        confirm = self.show_confirmation_dialog(
            "Confirmation de suppression",
            "Voulez-vous vraiment supprimer cette demande ?",
            "Cette action est irréversible."
        )
        if confirm == QMessageBox.Yes:
            result = delete_demande_depense(demande_id)
            if result["success"]:
                self.show_success_message("Succès", "La demande a été supprimée avec succès!")
                self.refresh_data()
            else:
                self.show_error_message("Erreur", result["message"])

    def refresh_data(self):
        self.load_demandes()
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