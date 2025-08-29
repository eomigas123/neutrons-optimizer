"""
Sistema de elevação UAC para operações administrativas.
"""
import sys
import os
import ctypes
from ctypes import wintypes
import subprocess
from ...utils.logging import logger


class UACElevation:
    """Gerenciador de elevação de privilégios UAC."""
    
    @staticmethod
    def is_admin() -> bool:
        """Verifica se o processo atual tem privilégios de administrador."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.error(f"Erro ao verificar privilégios de admin: {e}")
            return False
    
    @staticmethod
    def elevate_current_process() -> bool:
        """Reinicia o processo atual com privilégios elevados."""
        if UACElevation.is_admin():
            return True
        
        try:
            # Obter o caminho do executável atual
            if getattr(sys, 'frozen', False):
                # Executável compilado
                script_path = sys.executable
            else:
                # Script Python
                script_path = os.path.abspath(sys.argv[0])
            
            # Parâmetros para passar para o processo elevado
            params = ' '.join(sys.argv[1:])
            
            # Usar ShellExecuteW para solicitar elevação
            result = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                script_path,
                params,
                None,
                1  # SW_SHOWNORMAL
            )
            
            if result > 32:  # Sucesso
                logger.info("Processo reiniciado com privilégios elevados")
                return True
            else:
                logger.error(f"Falha na elevação UAC: código {result}")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante elevação UAC: {e}")
            return False
    
    @staticmethod
    def run_elevated_command(command: str, timeout: int = 60) -> tuple[bool, str, str]:
        """Executa um comando com privilégios elevados."""
        try:
            # Criar comando PowerShell para executar com elevação
            ps_command = f'''
            Start-Process powershell -ArgumentList "-Command", "{command}" -Verb RunAs -Wait -WindowStyle Hidden
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            
            if success:
                logger.debug(f"Comando elevado executado com sucesso: {command}")
            else:
                logger.error(f"Falha no comando elevado: {command} | Erro: {stderr}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout no comando elevado: {command}")
            return False, "", "Timeout na execução"
        except Exception as e:
            logger.error(f"Erro ao executar comando elevado: {e}")
            return False, "", str(e)
    
    @staticmethod
    def ensure_admin_or_exit():
        """Garante que o processo tem privilégios de admin ou sai."""
        if not UACElevation.is_admin():
            logger.warning("Privilégios de administrador necessários")
            if UACElevation.elevate_current_process():
                sys.exit(0)  # Sair do processo atual
            else:
                logger.error("Não foi possível obter privilégios de administrador")
                sys.exit(1)


class AdminContext:
    """Context manager para operações que requerem privilégios de admin."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.was_admin = False
    
    def __enter__(self):
        self.was_admin = UACElevation.is_admin()
        if not self.was_admin:
            logger.warning(f"Operação '{self.operation_name}' requer privilégios de administrador")
            raise PermissionError(f"Privilégios de administrador necessários para: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Erro na operação administrativa '{self.operation_name}': {exc_val}")
        return False