"""
Otimização de reset de rede.
"""
from .base import BaseOptimization, OptimizationResult
from ..system.shell import shell
from ...utils.logging import logger


class NetworkResetOptimization(BaseOptimization):
    """Reset seguro de configurações de rede."""
    
    @property
    def display_name(self) -> str:
        return "Reset de Rede"
    
    @property
    def description(self) -> str:
        return "Limpa cache DNS e reseta Winsock"
    
    @property
    def category(self) -> str:
        return "Rede"
    
    @property
    def impact_level(self) -> str:
        return "medium"
    
    @property
    def estimated_time(self) -> int:
        return 30
    
    @property
    def requires_admin(self) -> bool:
        return True
    
    @property
    def requires_reboot(self) -> bool:
        return True
    
    def check_compatibility(self) -> bool:
        return True
    
    def simulate(self) -> OptimizationResult:
        return OptimizationResult(
            success=True,
            message="Será executado: flush DNS e reset Winsock (requer reinicialização)",
            details={'operations': ['ipconfig /flushdns', 'netsh winsock reset']}
        )
    
    def apply(self) -> OptimizationResult:
        try:
            results = []
            
            # Flush DNS
            result = shell.run_command("ipconfig /flushdns", timeout=30)
            results.append(f"DNS flush: {'✓' if result.success else '✗'}")
            
            # Reset Winsock
            result = shell.run_command("netsh winsock reset", timeout=30)
            results.append(f"Winsock reset: {'✓' if result.success else '✗'}")
            
            return OptimizationResult(
                success=True,
                message=f"Reset de rede concluído: {', '.join(results)}. Reinicialização necessária.",
                details={'results': results}
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def revert(self) -> OptimizationResult:
        return OptimizationResult(False, "Reset de rede não pode ser revertido")