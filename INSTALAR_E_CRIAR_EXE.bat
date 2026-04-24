@echo off
REM ========================================
REM  INSTALADOR COMPLETO AUTOMATIZADO
REM  FGTS Digital Robot
REM ========================================
REM
REM Este script faz TUDO automaticamente:
REM  1. Verifica/Instala Python
REM  2. Instala dependencias
REM  3. Cria o executavel .exe
REM
REM Voce so precisa:
REM  - Duplo clique
REM  - Aguardar
REM  - Pronto!
REM

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  INSTALADOR AUTOMATIZADO COMPLETO
echo  FGTS Digital Robot
echo ========================================
echo.
echo Este instalador vai fazer TUDO sozinho:
echo.
echo  1. Verificar se Python esta instalado
echo  2. Se nao, instalar Python automaticamente
echo  3. Instalar todas as dependencias
echo  4. Criar o arquivo .exe
echo.
echo ATENCAO:
echo  - Tempo total: 20-40 minutos
echo  - Precisa de internet
echo  - Tamanho download: ~500 MB
echo  - Pode pedir permissao de administrador
echo.
pause

REM ========================================
REM PASSO 1 - Verificar Python
REM ========================================

echo.
echo ========================================
echo  PASSO 1 - Verificando Python
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python ja esta instalado!
    python --version
    goto :instalar_dependencias
)

echo [AVISO] Python nao encontrado
echo.
echo Vou tentar instalar automaticamente...
echo.

REM ========================================
REM Tentar instalar Python via winget
REM ========================================

echo Tentando instalar via winget...
echo.

winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] winget disponivel, instalando Python...
    winget install Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements

    if %errorlevel% equ 0 (
        echo.
        echo [OK] Python instalado via winget!
        echo.
        echo IMPORTANTE: Feche esta janela e execute novamente!
        echo.
        pause
        exit /b 0
    )
)

REM ========================================
REM Se winget falhou, tentar baixar instalador
REM ========================================

echo.
echo winget nao disponivel ou falhou.
echo.
echo Vou baixar o instalador do Python...
echo.

REM Criar pasta temporaria
set TEMP_DIR=%TEMP%\fgts_installer
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

REM Baixar Python usando PowerShell
echo Baixando Python 3.12...
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe' -OutFile '%TEMP_DIR%\python_installer.exe'}"

if exist "%TEMP_DIR%\python_installer.exe" (
    echo.
    echo [OK] Download concluido!
    echo.
    echo Instalando Python...
    echo (Isso pode demorar alguns minutos)
    echo.

    REM Instalar Python silenciosamente com PATH
    "%TEMP_DIR%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

    echo.
    echo [OK] Python instalado!
    echo.
    echo IMPORTANTE: Feche esta janela e execute novamente!
    echo            (Precisa reiniciar para PATH funcionar)
    echo.
    pause
    exit /b 0
) else (
    echo.
    echo [ERRO] Nao consegui baixar o Python automaticamente.
    echo.
    echo SOLUCAO MANUAL:
    echo.
    echo 1. Acesse: https://www.python.org/downloads/
    echo 2. Baixe Python 3.12
    echo 3. Instale marcando: "Add to PATH"
    echo 4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

REM ========================================
REM PASSO 2 - Instalar Dependencias
REM ========================================

:instalar_dependencias

echo.
echo ========================================
echo  PASSO 2 - Instalando Dependencias
echo ========================================
echo.

echo Atualizando pip...
python -m pip install --upgrade pip --quiet

echo.
echo Instalando dependencias do projeto...
echo (Isso pode demorar 5-10 minutos)
echo.

python -m pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo.
    echo [AVISO] Algumas dependencias falharam.
    echo Tentando novamente sem --quiet...
    echo.
    python -m pip install -r requirements.txt
)

echo.
echo [OK] Dependencias instaladas!

REM ========================================
REM PASSO 3 - Instalar PyInstaller
REM ========================================

echo.
echo ========================================
echo  PASSO 3 - Instalando PyInstaller
echo ========================================
echo.

python -m pip install pyinstaller --quiet

echo [OK] PyInstaller instalado!

REM ========================================
REM PASSO 4 - Criar Executavel
REM ========================================

echo.
echo ========================================
echo  PASSO 4 - Criando Executavel
echo ========================================
echo.
echo ATENCAO: Este passo demora 10-20 minutos!
echo Nao feche esta janela!
echo.

REM Criar arquivo spec se nao existir
if not exist "fgts_robot.spec" (
    echo Criando arquivo de configuracao...
    python criar_executavel.py
)

echo.
echo Compilando executavel...
echo (Aguarde, isso e DEMORADO!)
echo.

pyinstaller --noconfirm --onefile --console --name "FGTS_Digital_Robot" ^
    --add-data "fgts_digital_robot;fgts_digital_robot/" ^
    --hidden-import streamlit ^
    --hidden-import playwright ^
    --hidden-import playwright.sync_api ^
    --hidden-import cryptography ^
    --hidden-import pydantic ^
    --hidden-import bs4 ^
    --hidden-import openpyxl ^
    --hidden-import plotly ^
    run_fgts_robot.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCESSO!
    echo ========================================
    echo.
    echo O executavel foi criado com sucesso!
    echo.
    echo Localizacao:
    echo %CD%\dist\FGTS_Digital_Robot.exe
    echo.
    echo Tamanho aproximado: 300-500 MB
    echo.
    echo COMO USAR:
    echo  1. Copie o arquivo .exe
    echo  2. Cole em qualquer computador Windows
    echo  3. Duplo clique para executar
    echo  4. Aguarde abrir no navegador
    echo.
    echo DICA: Voce pode desinstalar Python agora se quiser!
    echo       O .exe nao precisa mais dele.
    echo.
) else (
    echo.
    echo ========================================
    echo  ERRO NA CRIACAO
    echo ========================================
    echo.
    echo Algo deu errado ao criar o executavel.
    echo.
    echo POSSIVEL SOLUCAO:
    echo  1. Execute: python criar_executavel.py
    echo  2. Escolha opcao A (interface grafica)
    echo  3. Siga as instrucoes na tela
    echo.
)

echo.
pause
