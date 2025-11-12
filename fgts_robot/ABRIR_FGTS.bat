@echo off
REM Script para abrir a interface web do Robô FGTS Digital no Windows
REM Uso: Clique duas vezes neste arquivo

title Robô FGTS Digital - Interface Web

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║        🤖 ROBÔ FGTS DIGITAL - INTERFACE WEB 🤖               ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Verificar se está no ambiente virtual
if exist "venv\Scripts\activate.bat" (
    echo ✓ Ativando ambiente virtual...
    call venv\Scripts\activate.bat
    echo.
) else (
    echo ⚠️  Ambiente virtual não encontrado
    echo    Execute primeiro: instalar.bat
    echo.
    pause
    exit /b 1
)

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    pause
    exit /b 1
)

REM Verificar Streamlit
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit não instalado!
    echo    Instalando agora...
    pip install streamlit
    echo.
)

REM Executar interface web
echo 🚀 Iniciando interface web...
echo.
echo    A interface será aberta automaticamente no navegador
echo.
echo 💡 Para encerrar, feche esta janela ou pressione Ctrl+C
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

python run_fgts_web.py

pause
