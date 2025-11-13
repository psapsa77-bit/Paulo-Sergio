# 📜 Como Instalar Certificado Digital no Windows

Para que o robô funcione corretamente usando Chrome ou Edge, você precisa **instalar seu certificado .pfx no Windows**.

---

## 🚀 Instalação Rápida (3 passos)

### Passo 1: Abrir o arquivo .pfx

1. Localize seu arquivo de certificado (ex: `certificado.pfx` ou `meu_certificado.pfx`)
2. **Clique duas vezes** no arquivo `.pfx`
3. Uma janela "Assistente para Importação de Certificados" abrirá

### Passo 2: Seguir o assistente

1. **Localização do Armazenamento**:
   - Selecione: ✅ **"Usuário Atual"**
   - Clique em "Avançar"

2. **Arquivo para Importar**:
   - O caminho do arquivo já estará preenchido
   - Clique em "Avançar"

3. **Senha do Certificado**:
   - Digite a **senha do seu certificado**
   - ✅ Marque: **"Marcar esta chave como exportável"**
   - ✅ Marque: **"Incluir todas as propriedades estendidas"**
   - Clique em "Avançar"

4. **Armazenamento de Certificados**:
   - Selecione: ✅ **"Colocar todos os certificados no repositório a seguir"**
   - Clique em "Procurar..."
   - Selecione: **"Pessoal"**
   - Clique em "OK"
   - Clique em "Avançar"

5. **Conclusão**:
   - Revise as configurações
   - Clique em "Concluir"
   - Você verá uma mensagem: **"A importação foi bem-sucedida"**
   - Clique em "OK"

### Passo 3: Configurar o robô

No arquivo `.env`, configure para usar Chrome ou Edge:

```env
BROWSER_TYPE=chrome
# ou
BROWSER_TYPE=msedge
```

---

## ✅ Verificar se Certificado Está Instalado

### Método 1: Gerenciador de Certificados

1. Pressione `Win + R`
2. Digite: `certmgr.msc`
3. Pressione Enter
4. Navegue: **Pessoal → Certificados**
5. Procure seu certificado na lista

Você deve ver:
- Nome do titular (sua empresa/CPF)
- Emissor (ex: AC CERTISIGN, AC SERASA, etc.)
- Data de validade

### Método 2: Chrome/Edge

1. Abra o Chrome ou Edge
2. Digite na barra de endereços:
   - Chrome: `chrome://settings/certificates`
   - Edge: `edge://settings/privacy`
3. Clique em "Gerenciar certificados"
4. Aba "Pessoal" → Você deve ver seu certificado

---

## 🔧 Solução de Problemas

### Erro: "A senha especificada está incorreta"

**Causa**: Você digitou a senha errada do certificado.

**Solução**:
- Tente novamente com a senha correta
- A senha foi definida quando o certificado foi criado/exportado

---

### Erro: "Não é possível importar o certificado"

**Causa**: Arquivo .pfx corrompido ou formato inválido.

**Solução**:
- Verifique se o arquivo é realmente .pfx (não .cer ou .pem)
- Tente baixar o certificado novamente
- Entre em contato com quem emitiu o certificado

---

### Certificado não aparece no Chrome/Edge

**Causa**: Certificado instalado no local errado.

**Solução**:
1. Remova o certificado atual
2. Reinstale seguindo o guia acima
3. Certifique-se de selecionar **"Pessoal"** como repositório

---

### Remover Certificado

Se precisar remover e reinstalar:

1. Pressione `Win + R`
2. Digite: `certmgr.msc`
3. Navegue: **Pessoal → Certificados**
4. Clique com botão direito no certificado
5. Selecione **"Excluir"**
6. Confirme
7. Reinstale seguindo o guia acima

---

## 🎯 Configuração Final

Depois de instalar o certificado no Windows, configure o `.env`:

```env
# ============================================
# CERTIFICADO DIGITAL
# ============================================
# O caminho não é mais necessário quando usa Chrome/Edge!
# Mas mantenha para referência ou se voltar a usar Chromium
CERT_PATH=certificados/certificado.pfx
CERT_PASSWORD=sua_senha_aqui

# ============================================
# NAVEGADOR
# ============================================
# IMPORTANTE: Use chrome ou msedge!
BROWSER_TYPE=chrome

# Modo visual (para ver o que está acontecendo)
HEADLESS=False
```

---

## 💡 Diferenças entre Navegadores

| Navegador | Acesso a Certificados | Recomendado |
|-----------|----------------------|-------------|
| **Chrome** | ✅ Sim (usa os do Windows) | ✅ **SIM** |
| **Edge** | ✅ Sim (usa os do Windows) | ✅ **SIM** |
| **Chromium** | ❌ Não (precisa configurar manual) | ⚠️ Não recomendado |
| **Firefox** | ⚠️ Limitado | ❌ Não usar |

---

## 🎓 Resumo

1. **Instale o certificado no Windows** (clique duas vezes no .pfx)
2. **Configure** `BROWSER_TYPE=chrome` no `.env`
3. **Execute o robô** - Ele usará o certificado do sistema automaticamente!

**Não precisa mais converter para .pem ou configurar manualmente!** 🎉

---

## 📞 Ajuda

Se tiver problemas:

1. Verifique se o certificado está em **Pessoal** (certmgr.msc)
2. Verifique se não está expirado
3. Teste abrir um site que requer certificado no Chrome/Edge manualmente
4. Veja os logs do robô para mais detalhes

---

**Atualizado em**: 2025-01-13
**Versão**: 2.0.0
