"""
Otimização de limpeza do cache do Windows Update.
"""
from pathlib import Path
from .base import BaseOptimization, OptimizationResult
from ..system.services import ServiceManager
from ...utils.logging import logger


class WindowsUpdateCacheOptimization(BaseOptimization):
    """Limpeza do cache do Windows Update."""
    
    @property
    def display_name(self) -> str:
        return "Limpeza do Cache Windows Update"
    
    @property
    def description(self) -> str:
        return "Remove downloads antigos do Windows Update"
    
    @property
    def category(self) -> str:
        return "Armazenamento"
    
    @property
    def impact_level(self) -> str:
        return "medium"
    
    @property
    def estimated_time(self) -> int:
        return 60
    
    @property
    def requires_admin(self) -> bool:
        return True
    
    @property
    def requires_reboot(self) -> bool:
        return False
    
    def check_compatibility(self) -> bool:
        return True
    
    def simulate(self) -> OptimizationResult:
        try:
            download_dir = Path("C:") / "Windows" / "SoftwareDistribution" / "Download"
            if download_dir.exists():
                size = sum(f.stat().st_size for f in download_dir.rglob('*') if f.is_file())
                return OptimizationResult(
                    success=True,
                    message=f"Cache WU: {size / (1024*1024):.1f} MB",
                    details={'size_mb': size / (1024*1024)}
                )
            return OptimizationResult(True, "Nenhum cache encontrado")
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def apply(self) -> OptimizationResult:
        try:
            # Parar serviços
            ServiceManager.stop_service("wuauserv")
            ServiceManager.stop_service("bits")
            
            # Limpar downloads
            download_dir = Path("C:") / "Windows" / "SoftwareDistribution" / "Download"
            files_removed = 0
            size_freed = 0
            
            if download_dir.exists():
                for item in download_dir.rglob('*'):
                    if item.is_file():
                        try:
                            size_freed += item.stat().st_size
                            item.unlink()
                            files_removed += 1
                        except:
                            pass
            
            # Reiniciar serviços
            ServiceManager.start_service("bits")
            ServiceManager.start_service("wuauserv")
            
            return OptimizationResult(
                success=True,
                message=f"Cache limpo: {size_freed / (1024*1024):.1f} MB liberados",
                details={'files_removed': files_removed, 'size_freed_mb': size_freed / (1024*1024)}
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def revert(self) -> OptimizationResult:
        return OptimizationResult(False, "Cache do Windows Update não pode ser revertido")