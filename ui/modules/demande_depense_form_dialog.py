from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit,
                            QDoubleSpinBox, QPushButton, QHBoxLayout,
                            QMessageBox, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette

from services.demande_depense_service import get_demandes_depense, update_demande_depense, create_demande_depense


class DemandeDepenseFormDialog(QDialog):
    def __init__(self, parent=None, demande_id=None):
        super().__init__(parent)
        self.demande_id = demande_id
        self.setWindowTitle("📝 Demande de Dépense")
        self.resize(450, 300)
        self.setup_ui_style()
        self.init_ui()

        if demande_id:
            self.load_demande_data()

    def setup_ui_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #34495e;
                font-weight: 500;
                margin-bottom: 5px;
            }
            QTextEdit, QDoubleSpinBox {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit {
                min-height: 100px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("NOUVELLE DEMANDE DE DÉPENSE" if not self.demande_id else "MODIFIER DEMANDE")
        header.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }
        """)
        layout.addWidget(header)

        # Motif
        self.motif_input = QTextEdit()
        self.motif_input.setPlaceholderText("Décrivez le motif de cette dépense...")
        layout.addWidget(QLabel("Motif :"))
        layout.addWidget(self.motif_input)

        # Montant
        self.montant_input = QDoubleSpinBox()
        self.montant_input.setMaximum(1_000_000_000)
        self.montant_input.setPrefix("💰 ")
        self.montant_input.setSuffix(" FCFA")
        self.montant_input.setDecimals(0)
        self.montant_input.setSingleStep(1000)
        layout.addWidget(QLabel("Montant estimé :"))
        layout.addWidget(self.montant_input)

        # Boutons
        btn_frame = QFrame()
        btn_frame.setStyleSheet("background: transparent;")
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 10, 0, 0)
        btn_layout.setSpacing(15)

        cancel_btn = QPushButton("✖ Annuler")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        self.submit_btn = QPushButton("✔ Enregistrer")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.submit_btn.clicked.connect(self.submit)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.submit_btn)

        layout.addWidget(btn_frame)
        self.setLayout(layout)

    def load_demande_data(self):
        result = get_demandes_depense()
        if result["success"]:
            demande = next((d for d in result["data"] if d["id"] == self.demande_id), None)
            if demande:
                self.motif_input.setPlainText(demande["motif"])
                self.montant_input.setValue(float(demande["montant_estime"]))

    def submit(self):
        motif = self.motif_input.toPlainText().strip()
        montant = self.montant_input.value()

        if not motif or montant <= 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Champs incomplets")
            msg.setText("Veuillez remplir tous les champs correctement.")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: #e67e22;
                }
            """)
            msg.exec_()
            return

        data = {"motif": motif, "montant_estime": montant}

        if self.demande_id:
            result = update_demande_depense(self.demande_id, data)
        else:
            result = create_demande_depense(data)

        msg = QMessageBox(self)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
        """)

        if result["success"]:
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Succès")
            msg.setText(result["message"])
            msg.exec_()
            self.accept()
        else:
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Erreur")
            msg.setText(result["message"])
            msg.exec_()