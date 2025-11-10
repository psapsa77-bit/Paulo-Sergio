# 📋 Labor Termination Analyzer

Aplicativo completo para ler, analisar e explicar rescisões trabalhistas brasileiras, com geração automática de relatórios visuais em PDF e HTML.

---

## 🎓 **NOVO USUÁRIO? COMECE AQUI!**

> **Nunca usou programação antes?** Não tem problema! Criamos um processo SUPER SIMPLES:

### ⚡ 3 Passos para Usar:

```
1️⃣ Duplo clique em: INSTALAR_WINDOWS.bat (ou instalar.sh no Mac/Linux)
2️⃣ Duplo clique em: ABRIR_PROGRAMA.bat (ou abrir.sh)
3️⃣ Faça upload do PDF da rescisão OU preencha o formulário
4️⃣ Baixe o relatório em PDF!
```

📖 **Leia o arquivo:** [COMO_USAR.md](COMO_USAR.md) - Guia passo a passo com prints

📄 **Ou leia:** [LEIA-ME.txt](LEIA-ME.txt) - Instruções rápidas

---

## 🎯 Funcionalidades

- 🎉 **NOVO! Extração de PDF**: Extrai dados automaticamente de PDFs de rescisão trabalhista
- 🔍 **OCR Integrado**: Suporta PDFs escaneados com reconhecimento óptico de caracteres
- ✅ **Análise Completa**: Processa todos os componentes de uma rescisão trabalhista
- 📊 **Explicações Detalhadas**: Explica cada verba e desconto de forma clara e didática
- 🌐 **Interface Web**: Interface web moderna e intuitiva com Streamlit
- 📄 **Relatórios HTML**: Gera relatórios visuais e interativos em HTML
- 📑 **Relatórios PDF**: Converte relatórios para PDF profissional
- 💻 **Interface CLI**: Interface de linha de comando fácil de usar
- 📈 **Gráficos Interativos**: Visualizações com Plotly na interface web
- 🎨 **Visual Atraente**: Design moderno e responsivo para os relatórios
- 📚 **Tipos de Rescisão**: Suporta todos os tipos (sem justa causa, com justa causa, pedido de demissão, acordo)

## 🚀 Instalação

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Instalação via pip

```bash
# Clone o repositório
git clone https://github.com/psapsa77-bit/Paulo-Sergio.git
cd Paulo-Sergio

# Instale o pacote
pip install -e .
```

### Instalação de Dependências (Desenvolvimento)

```bash
pip install -r requirements.txt
```

## 📖 Como Usar

### Modo 1: Interface Web (Recomendado) 🌐

A interface web oferece a experiência mais completa e visual:

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar a interface web
python run_web.py

# OU diretamente com streamlit
streamlit run labor_termination_analyzer/web.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`

**Funcionalidades da Interface Web:**

- 📤 **Upload de arquivo JSON** ou entrada manual via formulário
- 📊 **Visualização em tempo real** da análise
- 📈 **Gráficos interativos** das verbas e totais
- 📥 **Download direto** de relatórios HTML, PDF e JSON
- 💡 **Interface intuitiva** com validação de dados
- 🎨 **Design responsivo** e moderno

### Modo 2: Linha de Comando (CLI) 💻

Para uso rápido via terminal:

#### 1. Criar um Arquivo de Exemplo

```bash
rescisao exemplo
```

Isso criará um arquivo `exemplo_rescisao.json` com dados de exemplo.

#### 2. Analisar uma Rescisão

```bash
# Mostrar análise no terminal
rescisao analisar exemplo_rescisao.json

# Gerar relatório HTML
rescisao analisar exemplo_rescisao.json --html relatorio.html

# Gerar relatório PDF
rescisao analisar exemplo_rescisao.json --pdf relatorio.pdf

# Gerar ambos (HTML e PDF)
rescisao analisar exemplo_rescisao.json --html relatorio.html --pdf relatorio.pdf
```

### Modo 3: Uso Programático (API Python) 🐍

Você também pode usar o aplicativo como biblioteca Python:

```python
from labor_termination_analyzer import (
    RescisaoParser,
    RescisaoAnalyzer,
    HTMLGenerator,
    PDFGenerator
)

# Parse de dados
rescisao = RescisaoParser.from_json_file("dados.json")

# Análise
analyzer = RescisaoAnalyzer(rescisao)
resumo = analyzer.gerar_resumo_completo()

# Gerar relatórios
html_gen = HTMLGenerator()
html_gen.gerar(rescisao, "relatorio.html")

