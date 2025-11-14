@echo off
REM ====================================================================
REM    ROBO DET - VERIFICADOR DE MENSAGENS
REM    Instalacao Automatica v2.0
REM ====================================================================

title Instalacao do Robo DET

cls
echo.
echo ====================================================================
echo.
echo           ROBO DET - VERIFICADOR DE MENSAGENS
echo.
echo                 INSTALACAO AUTOMATICA v2.0
echo.
echo ====================================================================
echo.
echo.
echo Este script vai instalar tudo automaticamente:
echo.
echo    [OK] Criar ambiente virtual Python
echo    [OK] Instalar todas as dependencias
echo    [OK] Instalar navegadores necessarios
echo    [OK] Configurar o robo
echo.
echo Tempo estimado: 2-5 minutos
echo.
echo ====================================================================
echo.
echo Aguarde, o processo vai iniciar em 3 segundos...
timeout /t 3 /nobreak >nul
echo.

REM Verificar se Python esta instalado
echo ====================================================================
echo ETAPA 1/5: Verificando Python...
echo ====================================================================
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale o Python primeiro:
    echo    1. Acesse: https://www.python.org/downloads/
    echo    2. Baixe Python 3.8 ou superior
    echo    3. IMPORTANTE: Marque "Add Python to PATH" durante instalacao
    echo    4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python encontrado!
echo.

REM Verificar se esta na pasta correta
cd /d "%~dp0"

REM Criar ambiente virtual
echo.
echo ====================================================================
echo ETAPA 2/5: Criando ambiente virtual...
echo ====================================================================

if exist "venv" (
    echo [AVISO] Ambiente virtual ja existe. Removendo para reinstalar...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    color 0C
    echo [ERRO] Nao foi possivel criar ambiente virtual!
    pause
    exit /b 1
)
echo [OK] Ambiente virtual criado!
echo.

REM Ativar ambiente virtual
echo ====================================================================
echo ETAPA 3/5: Ativando ambiente virtual...
echo ====================================================================
call venv\Scripts\activate.bat
if errorlevel 1 (
    color 0C
    echo [ERRO] Nao foi possivel ativar ambiente virtual!
    pause
    exit /b 1
)
echo [OK] Ambiente virtual ativado!
echo.

REM Atualizar pip
echo ====================================================================
echo ETAPA 4/5: Instalando dependencias...
echo ====================================================================
echo.
echo Atualizando pip...
python -m pip install --upgrade pip --quiet
echo [OK] Pip atualizado!
echo.

REM Instalar dependencias
echo Instalando bibliotecas Python...
echo (isso pode demorar alguns minutos)
echo.

if not exist "det_robot\requirements.txt" (
    color 0C
    echo [ERRO] Arquivo requirements.txt nao encontrado!
    echo Certifique-se de que esta na pasta correta do projeto.
    pause
    exit /b 1
)

pip install -r det_robot\requirements.txt
if errorlevel 1 (
    color 0C
    echo [ERRO] Nao foi possivel instalar dependencias!
    pause
    exit /b 1
)
echo [OK] Bibliotecas instaladas!
echo.

REM Instalar navegadores do Playwright
echo ====================================================================
echo ETAPA 5/5: Instalando navegadores...
echo ====================================================================
echo.
echo Instalando Chromium para o robo...
echo (isso pode demorar alguns minutos)
echo.
python -m playwright install chromium
if errorlevel 1 (
    echo [AVISO] Nao foi possivel instalar Chromium
    echo          O robo tentara usar Chrome ou Edge do sistema
)
echo [OK] Navegadores configurados!
echo.

REM Criar diretorios necessarios
echo Criando diretorios...
cd det_robot
if not exist "logs" mkdir logs
if not exist "resultados" mkdir resultados
cd ..
echo [OK] Diretorios criados!
echo.

REM Finalizacao
color 0A
echo.
echo ====================================================================
echo.
echo               INSTALACAO CONCLUIDA COM SUCESSO!
echo.
echo ====================================================================
echo.
echo Tudo pronto para usar o Robo DET!
echo.
echo.
echo COMO USAR:
echo.
echo    1. Clique duas vezes no arquivo: ABRIR_DET.bat
echo    2. Na interface web, digite os CNPJs das empresas
echo    3. Clique em "Processar Empresas"
echo    4. Selecione seu certificado digital quando solicitado
echo    5. Aguarde o robo verificar as mensagens
echo.
echo.
echo Resultados salvos em: det_robot\resultados\
echo Logs salvos em: det_robot\logs\
echo.
echo.
echo DICAS IMPORTANTES:
echo    - Mantenha seu certificado digital valido
echo    - Tenha o PIN do certificado em maos
echo    - Use Chrome ou Edge instalado (melhor suporte a certificados)
echo.
echo ====================================================================
echo.
pause
