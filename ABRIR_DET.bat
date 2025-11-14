@echo off
REM Script para abrir o Robô DET no Windows
REM Autor: Paulo Sergio

title Robô DET - Verificador de Mensagens

echo ====================================================================
echo        ROBÔ DET - VERIFICADOR DE MENSAGENS
echo ====================================================================
echo.
echo Iniciando aplicacao...
echo.

REM Ativar ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Executar aplicação
python run_det.py

pause
