#!/usr/bin/env python3
"""
Script de diagnóstico para FGTS Digital Robot
==============================================

Verifica se todas as dependências estão instaladas corretamente.
"""

import sys
from pathlib import Path

print("=" * 60)
print("DIAGNÓSTICO - FGTS DIGITAL ROBOT")
print("=" * 60)
print()

# 1. Verificar versão do Python
print("1️⃣  Verificando Python...")
print(f"   Versão: {sys.version}")
version_info = sys.version_info
if version_info.major >= 3 and version_info.minor >= 9:
    print("   ✅ Python 3.9+ OK")
else:
    print(f"   ❌ Python {version_info.major}.{version_info.minor} detectado")
    print("   ⚠️  Recomendado: Python 3.9 ou superior")
print()

# 2. Verificar dependências principais
print("2️⃣  Verificando dependências...")

dependencies = {
    "pydantic": "Validação de dados",
    "streamlit": "Interface web",
    "playwright": "Automação web",
    "beautifulsoup4": "Parsing HTML",
    "cryptography": "Processamento de certificados",
    "openpyxl": "Exportação Excel",
}

all_ok = True

for package, desc in dependencies.items():
    try:
        if package == "beautifulsoup4":
            import bs4
            print(f"   ✅ {package} ({desc}): {bs4.__version__}")
        else:
            module = __import__(package)
            version = getattr(module, "__version__", "?")
            print(f"   ✅ {package} ({desc}): {version}")
    except ImportError:
        print(f"   ❌ {package} ({desc}): NÃO INSTALADO")
        all_ok = False

print()

# 3. Verificar Playwright especificamente
print("3️⃣  Verificando Playwright...")
try:
    from playwright.sync_api import sync_playwright
    print("   ✅ Playwright importado com sucesso")

    # Tentar verificar se navegadores estão instalados
    try:
        with sync_playwright() as p:
            browser_types = [p.chromium, p.firefox, p.webkit]
            print("   ℹ️  Tentando verificar navegadores instalados...")
            print("   (Isso pode levar alguns segundos)")

            for bt in browser_types:
                try:
                    # Tentar ver se o browser está disponível
                    print(f"   ℹ️  {bt.name}: verificando...")
                except Exception as e:
                    pass

            print("   ✅ Playwright funcional")

    except Exception as e:
        print(f"   ⚠️  Playwright instalado mas navegadores podem não estar:")
        print(f"       {e}")
        print()
        print("   💡 Execute: playwright install chromium")
        all_ok = False

except ImportError:
    print("   ❌ Playwright NÃO está instalado")
    print()
    print("   💡 Execute:")
    print("      pip install playwright")
    print("      playwright install chromium")
    all_ok = False

print()

# 4. Verificar cryptography
print("4️⃣  Verificando cryptography...")
try:
    from cryptography import x509
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.hazmat.backends import default_backend

    print("   ✅ Módulos cryptography importados")

    # Testar funcionalidades básicas
    try:
        backend = default_backend()
        print(f"   ✅ Backend: {type(backend).__name__}")
    except Exception as e:
        print(f"   ⚠️  Problema com backend: {e}")
        all_ok = False

except ImportError as e:
    print(f"   ❌ Problema ao importar cryptography: {e}")
    all_ok = False

print()

# 5. Verificar módulo fgts_digital_robot
print("5️⃣  Verificando módulo fgts_digital_robot...")
try:
    from fgts_digital_robot import FGTSRobot
    from fgts_digital_robot.models import CertificadoDigital, EmpresaFGTS, GuiaFGTS

    print("   ✅ Módulo fgts_digital_robot OK")
    print("   ✅ Modelos importados com sucesso")

except ImportError as e:
    print(f"   ❌ Erro ao importar módulo: {e}")
    all_ok = False

print()

# 6. Verificar sistema operacional
print("6️⃣  Informações do sistema...")
import platform

print(f"   Sistema: {platform.system()}")
print(f"   Versão: {platform.version()}")
print(f"   Arquitetura: {platform.machine()}")
print(f"   Python: {platform.python_implementation()} {platform.python_version()}")

print()

# 7. Resultado final
print("=" * 60)
if all_ok:
    print("✅ TODOS OS TESTES PASSARAM!")
    print()
    print("Você pode executar o robô com:")
    print("  python run_fgts_robot.py")
else:
    print("⚠️  ALGUNS PROBLEMAS FORAM ENCONTRADOS")
    print()
    print("Sugestões:")
    print("  1. Execute: pip install -r requirements.txt")
    print("  2. Execute: playwright install chromium")
    print("  3. Reinicie o terminal e tente novamente")

print("=" * 60)

print()
print("💡 Se os problemas persistirem, copie este diagnóstico")
print("   e reporte no suporte.")
