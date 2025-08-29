"""
Sistema de logging centralizado para o Nêutrons Optimizer.
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import json


class OptimizationLogger:
    """Logger customizado para otimizações do sistema."""
    
    def __init__(self):
        self.log_file = Path.home() / "AppData" / "Local" / "NeutronsOptimizer" / "logs" / "optimizer.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging
        self.logger = logging.getLogger("NeutronsOptimizer")
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para arquivo
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adicionar handlers se não existirem
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, operation: str = None):
        """Log de informação."""
        if operation:
            message = f"[{operation}] {message}"
        self.logger.info(message)
    
    def warning(self, message: str, operation: str = None):
        """Log de warning."""
        if operation:
            message = f"[{operation}] {message}"
        self.logger.warning(message)
    
    def error(self, message: str, operation: str = None):
        """Log de erro."""
        if operation:
            message = f"[{operation}] {message}"
        self.logger.error(message)
    
    def debug(self, message: str, operation: str = None):
        """Log de debug."""
        if operation:
            message = f"[{operation}] {message}"
        self.logger.debug(message)
    
    def log_operation_start(self, operation: str, details: Dict[str, Any] = None):
        """Log do início de uma operação."""
        msg = f"Iniciando operação: {operation}"
        if details:
            msg += f" | Detalhes: {json.dumps(details, ensure_ascii=False)}"
        self.info(msg, operation)
    
    def log_operation_success(self, operation: str, results: Dict[str, Any] = None):
        """Log de sucesso de uma operação."""
        msg = f"Operação concluída com sucesso: {operation}"
        if results:
            msg += f" | Resultados: {json.dumps(results, ensure_ascii=False)}"
        self.info(msg, operation)
    
    def log_operation_error(self, operation: str, error: str):
        """Log de erro de uma operação."""
        self.error(f"Falha na operação: {operation} | Erro: {error}", operation)
    
    def get_recent_logs(self, hours: int = 24) -> List[str]:
        """Retorna logs recentes."""
        try:
            if not self.log_file.exists():
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Filtrar por data se necessário (implementação simplificada)
            return [line.strip() for line in lines[-1000:]]  # Últimas 1000 linhas
        except Exception as e:
            self.error(f"Erro ao ler logs: {e}")
            return []
    
    def clear_old_logs(self, days: int = 30):
        """Limpa logs antigos."""
        try:
            log_dir = self.log_file.parent
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    self.info(f"Log antigo removido: {log_file.name}")
        except Exception as e:
            self.error(f"Erro ao limpar logs antigos: {e}")


# Instância global do logger
logger = OptimizationLogger()