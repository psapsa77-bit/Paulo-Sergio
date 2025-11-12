#!/usr/bin/env python3
"""
Script de teste para verificar se os imports estão funcionando corretamente
"""
import sys
from pathlib import Path

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

print("📋 Testando imports do Robô FGTS...")
print()

# Teste 1: Import do config
print("1. Testando import do config...")
try:
    import config
    print("   ✓ config importado com sucesso")
    print(f"   - BASE_DIR: {config.BASE_DIR}")
except ImportError as e:
    print(f"   ✗ Erro ao importar config: {e}")

print()

# Teste 2: Import do __init__
print("2. Testando import do __init__...")
try:
    import __init__
    print("   ✓ __init__ importado com sucesso")
except ImportError as e:
    print(f"   ✗ Erro ao importar __init__: {e}")

print()

# Teste 3: Verificar estrutura de arquivos
print("3. Verificando estrutura de arquivos...")
arquivos_necessarios = [
    'config.py',
    'robo_fgts.py',
    'main.py',
    '__init__.py',
    'requirements.txt',
    '.env.example',
    'README.md'
]

for arquivo in arquivos_necessarios:
    caminho = Path(__file__).parent / arquivo
    if caminho.exists():
        print(f"   ✓ {arquivo}")
    else:
        print(f"   ✗ {arquivo} não encontrado")

print()

# Teste 4: Verificar diretórios
print("4. Verificando diretórios...")
diretorios = [
    'certificados',
    'resultados',
    'logs',
    'logs/screenshots'
]

for diretorio in diretorios:
    caminho = Path(__file__).parent / diretorio
    if caminho.exists() and caminho.is_dir():
        print(f"   ✓ {diretorio}/")
    else:
        print(f"   ✗ {diretorio}/ não encontrado")

print()
print("=" * 60)
print("✅ Verificação de estrutura concluída!")
print()
print("⚠️  Nota: Para executar o robô, instale as dependências:")
print("   pip install -r requirements.txt")
print("   playwright install chromium")
