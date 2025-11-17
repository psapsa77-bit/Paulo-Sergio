#!/bin/bash
# Instalador automático do DET Robot
# Este script instala TUDO que você precisa

clear
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║           DET ROBOT - INSTALAÇÃO AUTOMÁTICA             ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Este script vai instalar tudo automaticamente."
echo "Você não precisa fazer nada, apenas aguardar!"
echo ""
read -p "Pressione ENTER para começar a instalação..."

ERRO=0

# Função para exibir status
status_ok() {
    echo "✅ $1"
}

status_erro() {
    echo "❌ $1"
    ERRO=1
}

status_aviso() {
    echo "⚠️  $1"
}

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PASSO 1/5: Verificando Python"
echo "═══════════════════════════════════════════════════════════"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    status_ok "Python instalado: versão $PYTHON_VERSION"
else
    status_erro "Python 3 não encontrado!"
    echo ""
    echo "INSTALE O PYTHON:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PASSO 2/5: Verificando pip (gerenciador de pacotes)"
echo "═══════════════════════════════════════════════════════════"

if command -v pip3 &> /dev/null; then
    status_ok "pip instalado"
else
    echo "Instalando pip..."
    sudo apt install python3-pip -y || status_erro "Falha ao instalar pip"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PASSO 3/5: Verificando navegador"
echo "═══════════════════════════════════════════════════════════"

NAVEGADOR_ENCONTRADO=0

if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version 2>/dev/null)
    status_ok "Google Chrome instalado: $CHROME_VERSION"
    NAVEGADOR_ENCONTRADO=1
elif command -v chromium-browser &> /dev/null; then
    CHROMIUM_VERSION=$(chromium-browser --version 2>/dev/null)
    status_ok "Chromium instalado: $CHROMIUM_VERSION"
    NAVEGADOR_ENCONTRADO=1
elif command -v firefox &> /dev/null; then
    FIREFOX_VERSION=$(firefox --version 2>/dev/null)
    status_ok "Firefox instalado: $FIREFOX_VERSION"
    NAVEGADOR_ENCONTRADO=1
fi

if [ $NAVEGADOR_ENCONTRADO -eq 0 ]; then
    status_aviso "Nenhum navegador suportado encontrado"
    echo ""
    echo "Deseja instalar o Chromium agora? (recomendado)"
    read -p "Digite 's' para SIM ou 'n' para NÃO: " INSTALAR_CHROMIUM

    if [ "$INSTALAR_CHROMIUM" = "s" ] || [ "$INSTALAR_CHROMIUM" = "S" ]; then
        echo "Instalando Chromium..."
        sudo apt update
        sudo apt install chromium-browser -y

        if [ $? -eq 0 ]; then
            status_ok "Chromium instalado com sucesso!"
        else
            status_erro "Falha ao instalar Chromium"
            echo ""
            echo "Instale manualmente:"
            echo "  Google Chrome: https://www.google.com/chrome/"
            echo "  Ou execute: sudo apt install firefox"
            exit 1
        fi
    else
        echo ""
        echo "⚠️  ATENÇÃO: Você precisa de um navegador!"
        echo ""
        echo "Instale um destes:"
        echo "  1. Google Chrome: https://www.google.com/chrome/"
        echo "  2. Chromium: sudo apt install chromium-browser"
        echo "  3. Firefox: sudo apt install firefox"
        echo ""
        read -p "Pressione ENTER depois de instalar um navegador..."
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PASSO 4/5: Instalando dependências Python"
echo "═══════════════════════════════════════════════════════════"

echo "Atualizando pip..."
pip3 install --upgrade pip --quiet

echo ""
echo "Instalando pacotes necessários (pode demorar alguns minutos)..."
echo ""

# Instalar dependências uma por uma com feedback
PACOTES=(
    "selenium"
    "webdriver-manager"
    "pydantic"
    "streamlit"
    "plotly"
    "typer"
    "rich"
    "openpyxl"
    "pandas"
)

for PACOTE in "${PACOTES[@]}"; do
    echo -n "  Instalando $PACOTE... "
    pip3 install "$PACOTE" --quiet 2>&1

    if [ $? -eq 0 ]; then
        echo "✅"
    else
        echo "❌"
        ERRO=1
    fi
done

# Instalar requirements.txt se existir
if [ -f "requirements.txt" ]; then
    echo ""
    echo "Instalando demais dependências do arquivo requirements.txt..."
    pip3 install -r requirements.txt --quiet
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "PASSO 5/5: Testando instalação"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Criar script de teste inline
cat > /tmp/teste_det_instalacao.py << 'TESTE_EOF'
import sys

print("Verificando módulos...")

modulos = {
    "selenium": "Automação web",
    "webdriver_manager": "Gerenciador de drivers",
    "streamlit": "Interface web",
    "pydantic": "Validação de dados",
}

todos_ok = True

for modulo, desc in modulos.items():
    try:
        __import__(modulo)
        print(f"  ✅ {modulo} ({desc})")
    except ImportError:
        print(f"  ❌ {modulo} ({desc})")
        todos_ok = False

if todos_ok:
    print("\n✅ Todos os módulos instalados corretamente!")
    sys.exit(0)
else:
    print("\n❌ Alguns módulos faltando")
    sys.exit(1)
TESTE_EOF

python3 /tmp/teste_det_instalacao.py

if [ $? -eq 0 ]; then
    status_ok "Teste de módulos passou!"
else
    status_erro "Alguns módulos não instalaram corretamente"
fi

rm /tmp/teste_det_instalacao.py

echo ""
echo "═══════════════════════════════════════════════════════════"

if [ $ERRO -eq 0 ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║            ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!          ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 O DET Robot está pronto para usar!"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "COMO USAR:"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Execute um destes comandos:"
    echo ""
    echo "  ./USAR_DET_ROBOT.sh"
    echo ""
    echo "  (ou)"
    echo ""
    echo "  python3 run_det_robot.py"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
else
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                                                          ║"
    echo "║         ⚠️  INSTALAÇÃO TEVE ALGUNS PROBLEMAS             ║"
    echo "║                                                          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Verifique os erros acima e tente corrigir."
    echo ""
    echo "Se precisar de ajuda, veja: SOLUCAO_PROBLEMAS_DET.md"
    echo ""
fi
