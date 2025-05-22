from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFrame, QGridLayout,
                             QSizePolicy, QSpacerItem)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer, QEvent, QSize
from services.auth_service import AuthService


class OTPDigitInput(QLineEdit):
    """Champ de saisie personnalisé pour un chiffre du code OTP"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(1)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(55, 65)
        self.setFont(QFont("Arial", 22, QFont.Bold))
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 8px;
                padding: 8px;
                background-color: #f5f5f5;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
                background-color: white;
            }
        """)

    def focusInEvent(self, event):
        """Sélectionne tout le texte lors du focus"""
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)


class Code2FAWidget(QWidget):
    """
    Widget de vérification du code 2FA envoyé par email.
    Version améliorée avec saisie de code par chiffre individuel et
    interface utilisateur professionnelle.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.code_fields = []
        self.countdown_timer = None
        self.countdown_seconds = 60
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
        """)
        self.init_ui()

    def init_ui(self):
        # Layout principal (centré)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Container central (carte avec ombre)
        card_container = QFrame()
        card_container.setObjectName("card_container")
        card_container.setStyleSheet("""
            #card_container {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(40, 50, 40, 50)
        card_layout.setSpacing(20)

        # Icône de sécurité en haut
        icon_layout = QHBoxLayout()
        security_icon_container = QFrame()
        security_icon_container.setFixedSize(80, 80)
        security_icon_container.setStyleSheet("""
            background-color: #e6f7ff;
            border-radius: 40px;
        """)
        icon_layout_inner = QVBoxLayout(security_icon_container)
        icon_layout_inner.setAlignment(Qt.AlignCenter)

        security_icon = QLabel()
        # Idéalement, remplacez par une vraie icône:
        # security_icon.setPixmap(QPixmap("icons/shield-check.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        security_icon.setText("🔒")
        security_icon.setFont(QFont("Arial", 24))
        security_icon.setStyleSheet("color: #0078d7;")
        icon_layout_inner.addWidget(security_icon)

        icon_layout.addStretch()
        icon_layout.addWidget(security_icon_container)
        icon_layout.addStretch()

        # Titres
        title = QLabel("Vérification en deux étapes")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333333;")
        user_email = AuthService.get_user_email()
        subtitle = QLabel(f"Nous avons envoyé un code à {user_email.capitalize()}")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666; margin-bottom: 10px;")
        subtitle.setWordWrap(True)

        instructions = QLabel(
            "Veuillez saisir le code à 6 chiffres pour confirmer votre identité"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #666666;")
        instructions.setWordWrap(True)

        # Champs de saisie du code (6 champs individuels)
        code_container = QFrame()
        code_layout = QHBoxLayout(code_container)
        code_layout.setSpacing(10)

        self.code_fields = []
        for i in range(6):
            digit_input = OTPDigitInput()
            digit_input.textChanged.connect(
                lambda text, field_index=i: self.on_text_changed(text, field_index)
            )
            self.code_fields.append(digit_input)
            code_layout.addWidget(digit_input)

        # Bouton de validation
        validate_button = QPushButton("Vérifier le code")
        validate_button.setMinimumHeight(50)
        validate_button.setCursor(Qt.PointingHandCursor)
        validate_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border-radius: 6px;
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
        validate_button.clicked.connect(self.validate_code)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")

        # Options supplémentaires
        options_container = QFrame()
        options_layout = QVBoxLayout(options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(8)

        # Texte et bouton de renvoi de code
        resend_layout = QHBoxLayout()
        resend_text = QLabel("Vous n'avez pas reçu le code ?")
        resend_text.setStyleSheet("color: #666666;")

        self.resend_button = QPushButton("Renvoyer le code")
        self.resend_button.setCursor(Qt.PointingHandCursor)
        self.resend_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #0078d7;
                font-weight: bold;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                color: #005fa3;
                text-decoration: underline;
            }
            QPushButton:disabled {
                color: #AAAAAA;
            }
        """)
        self.resend_button.clicked.connect(self.resend_code)

        resend_layout.addWidget(resend_text)
        resend_layout.addWidget(self.resend_button)
        resend_layout.addStretch()

        # Timer pour montrer le compte à rebours
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.hide()

        # Bouton retour à la connexion
        back_layout = QHBoxLayout()
        back_button = QPushButton("Retour à la connexion")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #0078d7;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                color: #005fa3;
                text-decoration: underline;
            }
        """)
        back_button.clicked.connect(lambda: self.parent.navigate_to(0))

        back_layout.addWidget(back_button)
        back_layout.addStretch()

        # Ajouter les widgets aux layouts
        options_layout.addLayout(resend_layout)
        options_layout.addWidget(self.countdown_label)
        options_layout.addSpacing(15)
        options_layout.addLayout(back_layout)

        # Assemblage du container principal
        card_layout.addLayout(icon_layout)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(instructions)
        card_layout.addSpacing(20)
        card_layout.addWidget(code_container)
        card_layout.addSpacing(10)
        card_layout.addWidget(validate_button)
        card_layout.addSpacing(10)
        card_layout.addWidget(separator)
        card_layout.addSpacing(5)
        card_layout.addWidget(options_container)

        # Ajouter le container au layout principal avec des marges automatiques
        main_layout.addStretch()
        main_layout.addWidget(card_container)
        main_layout.addStretch()

        # Définir la taille minimale
        self.setMinimumSize(600, 700)

        # Focus sur le premier champ de code
        self.code_fields[0].setFocus()

    def on_text_changed(self, text, field_index):
        """
        Gère la saisie dans les champs de code :
        - Passe au champ suivant si un chiffre est saisi
        - Vérifie automatiquement le code si tous les champs sont remplis
        """
        # Vérifier si le texte est un chiffre valide
        if text and not text.isdigit():
            self.code_fields[field_index].setText("")
            return

        # Si le champ est complété avec un chiffre, passer au suivant
        if text and field_index < 5:
            self.code_fields[field_index + 1].setFocus()

        # Si c'était une suppression (texte vide), revenir au champ précédent
        if not text and field_index > 0:
            self.code_fields[field_index - 1].setFocus()

        # Si tous les champs sont remplis, valider automatiquement
        if all(field.text() for field in self.code_fields):
            # Option: valider automatiquement après un délai court
            # QTimer.singleShot(500, self.validate_code)
            pass

    def validate_code(self):
        """
        Valide le code complet et redirige vers le dashboard si correct
        """
        # Récupérer le code complet
        code = ''.join(field.text() for field in self.code_fields)

        if len(code) != 6 or not code.isdigit():
            self.show_error_message("Code incomplet",
                                    "Veuillez saisir le code à 6 chiffres complet.")
            return

        # Appeler le service d'authentification
        response = AuthService.verify_code(code)

        if response.get("success"):
            self.show_success_message("Authentification réussie",
                                      "Votre identité a été vérifiée avec succès !")

            # 🔄 Forcer le rechargement du DashboardWidget avec le bon rôle
            self.parent.dashboard_widget.deleteLater()  # Supprimer l'ancien
            from ui.dashboard_widget import DashboardWidget  # Importer à chaud
            self.parent.dashboard_widget = DashboardWidget(self.parent)
            self.parent.stack.insertWidget(2, self.parent.dashboard_widget)  # Ajouter à la stack

            self.parent.navigate_to(2)  # Aller vers le dashboard

        else:
            self.show_error_message("Code incorrect",
                                    response.get("message", "Le code saisi n'est pas valide. Veuillez réessayer."))
            # Effacer tous les champs et placer le focus sur le premier
            for field in self.code_fields:
                field.clear()
            self.code_fields[0].setFocus()

    def resend_code(self):
        """
        Renvoie un nouveau code et démarre le compte à rebours
        """
        response = AuthService.resend_code()

        if response.get("success"):
            # Démarrer le compte à rebours
            self.start_countdown()
            self.show_info_message("Code envoyé",
                                   f"Un nouveau code a été envoyé à {AuthService.temp_email}")
        else:
            self.show_error_message("Erreur",
                                    response.get("message", "Impossible de renvoyer le code. Veuillez réessayer."))

    def start_countdown(self):
        """
        Démarre un compte à rebours pour le renvoi de code
        """
        self.countdown_seconds = 60
        self.resend_button.setEnabled(False)
        self.countdown_label.show()
        self.update_countdown()

        # Créer et démarrer le timer
        if self.countdown_timer is None:
            self.countdown_timer = QTimer(self)
            self.countdown_timer.timeout.connect(self.update_countdown)

        self.countdown_timer.start(1000)  # 1 seconde

    def update_countdown(self):
        """
        Met à jour l'affichage du compte à rebours
        """
        if self.countdown_seconds > 0:
            self.countdown_label.setText(f"Nouveau code disponible dans {self.countdown_seconds} secondes")
            self.countdown_seconds -= 1
        else:
            if self.countdown_timer:
                self.countdown_timer.stop()
            self.countdown_label.setText("Vous pouvez demander un nouveau code")
            self.resend_button.setEnabled(True)
            QTimer.singleShot(3000, lambda: self.countdown_label.hide())

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

    def show_info_message(self, title, message):
        """Affiche une boîte de message d'information stylisée"""
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