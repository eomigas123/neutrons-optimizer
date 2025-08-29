"""
Sistema de backup para operações de otimização.
"""
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import winreg
from ..system.registry import registry
from ..system.shell import shell
from ...utils.logging import logger


class BackupManager:
    """Gerenciador de backups para operações de otimização."""
    
    def __init__(self):
        self.backup_root = Path.home() / "AppData" / "Local" / "NeutronsOptimizer" / "backups"
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # Diretórios específicos
        self.registry_backups = self.backup_root / "registry"
        self.file_backups = self.backup_root / "files"
        self.service_backups = self.backup_root / "services"
        self.power_backups = self.backup_root / "power"
        
        # Criar diretórios
        for backup_dir in [self.registry_backups, self.file_backups, 
                          self.service_backups, self.power_backups]:
            backup_dir.mkdir(exist_ok=True)
    
    def create_operation_backup(self, operation_name: str) -> str:
        """Cria um backup completo para uma operação específica."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"{operation_name}_{timestamp}"
        
        backup_info = {
            'operation': operation_name,
            'timestamp': timestamp,
            'backup_id': backup_id,
            'registry_backups': [],
            'file_backups': [],
            'service_states': {},
            'power_settings': {},
            'startup_items': []
        }
        
        # Salvar info do backup
        info_file = self.backup_root / f"{backup_id}_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Backup criado para operação {operation_name}: {backup_id}")
        return backup_id
    
    def backup_registry_key(self, backup_id: str, hkey: int, subkey: str, 
                           description: str = "") -> bool:
        """Faz backup de uma chave específica do registro."""
        try:
            backup_path = registry.backup_key(hkey, subkey)
            if backup_path:
                # Atualizar info do backup
                self._update_backup_info(backup_id, 'registry_backups', {
                    'hkey': registry._get_hkey_name(hkey),
                    'subkey': subkey,
                    'backup_path': backup_path,
                    'description': description
                })
                return True
            return False
        except Exception as e:
            logger.error(f"Erro no backup do registro: {e}")
            return False
    
    def backup_file(self, backup_id: str, file_path: str, description: str = "") -> bool:
        """Faz backup de um arquivo específico."""
        try:
            source = Path(file_path)
            if not source.exists():
                logger.warning(f"Arquivo não encontrado para backup: {file_path}")
                return True  # Não é erro se não existe
            
            # Criar nome seguro para o backup
            safe_name = str(source).replace(":", "_").replace("\\", "_").replace("/", "_")
            backup_name = f"{backup_id}_{safe_name}"
            backup_path = self.file_backups / backup_name
            
            # Copiar arquivo
            shutil.copy2(source, backup_path)
            
            # Atualizar info do backup
            self._update_backup_info(backup_id, 'file_backups', {
                'original_path': str(source),
                'backup_path': str(backup_path),
                'description': description
            })
            
            logger.info(f"Arquivo copiado para backup: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro no backup do arquivo {file_path}: {e}")
            return False
    
    def backup_directory(self, backup_id: str, dir_path: str, description: str = "") -> bool:
        """Faz backup de um diretório completo."""
        try:
            source = Path(dir_path)
            if not source.exists():
                logger.warning(f"Diretório não encontrado para backup: {dir_path}")
                return True
            
            # Criar arquivo zip para o backup
            safe_name = str(source).replace(":", "_").replace("\\", "_").replace("/", "_")
            backup_name = f"{backup_id}_{safe_name}.zip"
            backup_path = self.file_backups / backup_name
            
            # Criar zip
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source.rglob('*'):
                    if file_path.is_file():
                        try:
                            arcname = file_path.relative_to(source)
                            zipf.write(file_path, arcname)
                        except Exception as e:
                            logger.warning(f"Erro ao adicionar {file_path} ao backup: {e}")
            
            # Atualizar info do backup
            self._update_backup_info(backup_id, 'file_backups', {
                'original_path': str(source),
                'backup_path': str(backup_path),
                'type': 'directory_zip',
                'description': description
            })
            
            logger.info(f"Diretório compactado para backup: {dir_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro no backup do diretório {dir_path}: {e}")
            return False
    
    def backup_service_state(self, backup_id: str, service_name: str) -> bool:
        """Faz backup do estado atual de um serviço."""
        try:
            from ..system.services import ServiceManager
            
            state = ServiceManager.get_service_status(service_name)
            info = ServiceManager.get_service_info(service_name)
            
            service_backup = {
                'name': service_name,
                'state': state.value,
                'info': info
            }
            
            # Atualizar info do backup
            self._update_backup_info(backup_id, 'service_states', service_backup, key=service_name)
            
            logger.info(f"Estado do serviço {service_name} salvo no backup")
            return True
            
        except Exception as e:
            logger.error(f"Erro no backup do serviço {service_name}: {e}")
            return False
    
    def backup_power_plan(self, backup_id: str) -> bool:
        """Faz backup do plano de energia atual."""
        try:
            # Obter plano atual
            result = shell.run_powershell("Get-WmiObject -Class Win32_PowerPlan -Namespace root\\cimv2\\power | Where-Object {$_.IsActive -eq $true} | Select-Object InstanceID, ElementName")
            
            if result.success:
                power_info = {
                    'output': result.stdout,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Atualizar info do backup
                self._update_backup_info(backup_id, 'power_settings', power_info)
                
                logger.info("Plano de energia atual salvo no backup")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erro no backup do plano de energia: {e}")
            return False
    
    def backup_startup_items(self, backup_id: str) -> bool:
        """Faz backup dos itens de inicialização."""
        try:
            startup_items = []
            
            # Registry startup locations
            startup_locations = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
            ]
            
            for hkey, subkey in startup_locations:
                try:
                    values = registry.enumerate_values(hkey, subkey)
                    for name, value in values.items():
                        startup_items.append({
                            'hkey': registry._get_hkey_name(hkey),
                            'subkey': subkey,
                            'name': name,
                            'value': value,
                            'type': 'registry'
                        })
                except Exception as e:
                    logger.debug(f"Erro ao ler {subkey}: {e}")
            
            # Atualizar info do backup
            self._update_backup_info(backup_id, 'startup_items', startup_items)
            
            logger.info(f"Itens de inicialização salvos no backup: {len(startup_items)} itens")
            return True
            
        except Exception as e:
            logger.error(f"Erro no backup dos itens de inicialização: {e}")
            return False
    
    def _update_backup_info(self, backup_id: str, section: str, data: Any, key: str = None):
        """Atualiza informações do backup."""
        try:
            info_file = self.backup_root / f"{backup_id}_info.json"
            
            # Carregar info existente
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    backup_info = json.load(f)
            else:
                backup_info = {}
            
            # Atualizar seção
            if key:
                if section not in backup_info:
                    backup_info[section] = {}
                backup_info[section][key] = data
            else:
                if section not in backup_info:
                    backup_info[section] = []
                if isinstance(backup_info[section], list):
                    backup_info[section].append(data)
                else:
                    backup_info[section] = data
            
            # Salvar
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao atualizar info do backup: {e}")
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um backup."""
        try:
            info_file = self.backup_root / f"{backup_id}_info.json"
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Erro ao ler info do backup: {e}")
            return None
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista todos os backups disponíveis."""
        backups = []
        try:
            for info_file in self.backup_root.glob("*_info.json"):
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        backup_info = json.load(f)
                        backup_info['info_file'] = str(info_file)
                        backups.append(backup_info)
                except Exception as e:
                    logger.warning(f"Erro ao ler backup {info_file}: {e}")
        except Exception as e:
            logger.error(f"Erro ao listar backups: {e}")
        
        # Ordenar por timestamp (mais recente primeiro)
        backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return backups
    
    def cleanup_old_backups(self, days: int = 30) -> int:
        """Remove backups antigos."""
        removed_count = 0
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            
            for backup_file in self.backup_root.rglob("*"):
                if backup_file.is_file() and backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    removed_count += 1
                    logger.debug(f"Backup antigo removido: {backup_file.name}")
            
            logger.info(f"Limpeza de backups concluída: {removed_count} arquivos removidos")
            
        except Exception as e:
            logger.error(f"Erro na limpeza de backups: {e}")
        
        return removed_count


# Instância global
backup_manager = BackupManager()