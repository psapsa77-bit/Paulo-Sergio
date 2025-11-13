# 🎓 Guia para Iniciantes - Robô FGTS Digital

**Bem-vindo!** Este guia vai te ajudar a instalar e usar o robô, **mesmo sem conhecimento de programação**. 😊

---

## 📋 O Que Você Vai Precisar

Antes de começar, certifique-se de ter:

- ✅ **Computador** com Windows, Linux ou macOS
- ✅ **Certificado Digital A1** (arquivo .pfx)
- ✅ **Senha do certificado**
- ✅ **Conexão com internet**

---

## 🚀 Instalação Automática (SUPER FÁCIL!)

### **Para Windows** 🪟

1. **Abra a pasta do robô:**
   - Vá até a pasta `fgts_robot`
   - Você verá vários arquivos

2. **Clique duas vezes no arquivo:**
   ```
   INSTALAR_TUDO.bat
   ```

3. **Aguarde a instalação:**
   - Uma janela preta vai abrir
   - O script vai instalar tudo automaticamente
   - Pode demorar **5 a 10 minutos**
   - ☕ Pegue um café enquanto espera!

4. **Pronto!** Quando terminar, você verá:
   ```
   ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
   ```

### **Para Linux/macOS** 🐧🍎

1. **Abra o Terminal:**
   - No Linux: Ctrl + Alt + T
   - No macOS: Cmd + Espaço, digite "Terminal"

2. **Vá para a pasta do robô:**
   ```bash
   cd fgts_robot
   ```

3. **Execute o instalador:**
   ```bash
   chmod +x INSTALAR_TUDO.sh
   ./INSTALAR_TUDO.sh
   ```

4. **Aguarde a instalação:**
   - Vai demorar **5 a 10 minutos**
   - ☕ Pegue um café!

5. **Pronto!** Quando terminar, você verá:
   ```
   ✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!
   ```

---

## 📝 Configuração Pós-Instalação

Após a instalação automática, você precisa fazer **apenas 2 coisas**:

### **1. Adicionar seu Certificado Digital**

**Windows:**
1. Copie seu arquivo `.pfx` (certificado)
2. Cole na pasta `certificados\` dentro de `fgts_robot`

**Linux/macOS:**
```bash
cp /caminho/do/seu/certificado.pfx certificados/
```

### **2. Configurar a Senha do Certificado**

**Windows:**
1. Abra o arquivo `.env` com o **Bloco de Notas**
2. Encontre a linha:
   ```
   CERT_PASSWORD=sua_senha_aqui
   ```
3. Troque `sua_senha_aqui` pela **senha do seu certificado**
4. Salve o arquivo (Ctrl + S)

**Linux/macOS:**
```bash
nano .env
```
- Encontre `CERT_PASSWORD=`
- Digite sua senha
- Salve: Ctrl + O, Enter, Ctrl + X

**Exemplo:**
```env
CERT_PATH=certificados/meu_certificado.pfx
CERT_PASSWORD=MinhaS3nh@123
HEADLESS=False
```

---

## ✅ Verificar se Está Tudo OK

Antes de usar o robô, vamos verificar se tudo foi instalado corretamente:

**Windows:**
```cmd
python diagnosticar.py
```

**Linux/macOS:**
```bash
python diagnosticar.py
```

**O que você deve ver:**

```
╔═══════════════════════════════════════════════════════════════╗
║        🔍 DIAGNÓSTICO DO ROBÔ FGTS DIGITAL 🔍                ║
╚═══════════════════════════════════════════════════════════════╝

📌 Teste 1: Versão do Python
   ✓ Python 3.10+ OK

📌 Teste 2: Dependências Python
   ✓ playwright      - Automação web
   ✓ pandas          - Manipulação de dados
   [...]

✅ TODOS OS TESTES PASSARAM!
```

**Se aparecer algum ❌ (erro):**
- Leia a mensagem de erro
- Siga as instruções que o script mostrar
- Ou pule para a seção [Problemas Comuns](#-problemas-comuns) abaixo

---

## 🎨 Usando o Robô - Interface Web (RECOMENDADO)

A forma **mais fácil** de usar o robô é através da interface web!

### **Passo 1: Abrir a Interface**

**Windows:**
- Clique duas vezes em:
  ```
  ABRIR_FGTS.bat
  ```

**Linux/macOS:**
```bash
./abrir_fgts.sh
```

### **Passo 2: Usar a Interface**

1. **O navegador vai abrir automaticamente** em `http://localhost:8501`

2. **Configure na Barra Lateral:**
   - Faça **upload do certificado** (ou ele já aparece se você colocou na pasta)
   - Digite a **senha do certificado**

3. **Adicione os CNPJs:**
   - Você pode:
     - **Digitar** um por um
     - **Colar** uma lista inteira
     - **Fazer upload** de um arquivo .txt

4. **Clique em "PROCESSAR"**
   - Aguarde o robô fazer o trabalho
   - Você verá uma **barra de progresso**

5. **Baixe o Resultado:**
   - Vá na aba **"Resultados"**
   - Clique em **"BAIXAR ARQUIVO EXCEL"**
   - Pronto! 🎉

---

## 💻 Usando o Robô - Linha de Comando

Se você prefere linha de comando (terminal):

### **Modo Mais Simples:**

