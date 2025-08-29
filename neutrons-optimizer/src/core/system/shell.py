"""
Execução segura de comandos do sistema com timeout e logging.
"""
import subprocess
import shlex
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import threading
import time
from ...utils.logging import logger


class CommandResult:
    """Resultado de execução de comando."""
    
    def __init__(self, returncode: int, stdout: str, stderr: str, timed_out: bool = False):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out
        self.success = returncode == 0 and not timed_out


class ShellExecutor:
    """Executor seguro de comandos do sistema."""
    
    def __init__(self):
        self.running_processes = {}
        self.process_lock = threading.Lock()
    
    def run_command(self, command: str, timeout: int = 60, cwd: Optional[str] = None,
                   env: Optional[Dict[str, str]] = None, shell: bool = True) -> CommandResult:
        """Executa um comando com timeout e logging."""
        try:
            logger.debug(f"Executando comando: {command}")
            
            # Preparar ambiente
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            # Executar comando
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=shell,
                cwd=cwd,
                env=exec_env
            )
            
            # Registrar processo
            process_id = id(process)
            with self.process_lock:
                self.running_processes[process_id] = process
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                result = CommandResult(process.returncode, stdout, stderr)
                
                if result.success:
                    logger.debug(f"Comando executado com sucesso: {command}")
                else:
                    logger.warning(f"Comando falhou: {command} | Código: {process.returncode}")
                    if stderr:
                        logger.debug(f"Stderr: {stderr}")
                
                return result
                
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout no comando: {command}")
                process.kill()
                stdout, stderr = process.communicate()
                return CommandResult(-1, stdout, stderr, timed_out=True)
            
            finally:
                # Remover processo da lista
                with self.process_lock:
                    self.running_processes.pop(process_id, None)
                
        except Exception as e:
            logger.error(f"Erro ao executar comando: {command} | Erro: {e}")
            return CommandResult(-1, "", str(e))
    
    def run_powershell(self, script: str, timeout: int = 60) -> CommandResult:
        """Executa um script PowerShell."""
        command = f'powershell.exe -ExecutionPolicy Bypass -Command "{script}"'
        return self.run_command(command, timeout)
    
    def run_cmd(self, command: str, timeout: int = 60) -> CommandResult:
        """Executa um comando no cmd."""
        command = f'cmd.exe /c "{command}"'
        return self.run_command(command, timeout)
    
    def run_elevated(self, command: str, timeout: int = 60) -> CommandResult:
        """Executa um comando com privilégios elevados via PowerShell."""
        ps_script = f"""
        Start-Process powershell -ArgumentList '-Command "{command}"' -Verb RunAs -Wait -WindowStyle Hidden
        """
        return self.run_powershell(ps_script, timeout)
    
    def kill_process_by_name(self, process_name: str) -> bool:
        """Mata processos por nome."""
        try:
            command = f"taskkill /f /im {process_name}"
            result = self.run_command(command, timeout=10)
            return result.success
        except Exception as e:
            logger.error(f"Erro ao matar processo {process_name}: {e}")
            return False
    
    def is_process_running(self, process_name: str) -> bool:
        """Verifica se um processo está rodando."""
        try:
            command = f"tasklist /fi \"imagename eq {process_name}\""
            result = self.run_command(command, timeout=10)
            return result.success and process_name.lower() in result.stdout.lower()
        except Exception as e:
            logger.error(f"Erro ao verificar processo {process_name}: {e}")
            return False
    
    def get_running_processes(self) -> List[Dict[str, str]]:
        """Lista processos em execução."""
        processes = []
        try:
            result = self.run_command("tasklist /fo csv", timeout=20)
            if result.success:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Pular cabeçalho
                    for line in lines[1:]:
                        parts = [part.strip('"') for part in line.split('","')]
                        if len(parts) >= 5:
                            processes.append({
                                'name': parts[0],
                                'pid': parts[1],
                                'session': parts[2],
                                'session_number': parts[3],
                                'memory': parts[4]
                            })
        except Exception as e:
            logger.error(f"Erro ao listar processos: {e}")
        
        return processes
    
    def cleanup_temp_files(self, temp_dir: Optional[str] = None) -> bool:
        """Limpa arquivos temporários."""
        try:
            if not temp_dir:
                temp_dir = os.environ.get('TEMP', 'C:\\Temp')
            
            # Usar PowerShell para limpeza segura
            ps_script = f"""
            Get-ChildItem -Path "{temp_dir}" -Recurse -Force | 
            Where-Object {{ $_.LastWriteTime -lt (Get-Date).AddDays(-1) }} |
            Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
            """
            
            result = self.run_powershell(ps_script, timeout=120)
            return result.success
            
        except Exception as e:
            logger.error(f"Erro na limpeza de temporários: {e}")
            return False
    
    def restart_explorer(self) -> bool:
        """Reinicia o Windows Explorer de forma segura."""
        try:
            # Matar explorer
            self.kill_process_by_name("explorer.exe")
            
            # Aguardar um pouco
            time.sleep(2)
            
            # Reiniciar explorer
            result = self.run_command("explorer.exe", timeout=10)
            return True  # Explorer pode não retornar código de sucesso
            
        except Exception as e:
            logger.error(f"Erro ao reiniciar Explorer: {e}")
            return False
    
    def check_disk_health(self, drive: str = "C:") -> Dict[str, str]:
        """Verifica saúde do disco."""
        health_info = {}
        try:
            # Verificar com chkdsk
            command = f"chkdsk {drive} /scan"
            result = self.run_command(command, timeout=60)
            health_info['chkdsk_result'] = 'success' if result.success else 'failed'
            health_info['chkdsk_output'] = result.stdout
            
            # Verificar SMART (se disponível)
            smart_command = f"wmic diskdrive get status"
            smart_result = self.run_command(smart_command, timeout=30)
            if smart_result.success:
                health_info['smart_status'] = smart_result.stdout
            
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do disco: {e}")
            health_info['error'] = str(e)
        
        return health_info
    
    def terminate_all_running(self):
        """Termina todos os processos em execução controlados por este executor."""
        with self.process_lock:
            for process in self.running_processes.values():
                try:
                    process.terminate()
                    logger.info(f"Processo terminado: PID {process.pid}")
                except Exception as e:
                    logger.error(f"Erro ao terminar processo: {e}")
            self.running_processes.clear()


# Instância global
shell = ShellExecutor()