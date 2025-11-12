# 🚀 Guia Rápido - Robô FGTS Digital

## Instalação e Configuração em 5 Minutos

### Passo 1: Instalar Dependências

```bash
cd fgts_robot

# Criar ambiente virtual (RECOMENDADO)
python3 -m venv venv

# Ativar ambiente virtual
# No Linux/macOS:
source venv/bin/activate

# No Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Instalar navegador Chromium
playwright install chromium
```

### Passo 2: Configurar Credenciais

```bash
# Copiar template de configuração
cp .env.example .env

# Editar configurações (use seu editor favorito)
nano .env  # ou: vim .env, code .env, notepad .env
```

Configure as seguintes variáveis no `.env`:

```env
CERT_PATH=certificados/seu_certificado.pfx
CERT_PASSWORD=sua_senha_do_certificado
HEADLESS=False
TIMEOUT=30000
LOG_LEVEL=INFO
```

### Passo 3: Adicionar Certificado

```bash
# Copiar seu certificado para a pasta
cp /caminho/do/seu/certificado.pfx certificados/
```

### Passo 4: Executar o Robô

#### Modo Interativo
```bash
python main.py
```

#### Com CNPJs Específicos
```bash
python main.py --cnpjs 12345678000190 98765432000110
```

#### De um Arquivo
```bash
# Criar arquivo com CNPJs
cat > lista_cnpjs.txt <<EOF
12345678000190
98765432000110
11122233000144
EOF

# Executar
python main.py --arquivo lista_cnpjs.txt
```

#### Ver Ajuda
```bash
python main.py --help
```

---

## 🐛 Solução de Problemas Comuns

### Erro: "ModuleNotFoundError: No module named 'dotenv'"

**Solução:** Instalar dependências
```bash
pip install -r requirements.txt
```

### Erro: "attempted relative import with no known parent package"

**Solução:** Execute o script a partir do diretório `fgts_robot/`
```bash
cd fgts_robot
python main.py
```

Ou use o caminho completo:
```bash
python fgts_robot/main.py
```

### Erro: "Certificado não encontrado"

**Solução:** Verifique o caminho no `.env` e se o arquivo existe
```bash
ls -la certificados/
```

### Erro: "playwright: command not found"

**Solução:** Instalar playwright
```bash
pip install playwright
playwright install chromium
```

### Navegador não abre (modo headless)

**Solução:** Configurar modo visual no `.env`
```env
HEADLESS=False
```

---

## 📖 Uso Programático

Se quiser usar o robô em seu próprio código Python:

```python
import sys
from pathlib import Path

# Adicionar diretório fgts_robot ao path
sys.path.insert(0, str(Path('fgts_robot').absolute()))

from robo_fgts import RoboFGTS

# Inicializar e usar
robo = RoboFGTS()
robo.processar_clientes(['12345678000190'])
```

---

## 🎯 Exemplos Práticos

Execute o arquivo de exemplos para ver diferentes formas de uso:

```bash
python exemplo_uso.py
```

---

## 📂 Estrutura de Saída

### Resultados
Os arquivos Excel são salvos em:
```
resultados/fgts_consulta_2025-11-12_14-30-00.xlsx
```

### Logs
Os logs de execução ficam em:
```
logs/fgts_robot_20251112_143000.log
```

### Screenshots (em caso de erro)
```
logs/screenshots/erro_20251112_143000.png
```

---

## ⚡ Dicas para Primeira Execução

1. **Teste em modo visual primeiro** (HEADLESS=False) para ver o que está acontecendo
2. **Comece com apenas 1 CNPJ** para testar
3. **Verifique os logs** se algo der errado
4. **Use o modo --help** para ver todas as opções

Exemplo de primeira execução:
```bash
# Configure modo visual
echo "HEADLESS=False" >> .env

# Teste com um CNPJ
python main.py --cnpjs 12345678000190

# Verifique resultado
ls -lh resultados/
```

---

## 📞 Precisa de Ajuda?

- Consulte o [README.md](README.md) completo
- Verifique os [exemplos](exemplo_uso.py)
- Execute o verificador: `python verificar_instalacao.py`

---

**Pronto para começar!** 🚀
