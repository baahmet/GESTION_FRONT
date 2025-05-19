from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
from services.auth_service import AuthService, update_my_account


class MonCompteWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.user_data = AuthService.user_data
        self.setup_ui_style()
        self.init_ui()
        self.setup_animations()

    def setup_ui_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header
        header = QLabel("MON COMPTE")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }
        """)
        main_layout.addWidget(header)

        # Conteneur du formulaire
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
            }
        """)
        form_container.setFixedWidth(500)

        # Ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 3)
        form_container.setGraphicsEffect(shadow)

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        # Photo de profil (placeholder)
        profile_pic = QLabel()
        profile_pic.setPixmap(
            QPixmap("assets/user-profile.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        profile_pic.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(profile_pic)

        # Formulaire
        self.form = QFormLayout()
        self.form.setHorizontalSpacing(20)
        self.form.setVerticalSpacing(15)

        # Style pour les labels
        label_style = "font-weight: 500; color: #34495e;"

        self.nom_input = QLineEdit(self.user_data.get("nom", ""))
        self.email_input = QLineEdit(self.user_data.get("email", ""))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Laisser vide pour ne pas changer")

        # Ajout des champs avec icônes
        self.add_form_row("👤 Nom :", self.nom_input)
        self.add_form_row("✉ Email :", self.email_input)
        self.add_form_row("🔒 Mot de passe :", self.password_input)

        form_layout.addLayout(self.form)
        main_layout.addWidget(form_container, 0, Qt.AlignHCenter)

        # Bouton Enregistrer
        self.save_btn = QPushButton("💾 Enregistrer les modifications")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.update_account)
        main_layout.addWidget(self.save_btn, 0, Qt.AlignHCenter)

    def add_form_row(self, label_text, input_widget):
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: 500; color: #34495e;")
        self.form.addRow(label, input_widget)

    def setup_animations(self):
        # Animation d'apparition
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_anim.start()

    def update_account(self):
        nom = self.nom_input.text().strip()
        email = self.email_input.text().strip()
        mot_de_passe = self.password_input.text().strip()

        if not nom or not email:
            self.show_message("Champs requis", "Le nom et l'email sont obligatoires.", "warning")
            return

        data = {
            "nom": nom,
            "email": email
        }
        if mot_de_passe:
            if len(mot_de_passe) < 6:
                self.show_message("Mot de passe faible", "Le mot de passe doit contenir au moins 6 caractères.",
                                  "warning")
                return
            data["mot_de_passe"] = mot_de_passe

        # Désactiver le bouton pendant la requête
        self.save_btn.setEnabled(False)
        self.save_btn.setText("⏳ En cours...")

        result = update_my_account(data)

        # Réactiver le bouton
        self.save_btn.setEnabled(True)
        self.save_btn.setText("💾 Enregistrer les modifications")

        if result["success"]:
            self.show_message("Succès", "Vos informations ont été mises à jour.", "success")
            AuthService.refresh_user_data()
        else:
            self.show_message("Erreur", result["message"], "error")

    def show_message(self, title, message, type_):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)

        if type_ == "success":
            msg.setIcon(QMessageBox.Information)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #27ae60;
                }
            """)
        elif type_ == "warning":
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #f39c12;
                }
            """)
        else:
            msg.setIcon(QMessageBox.Critical)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #e74c3c;
                }
            """)

        msg.exec_()