```bash
python main.py
```

O robô vai te perguntar os CNPJs um por um.

### **Processar CNPJs Específicos:**

```bash
python main.py --cnpjs 12345678000190 98765432000110
```

### **Processar de um Arquivo:**

1. Crie um arquivo `meus_cnpjs.txt` com os CNPJs (um por linha):
   ```
   12345678000190
   98765432000110
   11122233000144
   ```

2. Execute:
   ```bash
   python main.py --arquivo meus_cnpjs.txt
   ```

### **Ver Todas as Opções:**

```bash
python main.py --help
```

---

## 📊 Onde Ficam os Resultados?

Os arquivos Excel gerados ficam em:
```
fgts_robot/resultados/
```

Exemplo:
```
fgts_consulta_2025-11-13_18-45-30.xlsx
```

Cada aba do Excel tem os dados de uma empresa!

---

## ❓ Problemas Comuns

### **Problema: "Python não está instalado"**

**Solução:**
1. Baixe o Python: https://www.python.org/downloads/
2. **IMPORTANTE:** Marque a opção **"Add Python to PATH"** durante a instalação
3. Reinicie o computador
4. Execute o instalador novamente

### **Problema: "Certificado não encontrado"**

**Solução:**
1. Verifique se o arquivo `.pfx` está na pasta `certificados/`
2. Abra o arquivo `.env` e confira se o caminho está correto:
   ```env
   CERT_PATH=certificados/nome_do_seu_certificado.pfx
   ```

### **Problema: "Certificado inválido"**

**Possíveis causas:**
- **Senha errada:** Verifique a senha no arquivo `.env`
- **Certificado vencido:** Obtenha um novo certificado
- **Certificado A3:** O robô só funciona com certificado **A1** (arquivo .pfx)

### **Problema: "Erro ao acessar portal FGTS"**

**Soluções:**
1. **Teste sua conexão:**
   ```bash
   python testar_conexao.py
   ```

2. **Tente acessar manualmente:**
   - Abra o navegador
   - Acesse: https://fgtsdigital.sistema.gov.br/portal
   - Veja se o site está funcionando

3. **Verifique firewall:**
   - O firewall pode estar bloqueando
   - Libere acesso ao domínio `fgtsdigital.sistema.gov.br`

### **Problema: Interface web não abre**

**Solução:**
1. **Certifique-se que o Streamlit está instalado:**
   ```bash
   pip install streamlit
   ```

2. **Tente executar manualmente:**
   ```bash
   streamlit run web_fgts.py
   ```

3. **Verifique se a porta 8501 está livre:**
   - Feche outros programas que possam estar usando a porta
   - Ou tente uma porta diferente:
     ```bash
     streamlit run web_fgts.py --server.port 8502
     ```

---

## 🆘 Precisa de Mais Ajuda?

### **1. Execute o Diagnóstico**
```bash
python diagnosticar.py
```
Ele vai te dizer **exatamente** o que está errado.

### **2. Teste a Conexão**
```bash
python testar_conexao.py
```
Verifica se consegue acessar o portal FGTS.

### **3. Veja os Logs**
```bash
# Windows
type logs\fgts_robot_*.log

# Linux/macOS
cat logs/fgts_robot_*.log
```

### **4. Consulte a Documentação**
- **README.md** - Documentação completa
- **QUICKSTART.md** - Guia rápido
- **TROUBLESHOOTING.md** - Solução de problemas detalhada

### **5. Screenshots de Erro**
Se der erro, o robô tira um print automático em:
```
logs/screenshots/
```

---

## ✅ Checklist Final

Antes de usar o robô pela primeira vez, confirme:

- [ ] ✅ Python 3.10+ instalado
- [ ] ✅ Executei `INSTALAR_TUDO.bat` ou `INSTALAR_TUDO.sh`
- [ ] ✅ Certificado (.pfx) na pasta `certificados/`
- [ ] ✅ Senha configurada no arquivo `.env`
- [ ] ✅ `python diagnosticar.py` passou todos os testes
- [ ] ✅ `python testar_conexao.py` conseguiu acessar o portal

**Se todos os itens estão OK, você está pronto para usar o robô!** 🎉

---

## 🎯 Resumo Rápido (TL;DR)

1. Execute `INSTALAR_TUDO.bat` (Windows) ou `./INSTALAR_TUDO.sh` (Linux/macOS)
2. Copie seu certificado `.pfx` para `certificados/`
3. Edite `.env` e coloque a senha do certificado
4. Execute `python diagnosticar.py` para verificar
5. Clique duas vezes em `ABRIR_FGTS.bat` para usar a interface web
6. Pronto! 🚀

---

## 💡 Dicas Importantes

1. **Use a interface web** - É muito mais fácil que a linha de comando
2. **Teste com 1 CNPJ primeiro** - Antes de processar vários
3. **Modo visual** - Configure `HEADLESS=False` no `.env` para ver o navegador
4. **Mantenha backups** - Os arquivos em `resultados/` não são deletados
5. **Logs são seus amigos** - Se der erro, olhe os logs em `logs/`

---

**Pronto! Agora você sabe usar o Robô FGTS Digital! 🎉**

Se tiver qualquer dúvida, execute `python diagnosticar.py` e siga as instruções.

Boa sorte! 🍀
