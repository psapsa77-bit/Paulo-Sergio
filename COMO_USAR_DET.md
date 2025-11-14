# 🚀 Guia Rápido - Robô DET

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Instalação

**Windows:**
```
Execute: INSTALAR_DET.bat
```

**Linux/Mac:**
```bash
./instalar_det.sh
```

### 2️⃣ Executar

**Windows:**
```
Execute: ABRIR_DET.bat
```

**Linux/Mac:**
```bash
./abrir_det.sh
```

### 3️⃣ Acessar

Abra no navegador:
```
http://localhost:8503
```

## 📝 Passo a Passo Completo

### Passo 1: Cadastrar Empresas

1. Clique na aba **"🏢 Empresas"**
2. Preencha:
   - **Nome da Empresa**: Digite o nome
   - **CNPJ**: Digite apenas números (14 dígitos)
3. Clique em **"➕ Adicionar"**
4. Repita para cada empresa

**Exemplo:**
```
Nome: Minha Empresa Ltda
CNPJ: 12345678000199
```

### Passo 2: Processar Verificação

1. Clique na aba **"🚀 Processar"**
2. Verifique a lista de empresas cadastradas
3. Clique em **"🚀 INICIAR VERIFICAÇÃO"**
4. **Aguarde** a janela do navegador abrir
5. **Selecione** seu certificado digital quando solicitado
6. O robô fará o resto automaticamente!

### Passo 3: Ver Resultados

1. Clique na aba **"📊 Resultados"**
2. Visualize:
   - Total de empresas processadas
   - Empresas com mensagens
   - Empresas sem mensagens
   - Total de mensagens não lidas
3. **Expanda** cada empresa para ver detalhes
4. **Baixe** os relatórios (HTML ou JSON)

## 📊 Interpretando os Resultados

### Status da Empresa

- ✅ **Verde**: Sem mensagens não lidas
- ⚠️ **Amarelo**: Tem mensagens não lidas (ATENÇÃO!)
- ❌ **Vermelho**: Erro ao processar

### Detalhes da Mensagem

Para cada mensagem não lida você verá:
- 📧 **Assunto**: Título da mensagem
- 📅 **Data**: Quando foi enviada
- 👤 **Remetente**: Quem enviou
- 📎 **Anexo**: Se tem arquivo anexo

## 💡 Dicas Importantes

### ✅ Antes de Começar

- [ ] Certifique-se de ter certificado digital válido
- [ ] Verifique sua conexão com internet
- [ ] Feche outras instâncias do navegador
- [ ] Cadastre todas as empresas primeiro

### 🔐 Durante o Login

- **Aguarde** a janela do certificado aparecer
- **Selecione** o certificado correto
- **Digite** o PIN se solicitado
- **Não feche** o navegador manualmente

### 📬 Verificando Mensagens

- O robô verifica **automaticamente** cada empresa
- Você pode ver o progresso nos **logs**
- O processo pode levar alguns minutos
- **Não interrompa** durante a execução

### 💾 Salvando Resultados

**Formatos disponíveis:**

1. **HTML** - Para visualizar e imprimir
   - Design bonito e profissional
   - Pronto para apresentações
   - Fácil de compartilhar

2. **JSON** - Para processar dados
   - Formato estruturado
   - Fácil de integrar com outros sistemas
   - Contém todos os detalhes

## 🛠️ Gerenciar Empresas

### Adicionar Empresa

1. Aba **"🏢 Empresas"**
2. Preencher formulário
3. Clicar em **"➕ Adicionar"**

### Remover Empresa

1. Aba **"🏢 Empresas"**
2. Localizar a empresa
3. Clicar no botão **"🗑️"**

### Importar Lista

1. Aba **"🏢 Empresas"**
2. Seção **"Importar/Exportar"**
3. Clicar em **"📤 Importar Empresas (JSON)"**
4. Selecionar arquivo JSON

**Formato do arquivo:**
```json
[
  {
    "nome": "Empresa 1",
    "cnpj": "12345678000199"
  },
  {
    "nome": "Empresa 2",
    "cnpj": "98765432000188"
  }
]
```

### Exportar Lista

