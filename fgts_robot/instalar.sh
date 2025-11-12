#!/bin/bash
# Script de instalação do Robô FGTS Digital
# Uso: ./instalar.sh

set -e  # Sair em caso de erro

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║        🤖 INSTALAÇÃO DO ROBÔ FGTS DIGITAL 🤖                 ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
echo "📌 Verificando instalação do Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "   Instale Python 3.10 ou superior: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION encontrado"

# Verificar pip
echo ""
echo "📌 Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado!"
    exit 1
fi
echo "✓ pip3 encontrado"

# Criar ambiente virtual
echo ""
echo "📌 Criando ambiente virtual..."
if [ -d "venv" ]; then
    echo "⚠️  Ambiente virtual já existe"
    read -p "   Deseja recriar? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ Ambiente virtual recriado"
    fi
else
    python3 -m venv venv
    echo "✓ Ambiente virtual criado"
fi

# Ativar ambiente virtual
echo ""
echo "📌 Ativando ambiente virtual..."
source venv/bin/activate
echo "✓ Ambiente virtual ativado"

# Atualizar pip
echo ""
echo "📌 Atualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip atualizado"

# Instalar dependências
echo ""
echo "📌 Instalando dependências Python..."
pip install -r requirements.txt
echo "✓ Dependências instaladas"

# Instalar navegador Playwright
echo ""
echo "📌 Instalando navegador Chromium..."
playwright install chromium
echo "✓ Chromium instalado"

# Criar arquivo .env se não existir
echo ""
echo "📌 Configurando arquivo .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Arquivo .env criado a partir do template"
    echo ""
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais:"
    echo "   - CERT_PATH: caminho do seu certificado .pfx"
    echo "   - CERT_PASSWORD: senha do certificado"
else
    echo "⚠️  Arquivo .env já existe (não foi sobrescrito)"
fi

# Criar diretórios necessários
echo ""
echo "📌 Criando diretórios..."
mkdir -p certificados resultados logs logs/screenshots
echo "✓ Diretórios criados"

# Resumo
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ INSTALAÇÃO CONCLUÍDA! ✅                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "   1. Configure o arquivo .env com suas credenciais:"
echo "      nano .env"
echo ""
echo "   2. Copie seu certificado para a pasta certificados/:"
echo "      cp /caminho/do/certificado.pfx certificados/"
echo ""
echo "   3. Ative o ambiente virtual:"
echo "      source venv/bin/activate"
echo ""
echo "   4. Execute o robô:"
echo "      python main.py --help"
echo ""
echo "📚 Para mais informações, consulte o README.md"
echo ""
