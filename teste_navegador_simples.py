#!/usr/bin/env python3
"""
Teste simples e direto do navegador
"""

import sys

print("=" * 60)
print("TESTE SIMPLES DE NAVEGADOR")
print("=" * 60)

# 1. Verificar selenium
print("\n1. Verificando Selenium...")
try:
    import selenium
    print(f"   ✅ Selenium instalado: versão {selenium.__version__}")
except ImportError:
    print("   ❌ Selenium NÃO instalado!")
    print("   Execute: pip install selenium")
    sys.exit(1)

# 2. Verificar webdriver-manager
print("\n2. Verificando webdriver-manager...")
try:
    import webdriver_manager
    print(f"   ✅ webdriver-manager instalado")
    tem_wdm = True
except ImportError:
    print("   ⚠️  webdriver-manager NÃO instalado (recomendado)")
    print("   Execute: pip install webdriver-manager")
    tem_wdm = False

# 3. Tentar iniciar Chrome
print("\n3. Tentando iniciar Chrome...")
print("   (uma janela do navegador deve abrir)")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # Configurar opções
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Tentar com webdriver-manager
    if tem_wdm:
        print("   Usando webdriver-manager...")
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
    else:
        print("   Usando ChromeDriver do sistema...")
        service = Service()

    # Iniciar navegador
    print("   Iniciando navegador...")
    driver = webdriver.Chrome(service=service, options=options)

    print("   ✅ SUCESSO! Navegador aberto!")
    print(f"   Título da página: {driver.title}")

    # Acessar site de teste
    print("\n4. Testando acesso a site...")
    driver.get("https://www.google.com")
    print(f"   ✅ Acessou Google: {driver.title}")

    # Manter aberto por 5 segundos
    print("\n   Navegador ficará aberto por 5 segundos...")
    import time
    time.sleep(5)

    # Fechar
    driver.quit()
    print("   ✅ Navegador fechado")

    print("\n" + "=" * 60)
    print("✅ TESTE BEM SUCEDIDO!")
    print("=" * 60)
    print("\nSeu sistema está configurado corretamente!")
    print("O DET Robot deve funcionar normalmente.")

except Exception as e:
    print(f"\n   ❌ ERRO: {e}")
    print("\n" + "=" * 60)
    print("SOLUÇÕES POSSÍVEIS:")
    print("=" * 60)

    import traceback
    erro_completo = traceback.format_exc()

    if "chromedriver" in str(e).lower() or "executable" in str(e).lower():
        print("\n1. ChromeDriver não encontrado. Instale webdriver-manager:")
        print("   pip install webdriver-manager")
        print("\n2. Ou baixe manualmente:")
        print("   https://chromedriver.chromium.org/downloads")

    elif "chrome not found" in str(e).lower():
        print("\n1. Google Chrome não instalado. Instale:")
        print("   Ubuntu/Debian: sudo apt install google-chrome-stable")
        print("   Ou baixe em: https://www.google.com/chrome/")

    elif "session not created" in str(e).lower():
        print("\n1. Versão do ChromeDriver incompatível com Chrome")
        print("   Solução: pip install --upgrade webdriver-manager")

    else:
        print("\nErro completo:")
        print(erro_completo)

    sys.exit(1)
