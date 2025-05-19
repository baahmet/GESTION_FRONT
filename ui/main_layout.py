from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QStackedWidget, QPushButton, QMessageBox, QGraphicsDropShadowEffect, QSizePolicy,
    QFrame, QDialog
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QPalette, QIcon, QPixmap
from PyQt5.QtCore import QTimer

from modules.NotificationsWidget import NotificationsWidget
from modules.mon_compte_widget import MonCompteWidget
from modules.utilisateur_widget import UtilisateursWidget
from modules.dashboard_global_widget import DashboardGlobalWidget
from modules.budgets_widget import BudgetsWidget
from modules.depenses_widget import DepensesWidget
from modules.recettes_widget import RecettesWidget
from modules.commandes_widget import CommandesWidget
from modules.rapports_widget import RapportsWidget
from modules.journal_audit_widget import JournalAuditWidget
from services.auth_service import AuthService
from services.notification_service import get_notifications

class SidebarItem(QWidget):
    """Widget personnalisé pour les éléments de la barre latérale"""
    clicked = pyqtSignal(int)

    def __init__(self, text, icon, index):
        super().__init__()
        self.index = index
        self.selected = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)

        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 18px;")  # Taille d'icône agrandie

        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("""
            font-size: 16px;  /* Taille de police augmentée */
            font-family: 'Segoe UI', sans-serif;
            color: #e0e0e0;
            font-weight: 500;  /* Légèrement plus visible */
        """)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label, 1)

        self.setStyleSheet("""
            SidebarItem {
                border-left: 4px solid transparent;
                margin: 2px 10px;
                border-radius: 4px;
            }
            SidebarItem:hover {
                background-color: #003366;
            }
        """)

    def setSelected(self, selected):
        self.selected = selected
        if selected:
            self.setStyleSheet("""
                SidebarItem {
                    background-color: #004080;
                    border-left: 4px solid #1e88e5;
                    margin: 2px 10px;
                    border-radius: 4px;
                }
                QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                SidebarItem {
                    border-left: 4px solid transparent;
                    margin: 2px 10px;
                    border-radius: 4px;
                }
                SidebarItem:hover {
                    background-color: #003366;
                }
                QLabel {
                    color: #e0e0e0;
                }
            """)

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)
        super().mousePressEvent(event)


