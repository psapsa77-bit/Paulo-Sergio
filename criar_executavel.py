"""
Script para criar executável (.exe) do FGTS Digital Robot
=========================================================

Este script cria um arquivo .exe que pode ser executado sem precisar
instalar Python ou qualquer dependência.

Uso:
    python criar_executavel.py

Ou simplesmente duplo clique neste arquivo!
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(texto):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {texto}")
    print("=" * 70 + "\n")

def executar_comando(comando, descricao):
    """Executa comando e mostra progresso"""
    print(f"🔄 {descricao}...")
    print(f"   Executando: {' '.join(comando) if isinstance(comando, list) else comando}")
    print()

    try:
        resultado = subprocess.run(
            comando,
            check=True,
            shell=isinstance(comando, str),
            capture_output=False
        )
        print(f"✅ {descricao} - CONCLUÍDO!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao {descricao.lower()}")
        print(f"   Código: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    print_header("CRIADOR DE EXECUTÁVEL - FGTS DIGITAL ROBOT")

    print("Este script vai criar um arquivo .exe que:")
    print("  ✅ Não precisa de Python instalado")
    print("  ✅ Inclui todas as dependências")
    print("  ✅ Pode ser distribuído para outras pessoas")
    print("  ✅ Funciona com duplo clique")
    print()
    print("⚠️  ATENÇÃO:")
    print("  - O arquivo .exe será grande (~300-500 MB)")
    print("  - A criação pode demorar 10-20 minutos")
    print("  - Você precisa ter Python instalado agora (só desta vez)")
    print()

    input("Pressione ENTER para começar...")

    # Passo 1: Instalar PyInstaller
    print_header("PASSO 1 - Instalando PyInstaller")

    if not executar_comando(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        "Instalando PyInstaller"
    ):
        print("\n❌ Falha ao instalar PyInstaller")
        input("Pressione ENTER para sair...")
        return

    # Passo 2: Instalar auto-py-to-exe (interface gráfica)
    print_header("PASSO 2 - Instalando auto-py-to-exe")

    executar_comando(
        [sys.executable, "-m", "pip", "install", "auto-py-to-exe"],
        "Instalando auto-py-to-exe"
    )

    # Passo 3: Criar arquivo de configuração
    print_header("PASSO 3 - Criando configuração")

    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_fgts_robot.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('fgts_digital_robot', 'fgts_digital_robot'),
        ('labor_termination_analyzer', 'labor_termination_analyzer'),
    ],
    hiddenimports=[
        'streamlit',
        'playwright',
        'playwright.sync_api',
        'cryptography',
        'pydantic',
        'beautifulsoup4',
        'openpyxl',
        'plotly',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='FGTS_Digital_Robot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""

    with open("fgts_robot.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("✅ Arquivo de configuração criado: fgts_robot.spec")

    # Passo 4: Opções
    print_header("ESCOLHA O MÉTODO")

    print("Você tem 2 opções para criar o executável:")
    print()
    print("A) INTERFACE GRÁFICA (Recomendado para iniciantes)")
    print("   - Mais fácil de usar")
    print("   - Interface visual")
    print("   - Configuração com cliques")
    print()
    print("B) LINHA DE COMANDO (Automático)")
    print("   - Mais rápido")
    print("   - Totalmente automático")
    print("   - Usa configuração pronta")
    print()

    escolha = input("Digite A ou B: ").strip().upper()

    if escolha == "A":
        print()
        print_header("ABRINDO INTERFACE GRÁFICA")
        print()
        print("📋 INSTRUÇÕES:")
        print()
        print("1. Na janela que vai abrir:")
        print("   - Script Location: Selecione 'run_fgts_robot.py'")
        print("   - One File: Marque esta opção")
        print("   - Console Window: Marque esta opção")
        print()
        print("2. Clique em 'CONVERT .PY TO .EXE'")
        print()
        print("3. Aguarde a conversão (10-20 minutos)")
        print()
        print("4. O .exe estará na pasta 'output'")
        print()
        input("Pressione ENTER para abrir a interface...")

        executar_comando(
            [sys.executable, "-m", "auto_py_to_exe"],
            "Abrindo auto-py-to-exe"
        )

    else:
        print()
        print_header("CRIANDO EXECUTÁVEL AUTOMATICAMENTE")
        print()
        print("⏳ Isso vai demorar 10-20 minutos...")
        print("⏳ Não feche esta janela!")
        print()

        if executar_comando(
            ["pyinstaller", "fgts_robot.spec", "--clean"],
            "Compilando executável"
        ):
            print()
            print_header("✅ EXECUTÁVEL CRIADO COM SUCESSO!")
            print()
            print("📂 O arquivo .exe está em:")
            print(f"   {os.path.abspath('dist/FGTS_Digital_Robot.exe')}")
            print()
            print("📦 Tamanho aproximado: 300-500 MB")
            print()
            print("🎯 Como usar:")
            print("   1. Copie o arquivo FGTS_Digital_Robot.exe")
            print("   2. Cole em qualquer computador Windows")
            print("   3. Duplo clique para executar")
            print("   4. Abrirá no navegador automaticamente")
            print()
            print("⚠️  IMPORTANTE:")
            print("   - Na primeira execução, pode demorar mais")
            print("   - O Windows Defender pode alertar (é normal)")
            print("   - Clique em 'Mais informações' > 'Executar assim mesmo'")
            print()
        else:
            print()
            print("❌ Falha ao criar executável")
            print()
            print("💡 Tente usar a OPÇÃO A (Interface Gráfica)")

    print()
    print_header("PROCESSO CONCLUÍDO")
    print()
    input("Pressione ENTER para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        input("Pressione ENTER para sair...")
        sys.exit(1)
