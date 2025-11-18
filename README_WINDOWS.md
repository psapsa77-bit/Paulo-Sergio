# 🪟 DET Robot - Guia para Windows

## 📥 Como Baixar e Instalar

### Passo 1: Baixar os Arquivos

Baixe **TODOS** os arquivos do repositório para uma pasta no seu computador.

Exemplo: `C:\Users\SeuNome\DET_Robot\`

### Passo 2: Verificar Python

Abra o **Prompt de Comando** (CMD):
- Pressione `Win + R`
- Digite: `cmd`
- Pressione Enter

Digite o comando:
```cmd
python --version
```

**Se aparecer algo como `Python 3.9.0` ou superior:** ✅ Ótimo! Pule para o Passo 3

**Se aparecer erro:** ❌ Você precisa instalar o Python:

1. Acesse: https://www.python.org/downloads/
2. Baixe o instalador mais recente
3. **IMPORTANTE:** Marque a opção **"Add Python to PATH"** durante a instalação
4. Instale e reinicie o computador
5. Teste novamente com `python --version`

### Passo 3: Executar o Instalador

No **Prompt de Comando**, navegue até a pasta onde baixou os arquivos:

```cmd
cd C:\Users\SeuNome\DET_Robot
```

Execute o instalador:

```cmd
INSTALAR_TUDO.bat
```

**O que vai acontecer:**
- ✅ Verifica Python
- ✅ Verifica navegador (Chrome ou Firefox)
- ✅ Instala todas as bibliotecas necessárias
- ⏱️ Demora uns 3-5 minutos

**Se pedir para instalar um navegador:**
- Chrome: https://www.google.com/chrome/
- Firefox: https://www.mozilla.org/firefox/

---

## 🚀 Como Usar

### Opção 1: Duplo Clique (Mais Fácil)

1. Vá na pasta onde estão os arquivos
2. Dê duplo clique em: **`USAR_DET_ROBOT.bat`**
3. Pronto! O programa vai abrir

### Opção 2: Via CMD

```cmd
cd C:\Users\SeuNome\DET_Robot
USAR_DET_ROBOT.bat
```

### O que vai acontecer:

1. Uma janela do navegador vai abrir
2. Acesse: **http://localhost:8502**
3. Você verá a interface do DET Robot

---

## 🎯 Usando a Interface

### 1️⃣ Iniciar Navegador

- Clique no botão **"1️⃣ Iniciar Navegador"**
- Um navegador (Chrome/Firefox) vai abrir

### 2️⃣ Fazer Login

**Escolha o método:**

**✅ Recomendado: Manual**
- Marque: "Manual"
- Clique: "2️⃣ Fazer Login"
- O navegador abrirá a página do DET
- Faça login normalmente como você sempre faz
- Aguarde até aparecer "Login realizado com sucesso!"

**Automático (opcional):**
- Marque: "Automático (Gov.br)"
- Digite seu CPF
- Digite sua senha
- Clique: "2️⃣ Fazer Login"
- **Atenção:** Se tiver captcha ou 2FA, use o modo Manual

### 3️⃣ Extrair Mensagens

- Clique: **"3️⃣ Extrair Mensagens"**
- Aguarde alguns segundos
- As mensagens aparecerão na tela

### 4️⃣ Ver os Resultados

Os arquivos serão salvos automaticamente em:

```
C:\Users\SeuNome\DET_Robot\dados_det\
```

Você terá:
- 📄 **Arquivo JSON** - Dados completos
- 📊 **Arquivo CSV** - Para Excel
- 📗 **Arquivo Excel** - Com formatação
- 📝 **Arquivo TXT** - Relatório em texto

---

## ⚙️ Configurações (Barra Lateral)

### Navegador
- **Auto:** Detecta automaticamente
- **Chrome:** Força usar Chrome
- **Firefox:** Força usar Firefox

### Modo headless
- ❌ Desmarcado: Você vê o navegador (recomendado)
- ✅ Marcado: Navegador invisível (mais rápido)

### Extração
- **Apenas não lidas:** ✅ Marca
- **Limite de mensagens:** 100 (padrão)

### Armazenamento
- **Formatos:** JSON, CSV, Excel, Texto
- **Pasta:** Onde salvar os arquivos

---

## ❓ Problemas Comuns no Windows

### Problema 1: "Python não encontrado"

**Erro ao executar `python --version`**

**Solução:**

1. Baixe Python: https://www.python.org/downloads/
2. Durante instalação: **MARQUE** "Add Python to PATH"
3. Reinicie o computador
4. Tente novamente

### Problema 2: "pip não é reconhecido"

**Solução:**

```cmd
python -m pip install --upgrade pip
```

### Problema 3: "Navegador não abre"

**Execute o teste:**

```cmd
python teste_navegador_simples.py
```

Siga as instruções que aparecerem.

**Ou instale Chrome:**
https://www.google.com/chrome/

### Problema 4: "Selenium não instalado"

**Solução:**

```cmd
pip install selenium webdriver-manager
```

### Problema 5: "Erro de permissão"

**Execute o CMD como Administrador:**

1. Pressione `Win + R`
2. Digite: `cmd`
3. Pressione `Ctrl + Shift + Enter` (abre como admin)
4. Execute o instalador novamente

### Problema 6: "ChromeDriver incompatível"

**Solução:**

```cmd
pip install --upgrade webdriver-manager
```

Depois teste:

```cmd
python teste_navegador_simples.py
```

### Problema 7: Firewall ou Antivírus bloqueia

**Solução:**

1. Adicione exceção no antivírus para:
   - Python
   - A pasta do DET Robot
   - ChromeDriver

2. Ou desabilite temporariamente o antivírus

---

## 🔧 Reinstalar do Zero

Se nada funcionar, faça uma reinstalação limpa:

```cmd
REM 1. Desinstalar pacotes
pip uninstall selenium webdriver-manager streamlit -y

