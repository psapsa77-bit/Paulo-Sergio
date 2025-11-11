#!/bin/bash
# ========================================
#  INSTALADOR AUTOMÁTICO - FGTS ROBOT
# ========================================
#
# Duplo clique ou execute: ./INSTALAR_TUDO.sh
#

echo ""
echo "========================================"
echo "  INSTALADOR AUTOMÁTICO"
echo "  FGTS Digital Robot"
echo "========================================"
echo ""
echo "Este programa vai instalar tudo automaticamente."
echo ""
echo "Pode demorar alguns minutos..."
echo ""
read -p "Pressione ENTER para começar..."

echo ""
echo "Iniciando instalação..."
echo ""

# Executar script Python de instalação
python3 instalar_playwright.py

echo ""
echo "========================================"
echo "  PRONTO!"
echo "========================================"
echo ""
echo "Agora você pode executar o programa:"
echo ""
echo "  python3 run_fgts_robot.py"
echo ""
echo "E abrir no navegador:"
echo "  http://localhost:8502"
echo ""
read -p "Pressione ENTER para sair..."
