from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QMessageBox, QFrame,
    QSizePolicy, QStyle, QWidget
)
from services.notification_service import get_notifications, mark_as_read


class NotificationItem(QWidget):
    """Widget personnalisé pour afficher les notifications avec style"""

    def __init__(self, notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Indicateur de notification non lue
        self.indicator = QLabel()
        if not self.notification.get("lu", False):
            self.indicator.setText("●")
            self.indicator.setStyleSheet("color: #FFA500; font-size: 16px;")
        else:
            self.indicator.setText(" ")
        self.indicator.setFixedWidth(20)
        layout.addWidget(self.indicator)

        # Conteneur pour le message et la date
        content_layout = QVBoxLayout()

        # Message
        self.message_label = QLabel(self.notification["message"])
        font = QFont()
        font.setPointSize(10)
        if not self.notification.get("lu", False):
            font.setBold(True)
        self.message_label.setFont(font)
        self.message_label.setWordWrap(True)
        content_layout.addWidget(self.message_label)

        # Date
        date_text = self.notification["date_creation"][:16]
        self.date_label = QLabel(date_text)
        date_font = QFont()
        date_font.setPointSize(8)
        date_font.setItalic(True)
        self.date_label.setFont(date_font)
        self.date_label.setStyleSheet("color: #888888;")
        content_layout.addWidget(self.date_label)

        layout.addLayout(content_layout, 1)

        # Bouton Marquer comme lu
        if not self.notification.get("lu", False):
            self.read_button = QPushButton()
            self.read_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
            self.read_button.setToolTip("Marquer comme lu")
            self.read_button.setFixedSize(30, 30)
            self.read_button.setStyleSheet("background-color: #EFEFEF; border-radius: 15px;")
            layout.addWidget(self.read_button)


class NotificationsWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Centre de Notifications")
        self.setMinimumSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                padding: 10px;
            }
            QListWidget {
                border: 1px solid #DDDDDD;
                border-radius: 5px;
                background-color: white;
                alternate-background-color: #F9F9F9;
            }
            QPushButton {
                background-color: #4285F4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
            QPushButton:pressed {
                background-color: #2A56C6;
            }
            QFrame#header {
                background-color: #FFFFFF;
                border-bottom: 1px solid #DDDDDD;
            }
            QFrame#footer {
                background-color: #FFFFFF;
                border-top: 1px solid #DDDDDD;
            }
        """)

        self.setup_ui()

        # Auto-rafraîchissement toutes les 60 secondes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_notifications)
        self.refresh_timer.start(60000)  # 60 secondes

        self.load_notifications()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # En-tête
        header_frame = QFrame(self)
        header_frame.setObjectName("header")
        header_layout = QHBoxLayout(header_frame)

        self.title_label = QLabel("🔔 Centre de Notifications")
        self.title_label.setObjectName("title")
        header_layout.addWidget(self.title_label)

        main_layout.addWidget(header_frame)

        # Contenu principal
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)

        self.status_label = QLabel("Chargement des notifications...")
        content_layout.addWidget(self.status_label)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setFrameShape(QListWidget.NoFrame)
        self.list_widget.setSelectionMode(QListWidget.NoSelection)
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        content_layout.addWidget(self.list_widget)

        main_layout.addLayout(content_layout, 1)

        # Pied de page
        footer_frame = QFrame(self)
        footer_frame.setObjectName("footer")
        footer_layout = QHBoxLayout(footer_frame)

        self.mark_all_read_btn = QPushButton("Tout marquer comme lu")
        self.mark_all_read_btn.clicked.connect(self.mark_all_as_read)
        footer_layout.addWidget(self.mark_all_read_btn)

        footer_layout.addStretch(1)

        self.refresh_btn = QPushButton("🔄 Rafraîchir")
        self.refresh_btn.clicked.connect(self.load_notifications)
        footer_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(footer_frame)

    def load_notifications(self):
        """Charger et afficher les notifications"""
        self.list_widget.clear()
        self.status_label.setText("Chargement des notifications...")

        result = get_notifications()
        if result["success"]:
            notifications = result["data"]

            if not notifications:
                self.status_label.setText("Aucune notification pour le moment.")
                return

            self.status_label.setText(f"{len(notifications)} notification(s)")

            for notif in notifications:
                item = QListWidgetItem()
                widget = NotificationItem(notif)
                item.setSizeHint(widget.sizeHint())

                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, widget)

                # Connecter le bouton de marquer comme lu si présent
                if not notif.get("lu", False) and hasattr(widget, "read_button"):
                    widget.read_button.clicked.connect(
                        lambda checked=False, n=notif: self.mark_notification_as_read(n)
                    )

        else:
            self.status_label.setText("Erreur de chargement")
            QMessageBox.critical(self, "Erreur", result["message"])

    def mark_notification_as_read(self, notification):
        """Marquer une notification spécifique comme lue"""
        if notification.get("id"):
            result = mark_as_read(notification["id"])
            if result["success"]:
                self.load_notifications()
            else:
                QMessageBox.warning(self, "Avertissement",
                                    "Impossible de marquer cette notification comme lue")

    def mark_all_as_read(self):
        """Marquer toutes les notifications comme lues"""
        # Supposons que mark_as_read peut prendre un paramètre spécial pour tout marquer
        result = mark_as_read("all")
        if result["success"]:
            self.load_notifications()
            QMessageBox.information(self, "Succès", "Toutes les notifications ont été marquées comme lues")
        else:
            QMessageBox.warning(self, "Avertissement", "Impossible de marquer les notifications comme lues")