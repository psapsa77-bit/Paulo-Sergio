#!/bin/bash

echo "========================================"
echo "  LABOR TERMINATION ANALYZER"
echo "  Instalação Automática - Mac/Linux"
echo "========================================"
echo ""

echo "[1/3] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "ERRO: Python3 não encontrado!"
    echo ""
    echo "Por favor, instale o Python primeiro:"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install python3 python3-pip"
    echo ""
    echo "Mac (com Homebrew):"
    echo "  brew install python3"
    echo ""
    echo "Depois execute este instalador novamente."
    echo ""
    exit 1
fi

echo "OK! Python encontrado: $(python3 --version)"
echo ""

echo "[2/3] Instalando dependências..."
echo "Isso pode demorar alguns minutos..."

# Atualizar pip
python3 -m pip install --upgrade pip

# Instalar dependências
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERRO na instalação!"
    echo "Tente executar novamente ou instale manualmente:"
    echo "  python3 -m pip install -r requirements.txt"
    echo ""
    exit 1
fi

echo ""
echo "[3/3] Instalação concluída!"
echo ""
echo "========================================"
echo "  SUCESSO!"
echo "========================================"
echo ""
echo "Para abrir o programa:"
echo "  - Execute: ./abrir.sh"
echo "  Ou digite: python3 run_web.py"
echo ""

# Dar permissão de execução para o script de abrir
chmod +x abrir.sh

echo "Pressione Enter para sair..."
read
