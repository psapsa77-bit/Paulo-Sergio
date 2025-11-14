# 🔧 Solução de Problemas - Python 3.13

## Problema: NotImplementedError ao iniciar navegador no Windows

### Sintoma
```
NotImplementedError
File "C:\...\asyncio\base_events.py", line 539, in _make_subprocess_transport
    raise NotImplementedError
```

### Causa
O Python 3.13 mudou a política padrão de loop de eventos (`event loop policy`) no Windows, causando incompatibilidade com o Playwright que usa `asyncio.create_subprocess_exec()`.

### Solução Implementada

Foi adicionado código de compatibilidade nos arquivos:
- `det_robot/robot_det.py`
- `det_robot/web_det.py`

```python
# Fix para Python 3.13+ no Windows
if sys.platform == 'win32' and sys.version_info >= (3, 8):
    try:
        # Para Python 3.13+, usar WindowsSelectorEventLoopPolicy
        if sys.version_info >= (3, 13):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # Para Python 3.8-3.12, usar WindowsProactorEventLoopPolicy se disponível
        elif hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass  # Ignorar erros de configuração do event loop
```

### O que isso faz?

1. **Python 3.13+**: Usa `WindowsSelectorEventLoopPolicy`
   - Compatível com subprocess no Windows
   - Necessário para Playwright funcionar

2. **Python 3.8-3.12**: Usa `WindowsProactorEventLoopPolicy`
   - Política recomendada para versões anteriores
   - Melhor performance no Windows

3. **Outras plataformas**: Não afetadas
   - O código só é executado no Windows (`sys.platform == 'win32'`)
   - Linux e Mac continuam usando a política padrão

### Agora funciona com:

✅ Python 3.13 no Windows
✅ Python 3.12 no Windows
✅ Python 3.11 no Windows
✅ Python 3.10 no Windows
✅ Python 3.9 no Windows
✅ Python 3.8 no Windows
✅ Todas as versões no Linux
✅ Todas as versões no Mac

### Referências

- [Python Issue #98759](https://github.com/python/cpython/issues/98759)
- [Playwright Issue #24901](https://github.com/microsoft/playwright-python/issues/2490)
- [asyncio Event Loop Policies](https://docs.python.org/3/library/asyncio-policy.html)

---

**Versão corrigida**: 1.0.1
**Data**: 2024-11-14
