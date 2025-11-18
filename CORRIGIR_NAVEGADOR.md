# 🔧 Solução Rápida - Navegador Não Abre

## ⚡ DIAGNÓSTICO RÁPIDO (30 segundos)

Execute este comando:

```bash
python diagnostico_navegador.py
```

**Este script vai:**
- ✅ Verificar Python e Selenium
- ✅ Procurar navegadores instalados
- ✅ Testar ChromeDriver
- ✅ ABRIR o navegador para testar
- ✅ Mostrar EXATAMENTE qual é o problema

---

## 🎯 SOLUÇÕES MAIS COMUNS

### Solução 1: Instalar webdriver-manager (RESOLVE 90% DOS CASOS)

```bash
pip install webdriver-manager
```

**Por quê isso funciona:**
- Baixa automaticamente o ChromeDriver correto
- Sempre usa a versão compatível com seu Chrome
- Não precisa configurar PATH

**Depois de instalar, teste:**
```bash
python diagnostico_navegador.py
```

---

### Solução 2: Google Chrome não instalado

**Linux (Ubuntu/Debian):**
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

**Ou use Chromium:**
```bash
sudo apt install chromium-browser
```

**Windows:**
- Baixe: https://www.google.com/chrome/
- Instale normalmente
- Reinicie o computador

**Depois de instalar, teste:**
```bash
python diagnostico_navegador.py
```

---

### Solução 3: Selenium não instalado

```bash
pip install selenium
```

**Ou reinstalar:**
```bash
pip uninstall selenium -y
pip install selenium
```

---

### Solução 4: Versão incompatível Chrome/ChromeDriver

