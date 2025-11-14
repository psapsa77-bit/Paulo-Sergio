#!/bin/bash
# Script para abrir o Robô DET no Linux/Mac
# Autor: Paulo Sergio

echo "===================================================================="
echo "       ROBÔ DET - VERIFICADOR DE MENSAGENS"
echo "===================================================================="
echo ""
echo "Iniciando aplicação..."
echo ""

# Ativar ambiente virtual se existir
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Executar aplicação
python3 run_det.py
