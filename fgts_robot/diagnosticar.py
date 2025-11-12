#!/usr/bin/env python3
"""
Script de diagnóstico do Robô FGTS Digital

Verifica todas as dependências, configurações e possíveis problemas.
"""
import sys
from pathlib import Path

print("╔═══════════════════════════════════════════════════════════════╗")
print("║                                                               ║")
print("║        🔍 DIAGNÓSTICO DO ROBÔ FGTS DIGITAL 🔍                ║")
print("║                                                               ║")
print("╚═══════════════════════════════════════════════════════════════╝")
print()

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

erros = []
avisos = []

# Teste 1: Verificar Python
print("📌 Teste 1: Versão do Python")
print(f"   Versão: {sys.version}")
version_info = sys.version_info
if version_info.major >= 3 and version_info.minor >= 10:
    print("   ✓ Python 3.10+ OK")
else:
    erro = f"   ❌ Python 3.10+ necessário (você tem {version_info.major}.{version_info.minor})"
    print(erro)
    erros.append(erro)
print()

# Teste 2: Verificar módulos Python
print("📌 Teste 2: Dependências Python")

modulos = {
    "playwright": "Automação web",
    "pandas": "Manipulação de dados",
    "openpyxl": "Geração de Excel",
    "cryptography": "Certificados digitais",
    "dotenv": "Variáveis de ambiente (python-dotenv)",
    "streamlit": "Interface web"
}

for modulo, descricao in modulos.items():
    try:
        if modulo == "dotenv":
            __import__("dotenv")
        else:
            __import__(modulo)
        print(f"   ✓ {modulo:15s} - {descricao}")
    except ImportError:
        erro = f"   ❌ {modulo:15s} - NÃO INSTALADO ({descricao})"
        print(erro)
        erros.append(f"{modulo} não instalado")
print()

# Teste 3: Verificar arquivos de configuração
print("📌 Teste 3: Arquivos de Configuração")

try:
    import config
    print(f"   ✓ config.py carregado")
    print(f"   - URL Portal: {config.FGTS_URL_LOGIN}")
    print(f"   - Timeout: {config.BROWSER_TIMEOUT}ms")
    print(f"   - Headless: {config.HEADLESS}")
except Exception as e:
    erro = f"   ❌ Erro ao carregar config.py: {str(e)}"
    print(erro)
    erros.append("config.py com erro")
print()

# Teste 4: Verificar certificado
print("📌 Teste 4: Certificado Digital")

try:
    from pathlib import Path
    import config

    cert_path = Path(config.CERT_PATH)
    print(f"   Caminho configurado: {cert_path}")

    if cert_path.exists():
        tamanho = cert_path.stat().st_size
        print(f"   ✓ Certificado encontrado ({tamanho} bytes)")

        if tamanho < 100:
            aviso = "   ⚠ Arquivo muito pequeno - pode não ser um certificado válido"
            print(aviso)
            avisos.append("Certificado muito pequeno")
    else:
        erro = "   ❌ Certificado NÃO encontrado"
        print(erro)
        erros.append("Certificado não encontrado")

    if config.CERT_PASSWORD:
        print(f"   ✓ Senha configurada ({len(config.CERT_PASSWORD)} caracteres)")
    else:
        aviso = "   ⚠ Senha NÃO configurada no .env"
        print(aviso)
        avisos.append("Senha não configurada")

except Exception as e:
    erro = f"   ❌ Erro ao verificar certificado: {str(e)}"
    print(erro)
    erros.append(f"Erro verificando certificado: {str(e)}")
print()

# Teste 5: Verificar diretórios
print("📌 Teste 5: Estrutura de Diretórios")

try:
    import config

    diretorios = [
        ("Certificados", config.CERT_DIR),
        ("Resultados", config.RESULTS_DIR),
        ("Logs", config.LOGS_DIR),
        ("Screenshots", config.SCREENSHOT_DIR)
    ]

    for nome, caminho in diretorios:
        if caminho.exists():
            print(f"   ✓ {nome:15s} - {caminho}")
        else:
            aviso = f"   ⚠ {nome:15s} - NÃO EXISTE (será criado automaticamente)"
            print(aviso)

