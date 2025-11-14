# 📋 Analisador de Rescisões Trabalhistas

Aplicativo web para análise automatizada de rescisões trabalhistas usando inteligência artificial (Claude API).

## ✨ Funcionalidades

- 📤 Upload de documentos PDF (Termo de Rescisão - TRCT)
- 🤖 Análise automática com IA Claude
- 💰 Extração detalhada de verbas e descontos
- 📊 Visualização clara de créditos, débitos e valor líquido
- 📄 Geração de relatórios profissionais em HTML/PDF
- 💾 Armazenamento local de análises
- 🧪 Dados de exemplo para demonstração

## 🚀 Como Executar

### Pré-requisitos

- Node.js 18+ instalado
- npm ou yarn

### Instalação

1. Navegue até o diretório do projeto:
```bash
cd rescission-analyzer-app
```

2. Instale as dependências:
```bash
npm install
```

### Executar em Desenvolvimento

```bash
npm run dev
```

O aplicativo estará disponível em `http://localhost:5173`

### Build para Produção

```bash
npm run build
```

Os arquivos otimizados estarão em `dist/`

### Pré-visualizar Build

```bash
npm run preview
```

## 📖 Como Usar

### 1. Visualizar Exemplo
- Clique em **"Ver Exemplo"** para carregar dados de demonstração
- Explore a interface e veja como funciona a análise

### 2. Nova Análise
- Clique em **"Nova Análise"**
- Faça upload do Termo de Rescisão (PDF)
- Opcionalmente, preencha os valores de FGTS manualmente
- Clique em **"Analisar Documentos"**

### 3. Visualizar Resultados
- Veja o resumo financeiro com créditos, débitos e valor líquido
- Explore os detalhes de cada verba
- Leia as observações sobre a rescisão

### 4. Gerar Relatório
- Clique em **"Gerar Relatório"**
- Copie o HTML gerado
- Salve como arquivo `.html`
- Abra no navegador e use Ctrl+P para gerar PDF

## ⚙️ Configuração da API Claude

Para usar a análise automática com IA, você precisa configurar a API Key da Anthropic:

1. Obtenha uma API Key em: https://console.anthropic.com/
2. No código (`src/RescissionAnalyzer.tsx`), adicione o header de autenticação:

```typescript
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-api-key": "SUA_API_KEY_AQUI", // Adicione sua API key
    "anthropic-version": "2023-06-01"
  },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 8000,
    messages
  })
});
```

**Nota:** Para ambientes de produção, use variáveis de ambiente para armazenar a API Key de forma segura.

## 🛠️ Tecnologias Utilizadas

- **React 18** - Framework UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool moderna e rápida
- **Tailwind CSS** - Estilização com utility-first
- **Lucide React** - Ícones modernos
- **Claude API** - Análise de documentos com IA

## 📁 Estrutura do Projeto

```
rescission-analyzer-app/
├── src/
│   ├── App.tsx                    # Componente raiz
│   ├── RescissionAnalyzer.tsx     # Componente principal
│   ├── main.tsx                   # Entry point
│   ├── index.css                  # Estilos globais
│   └── vite-env.d.ts             # Types do Vite
├── public/                        # Arquivos estáticos
├── index.html                     # HTML template
├── package.json                   # Dependências
├── tsconfig.json                  # Config TypeScript
├── vite.config.ts                 # Config Vite
├── tailwind.config.js             # Config Tailwind
└── README.md                      # Este arquivo
```

## 🔒 Segurança

- ⚠️ **Nunca** exponha API Keys no código do cliente
- Use variáveis de ambiente para dados sensíveis
- Considere implementar um backend para gerenciar autenticação com a API Claude
- Os dados são armazenados localmente no navegador (localStorage)

## 🤝 Modo Fallback

Se a API Claude não estiver disponível, o aplicativo automaticamente:
- Exibe dados de exemplo (Wanessa Nascimento Sousa)
- Permite testar todas as funcionalidades
- Mostra alerta informativo ao usuário

## 📝 Notas Importantes

1. **Análise de PDF**: A qualidade da extração depende da formatação do PDF
2. **Timeout**: Análises com timeout de 60 segundos (ajustável)
3. **FGTS Manual**: Permite preencher valores de FGTS se não estiverem no PDF
4. **Formato de Datas**: Usa formato brasileiro (DD/MM/AAAA)
5. **Moeda**: Todos os valores em Real (R$)

## 🐛 Resolução de Problemas

### Erro ao fazer upload do PDF
- Verifique se o arquivo é um PDF válido
- Tamanho máximo recomendado: 10MB
- Certifique-se de que o PDF não está protegido por senha

### API não responde
- Verifique se a API Key está correta
- Confirme que há créditos disponíveis na conta Anthropic
- Verifique sua conexão com a internet
- O app usará dados de exemplo em caso de falha

### Build falha
```bash
# Limpe o cache e reinstale
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📄 Licença

Este projeto é fornecido como está, sem garantias. Adapte conforme necessário para seu caso de uso.

## 👨‍💻 Desenvolvimento

### Scripts Disponíveis

- `npm run dev` - Inicia servidor de desenvolvimento
- `npm run build` - Cria build de produção
- `npm run preview` - Pré-visualiza build
- `npm run lint` - Executa linter

### Melhorias Futuras

- [ ] Backend para gerenciar API keys de forma segura
- [ ] Suporte para múltiplos formatos de documento
- [ ] Exportação direta para PDF (sem HTML intermediário)
- [ ] Histórico de análises com busca e filtros
- [ ] Comparação entre rescisões
- [ ] Relatórios estatísticos
- [ ] Autenticação de usuários
- [ ] Armazenamento em nuvem

## 📧 Suporte

Para dúvidas sobre legislação trabalhista, consulte um advogado especializado. Este aplicativo é uma ferramenta de apoio e não substitui orientação jurídica profissional.

---

Desenvolvido com ❤️ usando React + TypeScript + Vite
