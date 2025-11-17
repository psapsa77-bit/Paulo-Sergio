# 🤖 DET Robot - Extrator Automático de Mensagens

> **Extraia mensagens do DET sem abrir uma por uma!**

## 📋 O que é isso?

O DET Robot acessa o **Domicílio Eletrônico Trabalhista (DET)** automaticamente e extrai todas as informações das mensagens **sem precisar abrir cada uma** (não marca como lida).

### ✨ O que ele faz:

✅ Faz login no DET automaticamente
✅ Lista todas as mensagens não lidas
✅ Extrai: assunto, data, prazo, tipo, remetente
✅ Salva em Excel, CSV, JSON ou texto
✅ Destaca mensagens urgentes (prazo acabando)
✅ Funciona em qualquer navegador (Chrome, Firefox)

---

## 🚀 Como Usar (SUPER FÁCIL!)

### 1️⃣ PRIMEIRA VEZ - Instalar

Abra o terminal nesta pasta e execute:

```bash
./INSTALAR_TUDO.sh
```

**Isso vai:**
- ✅ Verificar se Python está instalado
- ✅ Verificar se você tem um navegador
- ✅ Instalar tudo que precisa automaticamente
- ✅ Levar uns 2-5 minutos

---

### 2️⃣ TODA VEZ QUE FOR USAR

Execute:

```bash
./USAR_DET_ROBOT.sh
```

**Ou:**

```bash
python3 run_det_robot.py
```

Uma página web vai abrir automaticamente em: **http://localhost:8502**

---

### 3️⃣ NA INTERFACE WEB

1. **Clique em "Iniciar Navegador"**
   - Um navegador vai abrir

2. **Clique em "Fazer Login"**
   - Escolha "Manual" (mais fácil)
   - Faça login normalmente no navegador que abriu
   - Aguarde até aparecer "Login realizado com sucesso!"

3. **Clique em "Extrair Mensagens"**
   - Aguarde alguns segundos
   - As mensagens serão listadas na tela

4. **Pronto!**
   - Os arquivos foram salvos na pasta `dados_det/`
   - Você pode abrir no Excel ou visualizar na tela

---

## 📁 Arquivos Importantes

| Arquivo | Para que serve |
|---------|---------------|
| **LEIA_PRIMEIRO.txt** | Instruções básicas em texto |
| **INSTALAR_TUDO.sh** | Instalador automático (executar uma vez) |
| **USAR_DET_ROBOT.sh** | Executar o programa |
| **run_det_robot.py** | Executar via Python |
| **diagnostico_det.py** | Verificar problemas |
| **SOLUCAO_PROBLEMAS_DET.md** | Ajuda se algo der errado |

---

## 💾 Onde ficam os dados?

Depois de extrair, os arquivos ficam em: **`dados_det/`**

Você terá:
- 📄 **JSON** - Dados completos estruturados
- 📊 **CSV** - Para importar em planilhas
- 📗 **Excel** - Com formatação e cores
- 📝 **TXT** - Relatório em texto

---

## ❓ Deu problema?

### Problema 1: "Python não encontrado"

**Instale o Python:**

```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip
```

### Problema 2: "Navegador não abre"

**Execute o teste:**

```bash
python3 teste_navegador_simples.py
```

Ele vai mostrar exatamente o que está faltando.

### Problema 3: "Erro ao fazer login"

1. Use o modo **"Manual"** na interface
2. Faça login você mesmo no navegador
3. Se tiver captcha ou 2FA, é normal - resolva manualmente

### Problema 4: Outro erro

Execute o diagnóstico completo:

```bash
python3 diagnostico_det.py
```

Ou veja: **SOLUCAO_PROBLEMAS_DET.md**

---

## 🎯 Requisitos Mínimos

- 🐧 Linux (Ubuntu, Debian, Fedora, etc)
- 🐍 Python 3.9 ou mais novo
- 🌐 Navegador: Chrome, Chromium ou Firefox
- 📡 Internet

---

## 📸 Como Funciona (Visual)

```
Você               DET Robot           Site DET
  |                    |                   |
  |--[Clica Iniciar]-->|                   |
  |                    |--[Abre Chrome]--->|
  |                    |                   |
  |--[Clica Login]---->|                   |
  |                    |--[Acessa DET]---->|
  |                    |<--[Pede login]----|
  |                    |                   |
  |<-[Você faz login manualmente]-------->|
  |                    |                   |
  |--[Clica Extrair]-->|                   |
  |                    |--[Lê mensagens]-->|
  |                    |<--[Dados]---------|
  |                    |                   |
  |                    |--[Salva Excel]--->|
  |<-[Arquivo pronto]--|                   |
```

---

## 🔒 Segurança

✅ Suas senhas **NÃO** são salvas
✅ Tudo roda **no seu computador**
✅ Nenhum dado vai para internet
✅ Código aberto - você pode auditar

---

## 💡 Dicas

1. **Use modo Manual** - É mais fácil e funciona com qualquer tipo de login

2. **Marque "Apenas não lidas"** - Para extrair só as novas

3. **Deixe o navegador aberto** - Não feche enquanto extrai

4. **Verifique a pasta dados_det/** - É lá que ficam os arquivos

---

## 🆘 Precisa de Ajuda?

1. Leia: **LEIA_PRIMEIRO.txt**
2. Execute: `python3 diagnostico_det.py`
3. Veja: **SOLUCAO_PROBLEMAS_DET.md**
4. Teste: `python3 teste_navegador_simples.py`

---

## 📝 Licença

MIT License - Use à vontade!

---

**Desenvolvido para facilitar sua vida!** 🚀

Se funcionou, compartilhe com seus colegas! 😊
