@echo off
REM Script de instalação do Robô DET para Windows
REM Autor: Paulo Sergio

title Instalação - Robô DET

echo ====================================================================
echo        INSTALAÇÃO - ROBÔ DET
echo ====================================================================
echo.
echo Este script vai instalar todas as dependencias necessarias
echo.
echo ====================================================================
echo.

pause

echo.
echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo.
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.8 ou superior
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo [2/4] Criando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    echo Ambiente virtual criado com sucesso!
) else (
    echo Ambiente virtual ja existe
)

echo.
echo [3/4] Ativando ambiente virtual e instalando dependencias...
call venv\Scripts\activate.bat

echo.
echo Instalando pacotes Python...
pip install --upgrade pip
pip install -r det_robot\requirements.txt

echo.
echo [4/4] Instalando navegadores do Playwright...
python -m playwright install chromium

echo.
echo ====================================================================
echo        INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ====================================================================
echo.
echo Para executar o programa, use o arquivo: ABRIR_DET.bat
echo.
pause
