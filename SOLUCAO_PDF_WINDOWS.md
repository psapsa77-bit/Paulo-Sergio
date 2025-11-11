# 🔧 Solução para Problema de PDF no Windows

## ❗ O Problema

No Windows, a geração de PDF requer bibliotecas do sistema (GTK) que não vêm instaladas por padrão.

## ✅ SOLUÇÃO RÁPIDA (Recomendada)

**Use HTML ao invés de PDF!**

1. No programa, clique em **"📄 Baixar Relatório HTML"**
2. Abra o arquivo HTML no navegador (Chrome, Edge, Firefox)
3. Pressione **Ctrl+P** (ou clique em "Imprimir")
4. Em "Destino", escolha **"Salvar como PDF"**
5. Clique em **"Salvar"**

**Resultado:** PDF perfeito, idêntico ao que seria gerado pelo programa!

---

## 🔧 SOLUÇÃO ALTERNATIVA (Instalar GTK)

Se você REALMENTE quer gerar PDF direto pelo botão:

### Passo 1: Baixar GTK Runtime

Acesse: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

Baixe o arquivo mais recente (ex: `gtk3-runtime-3.24.x-x-x-ts-win64.exe`)

### Passo 2: Instalar

1. Execute o instalador baixado
2. Clique em "Next" → "Next" → "Install"
3. Aguarde a instalação
4. Clique em "Finish"

### Passo 3: Reiniciar

1. **IMPORTANTE:** Feche COMPLETAMENTE o programa
2. Abra novamente: duplo clique em `ABRIR_PROGRAMA.bat`
3. Agora o botão de PDF deve funcionar!

---

## 💡 Por Que Isso Acontece?

O WeasyPrint (biblioteca que gera PDF) precisa de componentes do GTK (biblioteca gráfica) que existem nativamente no Linux/Mac mas não no Windows.

---

## 📋 Qual Método Usar?

| Método | Vantagens | Desvantagens |
|--------|-----------|--------------|
| **HTML → PDF** | ✅ Funciona imediatamente<br>✅ Sem instalação extra<br>✅ Mesmo resultado | ⚠️ Um passo extra |
| **Instalar GTK** | ✅ PDF direto pelo botão | ⚠️ Download ~100MB<br>⚠️ Requer instalação |

**Recomendação:** Use HTML → PDF (Ctrl+P). É mais rápido!

---

## ❓ Perguntas Frequentes

**P: O HTML é diferente do PDF?**
R: Não! O HTML tem o mesmo conteúdo, formatação e visual do PDF.

**P: Posso enviar o HTML para o cliente?**
R: Pode! Mas é melhor converter para PDF primeiro (Ctrl+P → Salvar como PDF).

**P: Instalei o GTK mas ainda não funciona**
R: Certifique-se de ter fechado COMPLETAMENTE o programa e aberto novamente.

**P: Preciso instalar GTK em todos os computadores?**
R: Não! Use o método HTML → PDF. Funciona em qualquer computador.

---

## ✅ Resumo

```
┌─────────────────────────────────────────┐
│  RECOMENDADO (Sem instalação):         │
│  1. Baixar HTML                         │
│  2. Abrir no navegador                  │
│  3. Ctrl+P → Salvar como PDF            │
│  4. Pronto!                             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  ALTERNATIVO (Com instalação):          │
│  1. Instalar GTK Runtime                │
│  2. Reiniciar programa                  │
│  3. Botão PDF funciona                  │
└─────────────────────────────────────────┘
```

---

**Ambos os métodos geram PDFs perfeitos e profissionais!** 🎉
