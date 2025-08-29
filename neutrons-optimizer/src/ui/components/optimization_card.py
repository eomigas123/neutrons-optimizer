"""
Card de otimização para a interface principal.
"""
from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QProgressBar, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from ..theme.colors import NeutronColors as NC
from ..theme.styles import NeutronStyles
from ...core.optimizations.base import BaseOptimization, OptimizationStatus


class OptimizationCard(QFrame):
    """Card para exibir informações de uma otimização."""
    
    # Sinais
    simulate_requested = Signal(BaseOptimization)
    apply_requested = Signal(BaseOptimization)
    revert_requested = Signal(BaseOptimization)
    
    def __init__(self, optimization: BaseOptimization, parent=None):
        super().__init__(parent)
        self.optimization = optimization
        self.is_processing = False
        
        self._setup_ui()
        self._connect_signals()
        self._update_display()
    
    def _setup_ui(self):
        """Configura a interface do card."""
        self.setFixedHeight(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header com título e status
        header_layout = QHBoxLayout()
        
        # Título
        self.title_label = QLabel(self.optimization.display_name)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {NC.TEXT_PRIMARY};")
        
        # Status badge
        self.status_badge = QLabel()
        self.status_badge.setFixedSize(80, 24)
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                border-radius: 12px;
                font-size: 9pt;
                font-weight: bold;
                padding: 4px 8px;
            }}
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_badge)
        
        # Descrição
        self.description_label = QLabel(self.optimization.description)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(f"""
            color: {NC.TEXT_SECONDARY};
            font-size: 10pt;
            line-height: 1.4;
        """)
        
        # Informações adicionais
        info_layout = QHBoxLayout()
        
        # Categoria
        self.category_label = QLabel(f"📁 {self.optimization.category}")
        self.category_label.setStyleSheet(f"color: {NC.TEXT_MUTED}; font-size: 9pt;")
        
        # Impacto
        impact_colors = {
            "low": NC.SUCCESS,
            "medium": NC.WARNING, 
            "high": NC.ERROR
        }
        impact_color = impact_colors.get(self.optimization.impact_level, NC.TEXT_MUTED)
        self.impact_label = QLabel(f"⚡ {self.optimization.impact_level.title()}")
        self.impact_label.setStyleSheet(f"color: {impact_color}; font-size: 9pt;")
        
        # Tempo estimado
        self.time_label = QLabel(f"⏱️ ~{self.optimization.estimated_time}s")
        self.time_label.setStyleSheet(f"color: {NC.TEXT_MUTED}; font-size: 9pt;")
        
        info_layout.addWidget(self.category_label)
        info_layout.addWidget(self.impact_label)
        info_layout.addWidget(self.time_label)
        info_layout.addStretch()
        
        # Progress bar (inicialmente oculta)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {NC.SURFACE_VARIANT};
                border: 1px solid {NC.BORDER};
                border-radius: 4px;
                text-align: center;
                color: {NC.TEXT_PRIMARY};
                font-weight: bold;
                font-size: 9pt;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: {NC.get_gradient(NC.PRIMARY, NC.SECONDARY)};
                border-radius: 3px;
            }}
        """)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.simulate_btn = QPushButton("🔍 Simular")
        self.apply_btn = QPushButton("✅ Aplicar")
        self.revert_btn = QPushButton("↩️ Desfazer")
        
        # Estilizar botões
        button_style = """
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 9pt;
                min-width: 80px;
            }
        """
        
        self.simulate_btn.setStyleSheet(button_style + NeutronStyles.get_button_style("secondary"))
        self.apply_btn.setStyleSheet(button_style + NeutronStyles.get_button_style("primary"))
        self.revert_btn.setStyleSheet(button_style + NeutronStyles.get_button_style("danger"))
        
        buttons_layout.addWidget(self.simulate_btn)
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.revert_btn)
        buttons_layout.addStretch()
        
        # Adicionar tudo ao layout principal
        layout.addLayout(header_layout)
        layout.addWidget(self.description_label)
        layout.addLayout(info_layout)
        layout.addWidget(self.progress_bar)
        layout.addLayout(buttons_layout)
        
        # Aplicar estilo do card
        self._update_card_style()
    
    def _connect_signals(self):
        """Conecta os sinais dos botões."""
        self.simulate_btn.clicked.connect(lambda: self.simulate_requested.emit(self.optimization))
        self.apply_btn.clicked.connect(lambda: self.apply_requested.emit(self.optimization))
        self.revert_btn.clicked.connect(lambda: self.revert_requested.emit(self.optimization))
    
    def _update_display(self):
        """Atualiza a exibição baseada no status atual."""
        status = self.optimization.get_status()
        
        # Atualizar badge de status
        status_config = {
            OptimizationStatus.NOT_APPLIED: ("Não Aplicado", NC.TEXT_MUTED, NC.SURFACE_VARIANT),
            OptimizationStatus.APPLIED: ("Aplicado", NC.BACKGROUND, NC.SUCCESS),
            OptimizationStatus.SIMULATED: ("Simulado", NC.BACKGROUND, NC.INFO),
            OptimizationStatus.ERROR: ("Erro", NC.TEXT_PRIMARY, NC.ERROR),
            OptimizationStatus.PARTIAL: ("Parcial", NC.BACKGROUND, NC.WARNING)
        }
        
        text, text_color, bg_color = status_config.get(status, ("Desconhecido", NC.TEXT_MUTED, NC.SURFACE_VARIANT))
        
        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 12px;
                font-size: 9pt;
                font-weight: bold;
                padding: 4px 8px;
            }}
        """)
        
        # Atualizar disponibilidade dos botões
        self.simulate_btn.setEnabled(not self.is_processing)
        self.apply_btn.setEnabled(not self.is_processing and status != OptimizationStatus.APPLIED)
        self.revert_btn.setEnabled(not self.is_processing and self.optimization.can_revert())
        
        # Mostrar informações de admin se necessário
        if self.optimization.requires_admin:
            self.title_label.setText(f"🛡️ {self.optimization.display_name}")
        
        if self.optimization.requires_reboot:
            self.description_label.setText(f"{self.optimization.description} (Requer reinicialização)")
        
        # Atualizar estilo do card baseado no status
        self._update_card_style()
    
    def _update_card_style(self):
        """Atualiza o estilo visual do card."""
        status = self.optimization.get_status()
        
        # Cores da borda baseadas no status
        border_colors = {
            OptimizationStatus.NOT_APPLIED: NC.BORDER,
            OptimizationStatus.APPLIED: NC.SUCCESS,
            OptimizationStatus.SIMULATED: NC.INFO,
            OptimizationStatus.ERROR: NC.ERROR,
            OptimizationStatus.PARTIAL: NC.WARNING
        }
        
        border_color = border_colors.get(status, NC.BORDER)
        
        self.setStyleSheet(f"""
            OptimizationCard {{
                background-color: {NC.SURFACE_VARIANT};
                border: 2px solid {border_color};
                border-radius: 12px;
                margin: 4px;
            }}
            OptimizationCard:hover {{
                border-color: {NC.PRIMARY};
                background-color: {NC.SURFACE};
            }}
        """)
    
    def set_processing(self, processing: bool, message: str = ""):
        """Define o estado de processamento."""
        self.is_processing = processing
        
        if processing:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Modo indeterminado
            if message:
                self.progress_bar.setFormat(message)
        else:
            self.progress_bar.setVisible(False)
        
        self._update_display()
    
    def update_progress(self, value: int, maximum: int = 100, message: str = ""):
        """Atualiza o progresso da operação."""
        if self.is_processing:
            self.progress_bar.setRange(0, maximum)
            self.progress_bar.setValue(value)
            if message:
                self.progress_bar.setFormat(message)
    
    def show_result(self, success: bool, message: str):
        """Mostra o resultado de uma operação."""
        # Atualizar status
        self._update_display()
        
        # Animação de feedback visual
        self._animate_feedback(success)
        
        # Timer para ocultar mensagem
        if message:
            # Aqui poderia mostrar um tooltip ou notification
            self.setToolTip(message)
            QTimer.singleShot(3000, lambda: self.setToolTip(""))
    
    def _animate_feedback(self, success: bool):
        """Animação de feedback visual."""
        # Animação simples de escala
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutBack)
        
        original_geometry = self.geometry()
        
        # Pequeno "bounce" para feedback
        expanded = original_geometry.adjusted(-2, -2, 2, 2)
        
        self.animation.setStartValue(original_geometry)
        self.animation.setEndValue(expanded)
        
        # Voltar ao tamanho original
        def return_to_original():
            return_animation = QPropertyAnimation(self, b"geometry")
            return_animation.setDuration(200)
            return_animation.setStartValue(expanded)
            return_animation.setEndValue(original_geometry)
            return_animation.start()
        
        self.animation.finished.connect(return_to_original)
        self.animation.start()
    
    def refresh(self):
        """Atualiza completamente o card."""
        self._update_display()