except Exception as e:
    erro = f"   ❌ Erro ao verificar diretórios: {str(e)}"
    print(erro)
    erros.append(f"Erro verificando diretórios: {str(e)}")
print()

# Teste 6: Verificar Playwright
print("📌 Teste 6: Playwright (Navegador)")

try:
    from playwright.sync_api import sync_playwright

    print("   ✓ Playwright instalado")

    # Verificar se browser está instalado
    try:
        with sync_playwright() as p:
            browser_type = p.chromium
            # Apenas verificar se consegue obter informações do browser
            print("   ✓ Chromium disponível")
    except Exception as e:
        erro = "   ❌ Chromium NÃO instalado"
        print(erro)
        print("   Execute: playwright install chromium")
        erros.append("Chromium não instalado")

except ImportError:
    erro = "   ❌ Playwright não instalado"
    print(erro)
    print("   Execute: pip install playwright")
    erros.append("Playwright não instalado")
except Exception as e:
    aviso = f"   ⚠ Erro ao verificar Playwright: {str(e)}"
    print(aviso)
    avisos.append(f"Erro verificando Playwright: {str(e)}")
print()

# Teste 7: Testar importação do robô
print("📌 Teste 7: Importação do Robô")

try:
    from robo_fgts import RoboFGTS
    print("   ✓ RoboFGTS importado com sucesso")

    # Tentar criar instância
    try:
        robo = RoboFGTS()
        print("   ✓ Instância do robô criada com sucesso")
    except Exception as e:
        erro = f"   ❌ Erro ao criar instância: {str(e)}"
        print(erro)
        erros.append(f"Erro criando instância: {str(e)}")

except ImportError as e:
    erro = f"   ❌ Erro ao importar RoboFGTS: {str(e)}"
    print(erro)
    erros.append(f"Erro importando RoboFGTS: {str(e)}")
except Exception as e:
    erro = f"   ❌ Erro inesperado: {str(e)}"
    print(erro)
    erros.append(f"Erro inesperado: {str(e)}")
print()

# Resumo
print("="*70)
print()

if not erros and not avisos:
    print("✅ TODOS OS TESTES PASSARAM!")
    print()
    print("Seu ambiente está configurado corretamente.")
    print()
    print("Próximos passos:")
    print("  1. Teste a conexão: python testar_conexao.py")
    print("  2. Execute o robô: python main.py --help")
    print("  3. Ou abra a interface web: ABRIR_FGTS.bat (Windows) ou ./abrir_fgts.sh (Linux/macOS)")

elif erros:
    print(f"❌ ENCONTRADOS {len(erros)} ERRO(S) CRÍTICO(S):")
    print()
    for i, erro in enumerate(erros, 1):
        print(f"  {i}. {erro}")
    print()
    print("Soluções:")
    print()
    if "não instalado" in str(erros):
        print("  📦 Instalar dependências:")
        print("     pip install -r requirements.txt")
        print("     playwright install chromium")
        print()
    if "Certificado não encontrado" in str(erros):
        print("  📜 Adicionar certificado:")
        print("     cp /caminho/do/certificado.pfx certificados/")
        print("     Ou: configure CERT_PATH no .env")
        print()

elif avisos:
    print(f"⚠️  ENCONTRADOS {len(avisos)} AVISO(S):")
    print()
    for i, aviso in enumerate(avisos, 1):
        print(f"  {i}. {aviso}")
    print()
    print("O robô pode funcionar, mas verifique os avisos acima.")

print()
print("="*70)
print()
print("Para mais informações, consulte:")
print("  - README.md")
print("  - QUICKSTART.md")
print("  - TROUBLESHOOTING.md")
print()
