#!/bin/bash
# Script de instalação do FGTS Digital Robot
# Sistema: Linux/Mac

set -e

echo "🤖 Instalação do FGTS Digital Robot"
echo "===================================="
echo ""

# Verificar Python
echo "📌 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "   Instale Python 3.9+ e tente novamente"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "   ✅ Python $PYTHON_VERSION encontrado"
echo ""

# Verificar pip
echo "📌 Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip não encontrado!"
    exit 1
fi
echo "   ✅ pip encontrado"
echo ""

# Criar ambiente virtual (opcional)
read -p "Criar ambiente virtual? (s/n): " criar_venv

if [ "$criar_venv" = "s" ] || [ "$criar_venv" = "S" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "   ✅ Ambiente virtual criado e ativado"
fi
echo ""

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✅ Dependências instaladas"
echo ""

# Instalar Playwright
echo "🎭 Instalando navegadores do Playwright..."
playwright install chromium
echo "   ✅ Chromium instalado"
echo ""

# Instalar dependências do sistema (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Instalando dependências do sistema..."
    read -p "Instalar dependências do sistema? (requer sudo) (s/n): " instalar_deps

    if [ "$instalar_deps" = "s" ] || [ "$instalar_deps" = "S" ]; then
        playwright install-deps chromium
        echo "   ✅ Dependências do sistema instaladas"
    fi
fi
echo ""

# Verificar instalação
echo "✅ Verificando instalação..."
python3 -c "from fgts_digital_robot import FGTSRobot; print('   ✅ FGTS Robot instalado com sucesso!')"
echo ""

# Instruções finais
echo "🎉 Instalação concluída!"
echo ""
echo "📖 Próximos passos:"
echo ""
echo "1. Execute a interface web:"
echo "   python3 run_fgts_robot.py"
echo ""
echo "2. Ou use via Python:"
echo "   python3 exemplo_fgts_robot.py"
echo ""
echo "3. Leia a documentação:"
echo "   cat README_FGTS_ROBOT.md"
echo ""

if [ "$criar_venv" = "s" ] || [ "$criar_venv" = "S" ]; then
    echo "⚠️  Lembre-se de ativar o ambiente virtual antes de usar:"
    echo "   source venv/bin/activate"
    echo ""
fi

echo "✨ Bom uso!"
