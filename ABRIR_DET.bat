@echo off
chcp 65001 >nul
color 0B
title Robô DET - Verificador de Mensagens

:: Verificar se está na pasta correta
cd /d "%~dp0"

cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║            🤖 ROBÔ DET - VERIFICADOR DE MENSAGENS 📬               ║
echo ║                                                                    ║
echo ║                         Versão 2.0                                 ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo.

:: Verificar se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    color 0C
    echo ❌ ERRO: Ambiente virtual não encontrado!
    echo.
    echo 📥 Por favor, execute primeiro o arquivo: INSTALAR_DET.bat
    echo.
    pause
    exit /b 1
)

:: Verificar se run_det.py existe
if not exist "run_det.py" (
    color 0C
    echo ❌ ERRO: Arquivo run_det.py não encontrado!
    echo.
    echo 📥 Certifique-se de que está na pasta correta do projeto.
    echo.
    pause
    exit /b 1
)

echo 🔄 Iniciando o Robô DET...
echo.
echo ⏳ Aguarde, a interface web vai abrir automaticamente...
echo.

:: Ativar ambiente virtual
call venv\Scripts\activate.bat

:: Executar aplicação
python run_det.py

:: Se houver erro
if errorlevel 1 (
    color 0C
    echo.
    echo ═══════════════════════════════════════════════════════════════════
    echo ❌ ERRO ao executar o robô!
    echo ═══════════════════════════════════════════════════════════════════
    echo.
    echo 🔧 Possíveis soluções:
    echo    1. Execute o INSTALAR_DET.bat novamente
    echo    2. Verifique se o Python está instalado
    echo    3. Verifique os logs em: det_robot\logs\
    echo.
    pause
    exit /b 1
)

pause
