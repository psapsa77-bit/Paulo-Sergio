# 🚀 Guia Rápido - Robô DET v2.0

> **Novo!** Versão 2.0 com suporte aprimorado para certificados digitais

## ⚡ Início Rápido (3 passos)

### 1️⃣ Instalação (apenas uma vez)

**Windows:**
```
Clique duas vezes em: INSTALAR_DET.bat
```

Aguarde 2-5 minutos e pronto!

### 2️⃣ Executar o Robô

**Windows:**
```
Clique duas vezes em: ABRIR_DET.bat
```

Uma página web abrirá automaticamente em seu navegador.

### 3️⃣ Usar

1. Digite os CNPJs das empresas
2. Clique em "Processar Empresas"
3. Selecione seu certificado digital
4. Aguarde os resultados!

## 📝 Passo a Passo Detalhado

### Passo 1: Adicionar CNPJs das Empresas

Na interface web, você tem **duas opções**:

#### Opção A: Digitar CNPJs

Digite os CNPJs na caixa de texto, um por linha:

```
12345678000190
98765432000188
11223344000155
```

Você também pode incluir o nome da empresa:

```
12345678000190,Minha Empresa Ltda
98765432000188,Outra Empresa SA
11223344000155,Terceira Empresa ME
```

#### Opção B: Enviar Arquivo

Clique em "Browse files" e selecione um arquivo `.txt` ou `.json`:

**Arquivo TXT (exemplos.txt):**
```
12345678000190
98765432000188
11223344000155
```

Ou com nomes:
```
12345678000190,Minha Empresa Ltda
98765432000188,Outra Empresa SA
11223344000155,Terceira Empresa ME
```

**Arquivo JSON (empresas.json):**
```json
[
  {"cnpj": "12345678000190", "nome": "Minha Empresa Ltda"},
  {"cnpj": "98765432000188", "nome": "Outra Empresa SA"}
]
```

### Passo 2: Processar

1. Clique no botão **"🚀 Processar Empresas"**
2. Uma janela do navegador (Chrome ou Edge) abrirá
3. **IMPORTANTE:** Quando aparecer a janela de seleção, escolha seu certificado digital
4. Digite o PIN do certificado se solicitado
5. Aguarde enquanto o robô:
   - Faz login com o certificado
   - Acessa cada empresa
   - Verifica mensagens não lidas
   - Gera os relatórios

### Passo 3: Ver Resultados

#### Na Interface Web

Os resultados aparecem em tempo real na interface:
- ✅ Empresas processadas com sucesso
- ⚠️ Empresas com mensagens não lidas
- ❌ Erros (se houver)

#### Relatórios Salvos

Os relatórios são salvos automaticamente em:

