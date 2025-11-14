#!/usr/bin/env python3
"""
Script para executar o Robô DET (Interface Web)
Autor: Paulo Sergio
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Executa a interface web do Robô DET"""
    print("="*70)
    print("🤖 ROBÔ DET - VERIFICADOR DE MENSAGENS")
    print("="*70)
    print()
    print("🌐 Iniciando interface web...")
    print("📍 Acesse: http://localhost:8503")
    print()
    print("💡 Pressione Ctrl+C para encerrar")
    print("="*70)
    print()

    # Caminho do arquivo web
    web_file = Path(__file__).parent / "det_robot" / "web_det.py"

    # Executar Streamlit
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(web_file),
            "--server.port=8503",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
