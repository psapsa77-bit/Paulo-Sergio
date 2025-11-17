#!/bin/bash
# Script super simples para usar o DET Robot

clear

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║                    DET ROBOT                             ║"
echo "║       Extrator de Mensagens do DET                       ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Ir para o diretório do script
cd "$(dirname "$0")"

# Verificar se está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python não encontrado!"
    echo ""
    echo "Execute primeiro: ./INSTALAR_TUDO.sh"
    echo ""
    exit 1
fi

# Verificar se selenium está instalado
python3 -c "import selenium" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ DET Robot não está instalado!"
    echo ""
    echo "Execute primeiro: ./INSTALAR_TUDO.sh"
    echo ""
    exit 1
fi

echo "Iniciando DET Robot..."
echo ""
echo "Uma página web será aberta no seu navegador."
echo "Acesse: http://localhost:8502"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Executar
python3 run_det_robot.py
