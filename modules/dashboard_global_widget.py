from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect, QSpacerItem, QApplication, QScrollArea
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter, QLinearGradient, QBrush, QPen
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize, QRect, QPoint, pyqtProperty, \
    QParallelAnimationGroup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as cm
from services.auth_service import AuthService
from services.budget_service import get_budgets
from services.depense_service import get_depenses
from services.recette_service import get_recettes
import datetime
import random


class AnimatedProgressBar(QFrame):
    def __init__(self, value=0, max_value=100, color="#4C6EF5", bg_color="#E0E0E0", parent=None):
        super().__init__(parent)
        self.value = value
        self.max_value = max_value
        self.color = color
        self.bg_color = bg_color
        self._progress = 0
        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(1500)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setFixedHeight(8)
        self.setStyleSheet(f"background-color: {self.bg_color}; border-radius: 4px;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fond
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(self.bg_color)))
        painter.drawRoundedRect(self.rect(), 4, 4)

        # Barre de progression
        if self._progress > 0:
            progress_width = int(self.width() * self._progress)
            progress_rect = QRect(0, 0, progress_width, self.height())
            gradient = QLinearGradient(0, 0, progress_width, 0)
            base_color = QColor(self.color)
            gradient.setColorAt(0, base_color)
            gradient.setColorAt(1, base_color.lighter(120))
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(progress_rect, 4, 4)

    @pyqtProperty(float)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()

    def setValue(self, value):
        if self.max_value <= 0:
            self._progress = 0
        else:
            self.animation.setStartValue(self._progress)
            self.animation.setEndValue(min(1.0, max(0, value / self.max_value)))
            self.animation.start()


