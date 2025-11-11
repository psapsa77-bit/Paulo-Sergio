@echo off
REM Script de instalação do FGTS Digital Robot
REM Sistema: Windows

echo.
echo ========================================
echo  FGTS Digital Robot - Instalacao
echo ========================================
echo.

REM Verificar Python
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo        Instale Python 3.9+ e tente novamente
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% encontrado
echo.

REM Verificar pip
echo Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] pip nao encontrado!
    pause
    exit /b 1
)
echo [OK] pip encontrado
echo.

REM Criar ambiente virtual
set /p CRIAR_VENV="Criar ambiente virtual? (S/N): "
if /i "%CRIAR_VENV%"=="S" (
    echo.
    echo Criando ambiente virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [OK] Ambiente virtual criado
)
echo.

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip
echo.

REM Instalar dependências
echo Instalando dependencias Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Instalar Playwright
echo Instalando navegadores do Playwright...
playwright install chromium
if errorlevel 1 (
    echo [ERRO] Falha ao instalar Playwright
    pause
    exit /b 1
)
echo [OK] Chromium instalado
echo.

REM Verificar instalação
echo Verificando instalacao...
python -c "from fgts_digital_robot import FGTSRobot; print('[OK] FGTS Robot instalado com sucesso!')"
if errorlevel 1 (
    echo [ERRO] Verificacao falhou
    pause
    exit /b 1
)
echo.

REM Instruções finais
echo ========================================
echo  Instalacao concluida!
echo ========================================
echo.
echo Proximos passos:
echo.
echo 1. Execute a interface web:
echo    python run_fgts_robot.py
echo.
echo 2. Ou use via Python:
echo    python exemplo_fgts_robot.py
echo.
echo 3. Leia a documentacao:
echo    type README_FGTS_ROBOT.md
echo.

if /i "%CRIAR_VENV%"=="S" (
    echo [AVISO] Lembre-se de ativar o ambiente virtual:
    echo         venv\Scripts\activate.bat
    echo.
)

echo Bom uso!
echo.
pause
