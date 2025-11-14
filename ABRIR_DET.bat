@echo off
REM ====================================================================
REM    ROBO DET - VERIFICADOR DE MENSAGENS
REM    Script de Execucao v2.0
REM ====================================================================

title Robo DET - Verificador de Mensagens

REM Verificar se esta na pasta correta
cd /d "%~dp0"

cls
echo.
echo ====================================================================
echo.
echo           ROBO DET - VERIFICADOR DE MENSAGENS
echo.
echo                        Versao 2.0
echo.
echo ====================================================================
echo.
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    color 0C
    echo [ERRO] Ambiente virtual nao encontrado!
    echo.
    echo Por favor, execute primeiro o arquivo: INSTALAR_DET.bat
    echo.
    pause
    exit /b 1
)

REM Verificar se run_det.py existe
if not exist "run_det.py" (
    color 0C
    echo [ERRO] Arquivo run_det.py nao encontrado!
    echo.
    echo Certifique-se de que esta na pasta correta do projeto.
    echo.
    pause
    exit /b 1
)

echo Iniciando o Robo DET...
echo.
echo Aguarde, a interface web vai abrir automaticamente...
echo.

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Executar aplicacao
python run_det.py

REM Se houver erro
if errorlevel 1 (
    color 0C
    echo.
    echo ====================================================================
    echo [ERRO] Nao foi possivel executar o robo!
    echo ====================================================================
    echo.
    echo Possiveis solucoes:
    echo    1. Execute o INSTALAR_DET.bat novamente
    echo    2. Verifique se o Python esta instalado
    echo    3. Verifique os logs em: det_robot\logs\
    echo.
    pause
    exit /b 1
)

pause