class AnimatedTile(QFrame):
    def __init__(self, title, value, color, icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.color = color
        self.icon = icon
        self.setupUI()

        # Appliquer une animation de fade-in et scale
        self.setGraphicsEffect(QGraphicsDropShadowEffect(
            blurRadius=15,
            color=QColor(0, 0, 0, 30),
            offset=QPoint(0, 3)
        ))
        self.opacity = 0
        self.setStyleSheet(f"""
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid {color};
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Ligne d'en-tête
        header_layout = QHBoxLayout()

        title_label = QLabel(f"{self.icon}  {self.title}")
        title_label.setStyleSheet(f"color: #555; font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)

        # Couleur d'indicateur en haut à droite
        indicator = QFrame()
        indicator.setFixedSize(10, 10)
        indicator.setStyleSheet(f"background-color: {self.color}; border-radius: 5px;")
        header_layout.addWidget(indicator)

        layout.addLayout(header_layout)

        # Valeur
        value_label = QLabel(self.value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        value_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(value_label)

        # Barre ou indicateur visuel
        if hasattr(self, 'second_value') and hasattr(self, 'max_value'):
            progress_bar = AnimatedProgressBar(self.second_value, self.max_value, self.color)
            progress_text = QLabel(f"{self.second_value / self.max_value:.1%} du budget")
            progress_text.setAlignment(Qt.AlignRight)
            progress_text.setStyleSheet("color: #777; font-size: 12px;")
            layout.addWidget(progress_bar)
            layout.addWidget(progress_text)


class PulsatingIconLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.scale_factor = 1.0  # Définir l'attribut avant l'animation

        # Animation de pulsation
        self.animation = QPropertyAnimation(self, b"scale")
        self.animation.setDuration(1500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(1.1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Animation continue avec rebond
        self.animation.finished.connect(self.restartAnimation)

    def restartAnimation(self):
        # Inverse l'animation
        start_value = self.animation.endValue()
        end_value = self.animation.startValue()
        self.animation.setStartValue(start_value)
        self.animation.setEndValue(end_value)
        self.animation.start()

    @pyqtProperty(float)
    def scale(self):
        return self.scale_factor

    @scale.setter
    def scale(self, value):
        self.scale_factor = value
        self.setFixedSize(int(120 * value), int(120 * value))
        self.update()

    def startPulsating(self):
        self.animation.start()


class ResponsiveBarChart(FigureCanvas):
    def __init__(self, data, labels, colors, title="", parent=None):
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('none')
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

        self.setStyleSheet("background-color: transparent;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.data = data
        self.labels = labels
        self.colors = colors
        self.title = title

        # Animation timer
        self.timer = QTimer(self)
        self.current_heights = [0] * len(data)
        self.animation_steps = 20
        self.current_step = 0
        self.timer.timeout.connect(self.updateChart)

        self.plot()

    def plot(self):
        self.axes.clear()
        bars = self.axes.bar(self.labels, self.current_heights, color=self.colors)

        self.axes.set_title(self.title, fontsize=11, pad=10, fontweight='bold')
        self.axes.tick_params(axis='x', rotation=45, labelsize=9)
        self.axes.tick_params(axis='y', labelsize=9)
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)
        self.axes.spines['left'].set_alpha(0.3)
        self.axes.spines['bottom'].set_alpha(0.3)

        self.axes.set_ylim(0, max(self.data) * 1.2)

        # Format y-axis as money
        self.axes.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f'{x:,.0f}'.replace(',', ' ')))

        self.fig.tight_layout()
        self.draw()

    def startAnimation(self):
        self.current_step = 0
        self.timer.start(50)  # 50ms par frame

    def updateChart(self):
        self.current_step += 1
        progress = min(1.0, self.current_step / self.animation_steps)

        # Fonction d'assouplissement
        progress = self.easeOutCubic(progress)

        for i in range(len(self.data)):
            self.current_heights[i] = self.data[i] * progress

        self.plot()

        if self.current_step >= self.animation_steps:
            self.timer.stop()

    @staticmethod
    def easeOutCubic(x):
        return 1 - pow(1 - x, 3)


class ResponsiveDonutChart(FigureCanvas):
    def __init__(self, values, labels, colors, title="", parent=None):
        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.fig.patch.set_facecolor('none')
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

        self.setStyleSheet("background-color: transparent;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.values = values
        self.labels = labels
        self.colors = colors
        self.title = title

        # Animation
        self.timer = QTimer(self)
        self.current_values = [0] * len(values)
        self.animation_steps = 20
        self.current_step = 0
        self.timer.timeout.connect(self.updateChart)

        self.plot()

    def plot(self):
        self.axes.clear()

        if sum(self.current_values) > 0:
            wedges, texts, autotexts = self.axes.pie(
                self.current_values,
                labels=self.labels,
                colors=self.colors,
                autopct=lambda pct: f'{pct:.1f}%' if pct > 5 else '',
                shadow=False,
                startangle=90,
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
                textprops={'fontsize': 9},
            )

            # Donut hole
            circle = plt.Circle((0, 0), 0.7, fc='white')
            self.axes.add_artist(circle)

            # Format autotexts
            for autotext in autotexts:
                autotext.set_fontsize(8)
                autotext.set_fontweight('bold')

            # Titre central
            self.axes.text(0, 0, self.title,
                           ha='center', va='center',
                           fontsize=10, fontweight='bold')
        else:
            self.axes.text(0, 0, "Aucune donnée\ndisponible",
                           ha='center', va='center',
                           fontsize=10, color='gray')
            self.axes.axis('off')

        self.fig.tight_layout()
        self.draw()

    def startAnimation(self):
        self.current_step = 0
        self.timer.start(50)

    def updateChart(self):
        self.current_step += 1
        progress = min(1.0, self.current_step / self.animation_steps)

        # Fonction d'assouplissement
        progress = self.easeOutCubic(progress)

        for i in range(len(self.values)):
            self.current_values[i] = self.values[i] * progress

        self.plot()

        if self.current_step >= self.animation_steps:
            self.timer.stop()

    @staticmethod
    def easeOutCubic(x):
        return 1 - pow(1 - x, 3)


class InfoBadge(QFrame):
    def __init__(self, text, color="#1E88E5", parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)

        self.label = QLabel(text)
        self.label.setStyleSheet(f"""
            color: white;
            font-size: 11px;
            font-weight: bold;
        """)
        layout.addWidget(self.label)

        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: 12px;
        """)


class DashboardGlobalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_role = AuthService.get_user_role()

        # Palette de couleurs professionnelle
        self.color_palette = {
            "primary": "#1976D2",
            "success": "#2E7D32",
            "danger": "#D32F2F",
            "warning": "#F57C00",
            "info": "#0288D1",
            "purple": "#7B1FA2",
            "teal": "#00796B",
            "pink": "#C2185B"
        }

        # Mettre un fond élégant
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)

        # Widgets pour les animations
        self.animated_widgets = []

        self.init_ui()
        self.load_data()

        # Démarrer les animations avec un léger décalage
        QTimer.singleShot(100, self.start_animations)

    def init_ui(self):
        # Conteneur principal avec défilement
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 5px;
            }
        """)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)

        scroll_area.setWidget(main_widget)

        # Layout principal pour le widget
        wrapper_layout = QVBoxLayout(self)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(scroll_area)

        # === En-tête avec Logo et Info ===
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1565C0, stop:1 #1976D2);
            border-radius: 15px;
            color: white;
        """)

        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(20)
        header_shadow.setColor(QColor(0, 0, 0, 50))
        header_shadow.setOffset(0, 5)
        header_frame.setGraphicsEffect(header_shadow)

        header_layout = QHBoxLayout(header_frame)

        # Logo animé
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)

        try:
            logo_label = PulsatingIconLabel()
            logo_pix = QPixmap("assets/logo_ufr.png").scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pix)
            logo_label.startPulsating()
            logo_layout.addWidget(logo_label)

            # Ajouter à la liste des widgets animés
            self.animated_widgets.append(logo_label)
        except:
            # Fallback si pas de logo
            logo_label = QLabel("UFR")
            logo_label.setStyleSheet("font-size: 40px; font-weight: bold; color: white;")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_layout.addWidget(logo_label)

        header_layout.addWidget(logo_container)

        # Textes d'en-tête
        header_text = QWidget()
        header_text_layout = QVBoxLayout(header_text)

        # Titre avec badge de mise à jour
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("TABLEAU DE BORD FINANCIER")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
        """)
        title_layout.addWidget(title_label)

        # Badge "Mise à jour"
        now = datetime.datetime.now()
        update_badge = InfoBadge(f"Mise à jour: {now.strftime('%d/%m/%Y')}", "#4CAF50")
        title_layout.addWidget(update_badge)
        title_layout.addStretch()

        header_text_layout.addWidget(title_container)

        # Sous-titre
        subtitle = QLabel("Outil de gestion financière - UFR Iba Der Thiam")
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 14px;")
        header_text_layout.addWidget(subtitle)

        # Informations supplémentaires
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        info_layout.setContentsMargins(0, 10, 0, 0)

        # Statut utilisateur
        user_status = QLabel(f"👤 Connecté en tant que: {self.user_role}")
        user_status.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 13px;")
        info_layout.addWidget(user_status)

        info_layout.addStretch()

        # Badge pour année académique
        year_badge = InfoBadge("Année Académique 2023-2024", "#FF5722")
        info_layout.addWidget(year_badge)

        header_text_layout.addWidget(info_container)
        header_text_layout.addStretch()

        header_layout.addWidget(header_text, 1)
        main_layout.addWidget(header_frame)

        # === Statistiques globales ===
        stats_title = QLabel("Indicateurs Clés de Performance")
        stats_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding-bottom: 5px;
            margin-top: 10px;
        """)
        main_layout.addWidget(stats_title)

        # Layout pour les cartes
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(20)
        main_layout.addLayout(self.cards_layout)

        # === Section des graphiques ===
        charts_title = QLabel("Analyse Visuelle des Finances")
        charts_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333;
            padding-bottom: 5px;
            margin-top: 10px;
        """)
        main_layout.addWidget(charts_title)

        # Conteneur des graphiques avec ombre et style
        self.graph_container = QFrame()
        self.graph_container.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
            padding: 20px;
        """)

        graph_shadow = QGraphicsDropShadowEffect()
        graph_shadow.setBlurRadius(15)
        graph_shadow.setColor(QColor(0, 0, 0, 30))
        graph_shadow.setOffset(0, 3)
        self.graph_container.setGraphicsEffect(graph_shadow)

        self.graph_layout = QHBoxLayout(self.graph_container)
        self.graph_layout.setContentsMargins(10, 10, 10, 10)
        self.graph_layout.setSpacing(20)
        main_layout.addWidget(self.graph_container)

        # === Section informative supplémentaire ===
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            background-color: #1976D2;
            border-radius: 15px;
            padding: 15px;
            color: white;
        """)

        info_shadow = QGraphicsDropShadowEffect()
        info_shadow.setBlurRadius(15)
        info_shadow.setColor(QColor(0, 0, 0, 30))
        info_shadow.setOffset(0, 3)
        info_frame.setGraphicsEffect(info_shadow)

        info_layout = QHBoxLayout(info_frame)

        # Contenu informatif
        info_text = QLabel(
            "<b>💡 Conseil budgétaire:</b> Pour une gestion optimale, suivez régulièrement "
            "l'évolution des dépenses par rapport aux budgets alloués."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(info_text)

        main_layout.addWidget(info_frame)

        # Ajouter un espace en bas pour le défilement
        main_layout.addStretch()

    def load_data(self):
        # Appeler uniquement la route des budgets (car le backend retourne déjà les bons calculs)
        result = get_budgets()
        if not result["success"]:
            # Gérer l'erreur si besoin
            placeholder = QLabel("Erreur lors du chargement des données")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #777; font-style: italic;")
            self.graph_layout.addWidget(placeholder)
            return

        budgets = result["data"]
        # Trouver le budget actif (en_cours) ou utiliser le premier disponible
        budget_actif = next((b for b in budgets if b["statut"] == "en_cours"), budgets[0] if budgets else None)

        if not budget_actif:
            placeholder = QLabel("Aucun budget actif trouvé")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #777; font-style: italic;")
            self.graph_layout.addWidget(placeholder)
            return

        # Extraction directe des valeurs calculées par le backend
        montant_total = budget_actif["montant_total"]
        montant_total_recettes = budget_actif["montant_total_recettes"]
        montant_total_depenses = budget_actif["montant_total_depenses_validees"]
        montant_disponible = budget_actif["montant_disponible"]

        # Formatage rapide
        def format_money(val):
            return f"{val:,.0f} F CFA".replace(",", " ")

        # === Cartes ===
        self.cards_layout.addWidget(
            AnimatedTile("BUDGET INITIAL", format_money(montant_total), self.color_palette["primary"], "💼"))
        self.cards_layout.addWidget(
            AnimatedTile("RECETTES", format_money(montant_total_recettes), self.color_palette["success"], "💰"))
        self.cards_layout.addWidget(
            AnimatedTile("DÉPENSES VALIDÉES", format_money(montant_total_depenses), self.color_palette["danger"], "📉"))
        self.cards_layout.addWidget(
            AnimatedTile("SOLDE DISPONIBLE", format_money(montant_disponible), self.color_palette["warning"], "⚖️"))

        # === Graphique donut : Dépenses VS Solde
        self.create_budget_chart(montant_total_depenses, montant_disponible)

        # === Graphique de répartition des dépenses (nécessite quand même un appel à get_depenses)
        depenses_result = get_depenses()
        if depenses_result["success"]:
            self.create_expense_distribution(depenses_result["data"])
        else:
            placeholder = QLabel("Impossible de charger les dépenses")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #777; font-style: italic;")
            self.graph_layout.addWidget(placeholder)

    def create_budget_chart(self, depenses_validees, solde_disponible):
        values = [depenses_validees, solde_disponible]
        labels = ["Dépensé", "Disponible"]
        colors = [self.color_palette["danger"], self.color_palette["success"]]

        # Sécurité pour éviter les valeurs négatives ou 0
        safe_values = [max(0, v) for v in values]
        if sum(safe_values) == 0:
            safe_values = [1, 0]  # Placeholder

        donut_chart = ResponsiveDonutChart(safe_values, labels, colors, "Budget Actif")
        self.graph_layout.addWidget(donut_chart)
        self.animated_widgets.append(donut_chart)

    def create_expense_distribution(self, depenses):
        if not depenses:
            placeholder = QLabel("Aucune dépense à afficher")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #777; font-style: italic;")
            self.graph_layout.addWidget(placeholder)
            return

        # Groupement des dépenses par type
        types_depenses = {}
        for dep in depenses:
            if dep.get("statut_validation") == "validee":
                type_dep = dep.get("type_depense", "Autres")
                types_depenses[type_dep] = types_depenses.get(type_dep, 0) + dep["montant"]

        if not types_depenses:
            placeholder = QLabel("Aucune dépense validée à afficher")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("color: #777; font-style: italic;")
            self.graph_layout.addWidget(placeholder)
            return

        # Trier par valeur décroissante
        sorted_types = sorted(types_depenses.items(), key=lambda x: x[1], reverse=True)
        types = [t[0] for t in sorted_types]
        valeurs = [t[1] for t in sorted_types]

        # Limiter à 5-6 types pour la lisibilité
        if len(types) > 6:
            autres_montant = sum(valeurs[5:])
            types = types[:5] + ["Autres"]
            valeurs = valeurs[:5] + [autres_montant]

        # Couleurs pour le graphique
        colors = [
            self.color_palette["primary"],
            self.color_palette["success"],
            self.color_palette["danger"],
            self.color_palette["warning"],
            self.color_palette["info"],
            self.color_palette["purple"]
        ]

        # Graphique à barres animé
        bar_chart = ResponsiveBarChart(valeurs, types, colors, "Répartition des Dépenses")
        self.graph_layout.addWidget(bar_chart)

        # Ajouter à la liste des animations
        self.animated_widgets.append(bar_chart)

    def start_animations(self):
        """Démarre les animations avec un léger décalage entre elles"""
        delay = 0
        for widget in self.animated_widgets:
            if isinstance(widget, ResponsiveBarChart) or isinstance(widget, ResponsiveDonutChart):
                QTimer.singleShot(delay, widget.startAnimation)
                delay += 300  # 300ms entre chaque animation