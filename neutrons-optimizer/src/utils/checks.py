"""
Verificações de pré-requisitos e segurança do sistema.
"""
import os
import shutil
import subprocess
import psutil
from pathlib import Path
from typing import Dict, List, Tuple
from .logging import logger


class SystemChecks:
    """Verificações do sistema antes de executar otimizações."""
    
    @staticmethod
    def check_admin_rights() -> bool:
        """Verifica se o programa está rodando como administrador."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.error(f"Erro ao verificar privilégios de admin: {e}")
            return False
    
    @staticmethod
    def check_disk_space(minimum_gb: float = 1.0) -> Tuple[bool, float]:
        """Verifica espaço livre em disco."""
        try:
            total, used, free = shutil.disk_usage("C:\\")
            free_gb = free / (1024**3)
            return free_gb >= minimum_gb, free_gb
        except Exception as e:
            logger.error(f"Erro ao verificar espaço em disco: {e}")
            return False, 0.0
    
    @staticmethod
    def check_running_processes(process_names: List[str]) -> Dict[str, bool]:
        """Verifica se processos específicos estão rodando."""
        running = {}
        try:
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info['name'].lower()
                for target in process_names:
                    if target.lower() in proc_name:
                        running[target] = True
            
            # Preencher os não encontrados
            for name in process_names:
                if name not in running:
                    running[name] = False
                    
        except Exception as e:
            logger.error(f"Erro ao verificar processos: {e}")
            # Retornar False para todos se houver erro
            running = {name: False for name in process_names}
        
        return running
    
    @staticmethod
    def check_system_restore_enabled() -> bool:
        """Verifica se a Restauração do Sistema está habilitada."""
        try:
            # Verificar via PowerShell
            cmd = ['powershell', '-Command', 
                   'Get-ComputerRestorePoint | Select-Object -First 1']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0 and result.stdout.strip()
        except Exception as e:
            logger.warning(f"Não foi possível verificar restauração do sistema: {e}")
            return False
    
    @staticmethod
    def create_restore_point(description: str = "Nêutrons Optimizer") -> bool:
        """Cria um ponto de restauração do sistema."""
        try:
            cmd = ['powershell', '-Command', 
                   f'Checkpoint-Computer -Description "{description}" -RestorePointType MODIFY_SETTINGS']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"Ponto de restauração criado: {description}")
                return True
            else:
                logger.warning(f"Falha ao criar ponto de restauração: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Erro ao criar ponto de restauração: {e}")
            return False
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Coleta informações básicas do sistema."""
        info = {}
        try:
            # Informações de memória
            memory = psutil.virtual_memory()
            info['ram_total'] = f"{memory.total / (1024**3):.1f} GB"
            info['ram_available'] = f"{memory.available / (1024**3):.1f} GB"
            info['ram_percent'] = f"{memory.percent}%"
            
            # Informações de disco
            disk = psutil.disk_usage('C:')
            info['disk_total'] = f"{disk.total / (1024**3):.1f} GB"
            info['disk_free'] = f"{disk.free / (1024**3):.1f} GB"
            info['disk_percent'] = f"{(disk.used / disk.total) * 100:.1f}%"
            
            # CPU
            info['cpu_cores'] = str(psutil.cpu_count())
            info['cpu_freq'] = f"{psutil.cpu_freq().max:.0f} MHz" if psutil.cpu_freq() else "N/A"
            
        except Exception as e:
            logger.error(f"Erro ao coletar informações do sistema: {e}")
        
        return info
    
    @staticmethod
    def validate_optimization_requirements() -> Dict[str, bool]:
        """Valida requisitos para executar otimizações."""
        checks = {}
        
        # Verificar se é administrador
        checks['admin_rights'] = SystemChecks.check_admin_rights()
        
        # Verificar espaço em disco
        has_space, space_gb = SystemChecks.check_disk_space(1.0)
        checks['disk_space'] = has_space
        
        # Verificar se processos críticos não estão rodando
        critical_processes = ['chrome', 'firefox', 'edge', 'steam', 'discord']
        running_processes = SystemChecks.check_running_processes(critical_processes)
        checks['no_critical_processes'] = not any(running_processes.values())
        
        # Log dos resultados
        for check, passed in checks.items():
            status = "✓" if passed else "✗"
            logger.info(f"Verificação {check}: {status}")
        
        return checks