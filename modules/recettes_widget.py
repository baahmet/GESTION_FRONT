from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QHBoxLayout,
                             QLineEdit, QComboBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QBrush

from services.auth_service import AuthService
from services.recette_service import get_recettes, delete_recette
from ui.modules.recette_form_dialog import RecetteFormDialog, ModifierRecetteDialog
import datetime
import math


class RecettesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = AuthService.get_user_role()
        self.recettes = []
        self.filtered_recettes = []
        self.current_page = 1
        self.items_per_page = 10
        self.setup_ui()
        self.load_recettes()
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

        title = QLabel("GESTION DES RECETTES")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        header.addWidget(title)

        header.addStretch()

        # Bouton principal pour ajouter avec amélioration
        self.add_button = QPushButton("➕ Nouvelle Recette")
        self.add_button.setStyleSheet("""
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
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.ouvrir_dialog_ajout)
        self.add_button.setToolTip("Ajouter une nouvelle recette")
        header.addWidget(self.add_button)

        layout.addLayout(header)

        # Désactiver création pour CSA & Directeur
        if self.user_role in ["directeur", "csa"]:
            self.add_button.setVisible(False)

        # Ajout d'une barre de filtres
        filter_bar = QHBoxLayout()

        # Filtre par type
        self.type_filter = QComboBox()
        self.type_filter.addItem("Tous les types", "tous")
        self.type_filter.addItem("Subvention", "Subvention")
        self.type_filter.addItem("Paiement", "Paiement")
        self.type_filter.addItem("Don", "Don")
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
        self.results_label = QLabel("0 recettes")
        self.results_label.setStyleSheet("color: #7f8c8d;")
        filter_bar.addWidget(self.results_label)

        layout.addLayout(filter_bar)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Source", "Type", "Montant", "Justificatif", "Actions"])
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

    def load_recettes(self):
        result = get_recettes()
        if result["success"]:
            self.recettes = result["data"]
            self.filtered_recettes = self.recettes
            self.apply_filters()
        else:
            self.show_error_message("Erreur", result["message"])

    def apply_filters(self):
        # Récupérer les valeurs des filtres
        type_filter = self.type_filter.currentData()
        search_text = self.search_input.text().lower()

        # Filtrer les recettes
        self.filtered_recettes = []
        for recette in self.recettes:
            # Filtre par type
            if type_filter != "tous" and recette["type"] != type_filter:
                continue

            # Filtre par texte de recherche
            searchable_text = (
                    recette["date"].lower() +
                    recette["source"].lower() +
                    recette["type"].lower() +
                    str(recette["montant"])
            )

            if search_text and search_text not in searchable_text:
                continue

            self.filtered_recettes.append(recette)

        self.current_page = 1  # Reset to first page when filters change
        self.update_table()
        self.update_pagination()
        self.results_label.setText(f"{len(self.filtered_recettes)} recette(s) trouvée(s)")

    def change_items_per_page(self, text):
        self.items_per_page = int(text)
        self.current_page = 1  # Reset to first page when items per page changes
        self.update_table()
        self.update_pagination()

    def update_table(self):
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        paginated_recettes = self.filtered_recettes[start_index:end_index]

        self.table.setRowCount(len(paginated_recettes))

        for i, recette in enumerate(paginated_recettes):
            # Date
            date_item = QTableWidgetItem(recette["date"])
            self.table.setItem(i, 0, date_item)

            # Source
            source_item = QTableWidgetItem(recette["source"])
            self.table.setItem(i, 1, source_item)

            # Type
            type_item = QTableWidgetItem(recette["type"])
            self.table.setItem(i, 2, type_item)

            # Montant (aligné à droite)
            montant_item = QTableWidgetItem(f"{recette['montant']:,.2f} F")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 3, montant_item)

            # Justificatif
            justificatif = recette.get("justificatif") or "-"
            justif_item = QTableWidgetItem(justificatif)
            self.table.setItem(i, 4, justif_item)

            # Actions
            action_widget = self.create_action_widget(recette)
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

        total_pages = math.ceil(len(self.filtered_recettes) / self.items_per_page) or 1

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
        end_item = min(self.current_page * self.items_per_page, len(self.filtered_recettes))
        total_items = len(self.filtered_recettes)
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
        total_pages = math.ceil(len(self.filtered_recettes) / self.items_per_page)
        if self.current_page < total_pages:
            self.go_to_page(self.current_page + 1)

    def create_action_widget(self, recette):
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(5, 0, 5, 0)
        action_layout.setSpacing(8)

        # Bouton Modifier
        modifier_btn = QPushButton("✏️ Modifier")
        modifier_btn.setStyleSheet("""
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
        modifier_btn.setToolTip("Modifier cette recette")
        modifier_btn.setCursor(Qt.PointingHandCursor)
        modifier_btn.clicked.connect(lambda: self.modifier_recette(recette))
        action_layout.addWidget(modifier_btn)

        # Désactiver création pour CSA & Directeur
        if self.user_role in ["directeur", "csa"]:
            modifier_btn.setVisible(False)

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
        supprimer_btn.setToolTip("Supprimer cette recette")
        supprimer_btn.setCursor(Qt.PointingHandCursor)
        supprimer_btn.clicked.connect(lambda: self.supprimer_recette(recette))
        action_layout.addWidget(supprimer_btn)

        # Désactiver création pour CSA & Directeur
        if self.user_role in ["directeur", "csa"]:
            supprimer_btn.setVisible(False)

        action_layout.addStretch()
        return action_widget

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
        self.load_recettes()
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

    def ouvrir_dialog_ajout(self):
        dialog = RecetteFormDialog(self)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "La recette a été créée avec succès!")

    def modifier_recette(self, recette):
        dialog = ModifierRecetteDialog(recette, self)
        dialog.setWindowTitle("Modifier une recette")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
        """)
        if dialog.exec_():
            self.refresh_data()
            self.show_success_message("Succès", "La recette a été modifiée avec succès!")

    def supprimer_recette(self, recette):
        confirm = self.show_confirmation_dialog(
            "Confirmation de suppression",
            f"Voulez-vous vraiment supprimer cette recette de {recette['source']} ?",
            f"Montant: {recette['montant']:,.2f} F - Cette action est irréversible."
        )
        if confirm == QMessageBox.Yes:
            result = delete_recette(recette['budget'])
            if result["success"]:
                self.show_success_message("Succès", "La recette a été supprimée avec succès!")
                self.refresh_data()
            else:
                self.show_error_message("Erreur", result["message"])