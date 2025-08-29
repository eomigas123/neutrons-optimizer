"""
Otimização do Xbox Game Bar.
"""
import winreg
from .base import BaseOptimization, OptimizationResult
from ..system.registry import registry
from ...utils.logging import logger


class XboxGameBarOptimization(BaseOptimization):
    """Desabilitação do Xbox Game Bar e DVR."""
    
    @property
    def display_name(self) -> str:
        return "Desabilitar Xbox Game Bar"
    
    @property
    def description(self) -> str:
        return "Desabilita Xbox Game Bar e recursos de gravação"
    
    @property
    def category(self) -> str:
        return "Jogos"
    
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
    
    def _get_current_status(self) -> dict:
        """Verifica status atual do Game Bar."""
        status = {}
        try:
            # Game Bar habilitado
            value = registry.read_value(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\GameBar",
                "UseNexusForGameBarEnabled"
            )
            status['gamebar_enabled'] = value != 0 if value is not None else True
            
            # Game DVR habilitado
            value = registry.read_value(
                winreg.HKEY_CURRENT_USER,
                r"System\GameConfigStore",
                "GameDVR_Enabled"
            )
            status['gamedvr_enabled'] = value != 0 if value is not None else True
            
        except:
            status = {'gamebar_enabled': True, 'gamedvr_enabled': True}
        
        return status
    
    def simulate(self) -> OptimizationResult:
        try:
            status = self._get_current_status()
            changes = []
            
            if status['gamebar_enabled']:
                changes.append("Desabilitar Game Bar")
            if status['gamedvr_enabled']:
                changes.append("Desabilitar Game DVR")
            
            return OptimizationResult(
                success=True,
                message=f"Mudanças: {', '.join(changes) if changes else 'Nenhuma'}",
                details={'current_status': status, 'planned_changes': changes}
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def apply(self) -> OptimizationResult:
        try:
            # Backup
            if self.backup_id:
                from ..safety.backup import backup_manager
                backup_manager.backup_registry_key(
                    self.backup_id,
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\GameBar",
                    "Game Bar settings"
                )
                backup_manager.backup_registry_key(
                    self.backup_id,
                    winreg.HKEY_CURRENT_USER,
                    r"System\GameConfigStore",
                    "Game DVR settings"
                )
            
            results = []
            
            # Desabilitar Game Bar
            success = registry.write_value(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\GameBar",
                "UseNexusForGameBarEnabled",
                0,
                winreg.REG_DWORD
            )
            results.append(f"Game Bar: {'✓' if success else '✗'}")
            
            # Desabilitar Game DVR
            success = registry.write_value(
                winreg.HKEY_CURRENT_USER,
                r"System\GameConfigStore",
                "GameDVR_Enabled",
                0,
                winreg.REG_DWORD
            )
            results.append(f"Game DVR: {'✓' if success else '✗'}")
            
            return OptimizationResult(
                success=True,
                message=f"Xbox Game Bar desabilitado: {', '.join(results)}",
                details={'results': results}
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def revert(self) -> OptimizationResult:
        try:
            if not self.backup_id:
                return OptimizationResult(False, "Backup não disponível")
            
            from ..safety.restore import restore_manager
            success = restore_manager.restore_operation(self.backup_id)
            return OptimizationResult(success, "Xbox Game Bar restaurado" if success else "Falha na restauração")
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")