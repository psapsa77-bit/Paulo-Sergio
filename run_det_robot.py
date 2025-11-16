#!/usr/bin/env python3
"""
Script para executar o DET Robot com interface web Streamlit
"""

import subprocess
import sys
from pathlib import Path


def main():
    # Caminho do módulo web
    script_dir = Path(__file__).parent
    web_module = script_dir / "det_robot" / "web_interface.py"

    if not web_module.exists():
        print("Erro: Módulo web_interface.py não encontrado")
        print(f"Procurando em: {web_module}")
        sys.exit(1)

    print("=" * 50)
    print("  DET Robot - Interface Web")
    print("=" * 50)
    print()
    print("Iniciando interface Streamlit...")
    print("A interface será aberta automaticamente no navegador.")
    print()
    print("Para fechar, pressione Ctrl+C neste terminal.")
    print("=" * 50)

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
        print("\nEncerrando DET Robot...")
    except Exception as e:
        print(f"Erro ao iniciar: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
