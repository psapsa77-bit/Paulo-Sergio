@echo off
REM Instalador Automático do Robô FGTS Digital
REM Este script instala TUDO automaticamente para você!

title Instalador Robô FGTS Digital

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║     🤖 INSTALADOR AUTOMÁTICO - ROBÔ FGTS DIGITAL 🤖          ║
echo ║                                                               ║
echo ║            Instalando tudo automaticamente...                 ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo Passo 1 de 7: Verificando Python...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python não está instalado!
    echo.
    echo Por favor, instale Python 3.10 ou superior:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marque a opção "Add Python to PATH" durante a instalação!
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% encontrado
echo.

echo Passo 2 de 7: Criando ambiente virtual...
echo.

if exist "venv" (
    echo ⚠ Ambiente virtual já existe, vou usar o existente
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ✗ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo ✓ Ambiente virtual criado
)
echo.

echo Passo 3 de 7: Ativando ambiente virtual...
echo.
call venv\Scripts\activate.bat
echo ✓ Ambiente virtual ativado
echo.

echo Passo 4 de 7: Atualizando pip...
echo.
python -m pip install --upgrade pip -q
echo ✓ pip atualizado
echo.

echo Passo 5 de 7: Instalando dependências Python...
echo    (Isso pode demorar alguns minutos...)
echo.

echo    Instalando playwright...
pip install playwright>=1.40.0 -q
if errorlevel 1 (
    echo ✗ Erro ao instalar playwright
    pause
    exit /b 1
)
echo    ✓ Playwright instalado

echo    Instalando pandas...
pip install pandas>=2.1.0 -q
echo    ✓ Pandas instalado

echo    Instalando openpyxl...
pip install openpyxl>=3.1.0 -q
echo    ✓ OpenPyXL instalado

echo    Instalando cryptography...
pip install cryptography>=41.0.0 -q
echo    ✓ Cryptography instalado

echo    Instalando python-dotenv...
pip install python-dotenv>=1.0.0 -q
echo    ✓ Python-dotenv instalado

echo    Instalando python-dateutil...
pip install python-dateutil>=2.8.0 -q
echo    ✓ Python-dateutil instalado

echo    Instalando streamlit...
pip install streamlit>=1.28.0 -q
echo    ✓ Streamlit instalado

echo.
echo ✓ Todas as dependências Python instaladas!
echo.

echo Passo 6 de 7: Instalando navegador Chromium...
echo    (Isso pode demorar alguns minutos...)
echo.

playwright install chromium

if errorlevel 1 (
    echo ✗ Erro ao instalar Chromium
    pause
    exit /b 1
)
echo ✓ Chromium instalado
echo.

echo Passo 7 de 7: Configurando ambiente...
echo.

REM Criar arquivo .env se não existir
if not exist ".env" (
    copy .env.example .env >nul
    echo ✓ Arquivo .env criado
    echo.
    echo ⚠ IMPORTANTE: Você precisa editar o arquivo .env
    echo.
    echo    1. Adicione seu certificado na pasta 'certificados\'
    echo    2. Edite o arquivo .env e configure:
    echo       - CERT_PATH=certificados\seu_certificado.pfx
    echo       - CERT_PASSWORD=sua_senha
    echo.
) else (
    echo ⚠ Arquivo .env já existe (não foi modificado)
)

REM Criar diretórios
if not exist "certificados" mkdir certificados
if not exist "resultados" mkdir resultados
if not exist "logs" mkdir logs
if not exist "logs\screenshots" mkdir logs\screenshots
echo ✓ Diretórios criados
echo.

echo ═══════════════════════════════════════════════════════════════
echo.
echo        ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO! ✅
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📋 PRÓXIMOS PASSOS:
echo.
echo    1️⃣  Adicione seu certificado digital:
echo       Copie seu certificado.pfx para a pasta 'certificados\'
echo.
echo    2️⃣  Configure a senha do certificado:
echo       Abra o arquivo .env com o Bloco de Notas
echo       e configure CERT_PASSWORD=sua_senha
echo.
echo    3️⃣  Teste se tudo está OK:
echo       python diagnosticar.py
echo.
echo    4️⃣  Execute o robô:
echo       python main.py --help
echo.
echo    💡 OU use a interface web (mais fácil):
echo       Clique duas vezes em: ABRIR_FGTS.bat
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📚 Precisa de ajuda?
echo    - Leia: README.md
echo    - Guia rápido: QUICKSTART.md
echo    - Problemas: TROUBLESHOOTING.md
echo.
pause
