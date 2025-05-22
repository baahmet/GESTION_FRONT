from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFrame, QCheckBox, QSpacerItem,
                             QSizePolicy)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt
from services.auth_service import AuthService


class LoginWidget(QWidget):
    """
    Widget de connexion utilisateur amélioré.
    Interface professionnelle avec logo, champs stylisés et fonctionnalités supplémentaires.
    Appelle le backend (/login/) pour déclencher l'envoi du code 2FA.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent  # Référence à MainApp
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
        """)
        self.init_ui()

    def init_ui(self):
        # Layout principal avec deux sections côte à côte
        main_layout = QHBoxLayout(self)

        # ===== Section gauche (image/branding) =====
        left_section = QFrame()
        left_section.setStyleSheet("""
            background-color: #002147;
            border-radius: 8px 0px 0px 8px;
        """)
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(40, 40, 40, 40)

        # Logo/Nom de l'application
        logo_label = QLabel("GestionBudget")
        logo_label.setFont(QFont("Arial", 26, QFont.Bold))
        logo_label.setStyleSheet("color: white;")
        logo_label.setAlignment(Qt.AlignCenter)

        # Tagline
        tagline = QLabel("Système de Gestion Budgétaire")
        tagline.setFont(QFont("Arial", 14))
        tagline.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        tagline.setAlignment(Qt.AlignCenter)

        # Description
        description = QLabel(
            "Une solution complète pour gérer efficacement les budgets et les dépenses "
            "de votre organisation. Simplifiez vos processus financiers."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: rgba(255, 255, 255, 0.6); margin-top: 30px;")
        description.setAlignment(Qt.AlignCenter)

        # Information de sécurité
        security_info = QLabel("Authentification à deux facteurs pour une sécurité maximale")
        security_info.setWordWrap(True)
        security_info.setStyleSheet("color: rgba(255, 255, 255, 0.7); margin-top: 40px;")
        security_info.setAlignment(Qt.AlignCenter)

        # Copyright
        copyright_label = QLabel("© 2025 GestBudget - Tous droits réservés")
        copyright_label.setStyleSheet("color: rgba(255, 255, 255, 0.5); font-size: 11px;")
        copyright_label.setAlignment(Qt.AlignCenter)

        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addWidget(tagline)
        left_layout.addWidget(description)
        left_layout.addStretch()
        left_layout.addWidget(security_info)
        left_layout.addStretch()
        left_layout.addWidget(copyright_label)

        # ===== Section droite (formulaire) =====
        right_section = QFrame()
        right_section.setStyleSheet("""
            background-color: white;
            border-radius: 0px 8px 8px 0px;
        """)
        right_layout = QVBoxLayout(right_section)
        right_layout.setContentsMargins(50, 60, 50, 60)

        # Titre du formulaire
        login_title = QLabel("Connexion")
        login_title.setFont(QFont("Arial", 24, QFont.Bold))
        login_title.setStyleSheet("color: #333333; margin-bottom: 10px;")

        login_subtitle = QLabel("Connectez-vous pour accéder à votre compte")
        login_subtitle.setStyleSheet("color: #666666; margin-bottom: 30px;")

        # Formulaire avec champs améliorés
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)

        # Champ email avec intitulé
        email_label = QLabel("Adresse email")
        email_label.setStyleSheet("color: #333333; font-weight: bold; margin-bottom: -5px;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@domaine.com")
        self.email_input.setMinimumHeight(45)
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: #f5f5f5;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
                background-color: white;
            }
        """)

        # Champ mot de passe avec intitulé
        password_label = QLabel("Mot de passe")
        password_label.setStyleSheet("color: #333333; font-weight: bold; margin-bottom: -5px;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: #f5f5f5;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
                background-color: white;
            }
        """)

        # Options supplémentaires (ligne avec remember me et forgot password)
        options_layout = QHBoxLayout()
        remember_me = QCheckBox("Se souvenir de moi")
        remember_me.setStyleSheet("""
            QCheckBox {
                color: #555555;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)

        forgot_password = QPushButton("Mot de passe oublié ?")
        forgot_password.setCursor(Qt.PointingHandCursor)
        forgot_password.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #0078d7;
                text-align: right;
                padding: 0;
            }
            QPushButton:hover {
                color: #005fa3;
                text-decoration: underline;
            }
        """)

        options_layout.addWidget(remember_me)
        options_layout.addStretch()
        options_layout.addWidget(forgot_password)

        # Bouton de connexion
        login_button = QPushButton("Se connecter")
        login_button.setMinimumHeight(50)
        login_button.setCursor(Qt.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QPushButton:pressed {
                background-color: #004c82;
            }
        """)
        login_button.clicked.connect(self.attempt_login)

        # Ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")



        # Assemblage du formulaire
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addLayout(options_layout)
        form_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        form_layout.addWidget(login_button)
        form_layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        form_layout.addWidget(separator)
        form_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))


        # Ajouter le formulaire au layout droit
        right_layout.addWidget(login_title)
        right_layout.addWidget(login_subtitle)
        right_layout.addLayout(form_layout)
        right_layout.addStretch()

        # Ajout des deux sections au layout principal
        main_layout.addWidget(left_section, 4)  # Proportion 4/10
        main_layout.addWidget(right_section, 6)  # Proportion 6/10
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Configuration globale du widget
        self.setMinimumSize(1000, 600)

    def attempt_login(self):
        """
        Appelle le service d'authentification avec email/mot de passe.
        Si succès → navigue vers le widget Code 2FA
        Sinon → affiche une alerte stylisée
        """
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.show_error_message("Champs requis", "Veuillez entrer votre email et mot de passe.")
            return

        response = AuthService.login(email, password)

        if response.get("success"):
            AuthService.temp_email = email  # Stockage temporaire pour 2FA
            self.show_success_message("Code envoyé", "Un code de vérification a été envoyé à votre adresse email.")
            self.parent.navigate_to(1)  # Vers Code2FAWidget
        else:
            self.show_error_message("Erreur d'authentification",
                                    response.get("message", "Identifiants incorrects. Veuillez réessayer."))

    def show_error_message(self, title, message):
        """Affiche une boîte de message d'erreur stylisée"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # Style pour les boîtes de message
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-family: Arial;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 4px;
                padding: 6px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        msg_box.exec_()

    def show_success_message(self, title, message):
        """Affiche une boîte de message de succès stylisée"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # Style pour les boîtes de message
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-family: Arial;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 4px;
                padding: 6px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
        """)

        msg_box.exec_()