#!/usr/bin/env python3
"""
Diagnóstico SUPER detalhado do problema com navegador
"""

import sys
import os
import shutil
import platform

def linha(char="=", tamanho=60):
    print(char * tamanho)

def titulo(texto):
    print()
    linha("=")
    print(f"  {texto}")
    linha("=")

def ok(texto):
    print(f"✅ {texto}")

def erro(texto):
    print(f"❌ {texto}")

def aviso(texto):
    print(f"⚠️  {texto}")

def info(texto):
    print(f"ℹ️  {texto}")

# INÍCIO
print()
linha("*")
print("  DIAGNÓSTICO DETALHADO - PROBLEMA COM NAVEGADOR")
linha("*")

# 1. SISTEMA
titulo("1. INFORMAÇÕES DO SISTEMA")
sistema = platform.system()
versao_so = platform.version()
arquitetura = platform.machine()

print(f"Sistema Operacional: {sistema}")
print(f"Versão: {versao_so}")
print(f"Arquitetura: {arquitetura}")
print(f"Python: {sys.version}")

# 2. PYTHON E PIP
titulo("2. VERIFICANDO PYTHON E PIP")

try:
    import pip
    ok(f"pip instalado: versão {pip.__version__}")
except:
    erro("pip não encontrado!")
    print("\nInstale com: python -m ensurepip --upgrade")
    sys.exit(1)

# 3. SELENIUM
titulo("3. VERIFICANDO SELENIUM")

try:
    import selenium
    ok(f"Selenium instalado: versão {selenium.__version__}")

    # Verificar módulos específicos
    try:
        from selenium import webdriver
        ok("  - webdriver importado")
    except Exception as e:
        erro(f"  - Erro ao importar webdriver: {e}")

    try:
        from selenium.webdriver.chrome.service import Service
        ok("  - Chrome Service importado")
    except Exception as e:
        erro(f"  - Erro ao importar Chrome Service: {e}")

    try:
        from selenium.webdriver.chrome.options import Options
        ok("  - Chrome Options importado")
    except Exception as e:
        erro(f"  - Erro ao importar Chrome Options: {e}")

except ImportError:
    erro("Selenium NÃO instalado!")
    print("\nINSTALE COM:")
    print("  pip install selenium")
    sys.exit(1)

# 4. WEBDRIVER-MANAGER
titulo("4. VERIFICANDO WEBDRIVER-MANAGER")

try:
    import webdriver_manager
    ok(f"webdriver-manager instalado")

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        ok("  - ChromeDriverManager disponível")
    except Exception as e:
        erro(f"  - Erro ao importar ChromeDriverManager: {e}")

except ImportError:
    aviso("webdriver-manager NÃO instalado (recomendado)")
    print("\nINSTALE COM:")
    print("  pip install webdriver-manager")

# 5. NAVEGADORES
titulo("5. PROCURANDO NAVEGADORES NO SISTEMA")

navegadores_encontrados = []

# Comandos comuns de navegadores
comandos = {
    "Google Chrome": ["google-chrome", "google-chrome-stable", "chrome"],
    "Chromium": ["chromium-browser", "chromium"],
    "Firefox": ["firefox", "firefox-esr"],
}

print("\nProcurando no PATH:")
for nome, cmds in comandos.items():
    encontrado = False
    for cmd in cmds:
        caminho = shutil.which(cmd)
        if caminho:
            ok(f"{nome}: {caminho}")
            navegadores_encontrados.append((nome, caminho))
            encontrado = True

            # Tentar obter versão
            try:
                import subprocess
                if "chrome" in cmd or "chromium" in cmd:
                    version_cmd = [caminho, "--version"]
                elif "firefox" in cmd:
                    version_cmd = [caminho, "--version"]

                result = subprocess.run(version_cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"   Versão: {result.stdout.strip()}")
            except:
                pass

            break

    if not encontrado:
        erro(f"{nome}: não encontrado")

# Caminhos específicos por sistema
if sistema == "Windows":
    print("\nProcurando em locais padrão do Windows:")
    caminhos_windows = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ]

    for caminho in caminhos_windows:
        if os.path.exists(caminho):
            ok(f"Encontrado: {caminho}")
            navegadores_encontrados.append(("Chrome/Firefox", caminho))

if not navegadores_encontrados:
    erro("NENHUM NAVEGADOR ENCONTRADO!")
    print("\nINSTALE UM NAVEGADOR:")
    print("  - Google Chrome: https://www.google.com/chrome/")
    print("  - Firefox: https://www.mozilla.org/firefox/")
    sys.exit(1)

# 6. CHROMEDRIVER
titulo("6. VERIFICANDO CHROMEDRIVER")

