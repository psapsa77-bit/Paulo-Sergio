# Solução de Problemas - DET Robot

## Navegador não abre

### Diagnóstico Rápido

Execute este comando para identificar o problema:

```bash
python teste_navegador_simples.py
```

### Problema 1: Selenium não instalado

**Erro:** `ModuleNotFoundError: No module named 'selenium'`

**Solução:**
```bash
pip install selenium webdriver-manager
```

### Problema 2: ChromeDriver não encontrado

**Erro:** `selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH`

**Solução:**
```bash
# Instalar webdriver-manager (recomendado)
pip install webdriver-manager

# Ou instalar ChromeDriver manualmente
# Ubuntu/Debian:
sudo apt install chromium-chromedriver

# Verificar instalação:
chromedriver --version
```

### Problema 3: Chrome não instalado

**Erro:** `selenium.common.exceptions.SessionNotCreatedException: Message: session not created: Chrome failed to start`

**Solução - Instalar Chrome:**

**Ubuntu/Debian:**
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

**Ou usar Chromium:**
```bash
sudo apt install chromium-browser
```

**Verificar instalação:**
```bash
google-chrome --version
# ou
chromium-browser --version
```

### Problema 4: Versão incompatível Chrome/ChromeDriver

**Erro:** `session not created: This version of ChromeDriver only supports Chrome version XX`

**Solução:**
```bash
# Atualizar webdriver-manager
pip install --upgrade webdriver-manager

# Limpar cache
rm -rf ~/.wdm/

# Tentar novamente
python teste_navegador_simples.py
```

### Problema 5: Permissões no Linux

**Erro:** `Permission denied` ao executar ChromeDriver

**Solução:**
```bash
# Dar permissão de execução
chmod +x /usr/bin/chromedriver

# Ou se estiver usando webdriver-manager:
chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver
```

### Problema 6: Display não disponível (servidor sem interface)

**Erro:** `selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start: exited abnormally`

**Solução:** Use modo headless (sem interface gráfica)

```bash
# Via CLI
python -m det_robot.cli extrair --manual --headless

# Ou edite a configuração no código para usar headless=True
```

### Problema 7: Firefox em vez de Chrome

Se você só tem Firefox instalado:

```bash
# Instalar geckodriver
sudo apt install firefox-geckodriver

# Ou usar webdriver-manager
pip install webdriver-manager

# Testar
python -c "
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
driver.get('https://google.com')
print('Firefox funcionando!')
driver.quit()
"
```

## Outros Problemas

### Timeout ao acessar DET

**Solução:** Aumente o timeout

```python
from det_robot import BrowserManager

browser = BrowserManager(timeout=60)  # 60 segundos
```

### Login não funciona

1. **Use modo manual:**
```bash
python -m det_robot.cli extrair --manual
```

2. **Verifique suas credenciais Gov.br**

3. **Verifique se há captcha** - modo manual é necessário

4. **Verifique se tem 2FA ativado** - modo manual é necessário

### Site do DET mudou estrutura

Os seletores em `det_robot/auth.py` e `det_robot/scraper.py` podem precisar atualização.

**Solução temporária:**
1. Use modo manual para fazer login
2. Capture screenshot: `browser.capturar_screenshot("debug.png")`
3. Ajuste os seletores XPath conforme necessário

## Comandos Úteis

### Verificar instalações

```bash
# Python
python --version

# Navegadores
google-chrome --version
chromium-browser --version
firefox --version

# Drivers
chromedriver --version
geckodriver --version

# Dependências Python
pip list | grep selenium
pip list | grep webdriver-manager
```

### Reinstalar do zero

```bash
# Remover tudo
pip uninstall selenium webdriver-manager -y
rm -rf ~/.wdm/

# Reinstalar
pip install selenium webdriver-manager

# Testar
python teste_navegador_simples.py
```

### Logs detalhados

Para ver logs detalhados de erro:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from det_robot import BrowserManager
# ... seu código
```

## Ainda não funciona?

1. Execute o diagnóstico completo:
```bash
python diagnostico_det.py
```

2. Execute o teste simples:
```bash
python teste_navegador_simples.py
```

3. Veja os logs de erro e procure a solução acima

4. Se ainda não resolver, crie uma issue com:
   - Sistema operacional e versão
   - Versão do Python
   - Navegador instalado e versão
   - Erro completo (copie e cole)
