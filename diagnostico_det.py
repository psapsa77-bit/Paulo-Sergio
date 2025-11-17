#!/usr/bin/env python3
"""
Script de diagnóstico para o DET Robot
Identifica problemas comuns e testa componentes
"""

import sys
import subprocess
import shutil
from pathlib import Path


def verificar_python():
    """Verifica versão do Python"""
    print("=" * 60)
    print("1. VERIFICANDO PYTHON")
    print("=" * 60)

    version = sys.version_info
    print(f"Versão: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ ERRO: Python 3.9+ é necessário")
        return False
    else:
        print("✅ Versão do Python OK")
        return True


def verificar_navegadores():
    """Verifica se há navegadores instalados"""
    print("\n" + "=" * 60)
    print("2. VERIFICANDO NAVEGADORES")
    print("=" * 60)

    navegadores = {
        "Google Chrome": ["google-chrome", "google-chrome-stable", "chrome"],
        "Chromium": ["chromium-browser", "chromium"],
        "Firefox": ["firefox", "firefox-esr"],
    }

    encontrados = []

    for nome, comandos in navegadores.items():
        for cmd in comandos:
            caminho = shutil.which(cmd)
            if caminho:
                print(f"✅ {nome} encontrado em: {caminho}")
                encontrados.append((nome, caminho))
                break

    if not encontrados:
        print("❌ ERRO: Nenhum navegador suportado encontrado!")
        print("\nInstale um dos seguintes:")
        print("  - Google Chrome: https://www.google.com/chrome/")
        print("  - Chromium: sudo apt install chromium-browser")
        print("  - Firefox: sudo apt install firefox")
        return False

    return True


def verificar_dependencias():
    """Verifica se as dependências Python estão instaladas"""
    print("\n" + "=" * 60)
    print("3. VERIFICANDO DEPENDÊNCIAS PYTHON")
    print("=" * 60)

    deps_criticas = {
        "selenium": "Automação web",
        "pydantic": "Validação de dados",
    }

    deps_opcionais = {
        "webdriver_manager": "Gerenciador de drivers",
        "streamlit": "Interface web",
        "typer": "Interface CLI",
        "rich": "Formatação terminal",
    }

    todas_ok = True

    print("\nDependências críticas:")
    for modulo, desc in deps_criticas.items():
        try:
            __import__(modulo)
            print(f"  ✅ {modulo} - {desc}")
        except ImportError:
            print(f"  ❌ {modulo} - {desc} - NÃO INSTALADO")
            todas_ok = False

    print("\nDependências opcionais:")
    for modulo, desc in deps_opcionais.items():
        try:
            __import__(modulo)
            print(f"  ✅ {modulo} - {desc}")
        except ImportError:
            print(f"  ⚠️  {modulo} - {desc} - NÃO INSTALADO")

    if not todas_ok:
        print("\n❌ Instale as dependências com:")
        print("   pip install -r requirements.txt")
        return False

    return True


def testar_selenium():
    """Testa se o Selenium consegue iniciar um navegador"""
    print("\n" + "=" * 60)
    print("4. TESTANDO SELENIUM")
    print("=" * 60)

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.chrome.options import Options as ChromeOptions

        print("Tentando iniciar Chrome com Selenium...")

        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # Tentar com webdriver-manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("Usando webdriver-manager para baixar ChromeDriver...")
            service = ChromeService(ChromeDriverManager().install())
        except ImportError:
            print("webdriver-manager não disponível, usando ChromeDriver do sistema...")
            service = ChromeService()

        print("Iniciando navegador...")
        driver = webdriver.Chrome(service=service, options=options)

        print("✅ Navegador iniciado com sucesso!")
        print(f"   Título: {driver.title}")

        driver.quit()
        print("✅ Navegador fechado corretamente")

        return True

    except Exception as e:
        print(f"❌ ERRO ao testar Selenium: {e}")
        print("\nPossíveis soluções:")
        print("1. Instale webdriver-manager:")
        print("   pip install webdriver-manager")
        print("2. Ou baixe ChromeDriver manualmente:")
        print("   https://chromedriver.chromium.org/")
        return False


def testar_modulo_det():
    """Testa se o módulo det_robot pode ser importado"""
    print("\n" + "=" * 60)
    print("5. TESTANDO MÓDULO DET_ROBOT")
    print("=" * 60)

    try:
        from det_robot import BrowserManager, DETAuthenticator, DETScraper
        print("✅ Módulos importados com sucesso")

        # Testar BrowserManager
        print("\nTestando BrowserManager...")
        browser = BrowserManager(navegador="auto", headless=True, log_callback=print)
        print("✅ BrowserManager criado")

        print("\nIniciando navegador em modo headless...")
        browser.iniciar()
        print("✅ Navegador iniciado!")

        print("Acessando DET...")
        browser.acessar_det()
        print("✅ Site DET acessado!")

        print("Fechando navegador...")
        browser.fechar()
        print("✅ Navegador fechado!")

        return True

    except ImportError as e:
        print(f"❌ ERRO ao importar módulo: {e}")
        print("\nVerifique se a pasta det_robot/ está presente")
        return False
    except Exception as e:
        print(f"❌ ERRO ao testar módulo: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "DET ROBOT - DIAGNÓSTICO" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    testes = [
        verificar_python,
        verificar_navegadores,
        verificar_dependencias,
        testar_selenium,
        testar_modulo_det,
    ]

    resultados = []

    for teste in testes:
        try:
            resultado = teste()
            resultados.append(resultado)
            if not resultado:
                print(f"\n⚠️  Teste falhou. Corrija antes de continuar.\n")
                break
        except KeyboardInterrupt:
            print("\n\nDiagnóstico cancelado pelo usuário.")
            return 1
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            import traceback
            traceback.print_exc()
            resultados.append(False)
            break

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)

    if all(resultados):
        print("✅ Todos os testes passaram!")
        print("\nO DET Robot está pronto para uso!")
        print("\nPara usar:")
        print("  Interface Web:  python run_det_robot.py")
        print("  CLI:            python -m det_robot.cli extrair --manual")
        return 0
    else:
        print("❌ Alguns testes falharam.")
        print("\nSiga as instruções acima para corrigir os problemas.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
