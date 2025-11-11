#!/bin/bash

clear

echo "========================================"
echo "  INSTALADOR - Analisador de Rescisões"
echo "  Trabalhistas v2.0"
echo "========================================"
echo ""
echo "Este script irá instalar todas as"
echo "dependências necessárias."
echo ""
echo "Pressione Enter para continuar..."
read

clear
echo "========================================"
echo "  Etapa 1/3: Verificando Python"
echo "========================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ ERRO: Python3 não encontrado!"
    echo ""
    echo "Por favor, instale Python 3.9 ou superior:"
    echo ""
    echo "Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install python3 python3-pip python3-venv"
    echo ""
    echo "Fedora:"
    echo "  sudo dnf install python3 python3-pip"
    echo ""
    echo "Mac (com Homebrew):"
    echo "  brew install python3"
    echo ""
    exit 1
fi

python3 --version
echo "✅ Python encontrado!"
echo ""

echo "========================================"
echo "  Etapa 2/3: Atualizando pip"
echo "========================================"
echo ""

python3 -m pip install --upgrade pip
echo ""

echo "========================================"
echo "  Etapa 3/3: Instalando dependências"
echo "========================================"
echo ""
echo "Isso pode levar alguns minutos..."
echo ""

python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️ AVISO: Alguns pacotes podem ter falhado."
    echo "Tentando instalar o pacote..."
    echo ""
    python3 -m pip install -e .
fi

echo ""
echo "Instalando o pacote labor-termination-analyzer..."
python3 -m pip install -e .

clear
echo "========================================"
echo "  ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "========================================"
echo ""
echo "O aplicativo foi instalado com sucesso!"
echo ""
echo "PRÓXIMOS PASSOS:"
echo ""
echo "1️⃣  Execute: ./abrir.sh"
echo ""
echo "2️⃣  Ou no terminal: rescisao --help"
echo ""
echo "3️⃣  Para interface web: python3 run_web.py"
echo ""
echo "========================================"
echo "  Comandos disponíveis:"
echo "========================================"
echo ""
echo "rescisao exemplo          - Gera exemplo JSON"
echo "rescisao analisar arquivo.json - Analisa rescisão"
echo "rescisao extrair arquivo.pdf   - Extrai dados de PDF"
echo ""
echo "========================================"
echo ""

# Dar permissão de execução para scripts
chmod +x abrir.sh
chmod +x run_web.py 2>/dev/null

echo "Pressione Enter para sair..."
read
