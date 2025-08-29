"""
Otimização de limpeza do cache de shaders DirectX.
"""
import os
from pathlib import Path
from typing import Dict, Any

from .base import BaseOptimization, OptimizationResult
from ...utils.logging import logger


class DirectXShaderCacheOptimization(BaseOptimization):
    """Limpeza do cache de shaders DirectX."""
    
    @property
    def display_name(self) -> str:
        return "Limpeza do Cache DirectX"
    
    @property
    def description(self) -> str:
        return "Remove cache de shaders DirectX para resolver problemas gráficos"
    
    @property
    def category(self) -> str:
        return "Gráficos"
    
    @property
    def impact_level(self) -> str:
        return "medium"
    
    @property
    def estimated_time(self) -> int:
        return 15
    
    @property
    def requires_admin(self) -> bool:
        return False
    
    @property
    def requires_reboot(self) -> bool:
        return False
    
    def check_compatibility(self) -> bool:
        """Compatível com Windows que tem DirectX."""
        return True
    
    def _get_dx_cache_directories(self) -> Dict[str, Path]:
        """Retorna diretórios de cache DirectX."""
        cache_dirs = {}
        
        # Cache principal do DirectX
        dx_cache = Path.home() / "AppData" / "Local" / "D3DSCache"
        if dx_cache.exists():
            cache_dirs['D3DSCache'] = dx_cache
        
        # Cache de drivers NVIDIA
        nvidia_cache = Path.home() / "AppData" / "Local" / "NVIDIA Corporation" / "NvCache"
        if nvidia_cache.exists():
            cache_dirs['NVIDIA_Cache'] = nvidia_cache
        
        # Cache de drivers AMD
        amd_cache = Path.home() / "AppData" / "Local" / "AMD" / "DxCache"
        if amd_cache.exists():
            cache_dirs['AMD_DxCache'] = amd_cache
        
        # Cache de drivers Intel
        intel_cache = Path.home() / "AppData" / "Local" / "Intel" / "ShaderCache"
        if intel_cache.exists():
            cache_dirs['Intel_ShaderCache'] = intel_cache
        
        return cache_dirs
    
    def _calculate_cache_size(self, cache_dir: Path) -> int:
        """Calcula tamanho do cache em bytes."""
        total_size = 0
        try:
            for item in cache_dir.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, PermissionError):
            pass
        return total_size
    
    def _clean_cache_directory(self, cache_dir: Path) -> Dict[str, Any]:
        """Limpa um diretório de cache."""
        result = {
            'files_removed': 0,
            'folders_removed': 0,
            'size_freed': 0,
            'errors': []
        }
        
        try:
            # Remover arquivos
            for item in cache_dir.rglob('*'):
                try:
                    if item.is_file():
                        file_size = item.stat().st_size
                        item.unlink()
                        result['files_removed'] += 1
                        result['size_freed'] += file_size
                except (OSError, FileNotFoundError, PermissionError) as e:
                    result['errors'].append(f"{item.name}: {str(e)}")
            
            # Remover diretórios vazios
            for item in sorted(cache_dir.rglob('*'), key=lambda p: len(p.parts), reverse=True):
                try:
                    if item.is_dir() and not any(item.iterdir()):
                        item.rmdir()
                        result['folders_removed'] += 1
                except (OSError, PermissionError):
                    pass
                    
        except Exception as e:
            result['errors'].append(f"Erro geral: {str(e)}")
        
        return result
    
    def simulate(self) -> OptimizationResult:
        """Simula a limpeza do cache DirectX."""
        try:
            cache_dirs = self._get_dx_cache_directories()
            
            if not cache_dirs:
                return OptimizationResult(
                    success=True,
                    message="Nenhum cache DirectX encontrado",
                    details={'cache_directories': {}}
                )
            
            total_size = 0
            details = {
                'cache_directories': {},
                'total_size_bytes': 0,
                'total_size_mb': 0
            }
            
            for cache_name, cache_dir in cache_dirs.items():
                size = self._calculate_cache_size(cache_dir)
                total_size += size
                
                # Contar arquivos e pastas
                file_count = 0
                folder_count = 0
                for item in cache_dir.rglob('*'):
                    if item.is_file():
                        file_count += 1
                    elif item.is_dir():
                        folder_count += 1
                
                details['cache_directories'][cache_name] = {
                    'path': str(cache_dir),
                    'size_bytes': size,
                    'size_mb': round(size / (1024 * 1024), 2),
                    'file_count': file_count,
                    'folder_count': folder_count
                }
            
            details['total_size_bytes'] = total_size
            details['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return OptimizationResult(
                success=True,
                message=f"Simulação concluída: {details['total_size_mb']} MB de cache DirectX podem ser liberados",
                details=details
            )
            
        except Exception as e:
            return OptimizationResult(False, f"Erro na simulação: {e}")
    
    def apply(self) -> OptimizationResult:
        """Aplica a limpeza do cache DirectX."""
        try:
            cache_dirs = self._get_dx_cache_directories()
            
            if not cache_dirs:
                return OptimizationResult(
                    success=True,
                    message="Nenhum cache DirectX encontrado para limpar",
                    details={'cache_directories': {}}
                )
            
            total_freed = 0
            total_files = 0
            total_folders = 0
            details = {
                'cache_directories': {},
                'total_files_removed': 0,
                'total_folders_removed': 0,
                'total_size_freed_bytes': 0,
                'total_size_freed_mb': 0,
                'errors': []
            }
            
            for cache_name, cache_dir in cache_dirs.items():
                logger.info(f"Limpando cache DirectX: {cache_name}")
                
                # Fazer backup da estrutura do diretório se necessário
                from ..safety.backup import backup_manager
                if self.backup_id:
                    backup_manager.backup_directory(self.backup_id, str(cache_dir), f"Cache DirectX: {cache_name}")
                
                result = self._clean_cache_directory(cache_dir)
                
                total_freed += result['size_freed']
                total_files += result['files_removed']
                total_folders += result['folders_removed']
                
                details['cache_directories'][cache_name] = {
                    'path': str(cache_dir),
                    'files_removed': result['files_removed'],
                    'folders_removed': result['folders_removed'],
                    'size_freed_bytes': result['size_freed'],
                    'size_freed_mb': round(result['size_freed'] / (1024 * 1024), 2),
                    'errors': result['errors']
                }
                
                details['errors'].extend(result['errors'])
            
            details['total_files_removed'] = total_files
            details['total_folders_removed'] = total_folders
            details['total_size_freed_bytes'] = total_freed
            details['total_size_freed_mb'] = round(total_freed / (1024 * 1024), 2)
            
            return OptimizationResult(
                success=True,
                message=f"Cache DirectX limpo: {details['total_size_freed_mb']} MB liberados",
                details=details
            )
            
        except Exception as e:
            return OptimizationResult(False, f"Erro na limpeza: {e}")
    
    def revert(self) -> OptimizationResult:
        """Reverte a limpeza do cache DirectX."""
        try:
            if not self.backup_id:
                return OptimizationResult(
                    success=False,
                    message="Nenhum backup disponível para restauração"
                )
            
            from ..safety.restore import restore_manager
            
            success = restore_manager.restore_operation(self.backup_id)
            
            if success:
                return OptimizationResult(
                    success=True,
                    message="Cache DirectX restaurado do backup"
                )
            else:
                return OptimizationResult(
                    success=False,
                    message="Falha ao restaurar cache DirectX do backup"
                )
                
        except Exception as e:
            return OptimizationResult(False, f"Erro na restauração: {e}")