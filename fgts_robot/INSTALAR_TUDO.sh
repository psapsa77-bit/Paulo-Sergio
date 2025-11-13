#!/bin/bash
# Instalador Automático do Robô FGTS Digital
# Este script instala TUDO automaticamente para você!

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     🤖 INSTALADOR AUTOMÁTICO - ROBÔ FGTS DIGITAL 🤖          ║"
echo "║                                                               ║"
echo "║            Instalando tudo automaticamente...                 ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Parar se houver erro
set -e

# Cores para mensagens
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sem cor

# Função para mensagem de sucesso
sucesso() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Função para mensagem de erro
erro() {
    echo -e "${RED}✗ $1${NC}"
}

# Função para mensagem de aviso
aviso() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo "Passo 1 de 7: Verificando Python..."
echo ""

if ! command -v python3 &> /dev/null; then
    erro "Python 3 não está instalado!"
    echo ""
    echo "Por favor, instale Python 3.10 ou superior:"
    echo "https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
sucesso "Python $PYTHON_VERSION encontrado"
echo ""

echo "Passo 2 de 7: Criando ambiente virtual..."
echo ""

if [ -d "venv" ]; then
    aviso "Ambiente virtual já existe, vou usar o existente"
else
    python3 -m venv venv
    sucesso "Ambiente virtual criado"
fi
echo ""

echo "Passo 3 de 7: Ativando ambiente virtual..."
echo ""
source venv/bin/activate
sucesso "Ambiente virtual ativado"
echo ""

echo "Passo 4 de 7: Atualizando pip..."
echo ""
python -m pip install --upgrade pip -q
sucesso "pip atualizado"
echo ""

echo "Passo 5 de 7: Instalando dependências Python..."
echo "   (Isso pode demorar alguns minutos...)"
echo ""

# Instalar dependências uma por uma para melhor controle
pip install playwright>=1.40.0 -q && sucesso "✓ Playwright instalado"
pip install pandas>=2.1.0 -q && sucesso "✓ Pandas instalado"
pip install openpyxl>=3.1.0 -q && sucesso "✓ OpenPyXL instalado"
pip install cryptography>=41.0.0 -q && sucesso "✓ Cryptography instalado"
pip install python-dotenv>=1.0.0 -q && sucesso "✓ Python-dotenv instalado"
pip install python-dateutil>=2.8.0 -q && sucesso "✓ Python-dateutil instalado"
pip install streamlit>=1.28.0 -q && sucesso "✓ Streamlit instalado"

echo ""
sucesso "Todas as dependências Python instaladas!"
echo ""

echo "Passo 6 de 7: Instalando navegador Chromium..."
echo "   (Isso pode demorar alguns minutos...)"
echo ""

playwright install chromium

sucesso "Chromium instalado"
echo ""

echo "Passo 7 de 7: Configurando ambiente..."
echo ""

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    cp .env.example .env
    sucesso "Arquivo .env criado"
    echo ""
    aviso "IMPORTANTE: Você precisa editar o arquivo .env"
    echo ""
    echo "   1. Adicione seu certificado na pasta 'certificados/'"
    echo "   2. Edite o arquivo .env e configure:"
    echo "      - CERT_PATH=certificados/seu_certificado.pfx"
    echo "      - CERT_PASSWORD=sua_senha"
    echo ""
else
    aviso "Arquivo .env já existe (não foi modificado)"
fi

# Criar diretórios
mkdir -p certificados resultados logs logs/screenshots
sucesso "Diretórios criados"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "       ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO! ✅"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo ""
echo "   1️⃣  Adicione seu certificado digital:"
echo "      cp /caminho/do/certificado.pfx certificados/"
echo ""
echo "   2️⃣  Configure a senha do certificado:"
echo "      nano .env"
echo "      (ou use seu editor preferido)"
echo ""
echo "   3️⃣  Teste se tudo está OK:"
echo "      python diagnosticar.py"
echo ""
echo "   4️⃣  Execute o robô:"
echo "      python main.py --help"
echo ""
echo "   💡 OU use a interface web (mais fácil):"
echo "      ./abrir_fgts.sh"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📚 Precisa de ajuda?"
echo "   - Leia: README.md"
echo "   - Guia rápido: QUICKSTART.md"
echo "   - Problemas: TROUBLESHOOTING.md"
echo ""
