"""
Otimização de limpeza do cache de miniaturas.
"""
from pathlib import Path
from .base import BaseOptimization, OptimizationResult
from ..system.shell import shell
from ...utils.logging import logger


class ThumbnailsCacheOptimization(BaseOptimization):
    """Limpeza do cache de miniaturas do Windows."""
    
    @property
    def display_name(self) -> str:
        return "Limpeza do Cache de Miniaturas"
    
    @property
    def description(self) -> str:
        return "Remove cache de miniaturas para liberar espaço"
    
    @property
    def category(self) -> str:
        return "Armazenamento"
    
    @property
    def impact_level(self) -> str:
        return "low"
    
    @property
    def estimated_time(self) -> int:
        return 20
    
    @property
    def requires_admin(self) -> bool:
        return False
    
    @property
    def requires_reboot(self) -> bool:
        return False
    
    def check_compatibility(self) -> bool:
        return True
    
    def simulate(self) -> OptimizationResult:
        try:
            cache_dir = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer"
            size = sum(f.stat().st_size for f in cache_dir.glob("thumbcache*") if f.is_file())
            
            return OptimizationResult(
                success=True,
                message=f"Cache de miniaturas: {size / (1024*1024):.1f} MB",
                details={'size_mb': size / (1024*1024)}
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def apply(self) -> OptimizationResult:
        try:
            # Parar Explorer
            shell.kill_process_by_name("explorer.exe")
            
            # Limpar cache
            cache_dir = Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer"
            files_removed = 0
            for cache_file in cache_dir.glob("thumbcache*"):
                try:
                    cache_file.unlink()
                    files_removed += 1
                except:
                    pass
            
            # Reiniciar Explorer
            shell.restart_explorer()
            
            return OptimizationResult(
                success=True,
                message=f"Cache limpo: {files_removed} arquivos removidos"
            )
        except Exception as e:
            return OptimizationResult(False, f"Erro: {e}")
    
    def revert(self) -> OptimizationResult:
        return OptimizationResult(False, "Cache de miniaturas não pode ser revertido")