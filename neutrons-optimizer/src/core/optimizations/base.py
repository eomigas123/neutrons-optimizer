"""
Classe base para otimizações do sistema.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
from ...utils.logging import logger
from ..safety.backup import backup_manager
from ..safety.restore import restore_manager


class OptimizationStatus(Enum):
    """Status de uma otimização."""
    NOT_APPLIED = "not_applied"
    APPLIED = "applied"
    SIMULATED = "simulated"
    ERROR = "error"
    PARTIAL = "partial"


class OptimizationResult:
    """Resultado de uma operação de otimização."""
    
    def __init__(self, success: bool, message: str, details: Dict[str, Any] = None):
        self.success = success
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp
        }


class BaseOptimization(ABC):
    """Classe base para todas as otimizações."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.backup_id = None
        self.status = OptimizationStatus.NOT_APPLIED
        self.last_result = None
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Nome para exibição na interface."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição da otimização."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Categoria da otimização."""
        pass
    
    @property
    @abstractmethod
    def impact_level(self) -> str:
        """Nível de impacto: low, medium, high."""
        pass
    
    @property
    @abstractmethod
    def estimated_time(self) -> int:
        """Tempo estimado em segundos."""
        pass
    
    @property
    @abstractmethod
    def requires_admin(self) -> bool:
        """Se requer privilégios de administrador."""
        pass
    
    @property
    @abstractmethod
    def requires_reboot(self) -> bool:
        """Se requer reinicialização após aplicar."""
        pass
    
    @abstractmethod
    def check_compatibility(self) -> bool:
        """Verifica se a otimização é compatível com o sistema atual."""
        pass
    
    @abstractmethod
    def simulate(self) -> OptimizationResult:
        """Simula a aplicação da otimização sem fazer alterações."""
        pass
    
    @abstractmethod
    def apply(self) -> OptimizationResult:
        """Aplica a otimização."""
        pass
    
    @abstractmethod
    def revert(self) -> OptimizationResult:
        """Reverte a otimização."""
        pass
    
    def get_status(self) -> OptimizationStatus:
        """Retorna o status atual da otimização."""
        return self.status
    
    def is_applied(self) -> bool:
        """Verifica se a otimização está aplicada."""
        return self.status == OptimizationStatus.APPLIED
    
    def can_revert(self) -> bool:
        """Verifica se a otimização pode ser revertida."""
        return self.backup_id is not None and self.is_applied()
    
    def create_backup(self) -> bool:
        """Cria backup antes de aplicar a otimização."""
        try:
            self.backup_id = backup_manager.create_operation_backup(self.name)
            logger.info(f"Backup criado para {self.display_name}: {self.backup_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar backup para {self.display_name}: {e}")
            return False
    
    def _validate_environment(self) -> bool:
        """Valida o ambiente antes de executar a otimização."""
        if not self.check_compatibility():
            return False
        
        if self.requires_admin:
            from ..system.uac import UACElevation
            if not UACElevation.is_admin():
                logger.error(f"Privilégios de administrador necessários para {self.display_name}")
                return False
        
        return True
    
    def _safe_apply(self) -> OptimizationResult:
        """Aplica a otimização com tratamento de erro e backup."""
        try:
            # Validar ambiente
            if not self._validate_environment():
                return OptimizationResult(False, "Ambiente não compatível ou privilégios insuficientes")
            
            # Criar backup
            if not self.create_backup():
                return OptimizationResult(False, "Falha ao criar backup")
            
            # Aplicar otimização
            logger.info(f"Aplicando otimização: {self.display_name}")
            result = self.apply()
            
            if result.success:
                self.status = OptimizationStatus.APPLIED
                logger.info(f"Otimização aplicada com sucesso: {self.display_name}")
            else:
                self.status = OptimizationStatus.ERROR
                logger.error(f"Falha na otimização: {self.display_name} - {result.message}")
            
            self.last_result = result
            return result
            
        except Exception as e:
            error_msg = f"Erro inesperado na otimização {self.display_name}: {e}"
            logger.error(error_msg)
            self.status = OptimizationStatus.ERROR
            result = OptimizationResult(False, error_msg)
            self.last_result = result
            return result
    
    def _safe_revert(self) -> OptimizationResult:
        """Reverte a otimização com tratamento de erro."""
        try:
            if not self.can_revert():
                return OptimizationResult(False, "Otimização não pode ser revertida")
            
            logger.info(f"Revertendo otimização: {self.display_name}")
            result = self.revert()
            
            if result.success:
                self.status = OptimizationStatus.NOT_APPLIED
                logger.info(f"Otimização revertida com sucesso: {self.display_name}")
            else:
                self.status = OptimizationStatus.ERROR
                logger.error(f"Falha ao reverter otimização: {self.display_name} - {result.message}")
            
            self.last_result = result
            return result
            
        except Exception as e:
            error_msg = f"Erro inesperado ao reverter {self.display_name}: {e}"
            logger.error(error_msg)
            self.status = OptimizationStatus.ERROR
            result = OptimizationResult(False, error_msg)
            self.last_result = result
            return result
    
    def _safe_simulate(self) -> OptimizationResult:
        """Simula a otimização com tratamento de erro."""
        try:
            if not self._validate_environment():
                return OptimizationResult(False, "Ambiente não compatível ou privilégios insuficientes")
            
            logger.info(f"Simulando otimização: {self.display_name}")
            result = self.simulate()
            
            if result.success:
                self.status = OptimizationStatus.SIMULATED
                logger.info(f"Simulação concluída: {self.display_name}")
            else:
                logger.warning(f"Simulação indicou problemas: {self.display_name} - {result.message}")
            
            self.last_result = result
            return result
            
        except Exception as e:
            error_msg = f"Erro na simulação de {self.display_name}: {e}"
            logger.error(error_msg)
            result = OptimizationResult(False, error_msg)
            self.last_result = result
            return result
    
    def get_info(self) -> Dict[str, Any]:
        """Retorna informações completas da otimização."""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'category': self.category,
            'impact_level': self.impact_level,
            'estimated_time': self.estimated_time,
            'requires_admin': self.requires_admin,
            'requires_reboot': self.requires_reboot,
            'status': self.status.value,
            'is_applied': self.is_applied(),
            'can_revert': self.can_revert(),
            'compatible': self.check_compatibility(),
            'backup_id': self.backup_id,
            'last_result': self.last_result.to_dict() if self.last_result else None
        }