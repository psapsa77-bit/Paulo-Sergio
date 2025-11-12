# 🔧 Guia de Solução de Problemas - Robô FGTS Digital

Este guia ajuda a identificar e resolver os problemas mais comuns ao usar o robô.

## 📋 Índice

- [Problemas de Conexão](#problemas-de-conexão)
- [Problemas com Certificado](#problemas-com-certificado)
- [Problemas de Login](#problemas-de-login)
- [Erros Durante Processamento](#erros-durante-processamento)
- [Problemas com Interface Web](#problemas-com-interface-web)
- [Como Obter Mais Informações](#como-obter-mais-informações)

---

## 🌐 Problemas de Conexão

### ❌ Erro: "Erro ao acessar portal FGTS"

**Sintomas:**
```
[18:17:20] Acessando FGTS Digital: https://fgtsdigital.sistema.gov.br/portal
[18:17:21] Erro ao acessar portal FGTS
[18:17:21] ❌ Processamento falhou
```

**Possíveis Causas:**

1. **Portal FGTS está fora do ar**
   - Solução: Verifique manualmente se consegue acessar https://fgtsdigital.sistema.gov.br/portal no navegador
   - Se o site estiver fora do ar, aguarde e tente novamente mais tarde

2. **Problema de conexão com internet**
   - Solução: Verifique sua conexão
   - Teste: `ping fgtsdigital.sistema.gov.br`

3. **Firewall bloqueando acesso**
   - Solução: Verifique configurações de firewall
   - Libere acesso ao domínio `fgtsdigital.sistema.gov.br`

4. **URL do portal mudou**
   - Solução: Verifique se a URL está correta acessando manualmente
   - Se mudou, atualize em `config.py` (linha 32-34)

### 🧪 Como Testar a Conexão

Execute o script de teste:

```bash
cd fgts_robot
python testar_conexao.py
```

Este script irá:
- ✅ Verificar se o portal está acessível
- ✅ Mostrar o status HTTP da resposta
- ✅ Tirar screenshot da página
- ✅ Identificar problemas específicos

---

## 🔐 Problemas com Certificado

### ❌ Erro: "Certificado não encontrado"

**Sintomas:**
```
❌ Certificado não encontrado: certificados/certificado.pfx
```

**Solução:**

1. Verifique se o certificado está na pasta correta:
```bash
ls -la certificados/
```

2. Certifique-se que o caminho no `.env` está correto:
```env
CERT_PATH=certificados/seu_certificado.pfx
```

3. Se o arquivo tem outro nome, ajuste o caminho:
```env
CERT_PATH=certificados/empresa_2024.pfx
```

### ❌ Erro: "Certificado inválido"

**Sintomas:**
```
❌ Erro ao validar certificado
```

**Possíveis Causas:**

1. **Senha incorreta**
   - Solução: Verifique a senha do certificado no `.env`
   ```env
   CERT_PASSWORD=sua_senha_correta
   ```

2. **Certificado vencido**
   - Solução: Verifique a validade do certificado
   - Obtenha um certificado válido

3. **Formato incorreto**
   - O robô suporta apenas certificados A1 em formato .pfx
   - Certificados A3 (cartão/token) não são suportados

### ❌ Erro: "Certificado não está configurado corretamente no navegador"

**Sintomas:**
```
Botão de certificado digital não encontrado na página
Possíveis causas:
  2. Certificado não está configurado corretamente no navegador
```

**Solução:**

1. **Execute em modo visual** para ver o que está acontecendo:
```env
HEADLESS=False
```

2. **Verifique se o navegador reconhece o certificado:**
   - Execute o teste de conexão: `python testar_conexao.py`
   - Observe se aparece janela de seleção de certificado

3. **Reinstale o certificado** se necessário

---

## 🔑 Problemas de Login

### ❌ Erro: "Botão de certificado digital não encontrado"

**Sintomas:**
```
Procurando botão de certificado digital...
Botão de certificado digital não encontrado na página
```

**Possíveis Causas:**

1. **Estrutura do site mudou**
   - O portal FGTS pode ter alterado a interface
   - Solução: Reporte o problema para atualização dos seletores

2. **Página não carregou completamente**
   - Solução: Aumente o timeout no `.env`:
   ```env
   TIMEOUT=60000
   ```

3. **Navegando para URL errada**
   - Verifique se está acessando a URL correta
   - Execute: `python testar_conexao.py`

**Como Diagnosticar:**

1. Execute em modo visual:
```env
HEADLESS=False
```

2. Veja o que aparece na tela quando o robô acessa o portal

3. Verifique o screenshot salvo em:
```
logs/screenshots/login_botao_cert_TIMESTAMP.png
```

### ❌ Erro: "Login falhou" ou "Timeout aguardando página após login"

**Sintomas:**
```
Tentando fazer login...
Timeout aguardando página após login
❌ Processamento falhou
```

**Solução:**

1. **Verifique a senha do certificado:**
```env
CERT_PASSWORD=senha_correta_aqui
```

2. **Execute em modo visual** para ver o processo:
```env
HEADLESS=False
```

3. **Verifique os logs** para mais detalhes:
```bash
ls -lt logs/*.log | head -1
cat logs/fgts_robot_XXXXXXXX_XXXXXX.log
```

---

## ⚙️ Erros Durante Processamento

### ❌ Erro: "Não foi possível selecionar empresa"

**Sintomas:**
```
Selecionando empresa: 12345678000190
❌ Não foi possível selecionar empresa 12345678000190
```

**Possíveis Causas:**

1. **CNPJ não tem acesso**
   - Verifique se você tem procuração para este CNPJ
   - Tente acessar manualmente pelo portal

2. **CNPJ formatação incorreta**
   - Certifique-se de usar apenas números ou formato correto
   - Válido: `12345678000190` ou `12.345.678/0001-90`

3. **Dropdown de empresas não apareceu**
   - Pode haver apenas uma empresa no certificado
   - O robô continuará normalmente

### ❌ Erro: "Nenhuma guia encontrada"

**Sintomas:**
```
Extraindo guias para CNPJ...
✗ Nenhuma guia encontrada para 12345678000190
```

**Isso não é necessariamente um erro!**

Possíveis razões:
- Empresa realmente não tem guias no período
- Empresa está em dia com FGTS
- Não há guias pendentes

Se você acha que deveria haver guias:
1. Verifique manualmente no portal
2. Execute em modo visual para ver a tela
3. Verifique os logs para mais detalhes

---

## 🌐 Problemas com Interface Web

### ❌ Erro: "ModuleNotFoundError: No module named 'streamlit'"

**Sintomas:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solução:**
```bash
pip install streamlit
```

Ou reinstale todas as dependências:
```bash
pip install -r requirements.txt
```

### ❌ Interface web não abre

**Solução:**

1. **Verifique se Streamlit está instalado:**
```bash
python -c "import streamlit; print('OK')"
```

2. **Execute manualmente:**
```bash
cd fgts_robot
streamlit run web_fgts.py
```

3. **Verifique se a porta está livre:**
```bash
# Linux/macOS
netstat -tuln | grep 8501

# Windows
netstat -an | findstr 8501
```

4. **Tente porta alternativa:**
```bash
streamlit run web_fgts.py --server.port 8502
```

### ❌ Upload de certificado não funciona

**Sintomas:**
Interface aceita o upload mas o robô não encontra o certificado

**Solução:**

1. **Verifique se o arquivo foi salvo:**
```bash
ls -la certificados/
```

2. **Use o caminho absoluto no .env:**
```env
CERT_PATH=/caminho/completo/para/certificados/certificado.pfx
```

3. **Ou copie manualmente:**
```bash
cp /caminho/do/certificado.pfx certificados/
```

---

## 🔍 Como Obter Mais Informações

### 1. Verificar Logs Detalhados

Os logs ficam em `logs/`. O mais recente:
```bash
ls -lt logs/*.log | head -1
```

Ver conteúdo:
```bash
tail -100 logs/fgts_robot_XXXXXXXX_XXXXXX.log
```

### 2. Ativar Modo DEBUG

No arquivo `.env`:
```env
LOG_LEVEL=DEBUG
```

Isso mostrará muito mais informações nos logs.

### 3. Ver Screenshots de Erro

Screenshots automáticos são salvos em caso de erro:
```bash
ls -lt logs/screenshots/
```

Abra as imagens para ver exatamente o que o robô estava vendo.

### 4. Executar em Modo Visual

Edite `.env`:
```env
HEADLESS=False
```

Você verá o navegador em ação e poderá identificar onde está travando.

### 5. Executar Teste de Conexão

```bash
python testar_conexao.py
```

Este script faz um diagnóstico completo da conexão com o portal.

---

## 🆘 Ainda com Problemas?

Se após seguir este guia você ainda tiver problemas:

### 1. Colete Informações

Execute e salve a saída:
```bash
python verificar_instalacao.py > diagnostico.txt
python testar_conexao.py >> diagnostico.txt
```

### 2. Verifique os Logs

Copie as últimas 50 linhas do log mais recente:
```bash
tail -50 logs/*.log
```

### 3. Tire Screenshots

Se houver erro visual, tire prints da tela ou use os screenshots em `logs/screenshots/`

### 4. Informações do Ambiente

```bash
python --version
pip list | grep -E "(playwright|streamlit|pandas|cryptography)"
```

### 5. Reporte o Problema

Crie uma issue no GitHub com:
- Descrição do problema
- Logs (sem informações sensíveis!)
- Screenshots
- Passos para reproduzir

---

## ✅ Checklist de Verificação Rápida

Antes de processar, verifique:

- [ ] Certificado está na pasta `certificados/`
- [ ] Senha do certificado está correta no `.env`
- [ ] Consegue acessar https://fgtsdigital.sistema.gov.br/portal no navegador
- [ ] Dependências estão instaladas (`pip install -r requirements.txt`)
- [ ] Playwright browser está instalado (`playwright install chromium`)
- [ ] CNPJs são válidos (14 dígitos)
- [ ] Tem procuração eletrônica para os CNPJs

Execute o teste:
```bash
python testar_conexao.py
```

Se o teste passar, o robô deve funcionar! 🎉

---

**Dica:** Mantenha este guia salvo para consulta rápida! 📌
