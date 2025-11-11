#!/usr/bin/env python3
"""
Instalador Automático - FGTS Digital Robot
==========================================

Execute este script e ele vai instalar tudo automaticamente!

Duplo clique ou execute: python instalar_playwright.py
"""

import subprocess
import sys
import os

def print_separador():
    print("=" * 70)

def executar_comando(comando, descricao):
    """Executa um comando e mostra o progresso"""
    print(f"\n🔄 {descricao}...")
    print(f"   Executando: {comando}")
    print()

    try:
        if isinstance(comando, list):
            resultado = subprocess.run(comando, check=True, capture_output=False)
        else:
            resultado = subprocess.run(comando, shell=True, check=True, capture_output=False)

        print(f"✅ {descricao} - CONCLUÍDO!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao {descricao.lower()}")
        print(f"   Código de erro: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def main():
    print_separador()
    print("   INSTALADOR AUTOMÁTICO - FGTS DIGITAL ROBOT")
    print_separador()
    print()
    print("Este script vai instalar:")
    print("  1. Playwright (biblioteca de automação)")
    print("  2. Navegador Chromium")
    print("  3. Todas as dependências necessárias")
    print()
    print("Isso pode levar alguns minutos...")
    print()

    input("Pressione ENTER para começar...")
    print()

    # Passo 1: Atualizar pip
    print_separador()
    print("PASSO 1 - Atualizando pip")
    print_separador()

    executar_comando(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "Atualizando pip"
    )

    # Passo 2: Instalar todas as dependências
    print()
    print_separador()
    print("PASSO 2 - Instalando dependências do projeto")
    print_separador()

    executar_comando(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Instalando dependências"
    )

    # Passo 3: Instalar Playwright especificamente
    print()
    print_separador()
    print("PASSO 3 - Instalando Playwright")
    print_separador()

    sucesso_playwright = executar_comando(
        [sys.executable, "-m", "pip", "install", "playwright>=1.46.0"],
        "Instalando Playwright"
    )

    if not sucesso_playwright:
        print()
        print("⚠️  Houve um problema ao instalar o Playwright")
        print("   Tentando método alternativo...")
        executar_comando(
            [sys.executable, "-m", "pip", "install", "playwright", "--force-reinstall"],
            "Reinstalando Playwright"
        )

    # Passo 4: Instalar navegador Chromium
    print()
    print_separador()
    print("PASSO 4 - Baixando navegador Chromium")
    print_separador()
    print()
    print("⚠️  Este passo pode demorar alguns minutos (download de ~200 MB)")
    print()

    sucesso_chromium = executar_comando(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        "Instalando Chromium"
    )

    if not sucesso_chromium:
        print()
        print("⚠️  Tentando método alternativo...")
        executar_comando(
            "playwright install chromium",
            "Instalando Chromium (método 2)"
        )

    # Passo 5 (Linux): Instalar dependências do sistema
    if sys.platform.startswith('linux'):
        print()
        print_separador()
        print("PASSO 5 - Instalando dependências do sistema (Linux)")
        print_separador()

        executar_comando(
            [sys.executable, "-m", "playwright", "install-deps", "chromium"],
            "Instalando dependências do Linux"
        )

    # Verificação final
    print()
    print_separador()
    print("VERIFICAÇÃO FINAL")
    print_separador()
    print()

    print("🔍 Testando instalação...")
    print()

    # Testar Playwright
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright: INSTALADO")
    except ImportError:
        print("❌ Playwright: NÃO INSTALADO")

    # Testar outras dependências
    try:
        import streamlit
        print("✅ Streamlit: INSTALADO")
    except ImportError:
        print("❌ Streamlit: NÃO INSTALADO")

    try:
        from cryptography import x509
        print("✅ Cryptography: INSTALADO")
    except ImportError:
        print("❌ Cryptography: NÃO INSTALADO")

    try:
        from fgts_digital_robot import FGTSRobot
        print("✅ FGTS Digital Robot: INSTALADO")
    except ImportError:
        print("❌ FGTS Digital Robot: NÃO INSTALADO")

    # Resultado final
    print()
    print_separador()
    print("INSTALAÇÃO CONCLUÍDA!")
    print_separador()
    print()
    print("✨ Próximos passos:")
    print()
    print("1. Execute o programa:")
    print("   python run_fgts_robot.py")
    print()
    print("2. Abra seu navegador em:")
    print("   http://localhost:8502")
    print()
    print("3. Faça upload do seu certificado digital")
    print()
    print_separador()
    print()

    input("Pressione ENTER para sair...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("⚠️  Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Erro inesperado: {e}")
        print()
        input("Pressione ENTER para sair...")
        sys.exit(1)
