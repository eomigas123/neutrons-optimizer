#!/usr/bin/env python3
"""
Script para executar o Nêutrons Optimizer em modo de desenvolvimento.
"""
import sys
import os
from pathlib import Path

# Adicionar src ao path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    missing_deps = []
    
    try:
        import PySide6
    except ImportError:
        missing_deps.append("PySide6")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    if missing_deps:
        print("❌ Dependências faltando:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Para instalar:")
        print(f"   pip install {' '.join(missing_deps)}")
        print("\n   ou")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_platform():
    """Verifica se está rodando no Windows."""
    if os.name != 'nt':
        print("❌ Este aplicativo foi desenvolvido para Windows 10/11.")
        print(f"   Sistema detectado: {os.name}")
        return False
    return True

def main():
    """Função principal."""
    print("🚀 Iniciando Nêutrons Optimizer (Modo Desenvolvimento)")
    print("=" * 50)
    
    # Verificações
    if not check_platform():
        return 1
    
    if not check_dependencies():
        return 1
    
    print("✅ Verificações concluídas")
    print("⚛️  Iniciando aplicação...")
    print()
    
    try:
        # Importar e executar aplicação
        from app import main as app_main
        return app_main()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Verifique se você está no diretório correto")
        return 1
    
    except KeyboardInterrupt:
        print("\n⏹️  Aplicação interrompida pelo usuário")
        return 0
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())