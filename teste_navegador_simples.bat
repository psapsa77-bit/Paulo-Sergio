@echo off
REM Teste simples de navegador para Windows

cls
echo ================================================================
echo TESTE SIMPLES DE NAVEGADOR
echo ================================================================

REM 1. Verificar selenium
echo.
echo 1. Verificando Selenium...
python -c "import selenium; print('   OK Selenium instalado: versao', selenium.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo    X Selenium NAO instalado!
    echo    Execute: pip install selenium
    pause
    exit /b 1
)

REM 2. Verificar webdriver-manager
echo.
echo 2. Verificando webdriver-manager...
python -c "import webdriver_manager; print('   OK webdriver-manager instalado')" 2>nul
if %errorlevel% neq 0 (
    echo    ! webdriver-manager NAO instalado ^(recomendado^)
    echo    Execute: pip install webdriver-manager
    set TEM_WDM=0
) else (
    set TEM_WDM=1
)

REM 3. Tentar iniciar Chrome
echo.
echo 3. Tentando iniciar Chrome...
echo    ^(uma janela do navegador deve abrir^)
echo.

REM Criar script Python temporário para teste
echo import sys > teste_nav_temp.py
echo from selenium import webdriver >> teste_nav_temp.py
echo from selenium.webdriver.chrome.service import Service >> teste_nav_temp.py
echo from selenium.webdriver.chrome.options import Options >> teste_nav_temp.py
echo. >> teste_nav_temp.py
echo options = Options() >> teste_nav_temp.py
echo options.add_argument("--no-sandbox") >> teste_nav_temp.py
echo options.add_argument("--disable-dev-shm-usage") >> teste_nav_temp.py
echo options.add_argument("--disable-gpu") >> teste_nav_temp.py
echo. >> teste_nav_temp.py
echo try: >> teste_nav_temp.py
echo     from webdriver_manager.chrome import ChromeDriverManager >> teste_nav_temp.py
echo     print("   Usando webdriver-manager para baixar ChromeDriver...") >> teste_nav_temp.py
echo     service = Service(ChromeDriverManager().install()) >> teste_nav_temp.py
echo except ImportError: >> teste_nav_temp.py
echo     print("   Usando ChromeDriver do sistema...") >> teste_nav_temp.py
echo     service = Service() >> teste_nav_temp.py
echo. >> teste_nav_temp.py
echo print("   Iniciando navegador...") >> teste_nav_temp.py
echo driver = webdriver.Chrome(service=service, options=options) >> teste_nav_temp.py
echo print("   OK SUCESSO! Navegador aberto!") >> teste_nav_temp.py
echo print(f"   Titulo da pagina: {driver.title}") >> teste_nav_temp.py
echo. >> teste_nav_temp.py
echo print("") >> teste_nav_temp.py
echo print("4. Testando acesso a site...") >> teste_nav_temp.py
echo driver.get("https://www.google.com") >> teste_nav_temp.py
echo print(f"   OK Acessou Google: {driver.title}") >> teste_nav_temp.py
echo. >> teste_nav_temp.py
echo print("") >> teste_nav_temp.py
echo print("   Navegador ficara aberto por 5 segundos...") >> teste_nav_temp.py
echo import time >> teste_nav_temp.py
echo time.sleep(5) >> teste_nav_temp.py
echo. >> teste_nav_temp.py
echo driver.quit() >> teste_nav_temp.py
echo print("   OK Navegador fechado") >> teste_nav_temp.py
echo. >> teste_nav_temp.py
echo print("") >> teste_nav_temp.py
echo print("================================================================") >> teste_nav_temp.py
echo print("OK TESTE BEM SUCEDIDO!") >> teste_nav_temp.py
echo print("================================================================") >> teste_nav_temp.py
echo print("") >> teste_nav_temp.py
echo print("Seu sistema esta configurado corretamente!") >> teste_nav_temp.py
echo print("O DET Robot deve funcionar normalmente.") >> teste_nav_temp.py

python teste_nav_temp.py

if %errorlevel% equ 0 (
    del teste_nav_temp.py
    echo.
    pause
    exit /b 0
)

REM Se deu erro, mostrar soluções
echo.
echo ================================================================
echo SOLUCOES POSSIVEIS:
echo ================================================================
echo.
echo 1. ChromeDriver nao encontrado. Instale webdriver-manager:
echo    pip install webdriver-manager
echo.
echo 2. Google Chrome nao instalado. Baixe em:
echo    https://www.google.com/chrome/
echo.
echo 3. Versao incompativel. Atualize:
echo    pip install --upgrade webdriver-manager
echo.

del teste_nav_temp.py
pause
exit /b 1
