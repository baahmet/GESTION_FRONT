from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QInputDialog, QHBoxLayout, QWidget,
                             QLineEdit, QComboBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QBrush, QIcon
from services.ligne_budgetaire_service import (
    get_lignes_by_budget,
    create_ligne_budgetaire,
    update_ligne_budgetaire,
    delete_ligne_budgetaire
)
import math


class LigneBudgetaireDialog(QDialog):
    def __init__(self, budget, parent=None):
        super().__init__(parent)
        self.budget = budget
        self.setWindowTitle(f"Lignes budgétaires - {self.budget['exercice']}")
        self.resize(900, 600)  # Fenêtre redimensionnable
        self.current_page = 1
        self.items_per_page = 10
        self.setup_ui()
        self.load_lignes()

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

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()

        title = QLabel(f"LIGNES BUDGÉTAIRES - EXERCICE {self.budget['exercice']}")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 10px;
            }
        """)
        header.addWidget(title)
        header.addStretch()

        # Bouton d'ajout
        add_btn = QPushButton("➕ Ajouter une ligne")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.ajouter_ligne)
        add_btn.setToolTip("Ajouter une nouvelle ligne budgétaire")
        header.addWidget(add_btn)

        layout.addLayout(header)

        # Barre de filtres
        filter_bar = QHBoxLayout()

        # Filtre de recherche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
                min-width: 200px;
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
        self.results_label = QLabel("0 lignes")
        self.results_label.setStyleSheet("color: #7f8c8d;")
        filter_bar.addWidget(self.results_label)

        layout.addLayout(filter_bar)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nom de la ligne", "Montant alloué", "% du budget", "Actions"])
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

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        # Effet d'ombre
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

        self.setLayout(layout)

    def load_lignes(self):
        result = get_lignes_by_budget(self.budget['id'])
        if result['success']:
            self.all_lignes = result['data']
            self.filtered_lignes = self.all_lignes
            self.total_budget = sum(l['montant_alloue'] for l in self.all_lignes)
            self.apply_filters()
        else:
            self.show_error("Erreur", result['message'])

    def apply_filters(self):
        search_text = self.search_input.text().lower()

        # Filtrer les lignes
        self.filtered_lignes = []
        for ligne in self.all_lignes:
            # Filtre par texte de recherche
            searchable_text = (
                    ligne['article'].lower() +
                    f"{ligne['montant_alloue']:.2f}"
            )

            if search_text and search_text not in searchable_text:
                continue

            self.filtered_lignes.append(ligne)

        self.current_page = 1  # Reset to first page when filters change
        self.update_table()
        self.update_pagination()
        self.results_label.setText(f"{len(self.filtered_lignes)} ligne(s) trouvée(s)")

    def change_items_per_page(self, text):
        self.items_per_page = int(text)
        self.current_page = 1  # Reset to first page when items per page changes
        self.update_table()
        self.update_pagination()

    def update_table(self):
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        paginated_lignes = self.filtered_lignes[start_index:end_index]

        self.table.setRowCount(len(paginated_lignes))

        for i, ligne in enumerate(paginated_lignes):
            # Nom de la ligne
            nom_item = QTableWidgetItem(ligne['article'])
            self.table.setItem(i, 0, nom_item)

            # Montant alloué
            montant_item = QTableWidgetItem(f"{ligne['montant_alloue']:,.2f} F")
            montant_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 1, montant_item)

            # Pourcentage du budget
            if self.total_budget > 0:
                percent = (ligne['montant_alloue'] / self.total_budget) * 100
                percent_item = QTableWidgetItem(f"{percent:.1f}%")
                percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                # Colorer selon le pourcentage
                if percent > 30:
                    percent_item.setForeground(QBrush(QColor("#e74c3c")))
                elif percent > 15:
                    percent_item.setForeground(QBrush(QColor("#f39c12")))
                else:
                    percent_item.setForeground(QBrush(QColor("#27ae60")))

                self.table.setItem(i, 2, percent_item)

            # Actions
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)

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
                }
            """)
            modifier_btn.setCursor(Qt.PointingHandCursor)
            modifier_btn.clicked.connect(lambda _, l=ligne: self.modifier_ligne(l))
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
                }
            """)
            supprimer_btn.setCursor(Qt.PointingHandCursor)
            supprimer_btn.clicked.connect(lambda _, l=ligne: self.supprimer_ligne(l))
            action_layout.addWidget(supprimer_btn)

            self.table.setCellWidget(i, 3, action_widget)

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

        total_pages = math.ceil(len(self.filtered_lignes) / self.items_per_page) or 1

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
        end_item = min(self.current_page * self.items_per_page, len(self.filtered_lignes))
        total_items = len(self.filtered_lignes)
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
        total_pages = math.ceil(len(self.filtered_lignes) / self.items_per_page)
        if self.current_page < total_pages:
            self.go_to_page(self.current_page + 1)

    def ajouter_ligne(self):
        article, ok = QInputDialog.getText(self, "Nouvel article", "Nom de l'article :", text="Nouvel article")
        if not ok or not article.strip():
            return

        montant, ok = QInputDialog.getDouble(self, "Montant", f"Montant alloué pour '{article}' :", 1000.0, 0.01, 1e9,
                                             2)
        if not ok:
            return

        data = {
            "article": article.strip(),
            "montant_alloue": montant,
            "budget": self.budget['id']
        }

        result = create_ligne_budgetaire(data, self.budget['montant_disponible'])

        if result['success']:
            self.load_lignes()
            self.show_success("Succès", "La ligne budgétaire a été créée avec succès!")
        else:
            self.show_error("Erreur", result['message'])

    def modifier_ligne(self, ligne):
        article, ok = QInputDialog.getText(self, "Modifier article", "Nom de l'article :", text=ligne['article'])
        if not ok or not article.strip():
            return

        montant, ok = QInputDialog.getDouble(self, "Montant", "Nouveau montant :", ligne['montant_alloue'], 0.01, 1e9,
                                             2)
        if not ok:
            return

        data = {
            "article": article.strip(),
            "montant_alloue": montant,
            "budget": self.budget['id']
        }

        result = update_ligne_budgetaire(ligne['id'], data)
        if result['success']:
            self.load_lignes()
            self.show_success("Succès", "La ligne budgétaire a été modifiée avec succès!")
        else:
            self.show_error("Erreur", result['message'])

    def supprimer_ligne(self, ligne):
        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer la ligne '{ligne['article']}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            result = delete_ligne_budgetaire(ligne['id'])
            if result['success']:
                self.load_lignes()
                self.show_success("Succès", "La ligne budgétaire a été supprimée avec succès!")
            else:
                self.show_error("Erreur", result['message'])

    def show_error(self, title, message):
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

    def show_success(self, title, message):
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