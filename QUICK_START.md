# 🚀 Guia Rápido - Labor Termination Analyzer

## Início em 3 passos

### 1️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2️⃣ Iniciar a Interface Web

```bash
python run_web.py
```

### 3️⃣ Usar o Aplicativo

A interface web abrirá automaticamente no seu navegador em `http://localhost:8501`

---

## 🌐 Interface Web - Recursos

### Upload de Arquivo JSON
1. Escolha "Upload de Arquivo JSON" na barra lateral
2. Clique em "Browse files" ou arraste seu arquivo JSON
3. Veja a análise completa instantaneamente
4. Baixe relatórios em HTML, PDF ou JSON

### Formulário Manual
1. Escolha "Formulário Manual" na barra lateral
2. Preencha todos os campos do funcionário
3. Selecione o tipo de rescisão
4. Insira valores de verbas e descontos
5. Clique em "Analisar Rescisão"
6. Veja resultados e baixe relatórios

---

## 💻 Interface CLI - Comandos Rápidos

### Criar exemplo
```bash
rescisao exemplo
```

### Analisar e gerar relatórios
```bash
rescisao analisar exemplo_rescisao.json --html relatorio.html --pdf relatorio.pdf
```

---

## 📋 Exemplo de JSON

```json
{
  "funcionario": {
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "cargo": "Analista",
    "data_admissao": "2020-01-15",
    "data_demissao": "2025-11-10",
    "salario_bruto": "5000.00"
  },
  "tipo_rescisao": "sem justa causa",
  "verbas": {
    "saldo_salario": "1666.67",
    "aviso_previo_indenizado": "5000.00",
    "ferias_proporcionais": "4583.33",
    "um_terco_ferias": "1527.78",
    "decimo_terceiro_proporcional": "4583.33",
    "multa_fgts_40": "11680.00",
    "saldo_fgts": "29200.00"
  },
  "descontos": {
    "inss": "835.22",
    "irrf": "427.37"
  }
}
```

---

## 🎯 Tipos de Rescisão Suportados

- `sem justa causa` - Demissão sem justa causa (mais direitos)
- `com justa causa` - Demissão com justa causa (menos direitos)
- `pedido de demissao` - Pedido de demissão pelo funcionário
- `acordo` - Demissão por acordo/comum acordo

---

## 📊 O que você verá

### Interface Web
- ✅ Dados do funcionário organizados
- 📊 Gráfico de pizza das verbas
- 📈 Gráfico de barras dos totais
- 💰 Valor líquido destacado
- 📄 Explicação de cada verba e desconto
- 📥 Botões de download (HTML, PDF, JSON)

### Relatórios Gerados
- **HTML**: Relatório visual navegável
- **PDF**: Documento profissional para impressão
- **JSON**: Dados estruturados para backup

---

## ❓ Problemas Comuns

### Erro ao instalar dependências
```bash
# Atualize o pip primeiro
pip install --upgrade pip

# Instale novamente
pip install -r requirements.txt
```

### Porta 8501 já em uso
```bash
# Use uma porta diferente
streamlit run labor_termination_analyzer/web.py --server.port 8502
```

### Erro ao gerar PDF
Certifique-se de ter as dependências do WeasyPrint instaladas no sistema.

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**MacOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

---

## 🎓 Próximos Passos

1. ✅ Teste com os arquivos de exemplo em `labor_termination_analyzer/examples/`
2. 📝 Crie seus próprios arquivos JSON de rescisões
3. 🎨 Personalize os relatórios editando `labor_termination_analyzer/templates/rescisao.html`
4. 🔧 Use como biblioteca Python em seus próprios projetos

---

## 📞 Suporte

Para mais informações, consulte o [README.md](README.md) completo.
