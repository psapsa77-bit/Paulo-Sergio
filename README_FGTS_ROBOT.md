# 🤖 FGTS Digital Robot

**Automação completa para consulta de guias FGTS das suas empresas**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-1.46+-green.svg)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Uso Rápido](#-uso-rápido)
- [Interface Web](#-interface-web)
- [Uso Programático](#-uso-programático)
- [Exemplos](#-exemplos)
- [Arquitetura](#-arquitetura)
- [Segurança](#-segurança)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)

---

## 🎯 Visão Geral

O **FGTS Digital Robot** é uma solução de automação que permite acessar o portal FGTS Digital da Caixa Econômica Federal usando certificado digital e extrair automaticamente informações sobre guias pendentes e pagas de múltiplas empresas.

### Por que usar?

- ⏱️ **Economize tempo**: Consulte todas as empresas em poucos minutos
- 🔄 **Automação total**: De login à exportação de relatórios
- 📊 **Visualização clara**: Dashboards interativos e relatórios em Excel/JSON
- 🔒 **Seguro**: Usa certificado digital oficial e conexão criptografada
- 🏢 **Multi-empresa**: Alterne entre empresas automaticamente via procuração

---

## ✨ Funcionalidades

### 🔐 Autenticação
- ✅ Login automático com certificado digital A1 (.pfx/.p12)
- ✅ Validação de certificado (validade, titular, CPF/CNPJ)
- ✅ Suporte a procuração eletrônica
- ✅ Sessão segura com o portal oficial

### 🏢 Gestão de Empresas
- ✅ Listagem automática de empresas com procuração
- ✅ Alternância entre múltiplas empresas
- ✅ Consulta individual ou em lote

### 📋 Extração de Guias
- ✅ Guias mensais, rescisórias e complementares
- ✅ Status: pendentes, pagas, vencidas, parceladas
- ✅ Valores: principal, multa, juros e total
- ✅ Datas: competência, vencimento e pagamento
- ✅ Cálculo automático de dias de atraso

### 📊 Relatórios
- ✅ Dashboard interativo com gráficos
- ✅ Exportação em JSON
- ✅ Exportação em Excel (.xlsx)
- ✅ Estatísticas consolidadas
- ✅ Agrupamento por empresa e status

### 🖥️ Interface
- ✅ Interface web via Streamlit (fácil de usar)
- ✅ API Python (uso programático)
- ✅ Modo headless (execução em segundo plano)
- ✅ Logs detalhados para debug

---

## 📦 Requisitos

### Software
- Python 3.9 ou superior
- Sistema operacional: Windows, Linux ou macOS
- Navegador Chromium (instalado automaticamente pelo Playwright)

### Certificado Digital
- Certificado digital A1 válido (formato .pfx ou .p12)
- Senha do certificado
- Procuração eletrônica cadastrada no FGTS Digital para as empresas

### Conexão
- Internet estável
- Acesso ao portal https://fgtsdigital.caixa.gov.br

---

## 🚀 Instalação

### 1. Clonar o repositório (se aplicável)

```bash
git clone https://github.com/seu-usuario/Paulo-Sergio.git
cd Paulo-Sergio
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Instalar navegadores do Playwright

```bash
playwright install chromium
```

### 4. Verificar instalação

```bash
python -c "from fgts_digital_robot import FGTSRobot; print('✅ Instalado com sucesso!')"
```

---

## ⚡ Uso Rápido

### Interface Web (Recomendado)

```bash
python run_fgts_robot.py
```

Acesse: http://localhost:8502

### Uso via Python

```python
from fgts_digital_robot import FGTSRobot

# Criar robô
robot = FGTSRobot(
    certificado_path="certificado.pfx",
    senha_certificado="sua_senha"
)

# Autenticar
robot.autenticar()

# Listar empresas
empresas = robot.listar_empresas()

# Processar todas
relatorio = robot.processar_todas_empresas()

# Exportar
robot.exportar_relatorio(relatorio, "relatorio.xlsx", formato="excel")

# Fechar
robot.fechar()
```

---

## 🖥️ Interface Web

### Iniciando

```bash
python run_fgts_robot.py
```

### Passo a passo

1. **Upload do Certificado**
   - Clique em "Browse files"
   - Selecione seu arquivo .pfx ou .p12
   - Digite a senha do certificado

2. **Autenticação**
   - Clique em "🔐 Autenticar"
   - Aguarde o navegador abrir
   - O sistema pode solicitar seleção de certificado (selecione o correto)
   - Aguarde login automático

3. **Consultar Empresas**
   - Vá para aba "🏢 Empresas"
   - Visualize lista de empresas com procuração

4. **Extrair Guias**
   - Vá para aba "📋 Consultar Guias"
   - Selecione empresas (todas ou específicas)
   - Aplique filtros de status se desejar
   - Clique em "🚀 Executar Consulta"

5. **Dashboard**
   - Vá para aba "📊 Dashboard"
   - Visualize métricas, gráficos e tabelas

6. **Exportar**
   - Vá para aba "📥 Exportar"
   - Escolha formato (JSON ou Excel)
   - Clique em "💾 Baixar"

---

## 💻 Uso Programático

### Exemplo Básico

```python
from fgts_digital_robot import FGTSRobot

# Context manager (fecha automaticamente)
with FGTSRobot("certificado.pfx", "senha123") as robot:
    robot.autenticar()
    relatorio = robot.processar_todas_empresas()
    robot.exportar_relatorio(relatorio, "relatorio.json")
```

### Consultar Empresa Específica

```python
from fgts_digital_robot import FGTSRobot

robot = FGTSRobot("certificado.pfx", "senha123")
robot.autenticar()

# Listar empresas
empresas = robot.listar_empresas()
cnpj_alvo = empresas[0].cnpj

# Extrair guias de uma empresa
guias = robot.extrair_guias_empresa(cnpj_alvo)

for guia in guias:
    print(f"{guia.numero_guia} - {guia.status.value} - R$ {guia.valor_total}")

robot.fechar()
```

### Filtrar por Status

```python
from fgts_digital_robot import FGTSRobot, StatusGuia

with FGTSRobot("certificado.pfx", "senha123") as robot:
    robot.autenticar()

    # Apenas pendentes e vencidas
    relatorio = robot.processar_todas_empresas(
        filtrar_status=[StatusGuia.PENDENTE, StatusGuia.VENCIDA]
    )

    print(f"Guias pendentes: {relatorio.total_pendentes}")
    print(f"Valor pendente: R$ {relatorio.valor_total_pendente}")
```

### Modo Headless (Sem Interface Gráfica)

```python
robot = FGTSRobot("certificado.pfx", "senha123", headless=True)
# Resto do código...
```

---

## 📚 Exemplos

Veja o arquivo `exemplo_fgts_robot.py` para exemplos completos:

```bash
python exemplo_fgts_robot.py
```

Exemplos incluídos:
1. Exemplo básico (todas as empresas)
2. Empresa específica
3. Filtrar apenas pendentes
4. Exportação em múltiplos formatos
5. Análise de guias vencidas

---

## 🏗️ Arquitetura

### Estrutura de Módulos

```
fgts_digital_robot/
├── __init__.py          # Exportações principais
├── models.py            # Modelos Pydantic (dados)
├── authenticator.py     # Autenticação com certificado
├── navigator.py         # Navegação no portal
├── extractor.py         # Extração de dados HTML
├── robot.py             # Classe principal
└── web_interface.py     # Interface Streamlit
```

### Fluxo de Dados

```
1. Certificado Digital (.pfx)
        ↓
2. FGTSAuthenticator (validação)
        ↓
3. FGTSNavigator (Playwright + certificado)
        ↓
4. Acesso ao portal → Login automático
        ↓
5. Listagem de empresas
        ↓
6. Para cada empresa:
   - Selecionar empresa
   - Navegar para guias
   - Extrair HTML
        ↓
7. FGTSExtractor (BeautifulSoup)
        ↓
8. Lista de GuiaFGTS (Pydantic)
        ↓
9. RelatorioFGTS (consolidação)
        ↓
10. Exportação (JSON/Excel)
```

### Modelos de Dados

#### CertificadoDigital
```python
{
    "caminho": Path,
    "senha": str,
    "valido_ate": date,
    "cpf_cnpj": str,
    "nome_titular": str
}
```

#### EmpresaFGTS
```python
{
    "cnpj": str,
    "razao_social": str,
    "nome_fantasia": str,
    "tem_procuracao": bool,
    "data_procuracao": date
}
```

#### GuiaFGTS
```python
{
    "numero_guia": str,
    "tipo": TipoGuia,
    "status": StatusGuia,
    "cnpj_empresa": str,
    "competencia": str,
    "data_vencimento": date,
    "data_pagamento": date,
    "valor_principal": Decimal,
    "valor_total": Decimal,
    ...
}
```

#### RelatorioFGTS
```python
{
    "empresas": List[EmpresaFGTS],
    "guias": List[GuiaFGTS],
    "total_guias": int,
    "total_pendentes": int,
    "total_pagas": int,
    "valor_total_pendente": Decimal,
    "tempo_execucao_segundos": float
}
```

---

## 🔒 Segurança

### Boas Práticas

✅ **Certificado**
- Armazenado apenas em memória durante execução
- Nunca salvo em disco pelo robô
- Senha não é persistida

✅ **Conexão**
- HTTPS com validação de certificados SSL
- User-Agent legítimo
- Sem bypass de segurança

✅ **Dados**
- Logs anonimizados (sem senhas ou dados sensíveis)
- Relatórios salvos localmente
- Sem transmissão para servidores externos

✅ **Portal Oficial**
- Acessa apenas https://fgtsdigital.caixa.gov.br
- Não interage com sites de terceiros
- Respeita termos de uso da Caixa

### Recomendações

⚠️ **Não compartilhe**:
- Certificado digital
- Senha do certificado
- Relatórios gerados (contêm dados sensíveis)

⚠️ **Armazene com segurança**:
- Use criptografia para armazenar certificados
- Não versione certificados no Git (.gitignore)
- Use variáveis de ambiente para senhas em produção

⚠️ **Validação**:
- Verifique validade do certificado regularmente
- Mantenha procurações atualizadas
- Revogue procurações quando não mais necessárias

---

## 🐛 Troubleshooting

### Erro: "Certificado inválido"

**Causa**: Certificado corrompido, senha incorreta ou vencido

**Solução**:
```python
# Validar certificado antes
robot = FGTSRobot("certificado.pfx", "senha")
info = robot.validar_certificado()
print(info)  # Verificar informações
```

### Erro: "Timeout ao acessar portal"

**Causa**: Internet lenta ou portal instável

**Solução**:
```python
# Aumentar timeout
from fgts_digital_robot.navigator import FGTSNavigator
FGTSNavigator.TIMEOUT_LOGIN = 120000  # 2 minutos
```

### Erro: "Nenhuma empresa encontrada"

**Causa**: Sem procuração cadastrada

**Solução**:
1. Acesse manualmente o FGTS Digital
2. Vá em "Procurações" → "Outorga de Procurações"
3. Cadastre procuração para o CPF/CNPJ do certificado
4. Aguarde ativação (pode levar até 24h)

### Navegador não abre (headless=False)

**Causa**: Playwright não instalado corretamente

**Solução**:
```bash
playwright install chromium
playwright install-deps  # No Linux
```

### Erro ao extrair guias

**Causa**: HTML do portal mudou

**Solução**:
1. Faça screenshot: `robot.fazer_screenshot("debug.png")`
2. Verifique seletores em `navigator.py`
3. Ajuste seletores conforme novo HTML
4. Reporte issue no GitHub

### Erro: "openpyxl não instalado"

**Causa**: Dependência opcional não instalada

**Solução**:
```bash
pip install openpyxl
```

---

## ❓ FAQ

### 1. Preciso de certificado A3 (token/cartão)?

**Não**. O robô funciona apenas com certificado A1 (arquivo .pfx/.p12). Certificados A3 requerem hardware específico e não são suportados pelo Playwright.

### 2. Posso usar certificado de pessoa física?

**Sim**, desde que tenha procuração eletrônica cadastrada no FGTS Digital para as empresas que deseja consultar.

### 3. Quantas empresas posso consultar?

**Ilimitadas**, desde que você tenha procuração válida para todas elas.

### 4. O robô armazena meus dados?

**Não**. Tudo é processado localmente. O robô não envia dados para servidores externos.

### 5. É seguro usar?

**Sim**. O robô:
- Usa o portal oficial da Caixa
- Autentica com certificado digital válido
- Não armazena senhas
- Código open-source (você pode auditar)

### 6. Funciona em servidor sem interface gráfica?

**Sim**. Use `headless=True`:
```python
robot = FGTSRobot("cert.pfx", "senha", headless=True)
```

### 7. Posso agendar execuções automáticas?

**Sim**. Use cron (Linux) ou Task Scheduler (Windows):

```bash
# Cron exemplo (diário às 8h)
0 8 * * * cd /caminho/projeto && python script_automatico.py
```

### 8. O portal mudou, o que fazer?

Se o portal FGTS Digital mudar o layout:
1. Faça screenshot: `robot.fazer_screenshot("debug.png")`
2. Analise o HTML da página
3. Ajuste seletores CSS em `navigator.py`
4. Teste novamente

### 9. Posso contribuir com o projeto?

**Sim!** Pull requests são bem-vindos. Veja o arquivo CONTRIBUTING.md (se existir).

### 10. Qual a licença?

MIT License - uso livre, inclusive comercial.

---

## 📞 Suporte

### Problemas?

1. Verifique o [Troubleshooting](#-troubleshooting)
2. Consulte o [FAQ](#-faq)
3. Abra uma issue no GitHub
4. Envie email para: [email protegido]

### Logs

Para debug detalhado:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

robot = FGTSRobot("cert.pfx", "senha", log_level="DEBUG")
```

---

## 🎯 Roadmap

### Versão 1.1 (planejado)
- [ ] Suporte a certificado A3 via biblioteca externa
- [ ] Exportação em PDF
- [ ] Envio de relatórios por email
- [ ] Notificações de guias vencendo

### Versão 1.2 (planejado)
- [ ] API REST
- [ ] Dashboard web standalone
- [ ] Histórico de consultas
- [ ] Comparação entre períodos

---

## 👨‍💻 Autor

**Paulo Sergio**

- GitHub: [@psapsa77-bit](https://github.com/psapsa77-bit)
- Projeto: Labor Termination Analyzer & FGTS Digital Robot

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

## 🙏 Agradecimentos

- **Playwright Team** - Ferramenta de automação web
- **Pydantic** - Validação de dados
- **Streamlit** - Interface web interativa
- **Comunidade Python Brasil** - Suporte e inspiração

---

## ⚖️ Disclaimer

Este software é fornecido "como está", sem garantias de qualquer tipo. O autor não se responsabiliza por:
- Uso incorreto do software
- Problemas causados por mudanças no portal FGTS Digital
- Violação de termos de uso de terceiros
- Perda de dados ou danos consequentes

Use por sua própria conta e risco, respeitando os termos de uso do portal FGTS Digital da Caixa Econômica Federal.

---

**Feito com ❤️ em Python**
