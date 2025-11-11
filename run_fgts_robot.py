#!/usr/bin/env python3
"""
Script para executar a interface web do FGTS Digital Robot
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Executa a interface Streamlit"""

    # Caminho do arquivo web_interface.py
    web_file = Path(__file__).parent / "fgts_digital_robot" / "web_interface.py"

    if not web_file.exists():
        print(f"❌ Erro: Arquivo não encontrado: {web_file}")
        sys.exit(1)

    print("🤖 Iniciando FGTS Digital Robot...")
    print(f"📂 Arquivo: {web_file}")
    print("🌐 Abrindo interface web...")
    print()

    # Executar Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(web_file),
        "--server.port=8502",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ])

if __name__ == "__main__":
    main()
