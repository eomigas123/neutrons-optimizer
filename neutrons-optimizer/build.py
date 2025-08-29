#!/usr/bin/env python3
"""
Script para compilar o Nêutrons Optimizer com PyInstaller.
"""
import sys
import os
import shutil
import subprocess
from pathlib import Path


class BuildManager:
    """Gerenciador de build do aplicativo."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.spec_dir = self.build_dir / "spec"
        
    def check_dependencies(self):
        """Verifica dependências necessárias para o build."""
        print("🔍 Verificando dependências...")
        
        missing_deps = []
        
        try:
            import PySide6
            print("  ✅ PySide6")
        except ImportError:
            missing_deps.append("PySide6")
            print("  ❌ PySide6")
        
        try:
            import psutil
            print("  ✅ psutil")
        except ImportError:
            missing_deps.append("psutil")
            print("  ❌ psutil")
        
        try:
            import PyInstaller
            print("  ✅ PyInstaller")
        except ImportError:
            missing_deps.append("pyinstaller")
            print("  ❌ PyInstaller")
        
        if missing_deps:
            print(f"\n❌ Dependências faltando: {', '.join(missing_deps)}")
            print("💡 Instale com: pip install -r requirements.txt")
            return False
        
        print("✅ Todas as dependências estão disponíveis")
        return True
    
    def clean_build(self):
        """Limpa diretórios de build anteriores."""
        print("🧹 Limpando builds anteriores...")
        
        dirs_to_clean = [self.build_dir, self.dist_dir]
        
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  🗑️  Removido: {dir_path}")
        
        print("✅ Limpeza concluída")
    
    def create_spec_file(self):
        """Cria o arquivo .spec do PyInstaller."""
        print("📝 Criando arquivo de especificação...")
        
        self.spec_dir.mkdir(parents=True, exist_ok=True)
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
"""
Especificação PyInstaller para Nêutrons Optimizer.
"""

block_cipher = None

a = Analysis(
    ['{self.src_dir / "app.py"}'],
    pathex=['{self.src_dir}'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'psutil',
        'winreg',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NeutronsOptimizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='{self.spec_dir / "version_info.txt"}',
    icon=None,  # TODO: Adicionar ícone
    uac_admin=True,  # Solicitar UAC
)
'''
        
        spec_file = self.spec_dir / "neutrons_optimizer.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ Arquivo .spec criado: {spec_file}")
        return spec_file
    
    def create_version_info(self):
        """Cria arquivo de informações de versão."""
        print("📋 Criando informações de versão...")
        
        version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'MusashiSanS2'),
            StringStruct(u'FileDescription', u'Nêutrons Optimizer - Otimizador para Windows'),
            StringStruct(u'FileVersion', u'1.0.0.0'),
            StringStruct(u'InternalName', u'neutrons_optimizer'),
            StringStruct(u'LegalCopyright', u'Copyright © 2024 MusashiSanS2'),
            StringStruct(u'OriginalFilename', u'NeutronsOptimizer.exe'),
            StringStruct(u'ProductName', u'Nêutrons Optimizer'),
            StringStruct(u'ProductVersion', u'1.0.0.0')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        
        version_file = self.spec_dir / "version_info.txt"
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_info)
        
        print(f"✅ Arquivo de versão criado: {version_file}")
        return version_file
    
    def run_pyinstaller(self, spec_file):
        """Executa o PyInstaller."""
        print("🔨 Executando PyInstaller...")
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm", 
            str(spec_file)
        ]
        
        print(f"💻 Comando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            if result.returncode == 0:
                print("✅ PyInstaller executado com sucesso")
                return True
            else:
                print("❌ Erro no PyInstaller:")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout no PyInstaller (>5 minutos)")
            return False
        except Exception as e:
            print(f"❌ Erro ao executar PyInstaller: {e}")
            return False
    
    def create_installer_script(self):
        """Cria script básico de instalador."""
        print("📦 Criando script de instalador...")
        
        installer_script = f'''
; Script básico de instalador para Nêutrons Optimizer
; Para usar com Inno Setup

[Setup]
AppName=Nêutrons Optimizer
AppVersion=1.0.0
AppPublisher=MusashiSanS2
AppPublisherURL=https://github.com/MusashiSanS2
DefaultDirName={{pf}}\\Neutrons Optimizer
DefaultGroupName=Nêutrons Optimizer
OutputDir={self.build_dir}
OutputBaseFilename=NeutronsOptimizerSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=assets\\icon.ico

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"

[Files]
Source: "{self.dist_dir}\\NeutronsOptimizer.exe"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\Nêutrons Optimizer"; Filename: "{{app}}\\NeutronsOptimizer.exe"
Name: "{{commondesktop}}\\Nêutrons Optimizer"; Filename: "{{app}}\\NeutronsOptimizer.exe"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\NeutronsOptimizer.exe"; Description: "{{cm:LaunchProgram,Nêutrons Optimizer}}"; Flags: nowait postinstall skipifsilent
'''
        
        installer_file = self.build_dir / "installer.iss"
        with open(installer_file, 'w', encoding='utf-8') as f:
            f.write(installer_script)
        
        print(f"✅ Script de instalador criado: {installer_file}")
        return installer_file
    
    def copy_assets(self):
        """Copia assets necessários."""
        print("📁 Preparando assets...")
        
        assets_dir = self.build_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Criar ícone placeholder se não existir
        icon_file = assets_dir / "icon.ico"
        if not icon_file.exists():
            print("  ⚠️  Ícone não encontrado, criando placeholder")
            # Aqui você poderia criar um ícone básico ou copiar de outro lugar
        
        print("✅ Assets preparados")
    
    def build(self, clean=True):
        """Executa o processo completo de build."""
        print("🚀 Iniciando build do Nêutrons Optimizer")
        print("=" * 50)
        
        # Verificações
        if not self.check_dependencies():
            return False
        
        # Limpeza
        if clean:
            self.clean_build()
        
        # Preparação
        self.copy_assets()
        self.create_version_info()
        spec_file = self.create_spec_file()
        
        # Build
        if not self.run_pyinstaller(spec_file):
            return False
        
        # Pós-build
        self.create_installer_script()
        
        # Verificar resultado
        exe_file = self.dist_dir / "NeutronsOptimizer.exe"
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"✅ Build concluído com sucesso!")
            print(f"📋 Executável: {exe_file}")
            print(f"📏 Tamanho: {size_mb:.1f} MB")
            print(f"📦 Para criar instalador: use Inno Setup com {self.build_dir / 'installer.iss'}")
            return True
        else:
            print("❌ Executável não encontrado após build")
            return False


def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build do Nêutrons Optimizer")
    parser.add_argument("--no-clean", action="store_true", help="Não limpar build anterior")
    
    args = parser.parse_args()
    
    builder = BuildManager()
    
    try:
        success = builder.build(clean=not args.no_clean)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Build interrompido pelo usuário")
        return 1
    
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())