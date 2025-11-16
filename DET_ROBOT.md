# DET Robot - Extrator de Mensagens do Domicílio Eletrônico Trabalhista

## Sobre

O DET Robot é uma ferramenta de automação que extrai informações de mensagens do DET (Domicílio Eletrônico Trabalhista) **sem precisar abrir cada mensagem individualmente**. Isso evita que as mensagens sejam marcadas como lidas e permite monitorar prazos importantes.

## Funcionalidades

- **Login automático ou manual** via Gov.br
- **Extração sem leitura** - obtém dados das mensagens sem abri-las
- **Identificação de prazos** - destaca mensagens urgentes
- **Múltiplos formatos de exportação** - JSON, CSV, Excel, Texto
- **Interface gráfica** - web com Streamlit
- **Interface de linha de comando** - para automação
- **Usa navegador nativo** - Chrome, Chromium ou Firefox do sistema

## Requisitos

### Sistema

- Python 3.9 ou superior
- Navegador instalado: Google Chrome, Chromium ou Firefox
- Sistema operacional: Linux, Windows ou macOS

### Dependências Python

```bash
pip install selenium webdriver-manager streamlit plotly pandas openpyxl
```

Ou instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

## Instalação

1. Clone ou baixe o projeto
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Verifique se tem um navegador instalado:

```bash
# Linux
which google-chrome || which chromium-browser || which firefox

# macOS
ls /Applications/ | grep -E "Chrome|Firefox|Chromium"

# Windows
# Verifique em C:\Program Files\
```

## Como Usar

### Interface Web (Recomendado)

1. Execute o script:

```bash
# Linux/Mac
./ABRIR_DET_ROBOT.sh

# Ou diretamente
python run_det_robot.py
```

2. Acesse no navegador: `http://localhost:8502`

3. Na interface:
   - Configure o navegador e opções na barra lateral
   - Insira suas credenciais do Gov.br
   - Clique em "Iniciar Navegador"
   - Clique em "Fazer Login"
   - Clique em "Extrair Mensagens"

### Interface de Linha de Comando

```bash
# Extração com login automático
python -m det_robot.cli extrair --cpf 12345678900

# Login manual (você faz login no navegador)
python -m det_robot.cli extrair --manual

# Sem interface gráfica (headless)
python -m det_robot.cli extrair --cpf 12345678900 --headless

# Limitar número de mensagens
python -m det_robot.cli extrair --cpf 12345678900 --limite 50

# Exportar para múltiplos formatos
python -m det_robot.cli extrair --cpf 12345678900 --formato todos

# Testar navegador
python -m det_robot.cli testar-navegador

# Listar extrações anteriores
python -m det_robot.cli listar

# Visualizar extração salva
python -m det_robot.cli visualizar dados_det/extracao_det_20250116_143022.json
```

### Como Biblioteca Python

```python
from det_robot import BrowserManager, DETAuthenticator, DETScraper, DETStorage

# Iniciar navegador
browser = BrowserManager(navegador="auto", headless=False)
browser.iniciar()

# Autenticar
auth = DETAuthenticator(browser)
auth.acessar_pagina_login()
auth.login_govbr("12345678900", "sua_senha")

# Extrair mensagens
scraper = DETScraper(browser, auth)
resultado = scraper.executar_extracao_completa(apenas_nao_lidas=True, limite=100)

# Salvar dados
storage = DETStorage("./dados_det")
storage.salvar_json(resultado)
storage.salvar_csv(resultado)
storage.salvar_excel(resultado)

# Fechar navegador
browser.fechar()
```

## Estrutura do Módulo

```
det_robot/
├── __init__.py          # Inicialização e exports
├── models.py            # Modelos de dados (Pydantic)
├── browser.py           # Gerenciador de navegador nativo
├── auth.py              # Autenticação Gov.br
├── scraper.py           # Extração de mensagens
├── storage.py           # Armazenamento de dados
├── cli.py               # Interface de linha de comando
└── web_interface.py     # Interface web Streamlit
```

## Formatos de Exportação

### JSON

Formato completo com todos os dados estruturados:

```json
{
  "data_extracao": "2025-01-16T14:30:22",
  "empregador": {
    "cnpj_cpf": "12.345.678/0001-90",
    "mensagens_nao_lidas": 5
  },
  "mensagens": [
    {
      "id_mensagem": "msg_1_1705419022",
      "assunto": "Notificação de Fiscalização",
      "tipo": "notificacao",
      "data_envio": "2025-01-15T10:00:00",
      "prazo_resposta": "2025-01-25T23:59:59",
      "dias_restantes": 9,
      "status": "nao_lida"
    }
  ]
}
```

### CSV

Tabela com uma linha por mensagem, ideal para planilhas.

### Excel

Planilha formatada com cores e destaques para mensagens urgentes.

### Texto

Relatório legível em formato de texto simples.

## Segurança

- **Credenciais não são armazenadas** - apenas usadas durante a sessão
- **Execução local** - nenhum dado é enviado para servidores externos
- **Navegador controlado localmente** - você pode ver tudo que acontece
- **Código aberto** - você pode auditar o código

## Limitações

- **Estrutura do site pode mudar** - o DET pode atualizar seu layout e os seletores precisarão ser ajustados
- **Captcha** - se houver captcha no login, use modo manual
- **2FA** - autenticação de dois fatores requer modo manual
- **Performance** - extração depende da velocidade de carregamento do site

## Solução de Problemas

### Navegador não inicia

```bash
# Verificar se Chrome está instalado
google-chrome --version

# Instalar ChromeDriver automaticamente
pip install webdriver-manager
```

### Erro de login

- Verifique se o CPF está correto (apenas números)
- Verifique se a senha está correta
- Use modo manual se houver captcha ou 2FA
- Verifique se sua conta Gov.br tem nível prata ou ouro

### Mensagens não encontradas

- O site pode ter mudado sua estrutura
- Tente capturar screenshot para debug:

```python
browser.capturar_screenshot("debug.png")
```

### Timeout

Aumente o timeout nas configurações:

```python
browser = BrowserManager(timeout=60)  # 60 segundos
```

## Desenvolvimento

### Ajustar seletores

Se o site mudar, ajuste os seletores em `auth.py` e `scraper.py`:

```python
SELETORES = {
    "btn_entrar": [
        "//a[contains(text(), 'Entrar')]",
        # Adicione novos seletores aqui
    ],
}
```

### Adicionar novos campos

Edite `models.py` para adicionar campos nas mensagens:

```python
class MensagemDET(BaseModel):
    # Campos existentes...
    novo_campo: Optional[str] = None
```

## Contribuição

1. Faça fork do projeto
2. Crie uma branch para sua feature
3. Teste as alterações
4. Envie um pull request

## Licença

MIT License - Veja o arquivo LICENSE

## Aviso Legal

Esta ferramenta é para uso pessoal e educacional. O usuário é responsável pelo uso adequado e pelo cumprimento das normas do DET/MTE. Não nos responsabilizamos por uso indevido ou problemas decorrentes do uso desta ferramenta.
