"""
Otimização do plano de energia.
"""
from .base import BaseOptimization, OptimizationResult
from ..system.shell import shell
from ...utils.logging import logger
from ...utils.os_detect import windows_info


class PowerPlanOptimization(BaseOptimization):
    """Otimização do plano de energia para máximo desempenho."""
    
    @property
    def display_name(self) -> str:
        return "Plano de Energia High Performance"
    
    @property
    def description(self) -> str:
        return "Ativa o plano de energia de alto desempenho"
    
    @property
    def category(self) -> str:
        return "Energia"
    
    @property
    def impact_level(self) -> str:
        return "medium"
    
    @property
    def estimated_time(self) -> int:
        return 10
    
    @property
    def requires_admin(self) -> bool:
        return True
    
    @property
    def requires_reboot(self) -> bool:
        return False
    
    def check_compatibility(self) -> bool:
        return True
    
    def simulate(self) -> OptimizationResult:
        """Simula a aplicação do plano de energia."""
        try:
            # Verificar plano atual
            result = shell.run_powershell("powercfg /getactivescheme")
            current_plan = result.stdout if result.success else "Desconhecido"
            
            # Verificar se Ultimate Performance está disponível
            ultimate_available = windows_info.supports_ultimate_performance
            
            details = {
                'current_plan': current_plan,
                'ultimate_available': ultimate_available,
                'target_plan': 'Ultimate Performance' if ultimate_available else 'High Performance'
            }
            
            return OptimizationResult(
                success=True,
                message=f"Será aplicado plano: {details['target_plan']}",
                details=details
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro na simulação: {e}")
    
    def apply(self) -> OptimizationResult:
        """Aplica o plano de energia otimizado."""
        try:
            # Fazer backup do plano atual
            if self.backup_id:
                from ..safety.backup import backup_manager
                backup_manager.backup_power_plan(self.backup_id)
            
            # Tentar Ultimate Performance primeiro
            if windows_info.supports_ultimate_performance:
                result = shell.run_powershell("powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61")
                if result.success:
                    return OptimizationResult(True, "Plano Ultimate Performance ativado")
            
            # Fallback para High Performance
            result = shell.run_powershell("powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")
            if result.success:
                return OptimizationResult(True, "Plano High Performance ativado")
            
            return OptimizationResult(False, "Falha ao ativar plano de energia")
            
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def revert(self) -> OptimizationResult:
        """Reverte para o plano anterior."""
        try:
            if not self.backup_id:
                # Voltar para Balanced como padrão
                result = shell.run_powershell("powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e")
                return OptimizationResult(result.success, "Plano Balanced restaurado")
            
            from ..safety.restore import restore_manager
            success = restore_manager.restore_operation(self.backup_id)
            return OptimizationResult(success, "Plano anterior restaurado" if success else "Falha na restauração")
            
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")