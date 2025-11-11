#!/usr/bin/env python3
"""
Script para iniciar a interface web do Labor Termination Analyzer.

Uso:
    python run_web.py
    ou
    python3 run_web.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Inicia o servidor Streamlit."""
    # Usa app.py como entry point para evitar problemas de import
    app_path = Path(__file__).parent / 'app.py'

    if not app_path.exists():
        print("❌ ERRO: Arquivo app.py não encontrado!")
        print("Verifique se a instalação está completa.")
        sys.exit(1)

    # Comando do streamlit
    cmd = [
        sys.executable,
        '-m',
        'streamlit',
        'run',
        str(app_path),
        '--server.port=8501',
        '--server.headless=true',
        '--browser.gatherUsageStats=false'
    ]

    print("🚀 Iniciando interface web...")
    print("📍 Acesse: http://localhost:8501")
    print("")
    print("⚠️  Para parar o servidor, pressione Ctrl+C")
    print("")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n✅ Servidor encerrado.")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar: {e}")
        print("\nTente instalar o Streamlit:")
        print("  pip install streamlit")
        sys.exit(1)


if __name__ == '__main__':
    main()
