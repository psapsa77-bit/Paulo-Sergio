@echo off
REM Instalador automático do DET Robot para Windows
REM Este script instala TUDO que você precisa

cls
echo ================================================================
echo.
echo           DET ROBOT - INSTALACAO AUTOMATICA
echo.
echo ================================================================
echo.
echo Este script vai instalar tudo automaticamente.
echo Voce nao precisa fazer nada, apenas aguardar!
echo.
pause

set ERRO=0

echo.
echo ================================================================
echo PASSO 1/5: Verificando Python
echo ================================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python nao encontrado!
    echo.
    echo INSTALE O PYTHON:
    echo   Baixe em: https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Marque a opcao "Add Python to PATH" durante instalacao
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo OK Python instalado: versao %%i
)

echo.
echo ================================================================
echo PASSO 2/5: Verificando pip
echo ================================================================

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X pip nao encontrado!
    echo.
    echo Instalando pip...
    python -m ensurepip --upgrade
) else (
    echo OK pip instalado
)

echo.
echo ================================================================
echo PASSO 3/5: Verificando navegador
echo ================================================================

set NAVEGADOR_ENCONTRADO=0

where chrome >nul 2>&1
if %errorlevel% equ 0 (
    echo OK Google Chrome encontrado
    set NAVEGADOR_ENCONTRADO=1
    goto navegador_ok
)

where firefox >nul 2>&1
if %errorlevel% equ 0 (
    echo OK Firefox encontrado
    set NAVEGADOR_ENCONTRADO=1
    goto navegador_ok
)

if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo OK Google Chrome encontrado
    set NAVEGADOR_ENCONTRADO=1
    goto navegador_ok
)

if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo OK Google Chrome encontrado
    set NAVEGADOR_ENCONTRADO=1
    goto navegador_ok
)

if exist "C:\Program Files\Mozilla Firefox\firefox.exe" (
    echo OK Firefox encontrado
    set NAVEGADOR_ENCONTRADO=1
    goto navegador_ok
)

echo ! AVISO: Nenhum navegador suportado encontrado
echo.
echo Instale um dos seguintes:
echo   1. Google Chrome: https://www.google.com/chrome/
echo   2. Firefox: https://www.mozilla.org/firefox/
echo.
echo Pressione qualquer tecla depois de instalar um navegador...
pause >nul

:navegador_ok

echo.
echo ================================================================
echo PASSO 4/5: Instalando dependencias Python
echo ================================================================
echo.
echo Atualizando pip...
python -m pip install --upgrade pip --quiet

echo.
echo Instalando pacotes necessarios (pode demorar alguns minutos)...
echo.

REM Instalar cada pacote individualmente
echo   Instalando selenium...
python -m pip install selenium --quiet
if %errorlevel% neq 0 set ERRO=1

echo   Instalando webdriver-manager...
python -m pip install webdriver-manager --quiet
if %errorlevel% neq 0 set ERRO=1

echo   Instalando pydantic...
python -m pip install pydantic --quiet
if %errorlevel% neq 0 set ERRO=1

echo   Instalando streamlit...
python -m pip install streamlit --quiet
if %errorlevel% neq 0 set ERRO=1

echo   Instalando plotly...
python -m pip install plotly --quiet
if %errorlevel% neq 0 set ERRO=1

echo   Instalando typer...
python -m pip install typer --quiet
if %errorlevel% neq 0 set ERRO=1

echo   Instalando rich...
python -m pip install rich --quiet
if %errorlevel% neq 0 set ERRO=1

echo   Instalando openpyxl...
python -m pip install openpyxl --quiet
if %errorlevel% neq 0 set ERRO=1

echo   Instalando pandas...
python -m pip install pandas --quiet
if %errorlevel% neq 0 set ERRO=1

REM Instalar requirements.txt se existir
if exist "requirements.txt" (
    echo.
    echo Instalando demais dependencias do arquivo requirements.txt...
    python -m pip install -r requirements.txt --quiet
)

echo.
echo ================================================================
echo PASSO 5/5: Testando instalacao
echo ================================================================
echo.

REM Criar script de teste temporário
echo import sys > teste_temp.py
echo. >> teste_temp.py
echo print("Verificando modulos...") >> teste_temp.py
echo. >> teste_temp.py
echo modulos = { >> teste_temp.py
echo     "selenium": "Automacao web", >> teste_temp.py
echo     "webdriver_manager": "Gerenciador de drivers", >> teste_temp.py
echo     "streamlit": "Interface web", >> teste_temp.py
echo     "pydantic": "Validacao de dados", >> teste_temp.py
echo } >> teste_temp.py
echo. >> teste_temp.py
echo todos_ok = True >> teste_temp.py
echo. >> teste_temp.py
echo for modulo, desc in modulos.items(): >> teste_temp.py
echo     try: >> teste_temp.py
echo         __import__(modulo) >> teste_temp.py
echo         print(f"  OK {modulo} ({desc})") >> teste_temp.py
echo     except ImportError: >> teste_temp.py
echo         print(f"  X {modulo} ({desc})") >> teste_temp.py
echo         todos_ok = False >> teste_temp.py
echo. >> teste_temp.py
echo if todos_ok: >> teste_temp.py
echo     print("\nOK Todos os modulos instalados corretamente!") >> teste_temp.py
echo     sys.exit(0) >> teste_temp.py
echo else: >> teste_temp.py
echo     print("\nX Alguns modulos faltando") >> teste_temp.py
echo     sys.exit(1) >> teste_temp.py

python teste_temp.py
if %errorlevel% equ 0 (
    echo OK Teste de modulos passou!
) else (
    echo X Alguns modulos nao instalaram corretamente
    set ERRO=1
)

del teste_temp.py

echo.
echo ================================================================

if %ERRO% equ 0 (
    echo.
    echo ================================================================
    echo.
    echo            OK INSTALACAO CONCLUIDA COM SUCESSO!
    echo.
    echo ================================================================
    echo.
    echo O DET Robot esta pronto para usar!
    echo.
    echo ================================================================
    echo COMO USAR:
    echo ================================================================
    echo.
    echo Execute um destes comandos:
    echo.
    echo   USAR_DET_ROBOT.bat
    echo.
    echo   ^(ou^)
    echo.
    echo   python run_det_robot.py
    echo.
    echo ================================================================
) else (
    echo.
    echo ================================================================
    echo.
    echo         ! INSTALACAO TEVE ALGUNS PROBLEMAS
    echo.
    echo ================================================================
    echo.
    echo Verifique os erros acima e tente corrigir.
    echo.
    echo Se precisar de ajuda, veja: SOLUCAO_PROBLEMAS_DET.md
)

echo.
pause
