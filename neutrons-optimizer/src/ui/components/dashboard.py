"""
Dashboard com informações do sistema.
"""
import psutil
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QProgressBar, QFrame, QGridLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ..theme.colors import NeutronColors as NC
from ...utils.os_detect import windows_info
from ...utils.checks import SystemChecks


class SystemInfoCard(QFrame):
    """Card de informações do sistema."""
    
    def __init__(self, title: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self._setup_ui(title, value, subtitle)
    
    def _setup_ui(self, title: str, value: str, subtitle: str):
        """Configura a interface do card."""
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {NC.SURFACE_VARIANT};
                border: 1px solid {NC.BORDER};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame:hover {{
                border-color: {NC.PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Título
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            color: {NC.TEXT_MUTED};
            font-size: 9pt;
            font-weight: bold;
        """)
        
        # Valor principal
        self.value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(14)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {NC.PRIMARY};")
        
        # Subtítulo
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"""
            color: {NC.TEXT_SECONDARY};
            font-size: 8pt;
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        if subtitle:
            layout.addWidget(self.subtitle_label)
        layout.addStretch()
    
    def update_value(self, value: str, subtitle: str = ""):
        """Atualiza o valor do card."""
        self.value_label.setText(value)
        if subtitle:
            self.subtitle_label.setText(subtitle)


class SystemDashboard(QWidget):
    """Dashboard principal com informações do sistema."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_timer()
        self._update_info()
    
    def _setup_ui(self):
        """Configura a interface do dashboard."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Título do dashboard
        title_label = QLabel("📊 Status do Sistema")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {NC.PRIMARY}; margin-bottom: 8px;")
        
        # Grid de informações
        info_grid = QGridLayout()
        info_grid.setSpacing(12)
        
        # Cards de informação
        self.os_card = SystemInfoCard("Sistema Operacional", "Carregando...", "")
        self.cpu_card = SystemInfoCard("Processador", "Carregando...", "")
        self.memory_card = SystemInfoCard("Memória RAM", "Carregando...", "")
        self.disk_card = SystemInfoCard("Armazenamento", "Carregando...", "")
        
        # Adicionar cards ao grid
        info_grid.addWidget(self.os_card, 0, 0)
        info_grid.addWidget(self.cpu_card, 0, 1)
        info_grid.addWidget(self.memory_card, 1, 0)
        info_grid.addWidget(self.disk_card, 1, 1)
        
        # Status de otimizações
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {NC.SURFACE_VARIANT};
                border: 1px solid {NC.BORDER};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        
        status_layout = QVBoxLayout(status_frame)
        
        status_title = QLabel("🎯 Status das Otimizações")
        status_title.setStyleSheet(f"""
            color: {NC.TEXT_PRIMARY};
            font-size: 12pt;
            font-weight: bold;
            margin-bottom: 8px;
        """)
        
        # Informações de otimizações
        self.optimizations_info = QLabel("Nenhuma otimização aplicada ainda")
        self.optimizations_info.setStyleSheet(f"""
            color: {NC.TEXT_SECONDARY};
            font-size: 10pt;
        """)
        
        # Última atividade
        self.last_activity = QLabel("Última atividade: Nunca")
        self.last_activity.setStyleSheet(f"""
            color: {NC.TEXT_MUTED};
            font-size: 9pt;
            margin-top: 8px;
        """)
        
        status_layout.addWidget(status_title)
        status_layout.addWidget(self.optimizations_info)
        status_layout.addWidget(self.last_activity)
        status_layout.addStretch()
        
        # Adicionar tudo ao layout principal
        layout.addWidget(title_label)
        layout.addLayout(info_grid)
        layout.addWidget(status_frame)
        layout.addStretch()
    
    def _setup_timer(self):
        """Configura timer para atualização periódica."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_info)
        self.update_timer.start(5000)  # Atualizar a cada 5 segundos
    
    def _update_info(self):
        """Atualiza as informações do sistema."""
        try:
            # Informações do OS
            os_info = windows_info.get_summary()
            self.os_card.update_value(
                f"Windows {windows_info.release}",
                f"Build {windows_info.build}"
            )
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            cpu_count = psutil.cpu_count()
            self.cpu_card.update_value(
                f"{cpu_percent:.1f}%",
                f"{cpu_count} núcleos"
            )
            
            # Memória
            memory = psutil.virtual_memory()
            memory_used_gb = (memory.total - memory.available) / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            self.memory_card.update_value(
                f"{memory_used_gb:.1f} GB",
                f"de {memory_total_gb:.1f} GB ({memory.percent:.1f}%)"
            )
            
            # Disco
            disk = psutil.disk_usage('C:')
            disk_free_gb = disk.free / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            disk_percent = (disk.used / disk.total) * 100
            self.disk_card.update_value(
                f"{disk_free_gb:.1f} GB",
                f"livres de {disk_total_gb:.1f} GB ({disk_percent:.1f}% usado)"
            )
            
        except Exception as e:
            # Em caso de erro, mostrar informação básica
            self.os_card.update_value("Windows", "Informação indisponível")
            self.cpu_card.update_value("N/A", "Erro ao obter dados")
            self.memory_card.update_value("N/A", "Erro ao obter dados")
            self.disk_card.update_value("N/A", "Erro ao obter dados")
    
    def update_optimizations_status(self, applied_count: int, total_count: int, last_activity: str = None):
        """Atualiza o status das otimizações."""
        if applied_count == 0:
            status_text = "Nenhuma otimização aplicada ainda"
            status_color = NC.TEXT_MUTED
        elif applied_count == total_count:
            status_text = f"Todas as {total_count} otimizações aplicadas ✅"
            status_color = NC.SUCCESS
        else:
            status_text = f"{applied_count} de {total_count} otimizações aplicadas"
            status_color = NC.WARNING
        
        self.optimizations_info.setText(status_text)
        self.optimizations_info.setStyleSheet(f"""
            color: {status_color};
            font-size: 10pt;
            font-weight: bold;
        """)
        
        if last_activity:
            self.last_activity.setText(f"Última atividade: {last_activity}")
    
    def show_system_health(self):
        """Mostra informações de saúde do sistema."""
        try:
            checks = SystemChecks.validate_optimization_requirements()
            
            health_items = []
            
            if checks.get('admin_rights', False):
                health_items.append("✅ Privilégios de administrador")
            else:
                health_items.append("❌ Sem privilégios de administrador")
            
            if checks.get('disk_space', False):
                health_items.append("✅ Espaço em disco suficiente")
            else:
                health_items.append("⚠️ Pouco espaço em disco")
            
            if checks.get('no_critical_processes', True):
                health_items.append("✅ Sistema estável")
            else:
                health_items.append("⚠️ Processos críticos em execução")
            
            # Atualizar display com informações de saúde
            health_text = "\n".join(health_items)
            
            # Aqui você poderia mostrar em um tooltip ou dialog
            # Por enquanto, vamos apenas fazer log
            from ...utils.logging import logger
            logger.info(f"Saúde do sistema:\n{health_text}")
            
        except Exception as e:
            from ...utils.logging import logger
            logger.error(f"Erro ao verificar saúde do sistema: {e}")