#!/usr/bin/env python3
"""
Script de teste rápido para o DET Robot
Verifica se todos os módulos estão funcionando corretamente
"""

import sys
from pathlib import Path


def testar_imports():
    """Testa se todos os módulos podem ser importados"""
    print("Testando imports...")

    try:
        from det_robot import (
            BrowserManager,
            DETAuthenticator,
            DETScraper,
            DETStorage,
            MensagemDET,
            EmpregadorDET,
            ResultadoExtracao,
        )
        print("  ✓ Módulos principais importados com sucesso")
    except ImportError as e:
        print(f"  ✗ Erro ao importar módulos: {e}")
        return False

    try:
        from det_robot.models import ConfiguracaoDET, StatusMensagem, TipoMensagem
        print("  ✓ Modelos importados com sucesso")
    except ImportError as e:
        print(f"  ✗ Erro ao importar modelos: {e}")
        return False

    return True


def testar_dependencias():
    """Testa se as dependências estão instaladas"""
    print("\nTestando dependências...")

    deps = {
        "selenium": "Automação web",
        "pydantic": "Validação de dados",
        "streamlit": "Interface web",
        "plotly": "Gráficos",
        "typer": "CLI",
        "rich": "Formatação de terminal",
    }

    todas_ok = True

    for modulo, descricao in deps.items():
        try:
            __import__(modulo)
            print(f"  ✓ {modulo} ({descricao})")
        except ImportError:
            print(f"  ✗ {modulo} ({descricao}) - NÃO INSTALADO")
            todas_ok = False

    # Testar webdriver-manager (opcional mas recomendado)
    try:
        import webdriver_manager
        print(f"  ✓ webdriver-manager (Gerenciador de drivers)")
    except ImportError:
        print(f"  ⚠ webdriver-manager - Não instalado (recomendado)")

    # Testar openpyxl (opcional)
    try:
        import openpyxl
        print(f"  ✓ openpyxl (Suporte Excel)")
    except ImportError:
        print(f"  ⚠ openpyxl - Não instalado (opcional para Excel)")

    return todas_ok


def testar_navegadores():
    """Testa quais navegadores estão disponíveis"""
    print("\nTestando navegadores...")

    import shutil
    import platform

    sistema = platform.system().lower()
    encontrado = False

    navegadores = []

    if sistema == "linux":
        navegadores = [
            ("Google Chrome", ["google-chrome", "google-chrome-stable"]),
            ("Chromium", ["chromium-browser", "chromium"]),
            ("Firefox", ["firefox"]),
        ]
    elif sistema == "darwin":  # macOS
        navegadores = [
            ("Google Chrome", ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]),
            ("Firefox", ["/Applications/Firefox.app/Contents/MacOS/firefox"]),
        ]
    else:  # Windows
        print("  ⚠ Detecção de navegadores no Windows não implementada neste teste")
        return True

    for nome, caminhos in navegadores:
        for caminho in caminhos:
            if shutil.which(caminho) or Path(caminho).exists():
                print(f"  ✓ {nome} encontrado")
                encontrado = True
                break

    if not encontrado:
        print("  ✗ Nenhum navegador suportado encontrado!")
        print("    Instale Google Chrome, Chromium ou Firefox")

    return encontrado


def testar_modelos():
    """Testa se os modelos funcionam corretamente"""
    print("\nTestando modelos de dados...")

    try:
        from datetime import datetime
        from det_robot.models import (
            MensagemDET,
            EmpregadorDET,
            ResultadoExtracao,
            StatusMensagem,
            TipoMensagem,
        )

        # Criar mensagem de teste
        msg = MensagemDET(
            id_mensagem="teste_001",
            assunto="Notificação de Teste",
            tipo=TipoMensagem.NOTIFICACAO,
            data_envio=datetime.now(),
            remetente="Sistema de Teste",
            status=StatusMensagem.NAO_LIDA,
        )
        print(f"  ✓ MensagemDET criada: {msg.assunto}")

        # Criar empregador de teste
        emp = EmpregadorDET(
            cnpj_cpf="12.345.678/0001-90",
            razao_social="Empresa Teste LTDA",
            mensagens_nao_lidas=5,
        )
        print(f"  ✓ EmpregadorDET criado: {emp.cnpj_cpf}")

        # Criar resultado de teste
        resultado = ResultadoExtracao(
            mensagens=[msg],
            total_extraido=1,
            sucesso=True,
        )
        print(f"  ✓ ResultadoExtracao criado: {resultado.total_extraido} mensagem(s)")

        # Testar serialização JSON
        json_data = resultado.model_dump(mode="json")
        print(f"  ✓ Serialização JSON funcionando")

        return True

    except Exception as e:
        print(f"  ✗ Erro ao testar modelos: {e}")
        return False


def testar_storage():
    """Testa o módulo de armazenamento"""
    print("\nTestando armazenamento...")

    try:
        from datetime import datetime
        from det_robot.storage import DETStorage
        from det_robot.models import ResultadoExtracao, MensagemDET, StatusMensagem, TipoMensagem

        # Criar pasta temporária de teste
        pasta_teste = Path("./teste_det_storage")
        pasta_teste.mkdir(exist_ok=True)

        storage = DETStorage(str(pasta_teste))
        print(f"  ✓ DETStorage inicializado")

        # Criar resultado de teste
        msg = MensagemDET(
            id_mensagem="teste_001",
            assunto="Teste de armazenamento",
            tipo=TipoMensagem.COMUNICADO,
            data_envio=datetime.now(),
            remetente="Teste",
            status=StatusMensagem.NAO_LIDA,
        )

        resultado = ResultadoExtracao(
            mensagens=[msg],
            total_extraido=1,
            sucesso=True,
            tempo_execucao=1.5,
        )

        # Testar salvamento
        arquivo_json = storage.salvar_json(resultado, "teste.json")
        print(f"  ✓ JSON salvo: {arquivo_json}")

        # Testar carregamento
        resultado_carregado = storage.carregar_json(arquivo_json)
        print(f"  ✓ JSON carregado: {resultado_carregado.total_extraido} mensagem(s)")

        # Testar relatório texto
        relatorio = storage.gerar_relatorio_texto(resultado)
        print(f"  ✓ Relatório gerado: {len(relatorio)} caracteres")

        # Limpar teste
        import shutil
        shutil.rmtree(pasta_teste)
        print(f"  ✓ Pasta de teste removida")

        return True

    except Exception as e:
        print(f"  ✗ Erro ao testar storage: {e}")
        return False


def main():
    print("=" * 50)
    print("  DET Robot - Teste de Instalação")
    print("=" * 50)

    resultados = []

    resultados.append(("Imports", testar_imports()))
    resultados.append(("Dependências", testar_dependencias()))
    resultados.append(("Navegadores", testar_navegadores()))
    resultados.append(("Modelos", testar_modelos()))
    resultados.append(("Armazenamento", testar_storage()))

    print("\n" + "=" * 50)
    print("  RESUMO DOS TESTES")
    print("=" * 50)

    todos_ok = True
    for nome, resultado in resultados:
        status = "✓ OK" if resultado else "✗ FALHOU"
        print(f"  {nome}: {status}")
        if not resultado:
            todos_ok = False

    print("=" * 50)

    if todos_ok:
        print("\n✓ Todos os testes passaram!")
        print("\nPróximos passos:")
        print("  1. Execute: python run_det_robot.py")
        print("  2. Acesse: http://localhost:8502")
        print("  3. Faça login e extraia suas mensagens!")
        return 0
    else:
        print("\n✗ Alguns testes falharam!")
        print("\nVerifique as dependências e tente novamente.")
        print("Execute: pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
