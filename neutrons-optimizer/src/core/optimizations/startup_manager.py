"""
Otimização do gerenciador de inicialização.
"""
import winreg
from pathlib import Path
from typing import Dict, List, Any

from .base import BaseOptimization, OptimizationResult
from ..system.registry import registry
from ...utils.logging import logger


class StartupManagerOptimization(BaseOptimization):
    """Gerenciamento de itens de inicialização."""
    
    def __init__(self):
        super().__init__()
        self.disabled_items = []
    
    @property
    def display_name(self) -> str:
        return "Gerenciador de Inicialização"
    
    @property
    def description(self) -> str:
        return "Gerencia programas que iniciam com o Windows"
    
    @property
    def category(self) -> str:
        return "Inicialização"
    
    @property
    def impact_level(self) -> str:
        return "medium"
    
    @property
    def estimated_time(self) -> int:
        return 20
    
    @property
    def requires_admin(self) -> bool:
        return False
    
    @property
    def requires_reboot(self) -> bool:
        return True
    
    def check_compatibility(self) -> bool:
        """Sempre compatível."""
        return True
    
    def _get_startup_locations(self) -> List[tuple]:
        """Retorna locais de inicialização no registro."""
        return [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "HKCU RunOnce"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "HKLM RunOnce"),
        ]
    
    def _get_startup_folders(self) -> List[tuple]:
        """Retorna pastas de inicialização."""
        folders = []
        
        # Pasta de inicialização do usuário
        user_startup = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if user_startup.exists():
            folders.append((user_startup, "User Startup Folder"))
        
        # Pasta de inicialização do sistema
        system_startup = Path("C:") / "ProgramData" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if system_startup.exists():
            folders.append((system_startup, "System Startup Folder"))
        
        return folders
    
    def _get_all_startup_items(self) -> Dict[str, List[Dict[str, Any]]]:
        """Obtém todos os itens de inicialização."""
        startup_items = {
            'registry': [],
            'folders': []
        }
        
        # Itens do registro
        for hkey, subkey, location_name in self._get_startup_locations():
            try:
                values = registry.enumerate_values(hkey, subkey)
                for name, value in values.items():
                    startup_items['registry'].append({
                        'name': name,
                        'value': value,
                        'hkey': hkey,
                        'subkey': subkey,
                        'location': location_name,
                        'type': 'registry'
                    })
            except Exception as e:
                logger.debug(f"Erro ao ler {location_name}: {e}")
        
        # Itens das pastas
        for folder_path, location_name in self._get_startup_folders():
            try:
                for item in folder_path.iterdir():
                    if item.is_file():
                        startup_items['folders'].append({
                            'name': item.name,
                            'path': str(item),
                            'location': location_name,
                            'type': 'folder'
                        })
            except Exception as e:
                logger.debug(f"Erro ao ler pasta {location_name}: {e}")
        
        return startup_items
    
    def _is_item_safe_to_disable(self, item: Dict[str, Any]) -> tuple[bool, str]:
        """Verifica se um item é seguro para desabilitar."""
        name = item['name'].lower()
        value = item.get('value', '').lower() if 'value' in item else item.get('path', '').lower()
        
        # Itens críticos do sistema que não devem ser desabilitados
        critical_items = [
            'winlogon', 'userinit', 'explorer', 'dwm', 'ctfmon',
            'windows security', 'windows defender', 'microsoft edge update',
            'realtek', 'nvidia', 'amd', 'intel'
        ]
        
        # Itens comuns que podem ser desabilitados
        safe_to_disable = [
            'spotify', 'discord', 'steam', 'skype', 'adobe', 'java',
            'office', 'microsoft teams', 'zoom', 'dropbox', 'onedrive'
        ]
        
        # Verificar se é crítico
        for critical in critical_items:
            if critical in name or critical in value:
                return False, "Item crítico do sistema"
        
        # Verificar se é seguro
        for safe in safe_to_disable:
            if safe in name or safe in value:
                return True, "Item não essencial"
        
        # Por padrão, considerar seguro se não for crítico
        return True, "Item não crítico identificado"
    
    def _disable_registry_item(self, item: Dict[str, Any]) -> bool:
        """Desabilita um item do registro."""
        try:
            hkey = item['hkey']
            subkey = item['subkey']
            name = item['name']
            
            # Criar backup
            if self.backup_id:
                from ..safety.backup import backup_manager
                backup_manager.backup_registry_key(self.backup_id, hkey, subkey, f"Startup item: {name}")
            
            # Remover o valor
            success = registry.delete_value(hkey, subkey, name)
            
            if success:
                logger.info(f"Item de inicialização desabilitado: {name}")
                self.disabled_items.append(item)
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao desabilitar item {item['name']}: {e}")
            return False
    
    def _disable_folder_item(self, item: Dict[str, Any]) -> bool:
        """Desabilita um item da pasta."""
        try:
            file_path = Path(item['path'])
            
            # Criar backup
            if self.backup_id:
                from ..safety.backup import backup_manager
                backup_manager.backup_file(self.backup_id, str(file_path), f"Startup file: {item['name']}")
            
            # Renomear o arquivo para .disabled
            disabled_path = file_path.with_suffix(file_path.suffix + '.disabled')
            file_path.rename(disabled_path)
            
            logger.info(f"Arquivo de inicialização desabilitado: {item['name']}")
            item['disabled_path'] = str(disabled_path)
            self.disabled_items.append(item)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao desabilitar arquivo {item['name']}: {e}")
            return False
    
    def simulate(self) -> OptimizationResult:
        """Simula o gerenciamento de inicialização."""
        try:
            startup_items = self._get_all_startup_items()
            
            analysis = {
                'total_items': 0,
                'safe_to_disable': [],
                'critical_items': [],
                'registry_items': [],
                'folder_items': []
            }
            
            # Analisar itens do registro
            for item in startup_items['registry']:
                analysis['total_items'] += 1
                analysis['registry_items'].append({
                    'name': item['name'],
                    'value': item['value'],
                    'location': item['location']
                })
                
                safe, reason = self._is_item_safe_to_disable(item)
                if safe:
                    analysis['safe_to_disable'].append({
                        'name': item['name'],
                        'type': 'registry',
                        'location': item['location'],
                        'reason': reason
                    })
                else:
                    analysis['critical_items'].append({
                        'name': item['name'],
                        'type': 'registry',
                        'location': item['location'],
                        'reason': reason
                    })
            
            # Analisar itens das pastas
            for item in startup_items['folders']:
                analysis['total_items'] += 1
                analysis['folder_items'].append({
                    'name': item['name'],
                    'path': item['path'],
                    'location': item['location']
                })
                
                safe, reason = self._is_item_safe_to_disable(item)
                if safe:
                    analysis['safe_to_disable'].append({
                        'name': item['name'],
                        'type': 'folder',
                        'location': item['location'],
                        'reason': reason
                    })
                else:
                    analysis['critical_items'].append({
                        'name': item['name'],
                        'type': 'folder',
                        'location': item['location'],
                        'reason': reason
                    })
            
            return OptimizationResult(
                success=True,
                message=f"Análise concluída: {len(analysis['safe_to_disable'])} itens podem ser desabilitados de {analysis['total_items']} itens",
                details=analysis
            )
            
        except Exception as e:
            return OptimizationResult(False, f"Erro na simulação: {e}")
    
    def apply(self) -> OptimizationResult:
        """Aplica o gerenciamento de inicialização."""
        try:
            startup_items = self._get_all_startup_items()
            
            disabled_count = 0
            details = {
                'items_processed': 0,
                'items_disabled': 0,
                'disabled_items': [],
                'skipped_items': [],
                'errors': []
            }
            
            # Processar itens do registro
            for item in startup_items['registry']:
                details['items_processed'] += 1
                
                safe, reason = self._is_item_safe_to_disable(item)
                if safe:
                    if self._disable_registry_item(item):
                        disabled_count += 1
                        details['disabled_items'].append({
                            'name': item['name'],
                            'type': 'registry',
                            'location': item['location'],
                            'reason': reason
                        })
                    else:
                        details['errors'].append(f"Falha ao desabilitar {item['name']}")
                else:
                    details['skipped_items'].append({
                        'name': item['name'],
                        'type': 'registry',
                        'reason': reason
                    })
            
            # Processar itens das pastas
            for item in startup_items['folders']:
                details['items_processed'] += 1
                
                safe, reason = self._is_item_safe_to_disable(item)
                if safe:
                    if self._disable_folder_item(item):
                        disabled_count += 1
                        details['disabled_items'].append({
                            'name': item['name'],
                            'type': 'folder',
                            'location': item['location'],
                            'reason': reason
                        })
                    else:
                        details['errors'].append(f"Falha ao desabilitar {item['name']}")
                else:
                    details['skipped_items'].append({
                        'name': item['name'],
                        'type': 'folder',
                        'reason': reason
                    })
            
            details['items_disabled'] = disabled_count
            
            return OptimizationResult(
                success=True,
                message=f"Gerenciamento concluído: {disabled_count} itens desabilitados",
                details=details
            )
            
        except Exception as e:
            return OptimizationResult(False, f"Erro no gerenciamento: {e}")
    
    def revert(self) -> OptimizationResult:
        """Reverte o gerenciamento de inicialização."""
        try:
            if not self.backup_id:
                return OptimizationResult(
                    success=False,
                    message="Nenhum backup disponível para restauração"
                )
            
            from ..safety.restore import restore_manager
            
            success = restore_manager.restore_operation(self.backup_id)
            
            if success:
                self.disabled_items.clear()
                return OptimizationResult(
                    success=True,
                    message="Itens de inicialização restaurados"
                )
            else:
                return OptimizationResult(
                    success=False,
                    message="Falha ao restaurar itens de inicialização"
                )
                
        except Exception as e:
            return OptimizationResult(False, f"Erro na restauração: {e}")