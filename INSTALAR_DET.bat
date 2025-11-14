@echo off
chcp 65001 >nul
color 0A
title Instalação do Robô DET - Verificador de Mensagens

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║            🤖 ROBÔ DET - VERIFICADOR DE MENSAGENS 📬               ║
echo ║                                                                    ║
echo ║                    INSTALAÇÃO AUTOMÁTICA v2.0                      ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo.
echo 📋 Este script vai instalar tudo automaticamente:
echo    ✓ Criar ambiente virtual Python
echo    ✓ Instalar todas as dependências
echo    ✓ Instalar navegadores necessários
echo    ✓ Configurar o robô
echo.
echo ⏱️  Tempo estimado: 2-5 minutos
echo.
echo 🔄 Aguarde, o processo vai iniciar...
timeout /t 3 /nobreak >nul
echo.

:: Verificar se Python está instalado
echo ═══════════════════════════════════════════════════════════════════
echo 🔍 ETAPA 1/5: Verificando Python...
echo ═══════════════════════════════════════════════════════════════════
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo ❌ ERRO: Python não encontrado!
    echo.
    echo 📥 Por favor, instale o Python primeiro:
    echo    1. Acesse: https://www.python.org/downloads/
    echo    2. Baixe Python 3.8 ou superior
    echo    3. IMPORTANTE: Marque "Add Python to PATH" durante instalação
    echo    4. Execute este script novamente
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python encontrado!
echo.

:: Verificar se está na pasta correta
cd /d "%~dp0"

:: Criar ambiente virtual
echo.
echo ═══════════════════════════════════════════════════════════════════
echo 🔧 ETAPA 2/5: Criando ambiente virtual...
echo ═══════════════════════════════════════════════════════════════════

if exist "venv" (
    echo ⚠️  Ambiente virtual já existe. Removendo para reinstalar...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    color 0C
    echo ❌ ERRO ao criar ambiente virtual!
    pause
    exit /b 1
)
echo ✅ Ambiente virtual criado!
echo.

:: Ativar ambiente virtual
echo ═══════════════════════════════════════════════════════════════════
echo 🔌 ETAPA 3/5: Ativando ambiente virtual...
echo ═══════════════════════════════════════════════════════════════════
call venv\Scripts\activate.bat
if errorlevel 1 (
    color 0C
    echo ❌ ERRO ao ativar ambiente virtual!
    pause
    exit /b 1
)
echo ✅ Ambiente virtual ativado!
echo.

:: Atualizar pip
echo ═══════════════════════════════════════════════════════════════════
echo 📦 ETAPA 4/5: Instalando dependências...
echo ═══════════════════════════════════════════════════════════════════
echo.
echo 🔄 Atualizando pip...
python -m pip install --upgrade pip --quiet
echo ✅ Pip atualizado!
echo.

:: Instalar dependências
echo 🔄 Instalando bibliotecas Python...
echo    (isso pode demorar alguns minutos)
echo.

if not exist "det_robot\requirements.txt" (
    color 0C
    echo ❌ ERRO: Arquivo requirements.txt não encontrado!
    echo    Certifique-se de que está na pasta correta do projeto.
    pause
    exit /b 1
)

pip install -r det_robot\requirements.txt
if errorlevel 1 (
    color 0C
    echo ❌ ERRO ao instalar dependências!
    pause
    exit /b 1
)
echo ✅ Bibliotecas instaladas!
echo.

:: Instalar navegadores do Playwright
echo ═══════════════════════════════════════════════════════════════════
echo 🌐 ETAPA 5/5: Instalando navegadores...
echo ═══════════════════════════════════════════════════════════════════
echo.
echo 🔄 Instalando Chromium para o robô...
echo    (isso pode demorar alguns minutos)
echo.
python -m playwright install chromium
if errorlevel 1 (
    echo ⚠️  Aviso: Não foi possível instalar Chromium
    echo       O robô tentará usar Chrome ou Edge do sistema
)
echo ✅ Navegadores configurados!
echo.

:: Criar diretórios necessários
echo 🔄 Criando diretórios...
cd det_robot
if not exist "logs" mkdir logs
if not exist "resultados" mkdir resultados
cd ..
echo ✅ Diretórios criados!
echo.

:: Finalização
color 0A
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║                   ✅ INSTALAÇÃO CONCLUÍDA! ✅                      ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo 🎉 Tudo pronto para usar o Robô DET!
echo.
echo 📝 COMO USAR:
echo.
echo    1️⃣  Clique duas vezes no arquivo: ABRIR_DET.bat
echo    2️⃣  Na interface web, digite os CNPJs das empresas
echo    3️⃣  Clique em "Processar Empresas"
echo    4️⃣  Selecione seu certificado digital quando solicitado
echo    5️⃣  Aguarde o robô verificar as mensagens
echo.
echo 📂 Resultados salvos em: det_robot\resultados\
echo 📋 Logs salvos em: det_robot\logs\
echo.
echo 💡 DICAS IMPORTANTES:
echo    • Mantenha seu certificado digital válido
echo    • Tenha o PIN do certificado em mãos
echo    • Use Chrome ou Edge instalado (melhor suporte a certificados)
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