📂 **det_robot/resultados/**

Você encontrará:
- **HTML**: `mensagens_det_AAAAMMDD_HHMMSS.html` (relatório visual bonito)
- **JSON**: `mensagens_det_AAAAMMDD_HHMMSS.json` (dados em formato estruturado)

Clique duas vezes no arquivo HTML para abrir um relatório completo com:
- Resumo geral
- Detalhes por empresa
- Lista de mensagens não lidas
- Informações de data, remetente e anexos

## 🎯 Exemplos de Uso

### Exemplo 1: Verificar 3 empresas

```
Na caixa de texto, digite:

12345678000190,Empresa A
98765432000188,Empresa B
11223344000155,Empresa C

Clique em "Processar Empresas"
```

### Exemplo 2: Upload de arquivo

```
Crie um arquivo empresas.txt:

12345678000190
98765432000188
11223344000155

Clique em "Browse files"
Selecione o arquivo
Clique em "Processar Empresas"
```

## ⚙️ Recursos Avançados

### Formatos de Entrada Aceitos

O robô aceita vários formatos:

```
# Apenas CNPJ
12345678000190

# CNPJ com nome (vírgula)
12345678000190,Minha Empresa

# CNPJ com nome (ponto e vírgula)
12345678000190;Minha Empresa

# Linhas vazias e comentários são ignorados
# Este é um comentário
12345678000190

98765432000188
```

### Visualização de Empresas

Antes de processar, você pode clicar em **"👁️ Visualizar CNPJs"** para ver como o robô interpretou sua entrada.

### Download de Exemplos

Na interface, você pode baixar:
- **Exemplo TXT**: Arquivo de exemplo com CNPJs
- **Exemplo JSON**: Arquivo JSON estruturado

## 🔧 Configurações

### Portal DET

O robô acessa automaticamente:
- URL: https://det.sit.trabalho.gov.br/

### Navegadores Suportados

**Melhor compatibilidade:**
- ✅ Google Chrome (recomendado)
- ✅ Microsoft Edge (recomendado)

**Suporte limitado:**
- ⚠️ Chromium (certificados podem não funcionar)

O robô tenta automaticamente nesta ordem: Chrome → Edge → Chromium

### Logs do Sistema

Para debug e análise, os logs são salvos em:

📋 **det_robot/logs/**

Formato: `det_robot_AAAAMMDD_HHMMSS.log`

## ❓ Solução de Problemas

### Navegador não abre

**Problema:** O robô não consegue abrir o navegador

**Soluções:**
1. Execute `INSTALAR_DET.bat` novamente
2. Instale Google Chrome ou Microsoft Edge
3. Verifique os logs em `det_robot/logs/`

### Certificado não aparece

**Problema:** A janela de seleção de certificado não aparece

**Soluções:**
1. Verifique se o certificado está instalado no Windows
2. Use Chrome ou Edge (não Chromium)
3. Certifique-se que o certificado está válido
4. Feche outros navegadores abertos

### Erro de Python

**Problema:** "Python não encontrado"

**Solução:**
1. Instale Python de https://www.python.org/downloads/
2. **IMPORTANTE:** Marque "Add Python to PATH" ao instalar
3. Feche e abra o terminal novamente
4. Execute `INSTALAR_DET.bat` novamente

### CNPJs não reconhecidos

**Problema:** CNPJs não são lidos corretamente

**Soluções:**
1. Use apenas números (sem pontos, traços ou barras)
2. Certifique-se que tem 14 dígitos
3. Use uma linha por CNPJ
4. Evite espaços extras

### Mensagens não encontradas

**Problema:** O robô não encontra mensagens que existem

**Soluções:**
1. O portal DET pode ter mudado a estrutura
2. Verifique se você está logado corretamente
3. Tente manualmente no portal para confirmar
4. Veja os logs para detalhes do que aconteceu

## 💡 Dicas

### Para melhor desempenho:

1. **Certificado sempre pronto**: Tenha seu certificado e PIN em mãos
2. **Chrome ou Edge**: Use um destes navegadores instalados
3. **Internet estável**: Conexão estável evita timeouts
4. **Não interrompa**: Deixe o robô trabalhar até o fim
5. **Feche outras guias**: Evite muitas abas abertas durante a execução

### Para organização:

1. **Nomeie as empresas**: Use o formato `CNPJ,Nome` para identificar melhor
2. **Use arquivos**: Crie arquivos TXT com suas empresas favoritas
3. **Salve relatórios**: Os HTML são ótimos para compartilhar
4. **Verifique logs**: Em caso de dúvida, confira os logs

## 📊 Interpretando os Relatórios

### Relatório HTML

O relatório HTML mostra:

**Resumo:**
- 🏢 Total de empresas processadas
- 📬 Empresas com mensagens
- 📭 Empresas sem mensagens
- 📧 Total de mensagens encontradas

**Detalhes por Empresa:**
- Nome e CNPJ formatado
- Status do processamento
- Lista de mensagens não lidas com:
  - 📧 Assunto
  - 📅 Data
  - 👤 Remetente
  - 📎 Indicador de anexo

### Relatório JSON

O JSON contém os mesmos dados em formato estruturado, útil para:
- Integração com outros sistemas
- Análise automatizada
- Importação em planilhas

## 🔐 Segurança

### Certificados Digitais

- O robô **não armazena** informações do certificado
- O PIN do certificado **não é salvo**
- Você precisa selecionar o certificado **a cada execução**

### Dados das Empresas

- CNPJs são processados localmente
- Nenhum dado é enviado para servidores externos
- Relatórios ficam apenas no seu computador

### Portal DET

- O robô acessa o portal oficial do governo
- Usa sua autenticação legítima via certificado
- Não há bypass de segurança

## 📞 Suporte

Se continuar com problemas:

1. Leia este guia novamente com atenção
2. Confira `COMECE_AQUI.txt` na pasta raiz
3. Verifique os logs em `det_robot/logs/`
4. Execute `INSTALAR_DET.bat` novamente (resolve 90% dos problemas)

## 🎉 Pronto!

Agora você já sabe usar o Robô DET!

**Resumindo:**
1. Execute `INSTALAR_DET.bat` (só uma vez)
2. Execute `ABRIR_DET.bat` (sempre que precisar)
3. Digite CNPJs → Processar → Selecione certificado → Veja resultados!

---

**Desenvolvido com ❤️ por Paulo Sergio - Versão 2.0**
