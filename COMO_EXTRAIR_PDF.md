# 📄 Como Extrair Dados de PDF de Rescisão

## 🎯 Versão MELHORADA do Extrator

O extrator foi **muito melhorado** e agora é bem mais inteligente!

---

## ✅ O que o Extrator Faz AUTOMATICAMENTE:

1. **Extrai tabelas estruturadas** (não só texto)
2. **Identifica campos por contexto** (não só por palavra-chave exata)
3. **Reconhece múltiplos formatos** de valores:
   - R$ 1.234,56
   - 1234.56
   - 1,234.56
4. **Marca o que não conseguiu extrair** com `[Não identificado]`
5. **Mostra tudo para você revisar** antes de processar

---

## 🚀 Como Usar (PASSO A PASSO):

### 1️⃣ Fazer Upload

```
1. Abra o programa
2. Escolha: "Upload de PDF (NOVO!)"
3. Clique em "Browse files"
4. Selecione o PDF da rescisão
5. Aguarde a extração (3-10 segundos)
```

### 2️⃣ REVISAR Dados Extraídos

**MUITO IMPORTANTE:**

O programa vai mostrar TUDO que extraiu em um box chamado:
```
📝 Dados Extraídos (Clique para Revisar/Editar)
```

**Abra esse box e confira:**

✅ Nome do funcionário está correto?
✅ CPF está correto?
✅ Datas estão corretas?
✅ Valores das verbas estão corretos?
✅ Descontos estão corretos?

### 3️⃣ Corrigir se Necessário

Se algum campo estiver com `[Não identificado]` ou valor errado:

**OPÇÃO A (Mais fácil):**
1. Anote os valores corretos do PDF
2. Cancele o upload
3. Escolha "Formulário Manual"
4. Preencha os valores manualmente

**OPÇÃO B (Avançado):**
1. Baixe o JSON extraído
2. Edite no Bloco de Notas
3. Faça upload do JSON corrigido

### 4️⃣ Confirmar e Analisar

Quando tudo estiver OK:
```
Clique em: ✅ Confirmar e Analisar Dados Extraídos
```

---

## 💡 O que o Extrator Consegue Identificar:

### ✅ Funcionário:
- Nome completo
- CPF
- Cargo/função
- Data de admissão
- Data de demissão
- Salário bruto

### ✅ Verbas:
- Saldo de salário
- Aviso prévio (indenizado)
- Férias vencidas
- Férias proporcionais
- 1/3 sobre férias
- 13º salário proporcional
- FGTS e multa de 40%

### ✅ Descontos:
- INSS
- Imposto de Renda (IRRF)

### ✅ Tipo:
- Sem justa causa
- Com justa causa
- Pedido de demissão
- Acordo

---

## 🔍 Como o Extrator Funciona:

1. **Primeiro:** Tenta extrair TABELAS (mais preciso)
2. **Segundo:** Busca palavras-chave no texto
3. **Terceiro:** Identifica valores por proximidade
4. **Quarto:** Marca o que não achou
5. **Quinto:** Mostra TUDO para você revisar

---

## ⚠️ Quando o Extrator Pode Falhar:

O extrator é inteligente mas não é mágico. Pode ter dificuldade com:

❌ PDFs com layout muito diferente do padrão
❌ PDFs escaneados de baixa qualidade
❌ Textos muito compactos sem espaçamento
❌ Rescisões com nomes de campos muito diferentes
❌ Tabelas mal formatadas

**Solução:** Use o Formulário Manual nesses casos!

---

## 📋 Exemplo de PDF que Funciona BEM:

```
TERMO DE RESCISÃO DO CONTRATO DE TRABALHO

Nome: João da Silva
CPF: 123.456.789-00
Cargo: Analista
Data Admissão: 01/01/2020
Data Demissão: 10/11/2025
Salário: R$ 5.000,00

VERBAS RESCISÓRIAS:
Saldo de Salário       R$ 1.666,67
Aviso Prévio          R$ 5.000,00
Férias Proporcionais  R$ 4.583,33
1/3 Férias            R$ 1.527,78
13º Proporcional      R$ 4.583,33

DESCONTOS:
INSS                  R$ 835,22
IRRF                  R$ 427,37
```

Este formato é facilmente lido pelo extrator!

---

## 🎯 Dicas Para Melhor Extração:

1. **Use PDFs com texto selecionável** (não imagens)
2. **Prefira PDFs gerados por computador** (não escaneados)
3. **Verifique se o PDF tem boa formatação** (tabelas, linhas separadas)
4. **Sempre revise os dados extraídos** antes de confirmar
5. **Se der errado, use Formulário Manual** (é rápido também!)

---

## ✅ Checklist de Uso:

```
☐ 1. Fazer upload do PDF
☐ 2. Aguardar extração
☐ 3. ABRIR o box "Dados Extraídos"
☐ 4. REVISAR cada campo
☐ 5. Se correto → Confirmar
☐ 6. Se incorreto → Usar Formulário Manual
☐ 7. Baixar relatório
```

---

## 💬 Perguntas Frequentes:

**P: O extrator errou alguns valores. O que faço?**
R: Use o Formulário Manual. É rápido e você garante que está 100% correto.

**P: Posso editar os dados depois de extrair?**
R: Atualmente não. Mas você pode: cancelar → usar Formulário Manual → copiar os valores certos.

**P: Todos os PDFs funcionam?**
R: A maioria sim, mas depende do formato. PDFs bem estruturados funcionam melhor.

**P: Preciso instalar algo extra?**
R: Não! A extração básica já funciona. OCR (para PDFs escaneados) é opcional.

**P: Como sei se extraiu certo?**
R: Sempre mostra `[Não identificado]` quando não consegue. E você SEMPRE revisa antes de confirmar!

---

## 🎉 Resumo:

```
MELHOR CASO:
PDF → Upload → Revisa → Confirma → Relatório ✅

CASO MÉDIO:
PDF → Upload → Alguns erros → Formulário Manual → Relatório ✅

PIOR CASO:
PDF → Não extrai bem → Formulário Manual desde o início → Relatório ✅
```

**Em TODOS os casos você consegue gerar o relatório!** 🚀

---

**Dúvidas?** Teste com um PDF de exemplo primeiro!
