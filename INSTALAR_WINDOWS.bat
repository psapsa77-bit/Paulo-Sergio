@echo off
echo ========================================
echo   LABOR TERMINATION ANALYZER
echo   Instalacao Automatica - Windows
echo ========================================
echo.

echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERRO: Python nao encontrado!
    echo.
    echo Por favor, instale o Python primeiro:
    echo 1. Acesse: https://www.python.org/downloads/
    echo 2. Baixe a versao mais recente
    echo 3. Durante instalacao, marque: "Add Python to PATH"
    echo 4. Execute este instalador novamente
    echo.
    pause
    exit /b 1
)

echo OK! Python encontrado.
echo.

echo [2/3] Instalando dependencias...
echo Isso pode demorar alguns minutos...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERRO na instalacao!
    echo Tente executar novamente ou instale manualmente:
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Instalacao concluida!
echo.
echo ========================================
echo   SUCESSO!
echo ========================================
echo.
echo Para abrir o programa:
echo   - Duplo clique em: ABRIR_PROGRAMA.bat
echo.
echo Ou digite no terminal:
echo   python run_web.py
echo.
pause
