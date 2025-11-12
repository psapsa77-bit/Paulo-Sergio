#!/bin/bash
# Script para abrir a interface web do Robô FGTS Digital
# Uso: ./abrir_fgts.sh

set -e

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║        🤖 ROBÔ FGTS DIGITAL - INTERFACE WEB 🤖               ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Verificar se está no ambiente virtual
if [ -d "venv" ]; then
    echo "✓ Ativando ambiente virtual..."
    source venv/bin/activate
    echo ""
else
    echo "⚠️  Ambiente virtual não encontrado"
    echo "   Execute primeiro: ./instalar.sh"
    echo ""
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi

# Verificar Streamlit
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "❌ Streamlit não instalado!"
    echo "   Instalando agora..."
    pip install streamlit
    echo ""
fi

# Executar interface web
echo "🚀 Iniciando interface web..."
echo ""
echo "   A interface será aberta automaticamente no navegador"
echo ""
echo "💡 Para encerrar, pressione Ctrl+C"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

python3 run_fgts_web.py
