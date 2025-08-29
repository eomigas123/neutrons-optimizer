"""
Otimização de armazenamento (TRIM/Defrag).
"""
from .base import BaseOptimization, OptimizationResult
from ..system.shell import shell
from ...utils.logging import logger


class StorageTrimOptimization(BaseOptimization):
    """Otimização de armazenamento."""
    
    @property
    def display_name(self) -> str:
        return "Otimização de Armazenamento"
    
    @property
    def description(self) -> str:
        return "Executa TRIM em SSDs ou desfragmentação em HDDs"
    
    @property
    def category(self) -> str:
        return "Armazenamento"
    
    @property
    def impact_level(self) -> str:
        return "medium"
    
    @property
    def estimated_time(self) -> int:
        return 300
    
    @property
    def requires_admin(self) -> bool:
        return True
    
    @property
    def requires_reboot(self) -> bool:
        return False
    
    def check_compatibility(self) -> bool:
        return True
    
    def _detect_drive_type(self) -> str:
        """Detecta se o drive C: é SSD ou HDD."""
        try:
            result = shell.run_powershell(
                "Get-PhysicalDisk | Where-Object {$_.DeviceID -eq 0} | Select-Object MediaType"
            )
            if "SSD" in result.stdout:
                return "SSD"
            return "HDD"
        except:
            return "Unknown"
    
    def simulate(self) -> OptimizationResult:
        try:
            drive_type = self._detect_drive_type()
            operation = "TRIM" if drive_type == "SSD" else "Desfragmentação"
            
            return OptimizationResult(
                success=True,
                message=f"Será executado: {operation} no drive C: ({drive_type})",
                details={'drive_type': drive_type, 'operation': operation}
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def apply(self) -> OptimizationResult:
        try:
            drive_type = self._detect_drive_type()
            
            if drive_type == "SSD":
                # TRIM para SSD
                result = shell.run_command("defrag C: /L", timeout=300)
                operation = "TRIM"
            else:
                # Análise/otimização para HDD
                result = shell.run_command("defrag C: /A", timeout=300)
                operation = "Análise"
            
            return OptimizationResult(
                success=result.success,
                message=f"{operation} {'concluído' if result.success else 'falhou'}",
                details={'operation': operation, 'output': result.stdout}
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def revert(self) -> OptimizationResult:
        return OptimizationResult(False, "Otimização de armazenamento não pode ser revertida")