```bash
# Atualizar webdriver-manager
pip install --upgrade webdriver-manager

# Limpar cache
rm -rf ~/.wdm/          # Linux/Mac
rmdir /s /q %USERPROFILE%\.wdm   # Windows

# Reinstalar ChromeDriver
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

---

### Solução 5: Erro de permissão

**Linux/Mac:**
```bash
# Dar permissão ao ChromeDriver
chmod +x ~/.wdm/drivers/chromedriver/*/chromedriver

# Ou executar com sudo (não recomendado)
sudo python diagnostico_navegador.py
```

**Windows:**
- Execute o CMD como Administrador
- Clique direito no CMD
- "Executar como administrador"

---

## 🔍 DIAGNÓSTICO MANUAL

Se o script automático não resolver, faça estes testes:

### Teste 1: Verificar Python

```bash
python --version
# Deve mostrar: Python 3.9.x ou superior
```

❌ **Se der erro:** Instale Python 3.9+

### Teste 2: Verificar Selenium

```bash
python -c "import selenium; print(selenium.__version__)"
# Deve mostrar: 4.x.x
```

❌ **Se der erro:** `pip install selenium`

### Teste 3: Verificar Chrome

**Linux/Mac:**
```bash
google-chrome --version
# Deve mostrar: Google Chrome 120.x.x.x
```

**Windows:**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version
```

❌ **Se der erro:** Instale o Chrome

### Teste 4: Verificar webdriver-manager

```bash
python -c "import webdriver_manager; print('OK')"
# Deve mostrar: OK
```

❌ **Se der erro:** `pip install webdriver-manager`

### Teste 5: Testar abertura do navegador

```bash
python -c "
from selenium import webdriver
driver = webdriver.Chrome()
print('SUCESSO!')
driver.quit()
"
```

✅ **Se funcionou:** O problema não é o navegador
❌ **Se deu erro:** Veja a mensagem e procure abaixo

---

## 📋 ERROS COMUNS E SOLUÇÕES

### Erro: "chromedriver executable needs to be in PATH"

**Solução:**
```bash
pip install webdriver-manager
```

### Erro: "Chrome failed to start"

**Causas possíveis:**
1. Chrome não instalado → Instale o Chrome
2. Modo headless em servidor sem display → Use VNC ou desabilite headless
3. Permissões → Execute com permissões adequadas

**Solução:**
```bash
# Testar sem headless
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
# NÃO usar headless
driver = webdriver.Chrome(options=options)
driver.quit()
"
```

### Erro: "session not created: This version of ChromeDriver only supports Chrome version X"

**Solução:**
```bash
pip install --upgrade webdriver-manager
rm -rf ~/.wdm/
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

### Erro: "WebDriverException: Message: unknown error"

**Solução genérica:**
```bash
# 1. Reinstalar tudo
pip uninstall selenium webdriver-manager -y
pip install selenium webdriver-manager

# 2. Limpar cache
rm -rf ~/.wdm/  # Linux/Mac

# 3. Testar
python diagnostico_navegador.py
```

---

## 🆘 AINDA NÃO FUNCIONA?

### Opção 1: Usar Firefox em vez de Chrome

```bash
# Instalar Firefox
sudo apt install firefox  # Linux
# Ou baixe: https://www.mozilla.org/firefox/

# Instalar geckodriver
pip install webdriver-manager

# Testar
python -c "
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service

service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service)
print('Firefox funcionou!')
driver.quit()
"
```

### Opção 2: Modo debug com logs

```bash
# Criar arquivo teste_debug.py
cat > teste_debug.py << 'EOF'
import logging
logging.basicConfig(level=logging.DEBUG)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

try:
    from webdriver_manager.chrome import ChromeDriverManager
    print("1. webdriver-manager OK")

    service = Service(ChromeDriverManager().install())
    print("2. ChromeDriver instalado")

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    print("3. Opções configuradas")

    driver = webdriver.Chrome(service=service, options=options)
    print("4. NAVEGADOR ABERTO!")

    driver.get("https://www.google.com")
    print(f"5. Título: {driver.title}")

    driver.quit()
    print("6. SUCESSO TOTAL!")

except Exception as e:
    print(f"\nERRO: {e}")
    import traceback
    traceback.print_exc()
EOF

python teste_debug.py
```

### Opção 3: Reinstalação completa

```bash
# 1. Desinstalar tudo
pip uninstall selenium webdriver-manager -y

# 2. Limpar cache
rm -rf ~/.wdm/
rm -rf ~/.cache/selenium/

# 3. Reinstalar
pip install --upgrade pip
pip install selenium==4.15.0
pip install webdriver-manager==4.0.1

# 4. Testar
python diagnostico_navegador.py
```

---

## 🐧 Linux Específico

### Problema: Display não disponível

Se estiver em servidor sem interface gráfica:

```bash
# Instalar Xvfb (X virtual framebuffer)
sudo apt install xvfb

# Executar com Xvfb
xvfb-run python run_det_robot.py

# Ou usar headless mode
python -m det_robot.cli extrair --manual --headless
```

### Problema: Snap do Chromium

Se Chromium foi instalado via Snap:

```bash
# Remover snap
sudo snap remove chromium

# Instalar via apt
sudo apt install chromium-browser

# Ou instalar Chrome oficial
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

---

## 🪟 Windows Específico

### Problema: PATH do Chrome

```cmd
REM Adicionar Chrome ao PATH
setx PATH "%PATH%;C:\Program Files\Google\Chrome\Application"

REM Reiniciar CMD e testar
chrome --version
```

### Problema: Antivírus bloqueando

1. Adicione exceção para:
   - `C:\Users\SeuNome\.wdm\`
   - Pasta do Python
   - Pasta do projeto

2. Ou desabilite temporariamente

### Problema: Firewall

```cmd
REM Permitir Python no firewall
netsh advfirewall firewall add rule name="Python" dir=in action=allow program="%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
```

---

## ✅ CHECKLIST FINAL

Antes de desistir, confirme:

- [ ] Python 3.9+ instalado → `python --version`
- [ ] Selenium instalado → `pip list | grep selenium`
- [ ] webdriver-manager instalado → `pip list | grep webdriver`
- [ ] Chrome OU Firefox instalado → `google-chrome --version`
- [ ] Executou `python diagnostico_navegador.py`
- [ ] Leu as mensagens de erro COMPLETAS
- [ ] Tentou reinstalar: `pip install --upgrade selenium webdriver-manager`
- [ ] Limpou cache: `rm -rf ~/.wdm/`

---

## 📞 PRECISA DE AJUDA?

Se nada disso resolver, execute e me envie a saída:

```bash
python diagnostico_navegador.py > diagnostico.txt 2>&1
cat diagnostico.txt
```

Isso vai gerar um relatório completo do problema!
