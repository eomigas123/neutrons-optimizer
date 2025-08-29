#!/usr/bin/env python3
"""
Testes de fumaça para verificar se as otimizações básicas funcionam.
"""
import sys
import os
from pathlib import Path

# Adicionar src ao path
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Testa se todos os módulos podem ser importados."""
    print("🔍 Testando importações...")
    
    try:
        from core.optimizations import OPTIMIZATIONS
        print(f"  ✅ Importado {len(OPTIMIZATIONS)} otimizações")
        
        from core.system.registry import registry
        print("  ✅ Sistema de registro")
        
        from core.system.services import ServiceManager
        print("  ✅ Gerenciador de serviços")
        
        from core.safety.backup import backup_manager
        print("  ✅ Sistema de backup")
        
        from utils.logging import logger
        print("  ✅ Sistema de logging")
        
        from utils.os_detect import windows_info
        print("  ✅ Detecção de sistema")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de importação: {e}")
        return False


def test_optimization_compatibility():
    """Testa compatibilidade das otimizações."""
    print("🔧 Testando compatibilidade das otimizações...")
    
    try:
        from core.optimizations import OPTIMIZATIONS
        
        compatible_count = 0
        
        for opt_class in OPTIMIZATIONS:
            opt = opt_class()
            compatible = opt.check_compatibility()
            
            status = "✅" if compatible else "⚠️"
            print(f"  {status} {opt.display_name}: {'Compatível' if compatible else 'Incompatível'}")
            
            if compatible:
                compatible_count += 1
        
        print(f"📊 {compatible_count}/{len(OPTIMIZATIONS)} otimizações compatíveis")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False


def test_optimization_simulation():
    """Testa simulação das otimizações."""
    print("🎯 Testando simulação das otimizações...")
    
    try:
        from core.optimizations import OPTIMIZATIONS
        
        success_count = 0
        
        for opt_class in OPTIMIZATIONS:
            opt = opt_class()
            
            if not opt.check_compatibility():
                print(f"  ⏭️  {opt.display_name}: Pulado (incompatível)")
                continue
            
            try:
                result = opt.simulate()
                
                if result.success:
                    print(f"  ✅ {opt.display_name}: Simulação OK")
                    success_count += 1
                else:
                    print(f"  ⚠️  {opt.display_name}: {result.message}")
                    
            except Exception as e:
                print(f"  ❌ {opt.display_name}: Erro - {e}")
        
        print(f"📊 {success_count} simulações bem-sucedidas")
        return success_count > 0
        
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False


def test_system_info():
    """Testa coleta de informações do sistema."""
    print("💻 Testando informações do sistema...")
    
    try:
        from utils.os_detect import windows_info
        from utils.checks import SystemChecks
        
        # Informações do Windows
        print(f"  🖥️  Sistema: {windows_info.get_summary()}")
        print(f"  📦 Build: {windows_info.build}")
        print(f"  🎮 Suporte HAGS: {windows_info.supports_hags}")
        
        # Verificações do sistema
        info = SystemChecks.get_system_info()
        print(f"  💾 RAM: {info.get('ram_total', 'N/A')}")
        print(f"  💿 Disco: {info.get('disk_total', 'N/A')}")
        print(f"  🖥️  CPU: {info.get('cpu_cores', 'N/A')} núcleos")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False


def test_backup_system():
    """Testa sistema de backup básico."""
    print("💾 Testando sistema de backup...")
    
    try:
        from core.safety.backup import backup_manager
        
        # Criar backup teste
        backup_id = backup_manager.create_operation_backup("test_operation")
        print(f"  ✅ Backup criado: {backup_id}")
        
        # Verificar informações do backup
        backup_info = backup_manager.get_backup_info(backup_id)
        if backup_info:
            print(f"  ✅ Informações do backup recuperadas")
        else:
            print(f"  ⚠️  Não foi possível recuperar informações do backup")
        
        # Listar backups
        backups = backup_manager.list_backups()
        print(f"  📋 {len(backups)} backup(s) encontrado(s)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False


def test_logging_system():
    """Testa sistema de logging."""
    print("📝 Testando sistema de logging...")
    
    try:
        from utils.logging import logger
        
        # Testar diferentes níveis de log
        logger.info("Teste de log INFO")
        logger.warning("Teste de log WARNING")
        logger.debug("Teste de log DEBUG")
        
        # Testar log de operação
        logger.log_operation_start("test_operation", {"test": True})
        logger.log_operation_success("test_operation", {"result": "ok"})
        
        # Verificar logs recentes
        recent_logs = logger.get_recent_logs(1)
        print(f"  📋 {len(recent_logs)} logs recentes encontrados")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no teste: {e}")
        return False


def main():
    """Executa todos os testes de fumaça."""
    print("🧪 Iniciando Testes de Fumaça - Nêutrons Optimizer")
    print("=" * 55)
    
    tests = [
        ("Importações", test_imports),
        ("Compatibilidade", test_optimization_compatibility),
        ("Simulações", test_optimization_simulation),
        ("Informações do Sistema", test_system_info),
        ("Sistema de Backup", test_backup_system),
        ("Sistema de Logging", test_logging_system),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            print(f"💥 {test_name}: ERRO - {e}")
    
    print("\n" + "=" * 55)
    print(f"📊 Resultados: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("⚠️  Alguns testes falharam")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Testes interrompidos pelo usuário")
        sys.exit(1)