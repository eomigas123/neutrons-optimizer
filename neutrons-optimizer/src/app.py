"""
Aplicação principal do Nêutrons Optimizer.
"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont

from .ui.main_window import MainWindow
from .ui.theme.colors import NeutronColors as NC
from .core.system.uac import UACElevation
from .utils.logging import logger
from .utils.os_detect import windows_info
from .utils.checks import SystemChecks


class NeutronsOptimizerApp:
    """Aplicação principal do Nêutrons Optimizer."""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.splash = None
    
    def create_splash_screen(self) -> QSplashScreen:
        """Cria a tela de splash."""
        # Criar pixmap para o splash
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(NC.BACKGROUND))
        
        # Desenhar o splash
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fundo gradient
        gradient_brush = painter.brush()
        painter.fillRect(pixmap.rect(), QColor(NC.BACKGROUND))
        
        # Título
        painter.setPen(QColor(NC.PRIMARY))
        title_font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "⚛️ Nêutrons Optimizer")
        
        # Subtítulo
        painter.setPen(QColor(NC.TEXT_SECONDARY))
        subtitle_font = QFont("Arial", 10)
        painter.setFont(subtitle_font)
        subtitle_rect = pixmap.rect().adjusted(0, 50, 0, 0)
        painter.drawText(subtitle_rect, Qt.AlignCenter, "Otimizador moderno para Windows")
        
        # Créditos
        painter.setPen(QColor(NC.ACCENT))
        credits_font = QFont("Arial", 12, QFont.Bold)
        painter.setFont(credits_font)
        credits_rect = pixmap.rect().adjusted(0, 100, 0, -20)
        painter.drawText(credits_rect, Qt.AlignCenter | Qt.AlignBottom, "Feito por MusashiSanS2")
        
        painter.end()
        
        # Criar splash screen
        splash = QSplashScreen(pixmap)
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        return splash
    
    def show_splash_message(self, message: str):
        """Mostra mensagem no splash screen."""
        if self.splash:
            self.splash.showMessage(
                message,
                alignment=Qt.AlignBottom | Qt.AlignCenter,
                color=QColor(NC.PRIMARY)
            )
            QApplication.processEvents()
    
    def check_system_requirements(self) -> bool:
        """Verifica requisitos do sistema."""
        try:
            self.show_splash_message("Verificando sistema...")
            
            # Verificar Windows 10/11
            if not (windows_info.is_windows_10 or windows_info.is_windows_11):
                QMessageBox.critical(
                    None,
                    "Sistema Incompatível",
                    f"Este aplicativo requer Windows 10 ou 11.\n\n"
                    f"Sistema detectado: {windows_info.get_summary()}"
                )
                return False
            
            # Verificar espaço em disco
            has_space, space_gb = SystemChecks.check_disk_space(0.5)  # Mínimo 500MB
            if not has_space:
                QMessageBox.warning(
                    None,
                    "Pouco Espaço em Disco",
                    f"Espaço disponível muito baixo: {space_gb:.1f} GB\n\n"
                    f"Recomenda-se pelo menos 500 MB livres."
                )
            
            logger.info(f"Sistema compatível: {windows_info.get_summary()}")
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação do sistema: {e}")
            QMessageBox.critical(
                None,
                "Erro de Inicialização",
                f"Erro ao verificar requisitos do sistema:\n{e}"
            )
            return False
    
    def check_admin_privileges(self) -> bool:
        """Verifica e solicita privilégios de administrador se necessário."""
        try:
            self.show_splash_message("Verificando privilégios...")
            
            if UACElevation.is_admin():
                logger.info("Aplicativo executando com privilégios de administrador")
                return True
            
            # Perguntar se deseja elevar privilégios
            reply = QMessageBox.question(
                None,
                "Privilégios de Administrador",
                "Para funcionalidade completa, execute como administrador.\n\n"
                "Deseja reiniciar com privilégios elevados?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.show_splash_message("Elevando privilégios...")
                if UACElevation.elevate_current_process():
                    # O processo atual será encerrado e um novo iniciado
                    return False
                else:
                    QMessageBox.warning(
                        None,
                        "Falha na Elevação",
                        "Não foi possível obter privilégios de administrador.\n"
                        "Algumas funcionalidades podem estar limitadas."
                    )
            
            logger.warning("Aplicativo executando sem privilégios de administrador")
            return True
            
        except Exception as e:
            logger.error(f"Erro na verificação de privilégios: {e}")
            return True  # Continuar mesmo com erro
    
    def initialize_application(self):
        """Inicializa a aplicação."""
        try:
            self.show_splash_message("Inicializando componentes...")
            
            # Configurar logging
            logger.info("=== Nêutrons Optimizer Iniciado ===")
            logger.info(f"Sistema: {windows_info.get_summary()}")
            logger.info(f"Admin: {UACElevation.is_admin()}")
            
            # Verificar diretórios necessários
            self.show_splash_message("Preparando diretórios...")
            self._ensure_directories()
            
            # Limpeza de logs antigos
            logger.cleanup_old_logs(30)
            
            logger.info("Aplicação inicializada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
            QMessageBox.critical(
                None,
                "Erro de Inicialização",
                f"Erro ao inicializar aplicação:\n{e}"
            )
            return False
    
    def _ensure_directories(self):
        """Garante que os diretórios necessários existem."""
        directories = [
            Path.home() / "AppData" / "Local" / "NeutronsOptimizer",
            Path.home() / "AppData" / "Local" / "NeutronsOptimizer" / "logs",
            Path.home() / "AppData" / "Local" / "NeutronsOptimizer" / "backups",
            Path.home() / "AppData" / "Local" / "NeutronsOptimizer" / "backups" / "registry",
            Path.home() / "AppData" / "Local" / "NeutronsOptimizer" / "backups" / "files"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def create_main_window(self):
        """Cria a janela principal."""
        try:
            self.show_splash_message("Carregando interface...")
            
            self.main_window = MainWindow()
            logger.info("Janela principal criada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar janela principal: {e}")
            QMessageBox.critical(
                None,
                "Erro de Interface",
                f"Erro ao criar interface principal:\n{e}"
            )
            return False
    
    def run(self) -> int:
        """Executa a aplicação."""
        try:
            # Criar aplicação Qt
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Nêutrons Optimizer")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("MusashiSanS2")
            
            # Configurar ícone da aplicação (se disponível)
            # self.app.setWindowIcon(QIcon("path/to/icon.ico"))
            
            # Mostrar splash screen
            self.splash = self.create_splash_screen()
            self.splash.show()
            QApplication.processEvents()
            
            # Verificações do sistema
            if not self.check_system_requirements():
                return 1
            
            if not self.check_admin_privileges():
                return 0  # Processo sendo reiniciado com elevação
            
            # Inicializar aplicação
            if not self.initialize_application():
                return 1
            
            # Criar janela principal
            if not self.create_main_window():
                return 1
            
            # Mostrar janela principal e ocultar splash
            self.show_splash_message("Carregando...")
            QTimer.singleShot(1000, self._show_main_window)
            
            # Executar loop principal
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Erro fatal na aplicação: {e}")
            if self.app:
                QMessageBox.critical(
                    None,
                    "Erro Fatal",
                    f"Erro fatal na aplicação:\n{e}"
                )
            return 1
        
        finally:
            # Cleanup
            if self.splash:
                self.splash.close()
            logger.info("=== Nêutrons Optimizer Finalizado ===")
    
    def _show_main_window(self):
        """Mostra a janela principal e oculta o splash."""
        if self.main_window:
            self.main_window.show()
        if self.splash:
            self.splash.finish(self.main_window)


def main():
    """Função principal de entrada."""
    app = NeutronsOptimizerApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())