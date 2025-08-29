"""
Otimização de limpeza de arquivos temporários.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import psutil

from .base import BaseOptimization, OptimizationResult
from ..system.shell import shell
from ...utils.logging import logger


class TempCleanupOptimization(BaseOptimization):
    """Limpeza segura de arquivos temporários."""
    
    @property
    def display_name(self) -> str:
        return "Limpeza de Arquivos Temporários"
    
    @property
    def description(self) -> str:
        return "Remove arquivos temporários seguros para liberar espaço em disco"
    
    @property
    def category(self) -> str:
        return "Armazenamento"
    
    @property
    def impact_level(self) -> str:
        return "low"
    
    @property
    def estimated_time(self) -> int:
        return 30
    
    @property
    def requires_admin(self) -> bool:
        return False
    
    @property
    def requires_reboot(self) -> bool:
        return False
    
    def check_compatibility(self) -> bool:
        """Sempre compatível."""
        return True
    
    def _get_temp_directories(self) -> List[Path]:
        """Retorna lista de diretórios temporários seguros."""
        temp_dirs = []
        
        # Diretório TEMP do usuário
        user_temp = Path(os.environ.get('TEMP', tempfile.gettempdir()))
        if user_temp.exists():
            temp_dirs.append(user_temp)
        
        # Diretório TEMP do Windows (somente se admin)
        windows_temp = Path(os.environ.get('WINDIR', 'C:\\Windows')) / 'Temp'
        if windows_temp.exists():
            temp_dirs.append(windows_temp)
        
        # Diretórios de cache seguros
        safe_cache_dirs = [
            Path.home() / "AppData" / "Local" / "Temp",
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache",
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Temporary Internet Files"
        ]
        
        for cache_dir in safe_cache_dirs:
            if cache_dir.exists():
                temp_dirs.append(cache_dir)
        
        return temp_dirs
    
    def _get_browser_cache_dirs(self) -> Dict[str, Path]:
        """Retorna diretórios de cache de navegadores."""
        caches = {}
        
        # Chrome
        chrome_cache = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cache"
        if chrome_cache.exists():
            caches['Chrome'] = chrome_cache
        
        # Edge
        edge_cache = Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache"
        if edge_cache.exists():
            caches['Edge'] = edge_cache
        
        # Firefox
        firefox_profiles = Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
        if firefox_profiles.exists():
            for profile in firefox_profiles.iterdir():
                if profile.is_dir():
                    cache_dir = profile / "cache2"
                    if cache_dir.exists():
                        caches[f'Firefox-{profile.name}'] = cache_dir
                        break
        
        return caches
    
    def _calculate_directory_size(self, directory: Path) -> int:
        """Calcula o tamanho de um diretório em bytes."""
        total_size = 0
        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue
        except (OSError, PermissionError):
            pass
        return total_size
    
    def _is_browser_running(self, browser_name: str) -> bool:
        """Verifica se um navegador está rodando."""
        browser_processes = {
            'Chrome': ['chrome.exe', 'chrome'],
            'Edge': ['msedge.exe', 'msedge'],
            'Firefox': ['firefox.exe', 'firefox']
        }
        
        processes = browser_processes.get(browser_name, [])
        for proc in psutil.process_iter(['name']):
            try:
                if any(p.lower() in proc.info['name'].lower() for p in processes):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def _clean_directory_safe(self, directory: Path, max_age_hours: int = 24) -> Dict[str, Any]:
        """Limpa diretório de forma segura."""
        result = {
            'files_removed': 0,
            'size_freed': 0,
            'errors': []
        }
        
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for item in directory.rglob('*'):
                try:
                    if item.is_file():
                        # Verificar idade do arquivo
                        file_age = current_time - item.stat().st_mtime
                        if file_age > max_age_seconds:
                            file_size = item.stat().st_size
                            item.unlink()
                            result['files_removed'] += 1
                            result['size_freed'] += file_size
                    
                except (OSError, FileNotFoundError, PermissionError) as e:
                    result['errors'].append(f"{item}: {str(e)}")
                    continue
            
            # Remover diretórios vazios
            for item in directory.rglob('*'):
                try:
                    if item.is_dir() and not any(item.iterdir()):
                        item.rmdir()
                except (OSError, PermissionError):
                    pass
                    
        except Exception as e:
            result['errors'].append(f"Erro geral: {str(e)}")
        
        return result
    
    def simulate(self) -> OptimizationResult:
        """Simula a limpeza de temporários."""
        try:
            temp_dirs = self._get_temp_directories()
            browser_caches = self._get_browser_cache_dirs()
            
            total_size = 0
            details = {
                'temp_directories': {},
                'browser_caches': {},
                'total_size_bytes': 0,
                'total_size_mb': 0
            }
            
            # Calcular tamanho dos diretórios temporários
            for temp_dir in temp_dirs:
                size = self._calculate_directory_size(temp_dir)
                total_size += size
                details['temp_directories'][str(temp_dir)] = {
                    'size_bytes': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                }
            
            # Calcular tamanho dos caches de navegadores
            for browser, cache_dir in browser_caches.items():
                if not self._is_browser_running(browser.split('-')[0]):
                    size = self._calculate_directory_size(cache_dir)
                    total_size += size
                    details['browser_caches'][browser] = {
                        'size_bytes': size,
                        'size_mb': round(size / (1024 * 1024), 2),
                        'can_clean': True
                    }
                else:
                    details['browser_caches'][browser] = {
                        'size_bytes': 0,
                        'size_mb': 0,
                        'can_clean': False,
                        'reason': 'Navegador em execução'
                    }
            
            details['total_size_bytes'] = total_size
            details['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return OptimizationResult(
                success=True,
                message=f"Simulação concluída: {details['total_size_mb']} MB podem ser liberados",
                details=details
            )
            
        except Exception as e:
            return OptimizationResult(False, f"Erro na simulação: {e}")
    
    def apply(self) -> OptimizationResult:
        """Aplica a limpeza de temporários."""
        try:
            temp_dirs = self._get_temp_directories()
            browser_caches = self._get_browser_cache_dirs()
            
            total_freed = 0
            total_files = 0
            details = {
                'temp_directories': {},
                'browser_caches': {},
                'total_files_removed': 0,
                'total_size_freed_bytes': 0,
                'total_size_freed_mb': 0,
                'errors': []
            }
            
            # Limpar diretórios temporários
            for temp_dir in temp_dirs:
                logger.info(f"Limpando diretório temporário: {temp_dir}")
                result = self._clean_directory_safe(temp_dir)
                
                total_freed += result['size_freed']
                total_files += result['files_removed']
                
                details['temp_directories'][str(temp_dir)] = {
                    'files_removed': result['files_removed'],
                    'size_freed_bytes': result['size_freed'],
                    'size_freed_mb': round(result['size_freed'] / (1024 * 1024), 2),
                    'errors': result['errors']
                }
                
                details['errors'].extend(result['errors'])
            
            # Limpar caches de navegadores (se não estiverem rodando)
            for browser, cache_dir in browser_caches.items():
                browser_name = browser.split('-')[0]
                if not self._is_browser_running(browser_name):
                    logger.info(f"Limpando cache do {browser}")
                    result = self._clean_directory_safe(cache_dir, max_age_hours=1)
                    
                    total_freed += result['size_freed']
                    total_files += result['files_removed']
                    
                    details['browser_caches'][browser] = {
                        'files_removed': result['files_removed'],
                        'size_freed_bytes': result['size_freed'],
                        'size_freed_mb': round(result['size_freed'] / (1024 * 1024), 2),
                        'cleaned': True,
                        'errors': result['errors']
                    }
                    
                    details['errors'].extend(result['errors'])
                else:
                    details['browser_caches'][browser] = {
                        'cleaned': False,
                        'reason': f'{browser_name} está em execução'
                    }
            
            details['total_files_removed'] = total_files
            details['total_size_freed_bytes'] = total_freed
            details['total_size_freed_mb'] = round(total_freed / (1024 * 1024), 2)
            
            return OptimizationResult(
                success=True,
                message=f"Limpeza concluída: {details['total_size_freed_mb']} MB liberados, {total_files} arquivos removidos",
                details=details
            )
            
        except Exception as e:
            return OptimizationResult(False, f"Erro na limpeza: {e}")
    
    def revert(self) -> OptimizationResult:
        """A limpeza de temporários não pode ser revertida."""
        return OptimizationResult(
            success=False,
            message="A limpeza de arquivos temporários não pode ser revertida"
        )