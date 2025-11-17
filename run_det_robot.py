#!/usr/bin/env python3
"""
Script para executar o DET Robot com interface web Streamlit
"""

import subprocess
import sys
from pathlib import Path


def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""

    dependencias_faltando = []

    # Verificar Streamlit
    try:
        import streamlit
    except ImportError:
        dependencias_faltando.append("streamlit")

    # Verificar Selenium
    try:
        import selenium
    except ImportError:
        dependencias_faltando.append("selenium")

    if dependencias_faltando:
        print("╔═══════════════════════════════════════════════════════╗")
        print("║                                                       ║")
        print("║          ❌ DEPENDÊNCIAS NÃO INSTALADAS               ║")
        print("║                                                       ║")
        print("╚═══════════════════════════════════════════════════════╝")
        print()
        print("Faltam os seguintes pacotes:")
        for dep in dependencias_faltando:
            print(f"  • {dep}")
        print()
        print("SOLUÇÃO:")
        print()
        print("  Execute o instalador automático:")
        print("    ./INSTALAR_TUDO.sh")
        print()
        print("  Ou instale manualmente:")
        print("    pip3 install -r requirements.txt")
        print()
        return False

    return True


def main():
    print()
    print("╔═══════════════════════════════════════════════════════╗")
    print("║                                                       ║")
    print("║                    DET ROBOT                          ║")
    print("║          Extrator de Mensagens do DET                 ║")
    print("║                                                       ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print()

    # Verificar dependências
    if not verificar_dependencias():
        sys.exit(1)

    # Caminho do módulo web
    script_dir = Path(__file__).parent
    web_module = script_dir / "det_robot" / "web_interface.py"

    if not web_module.exists():
        print("❌ Erro: Módulo web_interface.py não encontrado")
        print(f"   Procurando em: {web_module}")
        print()
        print("Verifique se a pasta 'det_robot' está presente.")
        sys.exit(1)

    print("Iniciando interface web...")
    print()
    print("┌───────────────────────────────────────────────────────┐")
    print("│                                                       │")
    print("│  A interface será aberta automaticamente em:         │")
    print("│                                                       │")
    print("│       👉  http://localhost:8502                       │")
    print("│                                                       │")
    print("│  Se não abrir, copie e cole o link no navegador.     │")
    print("│                                                       │")
    print("└───────────────────────────────────────────────────────┘")
    print()
    print("Para FECHAR o programa: pressione Ctrl+C")
    print("═══════════════════════════════════════════════════════")
    print()

    # Executar Streamlit
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(web_module),
                "--server.port=8502",
                "--server.headless=true",
                "--browser.gatherUsageStats=false",
            ],
            cwd=str(script_dir),
        )
    except KeyboardInterrupt:
        print()
        print("═══════════════════════════════════════════════════════")
        print("DET Robot encerrado. Até logo!")
        print("═══════════════════════════════════════════════════════")
        print()
    except FileNotFoundError:
        print()
        print("❌ ERRO: Streamlit não encontrado!")
        print()
        print("Execute: ./INSTALAR_TUDO.sh")
        print()
        sys.exit(1)
    except Exception as e:
        print()
        print(f"❌ Erro ao iniciar: {e}")
        print()
        print("Tente executar o diagnóstico:")
        print("  python3 diagnostico_det.py")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