chromedriver_path = shutil.which("chromedriver")
if chromedriver_path:
    ok(f"ChromeDriver encontrado: {chromedriver_path}")

    # Verificar versão
    try:
        import subprocess
        result = subprocess.run([chromedriver_path, "--version"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   Versão: {result.stdout.strip()}")
    except:
        pass
else:
    aviso("ChromeDriver não encontrado no PATH")
    print("   O webdriver-manager vai baixar automaticamente")

# 7. TESTE REAL DO NAVEGADOR
titulo("7. TESTE REAL - INICIANDO NAVEGADOR")

print("\nTentando iniciar Chrome com Selenium...")
print("(Uma janela do navegador deve abrir)")
print()

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # Configurar opções
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    print("Passo 1: Configurações criadas")

    # Tentar com webdriver-manager
    driver = None
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("Passo 2: Usando webdriver-manager...")
        service = Service(ChromeDriverManager().install())
        print("Passo 3: ChromeDriver instalado/verificado")
    except ImportError:
        print("Passo 2: webdriver-manager não disponível")
        print("Passo 3: Usando ChromeDriver do sistema...")
        service = Service()

    print("Passo 4: Iniciando navegador...")
    driver = webdriver.Chrome(service=service, options=options)

    ok("NAVEGADOR INICIADO COM SUCESSO!")

    print("\nTestando acesso a site...")
    driver.get("https://www.google.com")
    print(f"Título da página: {driver.title}")

    ok("TESTE COMPLETO BEM SUCEDIDO!")

    print("\nNavegador ficará aberto por 3 segundos...")
    import time
    time.sleep(3)

    driver.quit()
    ok("Navegador fechado")

    # SUCESSO TOTAL
    print()
    linha("*")
    print()
    print("  ✅✅✅ TUDO FUNCIONANDO PERFEITAMENTE! ✅✅✅")
    print()
    linha("*")
    print()
    print("O DET Robot deve funcionar sem problemas.")
    print("Se ainda assim não funcionar, o problema pode estar em:")
    print("  1. Permissões de firewall/antivírus")
    print("  2. Proxy ou VPN")
    print("  3. Configurações específicas do DET Robot")
    print()

except Exception as e:
    erro("FALHA AO INICIAR NAVEGADOR!")
    print()
    print(f"Erro: {type(e).__name__}")
    print(f"Mensagem: {str(e)}")
    print()

    # DIAGNÓSTICO DO ERRO
    linha("=")
    print("  DIAGNÓSTICO DO ERRO")
    linha("=")

    erro_str = str(e).lower()

    if "chromedriver" in erro_str or "executable" in erro_str:
        print()
        print("❌ PROBLEMA: ChromeDriver não encontrado ou incompatível")
        print()
        print("SOLUÇÃO 1 - Instalar webdriver-manager (RECOMENDADO):")
        print("  pip install webdriver-manager")
        print()
        print("SOLUÇÃO 2 - Baixar ChromeDriver manualmente:")
        print("  1. Veja a versão do Chrome:")
        if sistema == "Windows":
            print("     chrome.exe --version")
        else:
            print("     google-chrome --version")
        print("  2. Baixe o ChromeDriver compatível em:")
        print("     https://chromedriver.chromium.org/downloads")
        print("  3. Coloque no PATH do sistema")

    elif "chrome not found" in erro_str or "no such file" in erro_str:
        print()
        print("❌ PROBLEMA: Google Chrome não instalado")
        print()
        print("SOLUÇÃO - Instalar Google Chrome:")
        print("  https://www.google.com/chrome/")

    elif "session not created" in erro_str:
        print()
        print("❌ PROBLEMA: Versão incompatível Chrome/ChromeDriver")
        print()
        print("SOLUÇÃO:")
        print("  pip install --upgrade webdriver-manager")
        print("  python -c \"from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()\"")

    elif "permission" in erro_str:
        print()
        print("❌ PROBLEMA: Erro de permissão")
        print()
        print("SOLUÇÃO:")
        if sistema == "Windows":
            print("  Execute o script como Administrador")
        else:
            print("  chmod +x /caminho/para/chromedriver")
            print("  Ou execute com: sudo python3 este_script.py")

    else:
        print()
        print("❌ PROBLEMA: Erro desconhecido")
        print()
        print("SOLUÇÕES GERAIS:")
        print("  1. Reinstalar Selenium:")
        print("     pip uninstall selenium -y")
        print("     pip install selenium")
        print()
        print("  2. Limpar cache do webdriver-manager:")
        if sistema == "Windows":
            print("     rmdir /s /q %USERPROFILE%\\.wdm")
        else:
            print("     rm -rf ~/.wdm/")
        print()
        print("  3. Tentar com Firefox:")
        print("     pip install webdriver-manager")
        print("     (O código tentará Firefox automaticamente)")

    # Stack trace completo
    print()
    linha("-")
    print("Stack Trace Completo:")
    linha("-")
    import traceback
    traceback.print_exc()

    if driver:
        try:
            driver.quit()
        except:
            pass

    sys.exit(1)

# FIM
print()
linha("*")
print("  DIAGNÓSTICO CONCLUÍDO")
linha("*")
print()
