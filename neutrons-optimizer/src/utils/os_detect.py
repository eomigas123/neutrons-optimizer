"""
Detecção de sistema operacional e versão do Windows.
"""
import platform
import subprocess
import winreg
from typing import Dict, Optional
from .logging import logger


class WindowsInfo:
    """Informações sobre o sistema Windows."""
    
    def __init__(self):
        self._info = self._gather_info()
    
    def _gather_info(self) -> Dict[str, str]:
        """Coleta informações do sistema."""
        info = {
            'version': platform.version(),
            'release': platform.release(),
            'architecture': platform.architecture()[0],
            'build': self._get_build_number(),
            'edition': self._get_edition(),
            'is_windows_10': False,
            'is_windows_11': False,
            'supports_hags': False,
            'supports_ultimate_performance': False
        }
        
        # Determinar versão do Windows
        build_num = int(info['build']) if info['build'].isdigit() else 0
        
        if build_num >= 22000:
            info['is_windows_11'] = True
            info['supports_hags'] = True
            info['supports_ultimate_performance'] = True
        elif build_num >= 10240:
            info['is_windows_10'] = True
            # HAGS disponível a partir do build 20H1 (19041)
            info['supports_hags'] = build_num >= 19041
            info['supports_ultimate_performance'] = True
        
        logger.info(f"Sistema detectado: Windows {info['release']} Build {info['build']}")
        return info
    
    def _get_build_number(self) -> str:
        """Obtém o número do build do Windows."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                build_number, _ = winreg.QueryValueEx(key, "CurrentBuildNumber")
                return str(build_number)
        except Exception as e:
            logger.warning(f"Não foi possível obter build number: {e}")
            return "0"
    
    def _get_edition(self) -> str:
        """Obtém a edição do Windows."""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                edition, _ = winreg.QueryValueEx(key, "ProductName")
                return str(edition)
        except Exception as e:
            logger.warning(f"Não foi possível obter edição do Windows: {e}")
            return "Windows"
    
    @property
    def version(self) -> str:
        """Versão do Windows."""
        return self._info['version']
    
    @property
    def release(self) -> str:
        """Release do Windows (10, 11, etc)."""
        return self._info['release']
    
    @property
    def build(self) -> str:
        """Build number do Windows."""
        return self._info['build']
    
    @property
    def edition(self) -> str:
        """Edição do Windows."""
        return self._info['edition']
    
    @property
    def architecture(self) -> str:
        """Arquitetura do sistema."""
        return self._info['architecture']
    
    @property
    def is_windows_10(self) -> bool:
        """Se é Windows 10."""
        return self._info['is_windows_10']
    
    @property
    def is_windows_11(self) -> bool:
        """Se é Windows 11."""
        return self._info['is_windows_11']
    
    @property
    def supports_hags(self) -> bool:
        """Se suporta Hardware Accelerated GPU Scheduling."""
        return self._info['supports_hags']
    
    @property
    def supports_ultimate_performance(self) -> bool:
        """Se suporta o plano Ultimate Performance."""
        return self._info['supports_ultimate_performance']
    
    def get_summary(self) -> str:
        """Retorna um resumo do sistema."""
        return f"{self.edition} (Build {self.build}) {self.architecture}"


# Instância global
windows_info = WindowsInfo()