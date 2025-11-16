#!/bin/bash
# Script para abrir o DET Robot no Linux/Mac

echo "================================================"
echo "  DET Robot - Extrator do DET"
echo "================================================"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não encontrado!"
    echo "Instale o Python 3.9 ou superior."
    exit 1
fi

# Ir para o diretório do script
cd "$(dirname "$0")"

# Verificar se as dependências estão instaladas
echo "Verificando dependências..."
python3 -c "import selenium" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependências do DET Robot..."
    pip3 install selenium webdriver-manager
fi

# Verificar navegador
echo "Verificando navegador disponível..."
if command -v google-chrome &> /dev/null; then
    echo "✓ Google Chrome encontrado"
elif command -v chromium-browser &> /dev/null; then
    echo "✓ Chromium encontrado"
elif command -v firefox &> /dev/null; then
    echo "✓ Firefox encontrado"
else
    echo "AVISO: Nenhum navegador suportado encontrado!"
    echo "Instale Google Chrome, Chromium ou Firefox."
fi

echo ""
echo "Iniciando DET Robot..."
echo "================================================"

# Executar
python3 run_det_robot.py
