from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QHBoxLayout,
                             QLineEdit, QComboBox, QGraphicsDropShadowEffect, QToolTip)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSortFilterProxyModel, QDate, pyqtSlot
from PyQt5.QtGui import QColor, QBrush, QFont, QIcon, QPalette

from services.auth_service import AuthService
from services.depense_service import (get_depenses, create_depense, superviser_depense,
                                      valider_depense, update_depense, delete_depense)

from ui.modules.depense_form_dialog import DepenseFormDialog
from ui.modules.demandes_depense_widget import DemandesDepenseWidget
import datetime
import math


class DepensesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = AuthService.get_user_role()
        self.all_depenses = []
        self.filtered_depenses = []
        self.current_page = 1
        self.items_per_page = 10
        self.setup_ui()
        self.load_depenses()
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

        title = QLabel("GESTION DES DÉPENSES")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header.addWidget(title)

        # Ajout d'un label pour le rôle de l'utilisateur
        role_label = QLabel(f"Connecté en tant que: {self.user_role.upper()}")
        role_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #7f8c8d;
                background-color: #ecf0f1;
                padding: 3px 8px;
                border-radius: 10px;
            }
        """)
        header.addWidget(role_label)

        header.addStretch()

        # Boutons principaux avec améliorations
        self.create_btn = QPushButton("➕ Nouvelle Dépense")
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
        self.create_btn.setToolTip("Créer une nouvelle demande de dépense")
        header.addWidget(self.create_btn)

        self.demande_btn = QPushButton("📩 Demandes en Attente")
        self.demande_btn.setStyleSheet("""
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
        self.demande_btn.setCursor(Qt.PointingHandCursor)
        self.demande_btn.clicked.connect(self.open_demandes_widget)
        self.demande_btn.setToolTip("Voir toutes les demandes en attente")
        header.addWidget(self.demande_btn)

        layout.addLayout(header)

        # Désactiver création pour CSA & Directeur
        if self.user_role in ["directeur", "csa"]:
            self.create_btn.setVisible(False)

        # Ajout d'une barre de filtres
        filter_bar = QHBoxLayout()

        # Filtre par statut
        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous les statuts", "tous")
        self.status_filter.addItem("En attente", "en_attente")
        self.status_filter.addItem("Validées", "validee")
        self.status_filter.addItem("Rejetées", "rejettee")
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

        # Sélecteur d'éléments par page
        self.items_per_page_combo = QComboBox()
        self.items_per_page_combo.addItems(["5", "10", "20", "50", "100"])
        self.items_per_page_combo.setCurrentText("10")
        self.items_per_page_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                min-width: 80px;
            }
        """)
        self.items_per_page_combo.currentTextChanged.connect(self.change_items_per_page)
        filter_bar.addWidget(QLabel("Items par page:"))
        filter_bar.addWidget(self.items_per_page_combo)

        # Affichage du nombre de résultats
        self.results_label = QLabel("0 dépenses")
        self.results_label.setStyleSheet("color: #7f8c8d;")
        filter_bar.addWidget(self.results_label)

        layout.addLayout(filter_bar)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Montant", "Ligne Budgétaire", "Statut", "Actions"])
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

        # Pagination
        self.pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(self.pagination_widget)
        pagination_layout.setContentsMargins(0, 10, 0, 10)
        pagination_layout.setSpacing(5)

        self.prev_btn = QPushButton("◀")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;
                color: #2c3e50;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:disabled {
                background-color: #ecf0f1;
                color: #95a5a6;
            }
        """)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self.go_to_previous_page)
        self.prev_btn.setToolTip("Page précédente")
        pagination_layout.addWidget(self.prev_btn)

        self.page_buttons_layout = QHBoxLayout()
        self.page_buttons_layout.setSpacing(5)
        pagination_layout.addLayout(self.page_buttons_layout)

        self.next_btn = QPushButton("▶")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #bdc3c7;
                color: #2c3e50;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:disabled {
                background-color: #ecf0f1;
                color: #95a5a6;
            }
        """)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self.go_to_next_page)
        self.next_btn.setToolTip("Page suivante")
        pagination_layout.addWidget(self.next_btn)

        pagination_layout.addStretch()

        self.page_info_label = QLabel()
        self.page_info_label.setStyleSheet("color: #7f8c8d;")
        pagination_layout.addWidget(self.page_info_label)

        layout.addWidget(self.pagination_widget)

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

    def load_depenses(self):
        result = get_depenses()
        if result["success"]:
            self.all_depenses = result["data"]
            self.filtered_depenses = self.all_depenses
            self.apply_filters()
        else:
            self.show_error_message("Erreur", result["message"])

    def apply_filters(self):
        # Récupérer les valeurs des filtres
        status_filter = self.status_filter.currentData()
        search_text = self.search_input.text().lower()

        # Filtrer les dépenses
        self.filtered_depenses = []
        for depense in self.all_depenses:
            # Filtre par statut
            if status_filter != "tous" and depense["statut_validation"] != status_filter:
                continue

            # Filtre par texte de recherche
            searchable_text = (
                    depense["date"].lower() +
                    depense["type_depense"].lower() +
                    str(depense["montant"]) +
                    depense.get("ligne_budgetaire_nom", "").lower()
            )

            if search_text and search_text not in searchable_text:
                continue

            self.filtered_depenses.append(depense)

        self.current_page = 1  # Reset to first page when filters change
        self.update_table()
        self.update_pagination()
        self.results_label.setText(f"{len(self.filtered_depenses)} dépense(s) trouvée(s)")

    def change_items_per_page(self, text):
        self.items_per_page = int(text)
        self.current_page = 1  # Reset to first page when items per page changes
        self.update_table()
        self.update_pagination()

    def update_table(self):
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        paginated_depenses = self.filtered_depenses[start_index:end_index]

        self.table.setRowCount(len(paginated_depenses))

        for i, depense in enumerate(paginated_depenses):
            # Date
            date_item = QTableWidgetItem(depense["date"])
            self.table.setItem(i, 0, date_item)

            # Type
            type_item = QTableWidgetItem(depense["type_depense"])
            self.table.setItem(i, 1, type_item)

            # Montant (aligné à droite)
            montant_item = QTableWidgetItem(f"{depense['montant']:,.2f} F")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 2, montant_item)

            # Ligne Budgétaire
            ligne_nom = depense.get("ligne_budgetaire_nom", "N/A")
            ligne_item = QTableWidgetItem(ligne_nom)
            self.table.setItem(i, 3, ligne_item)

            # Statut avec couleur et icône
            statut = self.format_status(depense["statut_validation"])
            statut_item = QTableWidgetItem(statut)
            statut_item.setForeground(self.get_status_color(depense["statut_validation"]))
            self.table.setItem(i, 4, statut_item)

            # Actions
            action_widget = self.create_action_widget(depense)
            self.table.setCellWidget(i, 5, action_widget)

            # Alternance des couleurs de ligne
            if i % 2 == 0:
                for j in range(self.table.columnCount()):
                    if self.table.item(i, j):
                        self.table.item(i, j).setBackground(QColor("#f8f9fa"))

    def update_pagination(self):
        # Clear existing page buttons
        for i in reversed(range(self.page_buttons_layout.count())):
            widget = self.page_buttons_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        total_pages = math.ceil(len(self.filtered_depenses) / self.items_per_page) or 1

        # Always show first page button
        self.add_page_button(1)

        # Show ellipsis if needed
        if self.current_page > 3:
            ellipsis = QLabel("...")
            ellipsis.setStyleSheet("color: #7f8c8d;")
            self.page_buttons_layout.addWidget(ellipsis)

        # Show current page and neighbors
        start_page = max(2, self.current_page - 1)
        end_page = min(total_pages - 1, self.current_page + 1)

        for page in range(start_page, end_page + 1):
            self.add_page_button(page)

        # Show ellipsis if needed
        if self.current_page < total_pages - 2:
            ellipsis = QLabel("...")
            ellipsis.setStyleSheet("color: #7f8c8d;")
            self.page_buttons_layout.addWidget(ellipsis)

        # Always show last page button if there's more than one page
        if total_pages > 1:
            self.add_page_button(total_pages)

        # Update page info label
        start_item = (self.current_page - 1) * self.items_per_page + 1
        end_item = min(self.current_page * self.items_per_page, len(self.filtered_depenses))
        total_items = len(self.filtered_depenses)
        self.page_info_label.setText(f"Affichage de {start_item}-{end_item} sur {total_items}")

        # Enable/disable navigation buttons
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

    def add_page_button(self, page):
        btn = QPushButton(str(page))
        btn.setCheckable(True)
        btn.setChecked(page == self.current_page)
        btn.setStyleSheet("""
            QPushButton {
                background-color: %s;
                color: %s;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
                color: white;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
            }
        """ % ("#ecf0f1" if page != self.current_page else "#3498db",
              "#2c3e50" if page != self.current_page else "white"))
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.go_to_page(page))
        self.page_buttons_layout.addWidget(btn)

    def go_to_page(self, page):
        self.current_page = page
        self.update_table()
        self.update_pagination()

    def go_to_previous_page(self):
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)

    def go_to_next_page(self):
        total_pages = math.ceil(len(self.filtered_depenses) / self.items_per_page)
        if self.current_page < total_pages:
            self.go_to_page(self.current_page + 1)

    def format_status(self, status):
        status_map = {
            "validee": "✅ Validée",
            "rejettee": "❌ Rejetée",
            "en_attente": "⏳ En attente"
        }
        return status_map.get(status, status.capitalize())

    def create_action_widget(self, depense):
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 0, 5, 0)
        action_layout.setSpacing(8)

        # Variable pour suivre si des boutons ont été ajoutés
        buttons_added = False

        # Afficher les actions seulement pour les dépenses en attente
        if depense["statut_validation"] == "en_attente":
            # Boutons pour Comptable
            if self.user_role == "comptable":
                self.add_action_button(action_layout, "✏️ Modifier", "#3498db",
                                       lambda: self.modifier_depense(depense), "Modifier cette dépense")
                self.add_action_button(action_layout, "🗑 Supprimer", "#e74c3c",
                                       lambda: self.supprimer_depense(depense["id"]), "Supprimer cette dépense")
                buttons_added = True

            # Bouton pour csa
            elif self.user_role == "csa":
                self.add_action_button(action_layout, "🕵️ Superviser", "#9b59b6",
                                       lambda: self.superviser_depense(depense["id"]), "Superviser cette dépense")
                buttons_added = True

            # Boutons pour directeur (seulement si déjà supervisé)
            elif self.user_role == "directeur" and depense.get("supervise_par"):
                self.add_action_button(action_layout, "✅ Valider", "#27ae60",
                                       lambda: self.valider_depense(depense["id"], "validee"), "Valider cette dépense")
                self.add_action_button(action_layout, "❌ Rejeter", "#e74c3c",
                                       lambda: self.valider_depense(depense["id"], "rejettee"), "Rejeter cette dépense")
                buttons_added = True

        # Si aucune action disponible
        if not buttons_added:
            if depense["statut_validation"] != "en_attente":
                status_text = "Traitement terminé"
            else:
                status_text = "Action indisponible"

            label = QLabel(status_text)
            label.setStyleSheet("color: #95a5a6; font-style: italic;")
            action_layout.addWidget(label)

        action_layout.addStretch()
        return action_widget

    def add_action_button(self, layout, text, color, callback, tooltip=""):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 12px;
                min-width: 80px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 40)};
            }}
        """)
        if tooltip:
            btn.setToolTip(tooltip)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def get_status_color(self, status):
        return {
            "validee": QColor("#27ae60"),
            "rejettee": QColor("#e74c3c"),
            "en_attente": QColor("#f39c12")
        }.get(status, QColor("#2c3e50"))

    def darken_color(self, hex_color, amount=20):
        color = QColor(hex_color)
        h, s, v, a = color.getHsv()
        return QColor.fromHsv(h, s, max(0, v - amount), a).name()

    def setup_animations(self):
        # Animation d'apparition du tableau
        self.anim = QPropertyAnimation(self.table, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def refresh_data(self):
        self.load_depenses()
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

    def open_form_dialog(self):
        dialog = DepenseFormDialog(self)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "La dépense a été créée avec succès!")

    def open_demandes_widget(self):
        dialog = DemandesDepenseWidget()
        dialog.setWindowTitle("Demandes de Dépense")
        dialog.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
        """)
        dialog.resize(900, 650)
        dialog.exec_()
        # Rafraîchir les données après fermeture de la fenêtre des demandes
        self.refresh_data()

    def modifier_depense(self, depense_data):
        dialog = DepenseFormDialog(self, depense_data=depense_data)
        dialog.setWindowTitle("Modifier une dépense")
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "La dépense a été modifiée avec succès!")

    def supprimer_depense(self, depense_id):
        confirm = self.show_confirmation_dialog(
            "Confirmation de suppression",
            "Voulez-vous vraiment supprimer cette dépense ?",
            "Cette action est irréversible."
        )
        if confirm == QMessageBox.Yes:
            result = delete_depense(depense_id)
            if result["success"]:
                self.show_success_message("Succès", result["message"])
                self.refresh_data()
            else:
                self.show_error_message("Erreur", result["message"])

    def superviser_depense(self, depense_id):
        confirm = self.show_confirmation_dialog(
            "Confirmation",
            "Voulez-vous superviser cette dépense ?",
            "Cette dépense sera marquée comme supervisée."
        )
        if confirm == QMessageBox.Yes:
            result = superviser_depense(depense_id)
            if result["success"]:
                self.show_success_message("Succès", result["message"])
                self.refresh_data()
            else:
                self.show_error_message("Erreur", result["message"])

    def valider_depense(self, depense_id, statut):
        action = "valider" if statut == "validee" else "rejeter"
        confirm = self.show_confirmation_dialog(
            f"Confirmation",
            f"Voulez-vous {action} cette dépense ?",
            f"Le statut de cette dépense sera définitivement changé."
        )
        if confirm == QMessageBox.Yes:
            result = valider_depense(depense_id, statut)
            if result["success"]:
                self.show_success_message("Succès", result["message"])
                self.refresh_data()
            else:
                self.show_error_message("Erreur", result["message"])