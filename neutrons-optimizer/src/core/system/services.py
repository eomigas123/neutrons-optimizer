"""
Gerenciamento seguro de serviços do Windows.
"""
import subprocess
import time
from typing import Dict, List, Optional, Tuple
from enum import Enum
from ...utils.logging import logger


class ServiceState(Enum):
    """Estados possíveis de um serviço."""
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    UNKNOWN = "UNKNOWN"


class ServiceManager:
    """Gerenciador seguro para serviços do Windows."""
    
    @staticmethod
    def get_service_status(service_name: str) -> ServiceState:
        """Obtém o status atual de um serviço."""
        try:
            cmd = ["sc", "query", service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.upper()
                if "RUNNING" in output:
                    return ServiceState.RUNNING
                elif "STOPPED" in output:
                    return ServiceState.STOPPED
                elif "PAUSED" in output:
                    return ServiceState.PAUSED
            
            return ServiceState.UNKNOWN
            
        except Exception as e:
            logger.error(f"Erro ao obter status do serviço {service_name}: {e}")
            return ServiceState.UNKNOWN
    
    @staticmethod
    def start_service(service_name: str, timeout: int = 30) -> bool:
        """Inicia um serviço."""
        try:
            # Verificar se já está rodando
            if ServiceManager.get_service_status(service_name) == ServiceState.RUNNING:
                logger.info(f"Serviço {service_name} já está rodando")
                return True
            
            # Iniciar serviço
            cmd = ["net", "start", service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                logger.info(f"Serviço {service_name} iniciado com sucesso")
                return True
            else:
                logger.error(f"Falha ao iniciar serviço {service_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ao iniciar serviço {service_name}")
            return False
        except Exception as e:
            logger.error(f"Erro ao iniciar serviço {service_name}: {e}")
            return False
    
    @staticmethod
    def stop_service(service_name: str, timeout: int = 30) -> bool:
        """Para um serviço."""
        try:
            # Verificar se já está parado
            if ServiceManager.get_service_status(service_name) == ServiceState.STOPPED:
                logger.info(f"Serviço {service_name} já está parado")
                return True
            
            # Parar serviço
            cmd = ["net", "stop", service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                logger.info(f"Serviço {service_name} parado com sucesso")
                return True
            else:
                logger.error(f"Falha ao parar serviço {service_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ao parar serviço {service_name}")
            return False
        except Exception as e:
            logger.error(f"Erro ao parar serviço {service_name}: {e}")
            return False
    
    @staticmethod
    def restart_service(service_name: str, timeout: int = 60) -> bool:
        """Reinicia um serviço."""
        try:
            # Parar o serviço
            if not ServiceManager.stop_service(service_name, timeout // 2):
                return False
            
            # Aguardar um pouco
            time.sleep(2)
            
            # Iniciar o serviço
            return ServiceManager.start_service(service_name, timeout // 2)
            
        except Exception as e:
            logger.error(f"Erro ao reiniciar serviço {service_name}: {e}")
            return False
    
    @staticmethod
    def get_service_info(service_name: str) -> Dict[str, str]:
        """Obtém informações detalhadas de um serviço."""
        info = {}
        try:
            cmd = ["sc", "qc", service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Extrair informações básicas
                for line in output.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key.strip()] = value.strip()
                
                # Obter status atual
                status = ServiceManager.get_service_status(service_name)
                info['STATUS'] = status.value
                
        except Exception as e:
            logger.error(f"Erro ao obter informações do serviço {service_name}: {e}")
        
        return info
    
    @staticmethod
    def list_services() -> List[Dict[str, str]]:
        """Lista todos os serviços instalados."""
        services = []
        try:
            cmd = ["sc", "query", "type=", "service", "state=", "all"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                current_service = {}
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    if line.startswith('SERVICE_NAME:'):
                        if current_service:
                            services.append(current_service)
                        current_service = {'name': line.split(':', 1)[1].strip()}
                    elif line.startswith('DISPLAY_NAME:'):
                        current_service['display_name'] = line.split(':', 1)[1].strip()
                    elif line.startswith('STATE'):
                        state_part = line.split()
                        if len(state_part) >= 4:
                            current_service['state'] = state_part[3]
                
                # Adicionar o último serviço
                if current_service:
                    services.append(current_service)
                    
        except Exception as e:
            logger.error(f"Erro ao listar serviços: {e}")
        
        return services


class ServiceOperation:
    """Context manager para operações seguras com serviços."""
    
    def __init__(self, service_name: str, operation: str):
        self.service_name = service_name
        self.operation = operation
        self.original_state = None
    
    def __enter__(self):
        # Salvar estado original
        self.original_state = ServiceManager.get_service_status(self.service_name)
        logger.info(f"Estado original do serviço {self.service_name}: {self.original_state.value}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Erro na operação {self.operation} do serviço {self.service_name}: {exc_val}")
            # Tentar restaurar estado original se houve erro
            if self.original_state == ServiceState.RUNNING:
                logger.info(f"Tentando restaurar serviço {self.service_name} para estado RUNNING")
                ServiceManager.start_service(self.service_name)
            elif self.original_state == ServiceState.STOPPED:
                logger.info(f"Tentando restaurar serviço {self.service_name} para estado STOPPED")
                ServiceManager.stop_service(self.service_name)
        return False


# Serviços comuns que podem ser manipulados com segurança
SAFE_SERVICES = {
    'wuauserv': 'Windows Update',
    'bits': 'Background Intelligent Transfer Service',
    'spooler': 'Print Spooler',
    'themes': 'Themes',
    'SysMain': 'Superfetch/Prefetch',
    'WSearch': 'Windows Search'
}