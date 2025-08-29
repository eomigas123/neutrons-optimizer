"""
Operações seguras no registro do Windows com backup automático.
"""
import winreg
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime
from ...utils.logging import logger


class RegistryManager:
    """Gerenciador seguro para operações no registro do Windows."""
    
    def __init__(self):
        self.backup_dir = Path.home() / "AppData" / "Local" / "NeutronsOptimizer" / "backups" / "registry"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_hkey_name(self, hkey: int) -> str:
        """Converte handle de chave para nome legível."""
        hkey_names = {
            winreg.HKEY_LOCAL_MACHINE: "HKLM",
            winreg.HKEY_CURRENT_USER: "HKCU",
            winreg.HKEY_CLASSES_ROOT: "HKCR",
            winreg.HKEY_USERS: "HKU",
            winreg.HKEY_CURRENT_CONFIG: "HKCC"
        }
        return hkey_names.get(hkey, "UNKNOWN")
    
    def backup_key(self, hkey: int, subkey: str) -> Optional[str]:
        """Cria backup de uma chave do registro."""
        try:
            hkey_name = self._get_hkey_name(hkey)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_subkey = subkey.replace("\\", "_").replace("/", "_")
            backup_filename = f"{hkey_name}_{safe_subkey}_{timestamp}.reg"
            backup_path = self.backup_dir / backup_filename
            
            # Criar comando reg export
            full_key = f"{hkey_name}\\{subkey}"
            cmd = ["reg", "export", full_key, str(backup_path), "/y"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Backup do registro criado: {backup_path}")
                return str(backup_path)
            else:
                logger.warning(f"Falha no backup do registro: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar backup do registro: {e}")
            return None
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restaura registro a partir de um backup."""
        try:
            if not Path(backup_path).exists():
                logger.error(f"Arquivo de backup não encontrado: {backup_path}")
                return False
            
            cmd = ["reg", "import", backup_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Registro restaurado do backup: {backup_path}")
                return True
            else:
                logger.error(f"Falha ao restaurar registro: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao restaurar registro: {e}")
            return False
    
    def read_value(self, hkey: int, subkey: str, value_name: str) -> Optional[Any]:
        """Lê um valor do registro."""
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                value, reg_type = winreg.QueryValueEx(key, value_name)
                logger.debug(f"Valor lido: {self._get_hkey_name(hkey)}\\{subkey}\\{value_name} = {value}")
                return value
        except FileNotFoundError:
            logger.debug(f"Chave/valor não encontrado: {self._get_hkey_name(hkey)}\\{subkey}\\{value_name}")
            return None
        except Exception as e:
            logger.error(f"Erro ao ler valor do registro: {e}")
            return None
    
    def write_value(self, hkey: int, subkey: str, value_name: str, value: Any, reg_type: int = winreg.REG_DWORD) -> bool:
        """Escreve um valor no registro com backup automático."""
        try:
            # Fazer backup da chave antes de modificar
            backup_path = self.backup_key(hkey, subkey)
            
            # Criar chave se não existir
            with winreg.CreateKey(hkey, subkey) as key:
                winreg.SetValueEx(key, value_name, 0, reg_type, value)
                logger.info(f"Valor escrito: {self._get_hkey_name(hkey)}\\{subkey}\\{value_name} = {value}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao escrever valor no registro: {e}")
            # Tentar restaurar backup se existir
            if backup_path:
                logger.info("Tentando restaurar backup devido ao erro...")
                self.restore_from_backup(backup_path)
            return False
    
    def delete_value(self, hkey: int, subkey: str, value_name: str) -> bool:
        """Remove um valor do registro com backup automático."""
        try:
            # Fazer backup da chave antes de modificar
            backup_path = self.backup_key(hkey, subkey)
            
            with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, value_name)
                logger.info(f"Valor removido: {self._get_hkey_name(hkey)}\\{subkey}\\{value_name}")
                return True
                
        except FileNotFoundError:
            logger.debug(f"Valor não encontrado para remoção: {self._get_hkey_name(hkey)}\\{subkey}\\{value_name}")
            return True  # Considerar sucesso se já não existe
        except Exception as e:
            logger.error(f"Erro ao remover valor do registro: {e}")
            # Tentar restaurar backup se existir
            if backup_path:
                logger.info("Tentando restaurar backup devido ao erro...")
                self.restore_from_backup(backup_path)
            return False
    
    def key_exists(self, hkey: int, subkey: str) -> bool:
        """Verifica se uma chave existe no registro."""
        try:
            with winreg.OpenKey(hkey, subkey):
                return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar existência da chave: {e}")
            return False
    
    def value_exists(self, hkey: int, subkey: str, value_name: str) -> bool:
        """Verifica se um valor existe no registro."""
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                winreg.QueryValueEx(key, value_name)
                return True
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar existência do valor: {e}")
            return False
    
    def enumerate_subkeys(self, hkey: int, subkey: str) -> List[str]:
        """Lista todas as subchaves de uma chave."""
        subkeys = []
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkeys.append(subkey_name)
                        i += 1
                    except OSError:
                        break
        except Exception as e:
            logger.error(f"Erro ao enumerar subchaves: {e}")
        
        return subkeys
    
    def enumerate_values(self, hkey: int, subkey: str) -> Dict[str, Any]:
        """Lista todos os valores de uma chave."""
        values = {}
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                i = 0
                while True:
                    try:
                        name, value, reg_type = winreg.EnumValue(key, i)
                        values[name] = value
                        i += 1
                    except OSError:
                        break
        except Exception as e:
            logger.error(f"Erro ao enumerar valores: {e}")
        
        return values
    
    def get_backup_files(self) -> List[Path]:
        """Retorna lista de arquivos de backup disponíveis."""
        try:
            return list(self.backup_dir.glob("*.reg"))
        except Exception as e:
            logger.error(f"Erro ao listar backups: {e}")
            return []


# Instância global
registry = RegistryManager()