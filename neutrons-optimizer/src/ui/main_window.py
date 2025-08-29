"""
Janela principal do Nêutrons Optimizer.
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QTabWidget, QScrollArea, QSplitter, QFrame,
                               QLabel, QPushButton, QTextEdit, QMessageBox,
                               QProgressBar, QStatusBar, QApplication)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from .theme.colors import NeutronColors as NC
from .theme.styles import NeutronStyles
from .theme.particles import AnimatedBackground
from .components.dashboard import SystemDashboard
from .components.optimization_card import OptimizationCard
from ..core.optimizations import OPTIMIZATIONS
from ..core.optimizations.base import BaseOptimization, OptimizationResult
from ..utils.logging import logger
from ..utils.checks import SystemChecks


class OptimizationWorker(QThread):
    """Worker thread para executar otimizações."""
    
    progress = Signal(int, str)
    finished = Signal(BaseOptimization, OptimizationResult)
    
    def __init__(self, optimization: BaseOptimization, operation: str):
        super().__init__()
        self.optimization = optimization
        self.operation = operation  # 'simulate', 'apply', 'revert'
    
    def run(self):
        """Executa a operação da otimização."""
        try:
            self.progress.emit(25, f"Iniciando {self.operation}...")
            
            if self.operation == 'simulate':
                result = self.optimization._safe_simulate()
            elif self.operation == 'apply':
                result = self.optimization._safe_apply()
            elif self.operation == 'revert':
                result = self.optimization._safe_revert()
            else:
                result = OptimizationResult(False, "Operação desconhecida")
            
            self.progress.emit(100, "Concluído")
            self.finished.emit(self.optimization, result)
            
        except Exception as e:
            error_result = OptimizationResult(False, f"Erro inesperado: {e}")
            self.finished.emit(self.optimization, error_result)


class MainWindow(QMainWindow):
    """Janela principal do aplicativo."""
    
    def __init__(self):
        super().__init__()
        self.optimizations = [opt() for opt in OPTIMIZATIONS]
        self.optimization_cards = {}
        self.current_worker = None
        
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
        self._check_admin_status()
    
    def _setup_ui(self):
        """Configura a interface principal."""
        self.setWindowTitle("Nêutrons Optimizer")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Aplicar stylesheet global
        self.setStyleSheet(NeutronStyles.get_main_stylesheet())
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal com fundo animado
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Fundo animado
        self.animated_bg = AnimatedBackground()
        main_layout.addWidget(self.animated_bg)
        
        # Container principal sobreposto
        self.main_container = QWidget()
        self.main_container.setStyleSheet("background-color: transparent;")
        
        container_layout = QHBoxLayout(self.main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(20)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Painel esquerdo - Dashboard
        self._setup_dashboard_panel(splitter)
        
        # Painel direito - Tabs principais
        self._setup_main_tabs(splitter)
        
        # Configurar proporções do splitter
        splitter.setSizes([350, 850])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        container_layout.addWidget(splitter)
        
        # Adicionar container sobre o fundo
        main_layout.addWidget(self.main_container)
        
        # Status bar
        self._setup_status_bar()
    
    def _setup_dashboard_panel(self, parent):
        """Configura o painel do dashboard."""
        dashboard_frame = QFrame()
        dashboard_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {NC.with_alpha(NC.SURFACE, 0.95)};
                border: 1px solid {NC.BORDER};
                border-radius: 12px;
            }}
        """)
        
        dashboard_layout = QVBoxLayout(dashboard_frame)
        dashboard_layout.setContentsMargins(16, 16, 16, 16)
        
        # Dashboard do sistema
        self.dashboard = SystemDashboard()
        dashboard_layout.addWidget(self.dashboard)
        
        # Botão de ponto de restauração
        restore_btn = QPushButton("🔄 Criar Ponto de Restauração")
        restore_btn.setStyleSheet(NeutronStyles.get_button_style("secondary"))
        restore_btn.clicked.connect(self._create_restore_point)
        dashboard_layout.addWidget(restore_btn)
        
        parent.addWidget(dashboard_frame)
    
    def _setup_main_tabs(self, parent):
        """Configura as abas principais."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {NC.with_alpha(NC.SURFACE, 0.95)};
                border: 1px solid {NC.BORDER};
                border-radius: 12px;
            }}
            QTabBar::tab {{
                background-color: {NC.SURFACE_VARIANT};
                color: {NC.TEXT_SECONDARY};
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {NC.PRIMARY};
                color: {NC.BACKGROUND};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {NC.HOVER};
                color: {NC.TEXT_PRIMARY};
            }}
        """)
        
        # Aba de otimizações
        self._setup_optimizations_tab()
        
        # Aba de logs
        self._setup_logs_tab()
        
        # Aba sobre
        self._setup_about_tab()
        
        parent.addWidget(self.tab_widget)
    
    def _setup_optimizations_tab(self):
        """Configura a aba de otimizações."""
        # Scroll area para os cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        # Container dos cards
        cards_container = QWidget()
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(16, 16, 16, 16)
        
        # Criar cards para cada otimização
        for optimization in self.optimizations:
            card = OptimizationCard(optimization)
            self.optimization_cards[optimization] = card
            
            # Conectar sinais
            card.simulate_requested.connect(self._on_simulate_requested)
            card.apply_requested.connect(self._on_apply_requested)
            card.revert_requested.connect(self._on_revert_requested)
            
            cards_layout.addWidget(card)
        
        cards_layout.addStretch()
        scroll_area.setWidget(cards_container)
        
        self.tab_widget.addTab(scroll_area, "🎯 Otimizações")
    
    def _setup_logs_tab(self):
        """Configura a aba de logs."""
        logs_widget = QWidget()
        logs_layout = QVBoxLayout(logs_widget)
        logs_layout.setContentsMargins(16, 16, 16, 16)
        
        # Título
        logs_title = QLabel("📋 Logs do Sistema")
        logs_title.setStyleSheet(f"""
            color: {NC.PRIMARY};
            font-size: 14pt;
            font-weight: bold;
            margin-bottom: 12px;
        """)
        
        # Área de texto para logs
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {NC.SURFACE_VARIANT};
                color: {NC.TEXT_PRIMARY};
                border: 1px solid {NC.BORDER};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
            }}
        """)
        
        # Botões de controle
        logs_controls = QHBoxLayout()
        
        refresh_logs_btn = QPushButton("🔄 Atualizar")
        clear_logs_btn = QPushButton("🗑️ Limpar")
        
        refresh_logs_btn.setStyleSheet(NeutronStyles.get_button_style("secondary"))
        clear_logs_btn.setStyleSheet(NeutronStyles.get_button_style("danger"))
        
        refresh_logs_btn.clicked.connect(self._refresh_logs)
        clear_logs_btn.clicked.connect(self._clear_logs)
        
        logs_controls.addWidget(refresh_logs_btn)
        logs_controls.addWidget(clear_logs_btn)
        logs_controls.addStretch()
        
        logs_layout.addWidget(logs_title)
        logs_layout.addWidget(self.logs_text)
        logs_layout.addLayout(logs_controls)
        
        self.tab_widget.addTab(logs_widget, "📋 Logs")
        
        # Carregar logs iniciais
        self._refresh_logs()
    
    def _setup_about_tab(self):
        """Configura a aba sobre."""
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_layout.setContentsMargins(32, 32, 32, 32)
        about_layout.setAlignment(Qt.AlignCenter)
        
        # Logo/Título
        title = QLabel("⚛️ Nêutrons Optimizer")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {NC.PRIMARY};
            margin-bottom: 16px;
        """)
        
        # Versão
        version = QLabel("Versão 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(f"""
            color: {NC.TEXT_SECONDARY};
            font-size: 12pt;
            margin-bottom: 24px;
        """)
        
        # Descrição
        description = QLabel("""
        Um otimizador seguro e moderno para Windows 10/11
        com interface inspirada em estruturas atômicas.
        
        • Limpeza segura de arquivos temporários
        • Otimizações de performance para jogos
        • Sistema de backup e restauração
        • Interface moderna com tema escuro
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet(f"""
            color: {NC.TEXT_PRIMARY};
            font-size: 11pt;
            line-height: 1.6;
            margin-bottom: 32px;
        """)
        
        # Créditos
        credits = QLabel("Feito por MusashiSanS2")
        credits_font = QFont()
        credits_font.setPointSize(14)
        credits_font.setBold(True)
        credits.setFont(credits_font)
        credits.setAlignment(Qt.AlignCenter)
        credits.setStyleSheet(f"""
            color: {NC.ACCENT};
            background-color: {NC.SURFACE_VARIANT};
            border: 2px solid {NC.ACCENT};
            border-radius: 12px;
            padding: 16px 32px;
            margin: 16px;
        """)
        
        about_layout.addWidget(title)
        about_layout.addWidget(version)
        about_layout.addWidget(description)
        about_layout.addStretch()
        about_layout.addWidget(credits)
        about_layout.addStretch()
        
        self.tab_widget.addTab(about_widget, "ℹ️ Sobre")
    
    def _setup_status_bar(self):
        """Configura a barra de status."""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {NC.SURFACE_VARIANT};
                color: {NC.TEXT_SECONDARY};
                border-top: 1px solid {NC.BORDER};
                padding: 4px 12px;
            }}
        """)
        
        # Informações básicas
        self.status_label = QLabel("Pronto")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar (oculta por padrão)
        self.main_progress = QProgressBar()
        self.main_progress.setVisible(False)
        self.main_progress.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.main_progress)
        
        self.setStatusBar(self.status_bar)
    
    def _setup_menu(self):
        """Configura o menu principal."""
        # Por enquanto, menu simples via status bar
        # Pode ser expandido com QMenuBar se necessário
        pass
    
    def _connect_signals(self):
        """Conecta sinais da aplicação."""
        # Timer para atualizar dashboard
        self.dashboard_timer = QTimer()
        self.dashboard_timer.timeout.connect(self._update_dashboard)
        self.dashboard_timer.start(10000)  # A cada 10 segundos
    
    def _check_admin_status(self):
        """Verifica status de administrador."""
        if not SystemChecks.check_admin_rights():
            self.status_label.setText("⚠️ Execute como administrador para todas as funcionalidades")
            self.status_label.setStyleSheet(f"color: {NC.WARNING};")
        else:
            self.status_label.setText("✅ Executando com privilégios de administrador")
            self.status_label.setStyleSheet(f"color: {NC.SUCCESS};")
    
    def _update_dashboard(self):
        """Atualiza informações do dashboard."""
        try:
            # Contar otimizações aplicadas
            applied_count = sum(1 for opt in self.optimizations if opt.is_applied())
            total_count = len(self.optimizations)
            
            # Atualizar dashboard
            self.dashboard.update_optimizations_status(applied_count, total_count)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar dashboard: {e}")
    
    def _on_simulate_requested(self, optimization: BaseOptimization):
        """Callback para simulação de otimização."""
        self._run_optimization(optimization, 'simulate')
    
    def _on_apply_requested(self, optimization: BaseOptimization):
        """Callback para aplicação de otimização."""
        # Confirmação para operações de alto impacto
        if optimization.impact_level == 'high':
            reply = QMessageBox.question(
                self,
                "Confirmação",
                f"A otimização '{optimization.display_name}' tem alto impacto.\n\n"
                f"Tem certeza que deseja continuar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        self._run_optimization(optimization, 'apply')
    
    def _on_revert_requested(self, optimization: BaseOptimization):
        """Callback para reversão de otimização."""
        reply = QMessageBox.question(
            self,
            "Confirmação",
            f"Deseja reverter a otimização '{optimization.display_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._run_optimization(optimization, 'revert')
    
    def _run_optimization(self, optimization: BaseOptimization, operation: str):
        """Executa uma otimização em thread separada."""
        if self.current_worker and self.current_worker.isRunning():
            QMessageBox.warning(self, "Aviso", "Já existe uma operação em andamento.")
            return
        
        # Atualizar UI
        card = self.optimization_cards[optimization]
        card.set_processing(True, f"{operation.title()}...")
        
        # Mostrar progress na status bar
        self.main_progress.setVisible(True)
        self.main_progress.setRange(0, 100)
        self.status_label.setText(f"{operation.title()} {optimization.display_name}...")
        
        # Criar e iniciar worker
        self.current_worker = OptimizationWorker(optimization, operation)
        self.current_worker.progress.connect(self._on_worker_progress)
        self.current_worker.finished.connect(self._on_worker_finished)
        self.current_worker.start()
    
    def _on_worker_progress(self, value: int, message: str):
        """Callback para progresso do worker."""
        self.main_progress.setValue(value)
        if message:
            self.status_label.setText(message)
    
    def _on_worker_finished(self, optimization: BaseOptimization, result: OptimizationResult):
        """Callback para conclusão do worker."""
        # Atualizar UI
        card = self.optimization_cards[optimization]
        card.set_processing(False)
        card.show_result(result.success, result.message)
        
        # Ocultar progress
        self.main_progress.setVisible(False)
        
        # Atualizar status
        if result.success:
            self.status_label.setText(f"✅ {result.message}")
            self.status_label.setStyleSheet(f"color: {NC.SUCCESS};")
        else:
            self.status_label.setText(f"❌ {result.message}")
            self.status_label.setStyleSheet(f"color: {NC.ERROR};")
        
        # Atualizar dashboard
        self._update_dashboard()
        
        # Limpar worker
        self.current_worker = None
        
        # Log da operação
        operation_type = "sucesso" if result.success else "erro"
        logger.info(f"Otimização {optimization.display_name}: {operation_type} - {result.message}")
    
    def _create_restore_point(self):
        """Cria um ponto de restauração do sistema."""
        try:
            self.status_label.setText("Criando ponto de restauração...")
            
            success = SystemChecks.create_restore_point("Nêutrons Optimizer")
            
            if success:
                self.status_label.setText("✅ Ponto de restauração criado")
                self.status_label.setStyleSheet(f"color: {NC.SUCCESS};")
                QMessageBox.information(self, "Sucesso", "Ponto de restauração criado com sucesso!")
            else:
                self.status_label.setText("❌ Falha ao criar ponto de restauração")
                self.status_label.setStyleSheet(f"color: {NC.ERROR};")
                QMessageBox.warning(self, "Erro", "Não foi possível criar o ponto de restauração.")
                
        except Exception as e:
            error_msg = f"Erro ao criar ponto de restauração: {e}"
            self.status_label.setText("❌ Erro no ponto de restauração")
            self.status_label.setStyleSheet(f"color: {NC.ERROR};")
            QMessageBox.critical(self, "Erro", error_msg)
            logger.error(error_msg)
    
    def _refresh_logs(self):
        """Atualiza os logs exibidos."""
        try:
            logs = logger.get_recent_logs(24)  # Últimas 24 horas
            self.logs_text.clear()
            
            if logs:
                self.logs_text.setPlainText('\n'.join(logs))
                # Scrollar para o final
                cursor = self.logs_text.textCursor()
                cursor.movePosition(cursor.End)
                self.logs_text.setTextCursor(cursor)
            else:
                self.logs_text.setPlainText("Nenhum log disponível.")
                
        except Exception as e:
            self.logs_text.setPlainText(f"Erro ao carregar logs: {e}")
    
    def _clear_logs(self):
        """Limpa a exibição de logs."""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja limpar a exibição de logs?\n(Os arquivos de log não serão removidos)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.logs_text.clear()
    
    def closeEvent(self, event):
        """Manipula o fechamento da janela."""
        # Parar worker se estiver rodando
        if self.current_worker and self.current_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirmação",
                "Uma operação está em andamento. Deseja cancelar e sair?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.current_worker.quit()
                self.current_worker.wait(3000)  # Aguardar até 3 segundos
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()