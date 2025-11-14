# 🚀 Analisador de Rescisões - Versão Standalone

## ✨ A Forma Mais Simples de Usar!

Este é um **arquivo HTML único** que funciona diretamente no navegador, sem instalações!

## 📥 Como Usar (3 passos simples)

### 1️⃣ Baixar o Arquivo
- Faça download do arquivo: `analisador-rescisao-standalone.html`

### 2️⃣ Abrir no Navegador
- **Duplo clique** no arquivo **OU**
- Clique com botão direito → "Abrir com" → Chrome/Edge/Firefox

### 3️⃣ Pronto! 🎉
- O aplicativo está funcionando!
- Clique em **"Ver Exemplo"** para ver uma demonstração
- Clique em **"Nova Análise"** para analisar seus documentos

---

## 🎯 Funcionalidades

✅ **Ver Exemplo** - Carrega dados de demonstração (Wanessa Nascimento Sousa)
✅ **Nova Análise** - Faça upload de PDF do Termo de Rescisão
✅ **Análise com IA** - Processamento automático com Claude API
✅ **Gerar Relatório** - Exporta HTML formatado para impressão/PDF
✅ **Armazenamento Local** - Seus dados ficam salvos no navegador

---

## ⚙️ Configurar API Claude (Opcional)

Para usar a análise automática com IA:

1. **Obtenha uma API Key** em: https://console.anthropic.com/

2. **Abra o arquivo** `analisador-rescisao-standalone.html` em um editor de texto

3. **Procure pela linha** (~linha 327):
```javascript
headers: {
    "Content-Type": "application/json",
    // ADICIONE SUA API KEY AQUI:
    // "x-api-key": "sua_api_key_aqui",
    // "anthropic-version": "2023-06-01"
},
```

4. **Descomente e adicione** sua API key:
```javascript
headers: {
    "Content-Type": "application/json",
    "x-api-key": "sk-ant-api03-XXXXX", // Sua API key aqui
    "anthropic-version": "2023-06-01"
},
```

5. **Salve o arquivo** e recarregue no navegador

**Nota:** Se não configurar a API, o aplicativo usará automaticamente dados de exemplo!

---

## 🌐 Sem Internet?

O aplicativo precisa de conexão apenas para:
- Carregar React, Tailwind CSS (CDN)
- Chamar API Claude (se configurada)

**Primeira vez:** Abra com internet para carregar as bibliotecas
**Depois:** O navegador guarda em cache e funciona offline (exceto API)

---

## 📱 Compatibilidade

Funciona em todos os navegadores modernos:
- ✅ Google Chrome
- ✅ Microsoft Edge
- ✅ Mozilla Firefox
- ✅ Safari
- ✅ Opera

**Versões mínimas recomendadas:** Chrome 90+, Edge 90+, Firefox 88+

---

## 🔒 Segurança e Privacidade

- ✅ **Dados locais** - Tudo fica no seu navegador
- ✅ **Sem servidor** - Nada é enviado para terceiros (exceto Claude API se configurada)
- ✅ **Código aberto** - Você pode inspecionar o código HTML
- ⚠️ **API Key** - Nunca compartilhe sua chave da Anthropic

---

## 💾 Como Gerar PDF do Relatório

1. Clique em **"Gerar Relatório"** em uma análise
2. Clique em **"Copiar HTML"**
3. Abra o **Bloco de Notas** (ou outro editor de texto)
4. Cole o código (Ctrl+V)
5. Salve como: `relatorio-rescisao.html`
6. Abra o arquivo no navegador
7. Pressione **Ctrl+P** para imprimir
8. Escolha **"Salvar como PDF"**

---

## 🆚 Diferença das Versões

| Recurso | Standalone (HTML) | React App (NPM) |
|---------|-------------------|-----------------|
| **Instalação** | ❌ Nenhuma | ✅ Node.js + NPM |
| **Usar** | Duplo clique | `npm run dev` |
| **Velocidade** | ⚡ Instantâneo | 🐢 Build necessário |
| **Funcionalidades** | ✅ Todas | ✅ Todas |
| **Recomendado para** | Usuários finais | Desenvolvedores |

---

## 🐛 Problemas Comuns

### Tela em branco
- Verifique se tem internet na primeira vez
- Abra o Console (F12) e veja se há erros
- Tente outro navegador

### API não funciona
- Verifique se adicionou a API key corretamente
- Confirme que tem créditos na conta Anthropic
- O app usa dados de exemplo se a API falhar

### Não consegue fazer upload
- Verifique se o arquivo é PDF válido
- Tamanho máximo: 10MB
- PDF não pode estar protegido por senha

---

## 📞 Suporte

- **Código não funciona?** Abra o Console do navegador (F12) e veja os erros
- **Dúvidas sobre rescisão?** Consulte um advogado trabalhista
- **API Claude?** Veja documentação em: https://docs.anthropic.com/

---

## 📄 Licença

Fornecido como está, sem garantias. Adapte conforme necessário.

---

**🎉 Aproveite a forma mais simples de analisar rescisões trabalhistas!**

Desenvolvido com ❤️ usando React + Tailwind CSS + Claude AI