pdf_gen = PDFGenerator()
pdf_gen.gerar(rescisao, "relatorio.pdf")
```

---

## 📋 Formato do Arquivo JSON

O arquivo JSON deve conter os seguintes campos:

```json
{
  "funcionario": {
    "nome": "Maria da Silva",
    "cpf": "123.456.789-00",
    "cargo": "Analista de Sistemas",
    "data_admissao": "2020-01-15",
    "data_demissao": "2025-11-10",
    "salario_bruto": "5000.00"
  },
  "tipo_rescisao": "sem justa causa",
  "verbas": {
    "saldo_salario": "1666.67",
    "aviso_previo_indenizado": "5416.67",
    "ferias_vencidas": "0.00",
    "ferias_proporcionais": "4583.33",
    "um_terco_ferias": "1527.78",
    "decimo_terceiro_proporcional": "4583.33",
    "multa_fgts_40": "11680.00",
    "saldo_fgts": "29200.00"
  },
  "descontos": {
    "inss": "835.22",
    "irrf": "427.37"
  },
  "observacoes": "Observações adicionais sobre a rescisão"
}
```

#### Tipos de Rescisão Suportados

- `"sem justa causa"` - Demissão sem justa causa
- `"com justa causa"` - Demissão com justa causa
- `"pedido de demissao"` - Pedido de demissão pelo funcionário
- `"acordo"` - Demissão por acordo (comum acordo)

#### Verbas Suportadas

- `saldo_salario` - Saldo de salário
- `aviso_previo_indenizado` - Aviso prévio indenizado
- `ferias_vencidas` - Férias vencidas
- `ferias_proporcionais` - Férias proporcionais
- `um_terco_ferias` - 1/3 constitucional sobre férias
- `decimo_terceiro_proporcional` - 13º salário proporcional
- `multa_fgts_40` - Multa de 40% do FGTS
- `saldo_fgts` - Saldo do FGTS
- `outras_verbas` - Objeto com verbas adicionais

#### Descontos Suportados

- `inss` - Contribuição previdenciária
- `irrf` - Imposto de renda retido na fonte
- `aviso_previo_indenizado` - Desconto de aviso prévio (quando aplicável)
- `outros_descontos` - Objeto com descontos adicionais

## 🎨 Exemplos de Saída

### Terminal

```
📋 Análise de Rescisão Trabalhista
Maria da Silva

👤 Dados do Funcionário
Nome: Maria da Silva
CPF: 123.456.789-00
Cargo: Analista de Sistemas
...

💰 Verbas Rescisórias
Saldo de Salário                R$ 1.666,67
Aviso Prévio Indenizado        R$ 5.416,67
...

💵 Resumo Financeiro
Total de Verbas: R$ 29.457,78
Total de Descontos: R$ 1.262,59
Valor Líquido a Receber: R$ 28.195,19
```

### HTML/PDF

Os relatórios gerados incluem:

- 🎨 Design moderno e profissional
- 📊 Tabelas organizadas
- 💡 Explicações detalhadas de cada verba e desconto
- 📈 Cálculos transparentes
- 📋 Informações completas do funcionário
- 💰 Resumo financeiro destacado

### Interface Web

A interface web oferece:

- 🌐 Acesso via navegador (localhost:8501)
- 📊 Visualização em tempo real dos dados
- 📈 Gráficos interativos com Plotly (pizza e barras)
- 📤 Upload de JSON ou formulário manual completo
- 💾 Download instantâneo de HTML, PDF e JSON
- ✨ Validação de dados em tempo real
- 🎨 Design moderno e responsivo

## 📚 Documentação das Verbas

### Verbas Rescisórias

**Saldo de Salário**: Corresponde aos dias trabalhados no mês da rescisão até a data do desligamento. É calculado proporcionalmente ao salário mensal dividido por 30 dias.

**Aviso Prévio Indenizado**: Quando o empregador dispensa o empregado sem justa causa sem cumprir o aviso prévio de 30 dias, deve pagar esse período. Adiciona-se 3 dias por ano trabalhado (até no máximo 90 dias).

**Férias Vencidas**: Férias que já foram adquiridas (completou 12 meses de trabalho) mas não foram gozadas. O trabalhador tem direito a receber o valor integral dessas férias acrescido de 1/3.

**Férias Proporcionais**: Corresponde às férias do período incompleto (menos de 12 meses desde as últimas férias ou admissão). É pago proporcionalmente aos meses trabalhados.

**1/3 Constitucional**: A Constituição Federal garante o adicional de 1/3 sobre o valor das férias. Esse valor é somado tanto às férias vencidas quanto às proporcionais.

**13º Salário Proporcional**: O 13º salário é pago proporcionalmente aos meses trabalhados no ano da rescisão. Cada mês trabalhado (15 dias ou mais) conta como 1/12 avos do 13º.

**Multa de 40% do FGTS**: Em caso de demissão sem justa causa, o empregador deve pagar multa de 40% sobre o total depositado no FGTS durante todo o contrato de trabalho.

**Saldo do FGTS**: Valor total depositado na conta do FGTS durante o contrato de trabalho. Em demissão sem justa causa, o trabalhador pode sacar todo o saldo.

### Descontos

**INSS**: Desconto obrigatório para a Previdência Social. A alíquota varia conforme o salário, seguindo a tabela progressiva do INSS (de 7,5% a 14%).

**IRRF**: Imposto de renda cobrado sobre os valores recebidos. Incide sobre verbas de natureza salarial, com alíquotas progressivas conforme a tabela do IR.

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
labor_termination_analyzer/
├── __init__.py          # Inicialização do pacote
├── models.py            # Modelos de dados (Pydantic)
├── parser.py            # Parser de dados JSON
├── analyzer.py          # Análise e explicações
├── generators.py        # Geradores HTML/PDF
├── cli.py              # Interface de linha de comando
└── templates/
    └── rescisao.html   # Template HTML
```

### Executar Testes

```bash
pytest tests/
```

### Formatar Código

```bash
black labor_termination_analyzer/
```

## 📝 Licença

MIT License

## 👤 Autor

Paulo Sergio

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## 📞 Suporte

Para dúvidas ou suporte, abra uma issue no GitHub.

---

**Nota**: Este aplicativo tem caráter informativo e educacional. Para questões legais específicas, consulte sempre um advogado trabalhista.
