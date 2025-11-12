# 🤖 Robô de Automação FGTS Digital

Robô de automação em Python para consulta de guias FGTS no portal FGTS Digital utilizando certificado digital A1.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Exemplos](#-exemplos)
- [Solução de Problemas](#-solução-de-problemas)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 🚀 Funcionalidades

- ✅ Autenticação automática com certificado digital A1 (.pfx)
- ✅ Gestão de múltiplas empresas via procuração eletrônica
- ✅ Extração completa de guias FGTS (pagas e pendentes)
- ✅ Exportação para Excel com abas separadas por empresa
- ✅ Sistema robusto de retry e tratamento de erros
- ✅ Logs detalhados para debug
- ✅ Screenshots automáticos em caso de erro
- ✅ Delays aleatórios para simular comportamento humano
- ✅ Interface CLI amigável

## 📦 Requisitos

### Requisitos de Sistema

- Python 3.10 ou superior
- Sistema Operacional: Windows, Linux ou macOS
- Certificado Digital A1 (formato .pfx)
- Acesso à internet

### Dependências Python

Todas as dependências estão listadas no arquivo `requirements.txt`:

- `playwright` - Automação web
- `pandas` - Manipulação de dados
- `openpyxl` - Criação de arquivos Excel
- `cryptography` - Manipulação de certificados
- `python-dotenv` - Gerenciamento de variáveis de ambiente

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/Paulo-Sergio.git
cd Paulo-Sergio/fgts_robot
```

### 2. Crie um ambiente virtual (recomendado)

```bash
# No Linux/macOS
python3 -m venv venv
source venv/bin/activate

# No Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Instale o navegador Chromium do Playwright

```bash
playwright install chromium
```

## ⚙️ Configuração

### 1. Configure o arquivo .env

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas informações:

```env
# Certificado Digital
CERT_PATH=certificados/seu_certificado.pfx
CERT_PASSWORD=sua_senha_do_certificado

# Configurações do Navegador
HEADLESS=False  # True para modo sem interface
TIMEOUT=30000   # Timeout em milissegundos
SLOW_MO=100     # Delay entre ações (ms)

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 2. Adicione seu certificado

Coloque seu certificado digital (.pfx) na pasta `certificados/`:

```bash
cp /caminho/do/seu/certificado.pfx certificados/
```

⚠️ **IMPORTANTE:** Nunca commite seu certificado ou arquivo .env no git!

## 📖 Uso

### Modo Interativo

Execute o script sem argumentos para o modo interativo:

```bash
python main.py
```

O programa solicitará que você digite os CNPJs um por vez.

### Modo Linha de Comando

#### Processar CNPJs específicos

```bash
python main.py --cnpjs 12345678000190 98765432000110
```

#### Processar CNPJs de um arquivo

Crie um arquivo `lista_cnpjs.txt` com um CNPJ por linha:

```
12345678000190
98765432000110
11122233000144
# Comentários são ignorados
```

Execute:

```bash
python main.py --arquivo lista_cnpjs.txt
```

#### Modo headless (sem interface gráfica)

```bash
python main.py --cnpjs 12345678000190 --headless
```

#### Especificar certificado diferente

```bash
python main.py --cert certificados/outro_cert.pfx --senha outra_senha --cnpjs 12345678000190
```

#### Confirmar automaticamente (modo não-interativo)

```bash
python main.py --cnpjs 12345678000190 --sim
```

#### Ver configurações atuais

```bash
python main.py --config
```

### Ajuda

Para ver todas as opções disponíveis:

```bash
python main.py --help
```

## 📁 Estrutura do Projeto

```
fgts_robot/
├── __init__.py              # Inicialização do módulo
├── main.py                  # Script principal (ponto de entrada)
├── robo_fgts.py            # Classe principal do robô
├── config.py               # Configurações e constantes
├── requirements.txt        # Dependências Python
├── .env.example           # Template de configuração
├── README.md              # Este arquivo
│
├── certificados/          # Certificados digitais (.pfx)
│   └── .gitkeep
│
├── resultados/            # Arquivos Excel gerados
│   └── .gitkeep
│
└── logs/                  # Logs e screenshots
    ├── .gitkeep
    └── screenshots/
        └── .gitkeep
```

## 📊 Formato de Saída

Os resultados são exportados em formato Excel (.xlsx) com as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| CNPJ | CNPJ da empresa |
| Empresa | Nome da empresa |
| Competência | Mês/Ano da guia |
| Status | Paga ou Pendente |
| Valor | Valor da guia |
| Vencimento | Data de vencimento |
| Código Barras | Código de barras (se pendente) |
| Data Consulta | Data/hora da consulta |

Cada empresa terá uma aba separada no arquivo Excel.

## 📚 Exemplos

### Exemplo 1: Uso Básico

```python
from fgts_robot import RoboFGTS

# Inicializar robô
robo = RoboFGTS()

# Lista de CNPJs
empresas = [
    '12345678000190',
    '98765432000110',
    '11122233000144'
]

# Processar
robo.processar_clientes(empresas)
```

### Exemplo 2: Configuração Personalizada

```python
from fgts_robot import RoboFGTS

# Inicializar com configurações específicas
robo = RoboFGTS(
    cert_path='certificados/meu_cert.pfx',
    cert_password='minha_senha',
    headless=True
)

# Processar
robo.processar_clientes(['12345678000190'])
```

### Exemplo 3: Processamento Assíncrono

```python
import asyncio
from fgts_robot import RoboFGTS

async def main():
    robo = RoboFGTS()
    await robo.processar_clientes_async(['12345678000190'])

asyncio.run(main())
```

## 🔍 Solução de Problemas

### Problema: "Certificado não encontrado"

**Solução:**
- Verifique se o caminho do certificado no `.env` está correto
- Certifique-se de que o arquivo .pfx existe na pasta `certificados/`

### Problema: "Certificado inválido"

**Solução:**
- Verifique se a senha do certificado está correta
- Certifique-se de que o certificado é do tipo A1 (não A3)
- Verifique se o certificado não está vencido

### Problema: "Timeout ao carregar página"

**Solução:**
- Aumente o valor de `TIMEOUT` no arquivo `.env`
- Verifique sua conexão com a internet
- Tente executar em modo não-headless para visualizar o problema

### Problema: "Elemento não encontrado"

**Solução:**
- O site do FGTS pode ter mudado. Verifique os logs
- Execute em modo não-headless (`HEADLESS=False`) para debug visual
- Verifique os screenshots salvos em `logs/screenshots/`

### Problema: Playwright não instalado

**Solução:**
```bash
pip install playwright
playwright install chromium
```

### Logs e Debug

- Todos os logs são salvos em `logs/`
- Screenshots de erro são salvos em `logs/screenshots/`
- Configure `LOG_LEVEL=DEBUG` no `.env` para logs mais detalhados

## 🛡️ Segurança

⚠️ **ATENÇÃO: Boas Práticas de Segurança**

1. **NUNCA** commite seu certificado digital no Git
2. **NUNCA** commite seu arquivo `.env` com senhas
3. Use sempre o arquivo `.env.example` como template
4. Mantenha seus certificados em local seguro
5. Use senhas fortes para os certificados
6. Revogue certificados comprometidos imediatamente

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](../LICENSE) para mais detalhes.

## 👤 Autor

**Paulo Sergio**

## 🙏 Agradecimentos

- [Playwright](https://playwright.dev/) - Framework de automação web
- [Pandas](https://pandas.pydata.org/) - Biblioteca de análise de dados
- [Cryptography](https://cryptography.io/) - Biblioteca criptográfica

---

**Nota:** Este robô foi desenvolvido para fins de automação legítima. Use-o de forma responsável e ética, respeitando os termos de uso do portal FGTS Digital.

## 📞 Suporte

Para reportar bugs ou solicitar features:
- Abra uma [issue](https://github.com/seu-usuario/Paulo-Sergio/issues)
- Entre em contato por email

---

Feito com ❤️ por Paulo Sergio
