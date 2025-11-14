#!/bin/bash
# Script de instalação do Robô DET para Linux/Mac
# Autor: Paulo Sergio

echo "===================================================================="
echo "       INSTALAÇÃO - ROBÔ DET"
echo "===================================================================="
echo ""
echo "Este script vai instalar todas as dependências necessárias"
echo ""
echo "===================================================================="
echo ""

read -p "Pressione ENTER para continuar..."

echo ""
echo "[1/4] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "ERRO: Python 3 não encontrado!"
    echo "Por favor, instale o Python 3.8 ou superior"
    exit 1
fi

python3 --version

echo ""
echo "[2/4] Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Ambiente virtual criado com sucesso!"
else
    echo "Ambiente virtual já existe"
fi

echo ""
echo "[3/4] Ativando ambiente virtual e instalando dependências..."
source venv/bin/activate

echo ""
echo "Instalando pacotes Python..."
pip install --upgrade pip
pip install -r det_robot/requirements.txt

echo ""
echo "[4/4] Instalando navegadores do Playwright..."
python -m playwright install chromium

echo ""
echo "===================================================================="
echo "       INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "===================================================================="
echo ""
echo "Para executar o programa, use o comando: ./abrir_det.sh"
echo ""
