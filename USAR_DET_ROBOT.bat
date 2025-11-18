@echo off
REM Script super simples para usar o DET Robot no Windows

cls

echo ================================================================
echo.
echo                    DET ROBOT
echo       Extrator de Mensagens do DET
echo.
echo ================================================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python nao encontrado!
    echo.
    echo Execute primeiro: INSTALAR_TUDO.bat
    echo.
    pause
    exit /b 1
)

REM Verificar se selenium está instalado
python -c "import selenium" 2>nul
if %errorlevel% neq 0 (
    echo X DET Robot nao esta instalado!
    echo.
    echo Execute primeiro: INSTALAR_TUDO.bat
    echo.
    pause
    exit /b 1
)

echo Iniciando DET Robot...
echo.
echo Uma pagina web sera aberta no seu navegador.
echo Acesse: http://localhost:8502
echo.
echo ================================================================
echo.

REM Executar
python run_det_robot.py

pause
