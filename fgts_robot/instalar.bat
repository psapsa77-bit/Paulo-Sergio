@echo off
REM Script de instalação do Robô FGTS Digital para Windows
REM Uso: instalar.bat

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║        🤖 INSTALAÇÃO DO ROBÔ FGTS DIGITAL 🤖                 ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Verificar Python
echo 📌 Verificando instalação do Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo    Instale Python 3.10 ou superior: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% encontrado
echo.

REM Verificar pip
echo 📌 Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip não encontrado!
    pause
    exit /b 1
)
echo ✓ pip encontrado
echo.

REM Criar ambiente virtual
echo 📌 Criando ambiente virtual...
if exist "venv" (
    echo ⚠️  Ambiente virtual já existe
    set /p RECREATE="   Deseja recriar? (s/N): "
    if /i "%RECREATE%"=="s" (
        rmdir /s /q venv
        python -m venv venv
        echo ✓ Ambiente virtual recriado
    )
) else (
    python -m venv venv
    echo ✓ Ambiente virtual criado
)
echo.

REM Ativar ambiente virtual
echo 📌 Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo ✓ Ambiente virtual ativado
echo.

REM Atualizar pip
echo 📌 Atualizando pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✓ pip atualizado
echo.

REM Instalar dependências
echo 📌 Instalando dependências Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)
echo ✓ Dependências instaladas
echo.

REM Instalar navegador Playwright
echo 📌 Instalando navegador Chromium...
playwright install chromium
if errorlevel 1 (
    echo ❌ Erro ao instalar Chromium
    pause
    exit /b 1
)
echo ✓ Chromium instalado
echo.

REM Criar arquivo .env se não existir
echo 📌 Configurando arquivo .env...
if not exist ".env" (
    copy .env.example .env >nul
    echo ✓ Arquivo .env criado a partir do template
    echo.
    echo ⚠️  IMPORTANTE: Edite o arquivo .env com suas credenciais:
    echo    - CERT_PATH: caminho do seu certificado .pfx
    echo    - CERT_PASSWORD: senha do certificado
) else (
    echo ⚠️  Arquivo .env já existe (não foi sobrescrito)
)
echo.

REM Criar diretórios necessários
echo 📌 Criando diretórios...
if not exist "certificados" mkdir certificados
if not exist "resultados" mkdir resultados
if not exist "logs" mkdir logs
if not exist "logs\screenshots" mkdir logs\screenshots
echo ✓ Diretórios criados
echo.

REM Resumo
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                  ✅ INSTALAÇÃO CONCLUÍDA! ✅                  ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.
echo 📋 Próximos passos:
echo.
echo    1. Configure o arquivo .env com suas credenciais:
echo       notepad .env
echo.
echo    2. Copie seu certificado para a pasta certificados\
echo       copy C:\caminho\do\certificado.pfx certificados\
echo.
echo    3. Ative o ambiente virtual:
echo       venv\Scripts\activate
echo.
echo    4. Execute o robô:
echo       python main.py --help
echo.
echo 📚 Para mais informações, consulte o README.md
echo.
pause
