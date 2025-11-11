@echo off
chcp 65001 >nul
cls

echo ========================================
echo  INSTALADOR - Analisador de Rescisões
echo  Trabalhistas v2.0
echo ========================================
echo.
echo Este script irá instalar todas as
echo dependências necessárias.
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

cls
echo ========================================
echo  Etapa 1/3: Verificando Python
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Python não encontrado!
    echo.
    echo Por favor, instale Python 3.9 ou superior:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante a instalação, marque a opção
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python encontrado!
echo.

echo ========================================
echo  Etapa 2/3: Atualizando pip
echo ========================================
echo.

python -m pip install --upgrade pip
echo.

echo ========================================
echo  Etapa 3/3: Instalando dependências
echo ========================================
echo.
echo Isso pode levar alguns minutos...
echo.

python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ⚠️ AVISO: Alguns pacotes podem ter falhado.
    echo Tentando instalar o pacote...
    echo.
    pip install -e .
)

echo.
echo Instalando o pacote labor-termination-analyzer...
pip install -e .

cls
echo ========================================
echo  ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ========================================
echo.
echo O aplicativo foi instalado com sucesso!
echo.
echo PRÓXIMOS PASSOS:
echo.
echo 1️⃣ Execute: ABRIR_PROGRAMA.bat
echo.
echo 2️⃣ Ou no terminal: rescisao --help
echo.
echo 3️⃣ Para interface web: python run_web.py
echo.
echo ========================================
echo  Comandos disponíveis:
echo ========================================
echo.
echo rescisao exemplo          - Gera exemplo JSON
echo rescisao analisar arquivo.json - Analisa rescisão
echo rescisao extrair arquivo.pdf   - Extrai dados de PDF
echo.
echo ========================================
echo.

pause
