#!/usr/bin/env python3
"""
Launcher para a interface web do FGTS Digital Robot.

Uso:
    python run_fgts_robot.py              # Porta padrão 8502
    python run_fgts_robot.py --port 8080  # Porta personalizada
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="FGTS Digital Robot - Interface Web")
    parser.add_argument("--port", type=int, default=8502, help="Porta do servidor (padrão: 8502)")
    parser.add_argument("--no-browser", action="store_true", help="Não abrir browser automaticamente")
    args = parser.parse_args()

    interface_path = Path(__file__).parent / "fgts_digital_robot" / "web_interface.py"

    if not interface_path.exists():
        print(f"Erro: Interface não encontrada em {interface_path}")
        sys.exit(1)

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(interface_path),
        "--server.port", str(args.port),
        "--server.address", "localhost",
    ]

    if args.no_browser:
        cmd += ["--server.headless", "true"]

    print(f"Iniciando FGTS Digital Robot na porta {args.port}…")
    print(f"Acesse: http://localhost:{args.port}")
    print("Pressione Ctrl+C para encerrar.\n")

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
    except FileNotFoundError:
        print("Erro: streamlit não encontrado. Execute: pip install streamlit")
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        print(f"Erro ao iniciar interface: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
