"""
Sistema de restauração para reverter operações de otimização.
"""
import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import winreg
from ..system.registry import registry
from ..system.services import ServiceManager, ServiceState
from ..system.shell import shell
from ...utils.logging import logger
from .backup import backup_manager


class RestoreManager:
    """Gerenciador de restauração para reverter otimizações."""
    
    def __init__(self):
        self.backup_manager = backup_manager
    
    def restore_operation(self, backup_id: str) -> bool:
        """Restaura uma operação completa a partir do backup."""
        try:
            backup_info = self.backup_manager.get_backup_info(backup_id)
            if not backup_info:
                logger.error(f"Backup não encontrado: {backup_id}")
                return False
            
            operation_name = backup_info.get('operation', 'Unknown')
            logger.info(f"Iniciando restauração da operação: {operation_name}")
            
            success = True
            
            # Restaurar registro
            if backup_info.get('registry_backups'):
                logger.info("Restaurando backups do registro...")
                for reg_backup in backup_info['registry_backups']:
                    if not self._restore_registry_backup(reg_backup):
                        success = False
            
            # Restaurar arquivos
            if backup_info.get('file_backups'):
                logger.info("Restaurando backups de arquivos...")
                for file_backup in backup_info['file_backups']:
                    if not self._restore_file_backup(file_backup):
                        success = False
            
            # Restaurar serviços
            if backup_info.get('service_states'):
                logger.info("Restaurando estados de serviços...")
                for service_name, service_data in backup_info['service_states'].items():
                    if not self._restore_service_state(service_name, service_data):
                        success = False
            
            # Restaurar plano de energia
            if backup_info.get('power_settings'):
                logger.info("Restaurando plano de energia...")
                if not self._restore_power_plan(backup_info['power_settings']):
                    success = False
            
            # Restaurar itens de inicialização
            if backup_info.get('startup_items'):
                logger.info("Restaurando itens de inicialização...")
                if not self._restore_startup_items(backup_info['startup_items']):
                    success = False
            
            if success:
                logger.info(f"Restauração da operação {operation_name} concluída com sucesso")
            else:
                logger.warning(f"Restauração da operação {operation_name} concluída com alguns erros")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro na restauração do backup {backup_id}: {e}")
            return False
    
    def _restore_registry_backup(self, reg_backup: Dict[str, str]) -> bool:
        """Restaura um backup específico do registro."""
        try:
            backup_path = reg_backup.get('backup_path')
            if not backup_path or not Path(backup_path).exists():
                logger.warning(f"Arquivo de backup do registro não encontrado: {backup_path}")
                return False
            
            # Usar o método do registry manager
            success = registry.restore_from_backup(backup_path)
            
            if success:
                logger.info(f"Registro restaurado: {reg_backup.get('description', 'N/A')}")
            else:
                logger.error(f"Falha ao restaurar registro: {reg_backup.get('description', 'N/A')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup do registro: {e}")
            return False
    
    def _restore_file_backup(self, file_backup: Dict[str, str]) -> bool:
        """Restaura um backup específico de arquivo."""
        try:
            original_path = file_backup.get('original_path')
            backup_path = file_backup.get('backup_path')
            backup_type = file_backup.get('type', 'file')
            
            if not backup_path or not Path(backup_path).exists():
                logger.warning(f"Arquivo de backup não encontrado: {backup_path}")
                return False
            
            if backup_type == 'directory_zip':
                # Restaurar diretório do zip
                return self._restore_directory_from_zip(original_path, backup_path)
            else:
                # Restaurar arquivo simples
                return self._restore_single_file(original_path, backup_path)
                
        except Exception as e:
            logger.error(f"Erro ao restaurar backup de arquivo: {e}")
            return False
    
    def _restore_single_file(self, original_path: str, backup_path: str) -> bool:
        """Restaura um único arquivo."""
        try:
            original = Path(original_path)
            backup = Path(backup_path)
            
            # Criar diretório pai se necessário
            original.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar arquivo de volta
            shutil.copy2(backup, original)
            
            logger.info(f"Arquivo restaurado: {original_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar arquivo {original_path}: {e}")
            return False
    
    def _restore_directory_from_zip(self, original_path: str, backup_zip: str) -> bool:
        """Restaura um diretório a partir do arquivo zip."""
        try:
            original_dir = Path(original_path)
            backup_zip_path = Path(backup_zip)
            
            # Remover diretório atual se existir
            if original_dir.exists():
                shutil.rmtree(original_dir, ignore_errors=True)
            
            # Criar diretório
            original_dir.mkdir(parents=True, exist_ok=True)
            
            # Extrair zip
            with zipfile.ZipFile(backup_zip_path, 'r') as zipf:
                zipf.extractall(original_dir)
            
            logger.info(f"Diretório restaurado: {original_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar diretório {original_path}: {e}")
            return False
    
    def _restore_service_state(self, service_name: str, service_data: Dict[str, Any]) -> bool:
        """Restaura o estado de um serviço."""
        try:
            target_state = service_data.get('state', 'UNKNOWN')
            
            if target_state == 'RUNNING':
                success = ServiceManager.start_service(service_name)
            elif target_state == 'STOPPED':
                success = ServiceManager.stop_service(service_name)
            else:
                logger.warning(f"Estado desconhecido para serviço {service_name}: {target_state}")
                return True  # Não é erro crítico
            
            if success:
                logger.info(f"Estado do serviço {service_name} restaurado para: {target_state}")
            else:
                logger.error(f"Falha ao restaurar estado do serviço {service_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao restaurar serviço {service_name}: {e}")
            return False
    
    def _restore_power_plan(self, power_settings: Dict[str, Any]) -> bool:
        """Restaura o plano de energia."""
        try:
            # Esta é uma implementação simplificada
            # Em um cenário real, seria necessário extrair e aplicar o GUID do plano
            logger.info("Restauração do plano de energia - implementação simplificada")
            
            # Por enquanto, apenas log das informações salvas
            output = power_settings.get('output', '')
            if 'Ultimate Performance' in output:
                # Tentar ativar Ultimate Performance
                result = shell.run_powershell(
                    "powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61"
                )
                if result.success:
                    logger.info("Plano Ultimate Performance restaurado")
                    return True
            
            # Tentar ativar High Performance como fallback
            result = shell.run_powershell(
                "powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
            )
            
            if result.success:
                logger.info("Plano High Performance restaurado como fallback")
                return True
            
            logger.warning("Não foi possível restaurar plano de energia específico")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao restaurar plano de energia: {e}")
            return False
    
    def _restore_startup_items(self, startup_items: List[Dict[str, Any]]) -> bool:
        """Restaura itens de inicialização."""
        try:
            success_count = 0
            total_items = len(startup_items)
            
            for item in startup_items:
                try:
                    if item.get('type') == 'registry':
                        hkey_name = item.get('hkey')
                        subkey = item.get('subkey')
                        name = item.get('name')
                        value = item.get('value')
                        
                        # Converter nome da chave para handle
                        hkey_map = {
                            'HKLM': winreg.HKEY_LOCAL_MACHINE,
                            'HKCU': winreg.HKEY_CURRENT_USER,
                            'HKCR': winreg.HKEY_CLASSES_ROOT,
                            'HKU': winreg.HKEY_USERS,
                            'HKCC': winreg.HKEY_CURRENT_CONFIG
                        }
                        
                        hkey = hkey_map.get(hkey_name)
                        if hkey and subkey and name and value:
                            if registry.write_value(hkey, subkey, name, value, winreg.REG_SZ):
                                success_count += 1
                                logger.debug(f"Item de inicialização restaurado: {name}")
                            else:
                                logger.warning(f"Falha ao restaurar item: {name}")
                        
                except Exception as e:
                    logger.warning(f"Erro ao restaurar item de inicialização: {e}")
            
            logger.info(f"Itens de inicialização restaurados: {success_count}/{total_items}")
            return success_count > 0 or total_items == 0
            
        except Exception as e:
            logger.error(f"Erro ao restaurar itens de inicialização: {e}")
            return False
    
    def list_available_restores(self) -> List[Dict[str, Any]]:
        """Lista todas as restaurações disponíveis."""
        backups = self.backup_manager.list_backups()
        
        # Adicionar informações úteis para exibição
        for backup in backups:
            backup['restore_available'] = True
            backup['items_count'] = self._count_backup_items(backup)
        
        return backups
    
    def _count_backup_items(self, backup_info: Dict[str, Any]) -> Dict[str, int]:
        """Conta itens em um backup."""
        counts = {
            'registry': len(backup_info.get('registry_backups', [])),
            'files': len(backup_info.get('file_backups', [])),
            'services': len(backup_info.get('service_states', {})),
            'startup_items': len(backup_info.get('startup_items', [])),
            'power_settings': 1 if backup_info.get('power_settings') else 0
        }
        
        counts['total'] = sum(counts.values())
        return counts
    
    def get_restore_preview(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Gera um preview do que será restaurado."""
        try:
            backup_info = self.backup_manager.get_backup_info(backup_id)
            if not backup_info:
                return None
            
            preview = {
                'operation': backup_info.get('operation', 'Unknown'),
                'timestamp': backup_info.get('timestamp', 'Unknown'),
                'actions': []
            }
            
            # Registry actions
            for reg_backup in backup_info.get('registry_backups', []):
                preview['actions'].append({
                    'type': 'registry',
                    'description': f"Restaurar registro: {reg_backup.get('description', 'N/A')}",
                    'details': f"{reg_backup.get('hkey')}\\{reg_backup.get('subkey')}"
                })
            
            # File actions
            for file_backup in backup_info.get('file_backups', []):
                preview['actions'].append({
                    'type': 'file',
                    'description': f"Restaurar arquivo: {file_backup.get('description', 'N/A')}",
                    'details': file_backup.get('original_path', 'N/A')
                })
            
            # Service actions
            for service_name, service_data in backup_info.get('service_states', {}).items():
                preview['actions'].append({
                    'type': 'service',
                    'description': f"Restaurar serviço: {service_name}",
                    'details': f"Estado: {service_data.get('state', 'Unknown')}"
                })
            
            # Power settings
            if backup_info.get('power_settings'):
                preview['actions'].append({
                    'type': 'power',
                    'description': "Restaurar plano de energia",
                    'details': "Plano anterior"
                })
            
            # Startup items
            startup_count = len(backup_info.get('startup_items', []))
            if startup_count > 0:
                preview['actions'].append({
                    'type': 'startup',
                    'description': f"Restaurar itens de inicialização",
                    'details': f"{startup_count} itens"
                })
            
            return preview
            
        except Exception as e:
            logger.error(f"Erro ao gerar preview de restauração: {e}")
            return None


# Instância global
restore_manager = RestoreManager()