1. Aba **"🏢 Empresas"**
2. Seção **"Importar/Exportar"**
3. Clicar em **"📥 Exportar Empresas (JSON)"**

## 🔍 Personalizar para seu Portal

O portal DET pode ter estrutura diferente. Para ajustar:

### 1. Identificar Seletores

1. Abra o portal no navegador
2. Pressione **F12** (ferramentas de desenvolvedor)
3. Clique no ícone de **inspetor** (seta)
4. Clique no elemento que deseja capturar
5. No painel, clique direito → **Copy** → **Copy selector**

### 2. Atualizar Config

Edite o arquivo: `det_robot/config.py`

```python
SELETORES = {
    "btn_certificado": "seu_seletor_aqui",
    "menu_mensagens": "seu_seletor_aqui",
    "mensagens_nao_lidas": "seu_seletor_aqui",
    # ... etc
}
```

### 3. Testar

Execute novamente e verifique se funciona!

## ❓ Perguntas Frequentes

### O robô armazena minhas senhas?

❌ **NÃO!** O robô:
- Usa apenas o certificado digital do sistema
- Não armazena senhas
- Não envia dados para internet
- Tudo fica no seu computador

### Posso processar várias empresas de uma vez?

✅ **SIM!** Você pode:
- Cadastrar quantas empresas quiser
- Processar todas de uma vez
- O robô faz automaticamente

### Preciso estar presente durante o processo?

⚠️ **PARCIALMENTE**:
- Você precisa selecionar o certificado no início
- Depois o robô trabalha sozinho
- Você pode acompanhar pelos logs

### Com que frequência devo verificar?

📅 **Sugestão**:
- Diariamente: Para empresas ativas
- Semanalmente: Para empresas com menos movimento
- Configure conforme sua necessidade

### Os relatórios ficam salvos?

✅ **SIM!**
- Todos os relatórios ficam em `det_robot/results/`
- Os logs ficam em `det_robot/logs/`
- Organizados por data e hora

### Posso usar em múltiplos computadores?

✅ **SIM!**
- Copie a pasta `det_robot` para outro PC
- Instale as dependências
- Configure o certificado digital
- Pronto!

## 🐛 Resolução Rápida de Problemas

### Problema: Erro ao instalar

**Solução:**
```bash
# Verificar Python
python --version

# Se não tiver, instale:
# https://www.python.org/downloads/
```

### Problema: Certificado não aparece

**Solução:**
- Verifique se o certificado está instalado
- Teste o certificado em outro site
- Reinicie o computador

### Problema: Não encontra mensagens

**Solução:**
- Verifique se tem mensagens no portal manualmente
- Pode ser necessário ajustar os seletores
- Consulte a seção "Personalizar para seu Portal"

### Problema: Processo trava

**Solução:**
- Aumente os timeouts em `config.py`
- Verifique sua internet
- Tente novamente

### Problema: Erro de permissão

**Windows:**
```bash
# Execute como Administrador
```

**Linux/Mac:**
```bash
# Ajuste permissões
chmod +x *.sh
```

## 📞 Precisa de Ajuda?

1. ✅ Leia este guia completo
2. ✅ Verifique os logs em `det_robot/logs/`
3. ✅ Consulte o README em `det_robot/README.md`
4. ✅ Teste com uma empresa primeiro
5. ✅ Verifique se o portal mudou sua estrutura

## 🎯 Checklist de Uso

Antes de cada execução:

- [ ] Certificado digital válido e instalado
- [ ] Internet funcionando
- [ ] Empresas cadastradas
- [ ] Navegador fechado (outras instâncias)
- [ ] Espaço em disco suficiente

Durante a execução:

- [ ] Selecionou o certificado correto
- [ ] Aguardando sem interromper
- [ ] Acompanhando os logs
- [ ] Sem fechar o navegador

Após a execução:

- [ ] Verificou os resultados
- [ ] Baixou os relatórios
- [ ] Verificou mensagens importantes
- [ ] Arquivou os documentos

## 🎉 Pronto!

Agora você está pronto para usar o **Robô DET**!

**Dica final:** Comece com 1 ou 2 empresas para se familiarizar com o processo, depois adicione mais! 🚀

---

**Precisa de mais ajuda?** Consulte o README completo em `det_robot/README.md`