class MainLayout(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.modules = {}
        self.sidebar_items = []
        self.current_module_index = 0

        # Configuration de l'interface
        self.setup_ui_style()
        self.init_ui()
        self.setup_animations()
        self.start_notification_refresh()
        self.previous_non_lues = 0

    def setup_ui_style(self):
        # Fond dégradé élégant
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(240, 245, 250))
        gradient.setColorAt(1, QColor(230, 235, 240))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

        # Police globale
        font = QFont("Segoe UI", 10)
        self.setFont(font)

    def init_ui(self):
        # Récupération des informations utilisateur
        user_role = AuthService.get_user_role()
        user_nom = AuthService.get_user_nom()

        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === Sidebar Modernisée ===
        self.setup_sidebar(user_role, user_nom, layout)

        # === Zone de contenu principale ===
        self.setup_content_area(user_nom, user_role, layout)

        # Par défaut : accueil
        self.select_sidebar_item(0)

    def setup_sidebar(self, user_role, user_nom, layout):
        """Configuration de la barre latérale"""
        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(280)  # Augmentation de la largeur pour éviter le débordement
        sidebar_container.setStyleSheet("""
            background-color: #002147;
            border-right: 1px solid #001a40;
        """)

        # Effet d'ombre
        sidebar_shadow = QGraphicsDropShadowEffect()
        sidebar_shadow.setBlurRadius(15)
        sidebar_shadow.setColor(QColor(0, 0, 0, 60))
        sidebar_shadow.setOffset(5, 0)
        sidebar_container.setGraphicsEffect(sidebar_shadow)

        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo UFR-SET avec fond
        logo_container = QWidget()
        logo_container.setStyleSheet("""
            background-color: #001a38;
            border-bottom: 1px solid #003366;
            padding: 15px;
        """)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignCenter)

        # Logo UFR-SET
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo_ufr.png")
        logo_pixmap = logo_pixmap.scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)

        # Titre sous le logo (sur deux lignes avec word-wrap)
        app_title = QLabel("Système de Gestion\nBudgétaire")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setWordWrap(True)  # Activation du retour à la ligne automatique
        app_title.setStyleSheet("""
            color: white;
            font-size: 16px;  /* Police plus grande */
            font-weight: bold;
            padding-top: 5px;
            text-align: center;
        """)
        logo_layout.addWidget(app_title)

        sidebar_layout.addWidget(logo_container)

        # En-tête sidebar
        sidebar_header = QLabel("MENU PRINCIPAL")
        sidebar_header.setStyleSheet("""
            color: #7fadf2;
            font-size: 14px;  /* Police plus grande */
            font-weight: bold;
            padding: 20px 15px 10px;
            border-bottom: 1px solid #003366;
        """)
        sidebar_layout.addWidget(sidebar_header)

        # Container pour les modules
        modules_container = QWidget()
        modules_layout = QVBoxLayout(modules_container)
        modules_layout.setContentsMargins(0, 5, 0, 5)
        modules_layout.setSpacing(2)

        # Configuration des modules selon le rôle
        self.setup_sidebar_modules(user_role, modules_layout)

        sidebar_layout.addWidget(modules_container, 1)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #003366; margin: 5px 15px;")
        sidebar_layout.addWidget(separator)

        # Pied de sidebar
        self.setup_sidebar_footer(user_nom, user_role, sidebar_layout)

        layout.addWidget(sidebar_container)

    def setup_sidebar_modules(self, user_role, modules_layout):
        """Configuration des modules selon le rôle de l'utilisateur"""
        # Définition des modules et icônes
        module_items = [("Accueil", "🏠")]  # Toujours affiché

        # Modules pour comptable (tous les accès)
        if user_role == "comptable":
            module_items += [
                ("Budgets", "💰"),
                ("Dépenses", "📉"),
                ("Recettes", "📈"),
                ("Commandes", "📦"),
                ("Rapports", "📊"),
                ("Journal d'audit", "📝"),
                ("Utilisateurs", "👥"),
                ("Mon Compte", "👤"),
            ]
        # Modules pour directeur et CSA (accès similaires)
        elif user_role in ["directeur", "csa"]:
            module_items += [
                ("Budgets", "💰"),
                ("Dépenses", "📉"),
                ("Recettes", "📈"),
                ("Commandes", "📦"),
                ("Rapports", "📊"),
                ("Journal d'audit", "📝"),
                ("Mon Compte", "👤"),
            ]

        # Map pour conserver la référence texte complète
        # Correction: commandeS => Commandes (avec S) pour correspondre au widget
        self.module_map = {
            "Commandes": "Commandes"  # Corrigé pour correspondre au nom exact du widget importé
        }

        # Création des éléments du menu
        for index, (item_text, item_icon) in enumerate(module_items):
            sidebar_item = SidebarItem(item_text, item_icon, index)
            sidebar_item.clicked.connect(self.select_sidebar_item)
            modules_layout.addWidget(sidebar_item)
            self.sidebar_items.append(sidebar_item)

    def setup_sidebar_footer(self, user_nom, user_role, sidebar_layout):
        """Configuration du pied de page de la barre latérale"""
        sidebar_footer = QWidget()
        sidebar_footer.setStyleSheet("background-color: #001a40;")
        footer_layout = QVBoxLayout(sidebar_footer)
        footer_layout.setContentsMargins(15, 15, 15, 15)

        # Informations utilisateur avec icône
        user_info_container = QWidget()
        user_info_layout = QHBoxLayout(user_info_container)
        user_info_layout.setContentsMargins(0, 0, 0, 0)

        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 20px; color: #a0c4ff;")  # Icône plus grande
        user_info_layout.addWidget(user_icon)

        user_details = QLabel(f"{user_nom}\n{user_role.upper()}")
        user_details.setStyleSheet("""
            color: #a0c4ff;
            font-size: 14px;  /* Plus grande police */
            padding: 5px;
        """)
        user_info_layout.addWidget(user_details)
        footer_layout.addWidget(user_info_container)

        # Bouton de déconnexion
        self.logout_btn = QPushButton("🚪  Déconnexion")
        self.logout_btn.setStyleSheet("""
            background-color: #d32f2f;
            color: white;
            padding: 12px;
            border-radius: 5px;
            border: none;
            font-weight: bold;
            margin-top: 10px;
            font-size: 15px;  /* Plus grande police */
        """)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout)
        footer_layout.addWidget(self.logout_btn)

        sidebar_layout.addWidget(sidebar_footer)

    def setup_content_area(self, user_nom, user_role, layout):
        """Configuration de la zone de contenu principale"""
        content_container = QWidget()
        content_container.setStyleSheet("background-color: #f5f7fa;")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Barre de navigation supérieure
        navbar = self.create_navbar(user_nom, user_role)
        content_layout.addWidget(navbar)

        # Zone des modules
        self.module_stack = QStackedWidget()
        self.module_stack.setStyleSheet("""
            QStackedWidget {
                background-color: white;
                border-radius: 8px;
                margin: 15px;
                border: 1px solid #e0e0e0;
            }
        """)

        # Effet d'ombre pour la zone de contenu
        stack_shadow = QGraphicsDropShadowEffect()
        stack_shadow.setBlurRadius(10)
        stack_shadow.setColor(QColor(0, 0, 0, 30))
        stack_shadow.setOffset(0, 2)
        self.module_stack.setGraphicsEffect(stack_shadow)

        content_layout.addWidget(self.module_stack, 1)
        layout.addWidget(content_container, 1)

    def create_navbar(self, user_nom, user_role):
        """Création de la barre de navigation supérieure"""
        navbar = QWidget()
        navbar.setFixedHeight(60)
        navbar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1e88e5, stop:1 #0d47a1);
            color: white;
            border-bottom: 1px solid #0d47a1;
        """)

        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(20, 0, 20, 0)

        # Logo UFR-SET à gauche
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo_ufr.png")
        logo_pixmap = logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        navbar_layout.addWidget(logo_label)

        # Titre avec du style
        title = QLabel("UNIVERSITÉ DE THIÈS - UFR-SET - SYSTÈME DE GESTION BUDGÉTAIRE")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 1px;
            margin-left: 15px;
        """)
        navbar_layout.addWidget(title)

        # Espacement
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        navbar_layout.addWidget(spacer)

        # Bouton Cloche Notifications 🔔
        # --- Bouton Cloche Notifications ---
        self.notification_btn = QPushButton("🔔")
        self.notification_btn.setCursor(Qt.PointingHandCursor)
        self.notification_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background: transparent;
                border: none;
                color: white;
            }
            QPushButton:hover {
                color: #ffd600;
            }
        """)
        self.notification_btn.clicked.connect(self.open_notifications)

        # --- Badge Rouge (pour non lues) ---
        self.badge_label = QLabel("0")
        self.badge_label.setStyleSheet("""
            QLabel {
                background-color: red;
                color: white;
                font-size: 10px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 16px;
                min-height: 16px;
                qproperty-alignment: AlignCenter;
            }
        """)
        self.badge_label.setVisible(False)  # Cache le badge si 0 notif

        # Conteneur Cloche + Badge
        notif_container = QWidget()
        notif_layout = QHBoxLayout(notif_container)
        notif_layout.setContentsMargins(0, 0, 0, 0)
        notif_layout.setSpacing(0)
        notif_layout.addWidget(self.notification_btn)

        notif_layout.addWidget(self.badge_label)

        navbar_layout.addWidget(notif_container)



        # Badge utilisateur avec design amélioré
        user_badge = QLabel(f"{user_nom.upper()} | {user_role.capitalize()}")
        user_badge.setStyleSheet("""
            font-size: 12px;
            padding: 5px 10px;
            background-color: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
        """)
        navbar_layout.addWidget(user_badge)



        return navbar

    def select_sidebar_item(self, index):
        """Sélectionne un élément de la barre latérale et change le module affiché"""
        # Désélectionner l'élément actuel
        if self.current_module_index < len(self.sidebar_items):
            self.sidebar_items[self.current_module_index].setSelected(False)

        # Sélectionner le nouvel élément
        self.sidebar_items[index].setSelected(True)
        self.current_module_index = index

        # Changer de module
        self.change_module(index)

    def change_module(self, index):
        """Change le module affiché dans la zone de contenu"""
        if index not in self.modules:
            # Animation de transition
            self.fade_out_content()

            # Récupérer le nom du module
            module_name = self.sidebar_items[index].text_label.text().strip()

            # Création du widget correspondant - Correction de la map pour s'assurer que tous les modules sont correctement définis
            widget_map = {
                "Accueil": DashboardGlobalWidget,
                "Budgets": BudgetsWidget,
                "Recettes": RecettesWidget,
                "Dépenses": DepensesWidget,
                "Commandes": CommandesWidget,  # Correction: il s'appelait "Commandes"
                "Rapports": RapportsWidget,
                "Journal d'audit": JournalAuditWidget,
                "Utilisateurs": UtilisateursWidget,
                "Mon Compte": MonCompteWidget,
            }

            # Utiliser module_map pour les alias si nécessaire
            widget_class = widget_map.get(module_name)

            if widget_class:
                widget = widget_class()
                self.modules[index] = widget
                self.module_stack.addWidget(widget)
            else:
                # Message d'erreur plus professionnel
                error_widget = QWidget()
                error_layout = QVBoxLayout(error_widget)

                error_icon = QLabel("⚠️")
                error_icon.setAlignment(Qt.AlignCenter)
                error_icon.setStyleSheet("font-size: 48px; color: #d32f2f; margin-bottom: 20px;")

                error_title = QLabel(f"Module {module_name} non disponible")
                error_title.setAlignment(Qt.AlignCenter)
                error_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #d32f2f;")

                error_message = QLabel("Ce module est en cours de développement et sera disponible prochainement.")
                error_message.setAlignment(Qt.AlignCenter)
                error_message.setStyleSheet("font-size: 16px; color: #666; margin-top: 10px;")

                error_layout.addStretch(1)
                error_layout.addWidget(error_icon)
                error_layout.addWidget(error_title)
                error_layout.addWidget(error_message)
                error_layout.addStretch(1)

                self.modules[index] = error_widget
                self.module_stack.addWidget(error_widget)

                print(f"Module non trouvé: {module_name}")  # Pour le débogage

            # Animation d'apparition
            self.fade_in_content()

        self.module_stack.setCurrentWidget(self.modules[index])

    def fade_out_content(self):
        """Animation de disparition du contenu"""
        fade_out = QPropertyAnimation(self.module_stack, b"windowOpacity")
        fade_out.setDuration(200)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        fade_out.start()

    def fade_in_content(self):
        """Animation d'apparition du contenu"""
        fade_in = QPropertyAnimation(self.module_stack, b"windowOpacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_in.setEasingCurve(QEasingCurve.OutCubic)
        fade_in.start()

    def logout(self):
        """Gestion de la déconnexion"""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Confirmation de déconnexion")
        msg_box.setText("Êtes-vous sûr de vouloir vous déconnecter ?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                font-size: 14px;
            }
            QMessageBox QPushButton {
                padding: 8px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton[text="Yes"] {
                background-color: #d32f2f;
                color: white;
            }
            QMessageBox QPushButton[text="Oui"] {
                background-color: #d32f2f;
                color: white;
            }
            QMessageBox QPushButton[text="No"] {
                background-color: #f0f0f0;
            }
            QMessageBox QPushButton[text="Non"] {
                background-color: #f0f0f0;
            }
        """)

        reply = msg_box.exec_()
        if reply == QMessageBox.Yes:
            # 1. Stopper le timer des notifications si actif
            if hasattr(self, 'refresh_timer') and self.refresh_timer.isActive():
                self.refresh_timer.stop()

            # 2. Effectuer la déconnexion synchrone
            AuthService.logout()
            print("Déconnexion effectuée - Token:", AuthService.token)  # Devrait être None

            # 3. Redirection immédiate sans animation
            if hasattr(self, 'main_window') and self.main_window:
                self.main_window.navigate_to(0)
            else:
                print("Erreur: main_window non disponible")



    def setup_animations(self):
        """Configuration des animations générales"""
        # Animation d'apparition au démarrage
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_anim.start()

    def resizeEvent(self, event):
        """Gestion du redimensionnement de la fenêtre"""
        super().resizeEvent(event)
        # Mettre à jour le dégradé du fond
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(240, 245, 250))
        gradient.setColorAt(1, QColor(230, 235, 240))
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

    def open_notifications(self):
        notif_dialog = NotificationsWidget(self)
        notif_dialog.exec_()  # Ouvre en mode modal

    def update_notification_badge(self, count):
        if count > 0:
            self.badge_label.setText(str(count))
            self.badge_label.setVisible(True)
        else:
            self.badge_label.setVisible(False)



    def show_notification_popup(self, message):
        popup = QDialog(self)
        popup.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        popup.setAttribute(Qt.WA_TranslucentBackground)
        popup.setStyleSheet("""
            QDialog {
                background-color: rgba(30, 136, 229, 0.9);
                color: white;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout(popup)
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)

        popup.move(self.width() - 300, 100)  # Position en haut à droite
        popup.show()

        # Auto-fermeture après 3 secondes
        QTimer.singleShot(3000, popup.close)


    def navigate_to_main_dashboard(self):
        self.sidebar.show()
        self.main_content.setCurrentIndex(0)
        # ✅ Démarre la récupération des notifications UNIQUEMENT maintenant
        self.start_notification_refresh()


    def start_notification_refresh(self):


        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_notifications)
        self.refresh_timer.start(10000)




    def refresh_notifications(self):
        # Vérifie si on a bien un token stocké avant de lancer
        if not AuthService.get_headers():
            print("Pas encore connecté, refresh notifications ignoré.")
            return
        result = get_notifications()
        if result["success"]:
            non_lues = [n for n in result["data"] if not n.get("lu", False)]
            count = len(non_lues)
            self.update_notification_badge(count)

            # POPUP si nouvelle notif reçue
            if count > self.previous_non_lues:
                new_notifs = count - self.previous_non_lues
                self.show_notification_popup(f"🔔 {new_notifs} nouvelle(s) notification(s)")
            self.previous_non_lues = count

        else:
            print("Erreur chargement notifications :", result["message"])

