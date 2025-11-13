# 🛡️ Sistema de Resolução de CAPTCHA

O Robô FGTS possui um sistema inteligente para detectar e resolver CAPTCHAs automaticamente.

## 📋 Índice

1. [Como Funciona](#como-funciona)
2. [Modo Manual (Padrão)](#modo-manual-padrão)
3. [Modo Automático (Avançado)](#modo-automático-avançado)
4. [Configuração](#configuração)
5. [Tipos de CAPTCHA Suportados](#tipos-de-captcha-suportados)
6. [Solução de Problemas](#solução-de-problemas)

---

## 🔍 Como Funciona

O robô verifica automaticamente se há CAPTCHA nas seguintes etapas:

1. **Após navegação inicial** - Quando acessa o portal
2. **Antes do certificado** - Antes de clicar no botão de certificado digital
3. **Após autenticação** - Depois de fazer login

Se um CAPTCHA for detectado, o robô pode:
- **Pausar e aguardar** você resolver manualmente (modo padrão)
- **Resolver automaticamente** usando serviço 2Captcha (modo avançado)

---

## 🖐️ Modo Manual (Padrão)

**Este é o modo recomendado para iniciantes!**

### Como Usar:

1. Certifique-se de que o modo manual está ativado no `.env`:
   ```env
   CAPTCHA_MANUAL=True
   HEADLESS=False
   ```

2. Execute o robô normalmente

3. Quando um CAPTCHA for detectado, você verá:
   ```
   ======================================================================
   🔴 CAPTCHA DETECTADO - AÇÃO NECESSÁRIA!
   ======================================================================
   Tipo: recaptcha_v2

   📋 INSTRUÇÕES:
     1. Vá até a janela do navegador que foi aberta
     2. Resolva o CAPTCHA manualmente
     3. Aguarde - o robô continuará automaticamente

   ⏱️  Tempo limite: 300 segundos (5 minutos)
   ======================================================================
   ```

4. **Vá até a janela do navegador** que foi aberta

5. **Resolva o CAPTCHA** clicando nas imagens ou marcando "Não sou robô"

6. **Aguarde** - O robô detecta automaticamente quando você resolveu e continua!

### Configurações:

```env
# Tempo máximo para resolver (em segundos)
CAPTCHA_TIMEOUT=300  # 5 minutos padrão
```

---

## 🤖 Modo Automático (Avançado)

**Para usuários avançados que querem automação completa.**

Este modo usa o serviço **2Captcha** para resolver CAPTCHAs automaticamente.

### Pré-requisitos:

1. **Conta no 2Captcha**
   - Acesse: https://2captcha.com
   - Crie uma conta
   - Adicione créditos (preço: ~$3 por 1000 CAPTCHAs)
   - Copie sua chave API

2. **Instalar biblioteca**
   ```bash
   pip install 2captcha-python
   ```

### Configuração:

1. Adicione sua chave API no `.env`:
   ```env
   CAPTCHA_MANUAL=False
   2CAPTCHA_API_KEY=sua_chave_api_aqui
   ```

2. Execute o robô normalmente - CAPTCHAs serão resolvidos automaticamente!

### Como Funciona:

1. Robô detecta CAPTCHA
2. Envia para 2Captcha resolver
3. Aguarda resposta (15-60 segundos)
4. Injeta resposta na página
5. Continua execução

### Custos:

- **reCAPTCHA v2**: ~$1.00 por 1000 resoluções
- **hCaptcha**: ~$2.00 por 1000 resoluções
- **Imagem**: ~$0.50 por 1000 resoluções

---

## ⚙️ Configuração

### Arquivo `.env`

```env
# ============================================
# CONFIGURAÇÕES DE CAPTCHA
# ============================================

# Modo manual: pausar e aguardar usuário resolver CAPTCHA
# Se False, tentará resolver automaticamente com 2Captcha (requer API key)
CAPTCHA_MANUAL=True

# Tempo máximo para aguardar resolução manual do CAPTCHA (segundos)
CAPTCHA_TIMEOUT=300

# Chave API do 2Captcha (opcional - apenas para resolução automática)
# Obtenha em: https://2captcha.com
# 2CAPTCHA_API_KEY=sua_chave_api_aqui
```

### Modo Headless e CAPTCHA

⚠️ **IMPORTANTE**: Se você usar `HEADLESS=True` (sem interface gráfica), **não poderá resolver CAPTCHAs manualmente!**

Opções:
- Use `HEADLESS=False` para resolução manual
- Use `HEADLESS=True` + 2Captcha para resolução automática

---

## 🎯 Tipos de CAPTCHA Suportados

### ✅ Detecção Automática:

1. **reCAPTCHA v2** (Google)
   - Checkbox "Não sou um robô"
   - Seleção de imagens

2. **hCaptcha**
   - Similar ao reCAPTCHA
   - Comum em sites gov.br

3. **CAPTCHA de Imagem**
   - Digite o texto da imagem
   - Menos comum hoje em dia

4. **CAPTCHA Generic**
   - Detectado via análise de HTML

### Resolução Manual:

✅ **Todos os tipos** - Você pode resolver qualquer CAPTCHA manualmente!

### Resolução Automática (2Captcha):

✅ **reCAPTCHA v2** - Suportado
✅ **hCaptcha** - Suportado
⚠️ **CAPTCHA de Imagem** - Suporte limitado
❌ **reCAPTCHA v3** - Não suportado (invisível)

---

## 🔧 Solução de Problemas

### Problema: "CAPTCHA detectado em modo HEADLESS!"

**Causa**: Você está tentando usar modo manual com navegador invisível.

**Solução**:
```env
HEADLESS=False
```

ou configure 2Captcha para resolver automaticamente.

---

### Problema: "Timeout: CAPTCHA não foi resolvido em 300 segundos"

**Causa**: Você demorou muito para resolver o CAPTCHA.

**Solução**: Aumente o timeout:
```env
CAPTCHA_TIMEOUT=600  # 10 minutos
```

---

### Problema: "Biblioteca 'twocaptcha' não instalada!"

**Causa**: Você configurou 2Captcha mas não instalou a biblioteca.

**Solução**:
```bash
pip install 2captcha-python
```

---

### Problema: CAPTCHA não foi detectado

**Causa**: O CAPTCHA usa tecnologia nova ou seletores diferentes.

**Solução**:
1. Tire um screenshot e reporte no GitHub
2. Use resolução manual como workaround
3. Aguarde atualização do robô

---

### Problema: 2Captcha não está funcionando

**Causas possíveis**:
- Chave API inválida
- Sem créditos na conta
- Tipo de CAPTCHA não suportado

**Solução**:
1. Verifique sua chave API
2. Verifique saldo em https://2captcha.com
3. Veja os logs para mais detalhes
4. Use modo manual como fallback

---

## 📊 Comparação de Modos

| Característica | Manual | Automático (2Captcha) |
|----------------|--------|-----------------------|
| **Custo** | ✅ Grátis | 💰 Pago (~$3/1000) |
| **Velocidade** | 🐌 Depende de você | ⚡ 15-60 segundos |
| **Configuração** | ✅ Simples | ⚙️ Requer API key |
| **Todos CAPTCHAs** | ✅ Sim | ⚠️ Maioria |
| **Modo Headless** | ❌ Não | ✅ Sim |
| **Recomendado para** | 👤 Iniciantes | 🏢 Uso em escala |

---

## 💡 Dicas

### Para Iniciantes:
- Use **modo manual** - é grátis e funciona sempre
- Configure `HEADLESS=False` para ver o navegador
- Aumente o timeout se precisar de mais tempo

### Para Uso em Produção:
- Configure **2Captcha** para automação completa
- Use `HEADLESS=True` para economizar recursos
- Monitore os custos no painel do 2Captcha

### Para Economizar:
- Use modo manual quando possível
- Reserve 2Captcha para execuções noturnas/automáticas
- Configure timeout menor para falhar mais rápido

---

## 📞 Suporte

Se você encontrar problemas com CAPTCHA:

1. **Verifique os logs** - Há mensagens detalhadas sobre o que aconteceu
2. **Tire screenshots** - Use `diagnosticar.py` para capturar o estado
3. **Reporte no GitHub** - Abra uma issue com logs e screenshots
4. **Modo manual sempre funciona** - Use como fallback

---

## 🎓 Exemplos de Uso

### Exemplo 1: Iniciante (Manual)

```bash
# .env
CAPTCHA_MANUAL=True
HEADLESS=False
CAPTCHA_TIMEOUT=600

# Executar
python main.py --cnpjs 12345678000190
```

### Exemplo 2: Avançado (Automático)

```bash
# .env
CAPTCHA_MANUAL=False
HEADLESS=True
2CAPTCHA_API_KEY=abc123...

# Executar
python main.py --cnpjs 12345678000190,98765432000100
```

### Exemplo 3: Híbrido (Tenta automático, fallback manual)

```bash
# .env
CAPTCHA_MANUAL=False  # Tenta automático primeiro
HEADLESS=False  # Permite fallback manual
2CAPTCHA_API_KEY=abc123...

# Se 2Captcha falhar, você pode resolver manualmente!
```

---

## 📈 Estatísticas

O robô loga todas as interações com CAPTCHA:

```
[INFO] ✋ CAPTCHA detectado: recaptcha_v2
[INFO] 🤖 Tentando resolver CAPTCHA automaticamente com 2Captcha...
[INFO] ✅ CAPTCHA resolvido automaticamente!
```

Você pode analisar os logs em `fgts_robot/logs/` para ver:
- Quantos CAPTCHAs foram encontrados
- Quanto tempo levou para resolver
- Taxa de sucesso

---

**Atualizado em**: 2025-01-13
**Versão**: 2.0.0