REM 2. Limpar cache
rmdir /s /q %USERPROFILE%\.wdm

REM 3. Reinstalar
INSTALAR_TUDO.bat
```

---

## 📂 Estrutura de Pastas no Windows

```
C:\Users\SeuNome\DET_Robot\
│
├── det_robot\                  (módulos Python)
│   ├── __init__.py
│   ├── browser.py
│   ├── auth.py
│   └── ...
│
├── dados_det\                  (arquivos extraídos - criado automaticamente)
│   ├── extracao_det_20250116_143022.json
│   ├── mensagens_det_20250116_143022.csv
│   └── ...
│
├── INSTALAR_TUDO.bat          ⭐ Execute primeiro (uma vez)
├── USAR_DET_ROBOT.bat         ⭐ Execute sempre que quiser usar
├── run_det_robot.py
├── requirements.txt
└── ...
```

---

## 🎬 Passo a Passo Visual

```
1. BAIXAR ARQUIVOS
   ↓
2. ABRIR CMD
   ↓
3. NAVEGAR ATÉ A PASTA
   cd C:\Users\SeuNome\DET_Robot
   ↓
4. EXECUTAR INSTALADOR
   INSTALAR_TUDO.bat
   ↓
5. AGUARDAR 3-5 MINUTOS
   ↓
6. EXECUTAR PROGRAMA
   USAR_DET_ROBOT.bat
   ↓
7. USAR INTERFACE WEB
   http://localhost:8502
```

---

## 💡 Dicas para Windows

1. **Use o Modo Manual de login** - Mais fácil e confiável

2. **Mantenha o CMD aberto** - Não feche enquanto usa

3. **Verifique a pasta dados_det** - É onde ficam os arquivos

4. **Se der erro de encoding** - Arquivos serão salvos em UTF-8

5. **Antivírus pode bloquear** - Adicione exceção se necessário

---

## 🆘 Precisa de Mais Ajuda?

**Teste de diagnóstico completo:**
```cmd
python diagnostico_det.py
```

**Teste rápido de navegador:**
```cmd
python teste_navegador_simples.py
```

**Ver documentação completa:**
- `LEIA_PRIMEIRO.txt` (texto simples)
- `README_DET_ROBOT.md` (visual)
- `SOLUCAO_PROBLEMAS_DET.md` (troubleshooting)

---

## ⚡ Atalhos no Windows

### Criar Atalho na Área de Trabalho

1. Vá até a pasta do DET Robot
2. Clique com botão direito em `USAR_DET_ROBOT.bat`
3. Escolha: **"Criar atalho"**
4. Arraste o atalho para a Área de Trabalho

Pronto! Agora é só dar duplo clique no atalho!

### Criar Tarefa Agendada (Avançado)

Você pode agendar para extrair mensagens automaticamente:

1. Abra o **Agendador de Tarefas** do Windows
2. Crie uma nova tarefa básica
3. Configure para executar: `USAR_DET_ROBOT.bat`
4. Defina horário (ex: todo dia às 8h)

---

**Desenvolvido para Windows!** 🪟

Qualquer dúvida, veja os arquivos de ajuda ou execute os testes de diagnóstico.
