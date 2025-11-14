# 🤖 Robô DET - Verificador de Mensagens

Robô automatizado para verificar mensagens não lidas no Portal DET (Delegacia Regional do Trabalho).

## 📋 Descrição

Este robô acessa o portal do DET (https://det.sit.trabalho.gov.br/) utilizando certificado digital e verifica se existem mensagens não lidas para as empresas cadastradas. Os resultados são apresentados em uma interface web moderna e podem ser exportados em formato HTML e JSON.

## ✨ Funcionalidades

- 🔐 **Login automático** com certificado digital
- 🏢 **Gerenciamento de múltiplas empresas**
- 📬 **Verificação de mensagens não lidas**
- 📊 **Relatórios visuais** em HTML
- 💾 **Exportação de dados** em JSON
- 🌐 **Interface web intuitiva** com Streamlit
- 📝 **Sistema de logs detalhado**
- 🔄 **Processamento em lote**

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Certificado digital instalado no sistema
- Conexão com internet

### Windows

1. Execute o arquivo de instalação:
```bash
INSTALAR_DET.bat
```

2. Aguarde a instalação das dependências

### Linux/Mac

1. Torne o script executável e execute:
```bash
chmod +x instalar_det.sh
./instalar_det.sh
```

### Instalação Manual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r det_robot/requirements.txt

# Instalar navegadores Playwright
python -m playwright install chromium
```

## 📖 Como Usar

### 1. Iniciar o Programa

**Windows:**
```bash
ABRIR_DET.bat
```

**Linux/Mac:**
```bash
./abrir_det.sh
```

**Ou diretamente:**
```bash
python run_det.py
```

### 2. Acessar Interface Web

Após iniciar, acesse no navegador:
```
http://localhost:8503
```

### 3. Cadastrar Empresas

1. Vá para a aba **"🏢 Empresas"**
2. Preencha o nome e CNPJ da empresa
3. Clique em **"➕ Adicionar"**
4. Repita para todas as empresas

### 4. Processar Verificação

1. Vá para a aba **"🚀 Processar"**
2. Clique em **"🚀 INICIAR VERIFICAÇÃO"**
3. Selecione o certificado digital quando solicitado
4. Aguarde o processamento

### 5. Visualizar Resultados

- Vá para a aba **"📊 Resultados"**
- Visualize as mensagens encontradas
- Faça download dos relatórios (HTML/JSON)

## 📁 Estrutura do Projeto

```
det_robot/
├── __init__.py          # Inicialização do módulo
├── config.py            # Configurações do sistema
├── robot_det.py         # Classe principal do robô
├── web_det.py           # Interface web Streamlit
├── requirements.txt     # Dependências Python
├── README.md            # Esta documentação
├── logs/                # Arquivos de log
├── results/             # Resultados em HTML/JSON
└── config/              # Configurações e dados
    └── empresas.json    # Lista de empresas cadastradas
```

## ⚙️ Configuração

### Seletores CSS/XPath

Os seletores CSS e XPath do portal podem ser ajustados no arquivo `config.py`:

```python
SELETORES = {
    "btn_certificado": "//button[contains(text(), 'Certificado Digital')]",
    "menu_mensagens": "//a[contains(text(), 'Mensagens')]",
    "mensagens_nao_lidas": ".mensagem.nao-lida",
    # ... outros seletores
}
```

### Timeouts

Ajuste os timeouts conforme necessário em `config.py`:

```python
TIMEOUT_PADRAO = 30      # segundos
TIMEOUT_LOGIN = 60       # segundos
TIMEOUT_NAVEGACAO = 30   # segundos
```

## 🔍 Personalizando Seletores

O portal DET pode ter uma estrutura diferente. Para ajustar os seletores:

1. **Abra o portal no navegador**
2. **Use as ferramentas de desenvolvedor** (F12)
3. **Inspecione os elementos** que deseja capturar
4. **Copie os seletores CSS ou XPath**
5. **Atualize em `config.py`**

Exemplo de como encontrar seletores:
- Botão de login: clique direito → Inspecionar → copie o seletor
- Lista de mensagens: mesmo processo
- Contador de mensagens: mesmo processo

## 📊 Relatórios

### Relatório HTML

- Design moderno e responsivo
- Métricas visuais em cards
- Lista detalhada de mensagens por empresa
- Pronto para impressão

### Relatório JSON

Estrutura do JSON:
```json
{
  "timestamp": "2024-01-01 10:00:00",
  "total_empresas_processadas": 5,
  "empresas_com_mensagens": 2,
  "total_mensagens_nao_lidas": 3,
  "mensagens": [
    {
      "assunto": "Notificação importante",
      "data": "01/01/2024",
      "remetente": "DET",
      "empresa_cnpj": "12345678000199",
      "empresa_nome": "Empresa Teste"
    }
  ],
  "resultados_por_empresa": [...]
}
```

## 🐛 Solução de Problemas

### Problema: Certificado digital não aparece

**Solução:**
- Verifique se o certificado está instalado no sistema
- Certifique-se de que o certificado não está expirado
- Tente reiniciar o navegador

### Problema: Seletores não encontrados

**Solução:**
- O portal pode ter mudado sua estrutura
- Atualize os seletores em `config.py`
- Consulte a seção "Personalizando Seletores"

### Problema: Timeout ao carregar páginas

**Solução:**
- Aumente os valores de timeout em `config.py`
- Verifique sua conexão com internet
- O servidor do DET pode estar lento

### Problema: Erro ao instalar Playwright

**Solução:**
```bash
# Reinstale o Playwright
pip uninstall playwright
pip install playwright
python -m playwright install chromium
```

## 📝 Logs

Os logs são salvos automaticamente em:
```
det_robot/logs/det_robot_YYYYMMDD_HHMMSS.log
```

Para visualizar os logs:
- Use a aba **"📝 Logs"** na interface web
- Ou abra os arquivos diretamente na pasta `logs/`

## 🔒 Segurança

- ✅ O robô **NÃO armazena** senhas ou dados do certificado
- ✅ A autenticação é feita via certificado digital do sistema
- ✅ Os dados ficam armazenados **localmente** no seu computador
- ✅ Nenhum dado é enviado para servidores externos

## 🤝 Contribuindo

Melhorias são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto é fornecido "como está", sem garantias de qualquer tipo.

## 👤 Autor

**Paulo Sergio**
- Versão: 1.0.0
- Data: 2024

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique a seção "Solução de Problemas"
2. Consulte os logs do sistema
3. Abra uma issue no repositório

## 🔄 Atualizações

### Versão 1.0.0 (2024)
- ✨ Lançamento inicial
- 🔐 Login com certificado digital
- 📬 Verificação de mensagens não lidas
- 📊 Relatórios HTML e JSON
- 🌐 Interface web com Streamlit
- 🏢 Gerenciamento de múltiplas empresas

## 📚 Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Playwright**: Automação web
- **Streamlit**: Interface web
- **HTML/CSS**: Relatórios visuais
- **JSON**: Exportação de dados

## ⚠️ Avisos Importantes

1. **Certificado Digital**: É necessário ter um certificado digital válido instalado no sistema
2. **Portal DET**: O robô depende da estrutura do portal, que pode mudar
3. **Uso Responsável**: Use o robô de forma responsável e ética
4. **Dados Sensíveis**: Não compartilhe os relatórios com dados sensíveis

## 🎯 Roadmap Futuro

- [ ] Notificações por email
- [ ] Agendamento automático
- [ ] Dashboard com histórico
- [ ] Suporte a múltiplos portais
- [ ] API REST

---

**Desenvolvido com ❤️ por Paulo Sergio**
