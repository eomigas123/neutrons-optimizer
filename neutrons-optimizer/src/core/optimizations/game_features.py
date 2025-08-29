"""
Otimização de recursos para jogos (Game Mode e HAGS).
"""
import winreg
from .base import BaseOptimization, OptimizationResult
from ..system.registry import registry
from ...utils.logging import logger
from ...utils.os_detect import windows_info


class GameFeaturesOptimization(BaseOptimization):
    """Otimização de recursos para jogos."""
    
    @property
    def display_name(self) -> str:
        return "Otimizações para Jogos"
    
    @property
    def description(self) -> str:
        return "Ativa Game Mode e Hardware Accelerated GPU Scheduling"
    
    @property
    def category(self) -> str:
        return "Jogos"
    
    @property
    def impact_level(self) -> str:
        return "high"
    
    @property
    def estimated_time(self) -> int:
        return 15
    
    @property
    def requires_admin(self) -> bool:
        return True
    
    @property
    def requires_reboot(self) -> bool:
        return True
    
    def check_compatibility(self) -> bool:
        return windows_info.is_windows_10 or windows_info.is_windows_11
    
    def simulate(self) -> OptimizationResult:
        """Simula a aplicação das otimizações para jogos."""
        try:
            details = {
                'game_mode_available': True,
                'hags_available': windows_info.supports_hags,
                'current_game_mode': self._get_game_mode_status(),
                'current_hags': self._get_hags_status() if windows_info.supports_hags else False
            }
            
            changes = []
            if not details['current_game_mode']:
                changes.append("Ativar Game Mode")
            if windows_info.supports_hags and not details['current_hags']:
                changes.append("Ativar Hardware Accelerated GPU Scheduling")
            
            details['planned_changes'] = changes
            
            return OptimizationResult(
                success=True,
                message=f"Mudanças planejadas: {', '.join(changes) if changes else 'Nenhuma'}",
                details=details
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro na simulação: {e}")
    
    def _get_game_mode_status(self) -> bool:
        """Verifica se o Game Mode está ativo."""
        try:
            value = registry.read_value(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\GameBar",
                "AutoGameModeEnabled"
            )
            return value == 1 if value is not None else False
        except:
            return False
    
    def _get_hags_status(self) -> bool:
        """Verifica se HAGS está ativo."""
        try:
            value = registry.read_value(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                "HwSchMode"
            )
            return value == 2 if value is not None else False
        except:
            return False
    
    def apply(self) -> OptimizationResult:
        """Aplica as otimizações para jogos."""
        try:
            results = []
            
            # Backup das configurações
            if self.backup_id:
                from ..safety.backup import backup_manager
                backup_manager.backup_registry_key(
                    self.backup_id,
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\GameBar",
                    "Game Mode settings"
                )
                if windows_info.supports_hags:
                    backup_manager.backup_registry_key(
                        self.backup_id,
                        winreg.HKEY_LOCAL_MACHINE,
                        r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                        "HAGS settings"
                    )
            
            # Ativar Game Mode
            success = registry.write_value(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\GameBar",
                "AutoGameModeEnabled",
                1,
                winreg.REG_DWORD
            )
            results.append(f"Game Mode: {'✓' if success else '✗'}")
            
            # Ativar HAGS se suportado
            if windows_info.supports_hags:
                success = registry.write_value(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                    "HwSchMode",
                    2,
                    winreg.REG_DWORD
                )
                results.append(f"HAGS: {'✓' if success else '✗'}")
            
            return OptimizationResult(
                success=True,
                message=f"Configurações aplicadas: {', '.join(results)}",
                details={'results': results}
            )
            
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def revert(self) -> OptimizationResult:
        """Reverte as otimizações para jogos."""
        try:
            if not self.backup_id:
                return OptimizationResult(False, "Backup não disponível")
            
            from ..safety.restore import restore_manager
            success = restore_manager.restore_operation(self.backup_id)
            return OptimizationResult(success, "Configurações revertidas" if success else "Falha na reversão")
            
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")