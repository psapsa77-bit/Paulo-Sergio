#!/usr/bin/env python3
"""
Script para executar a interface web do Robô FGTS Digital

Uso:
    python run_fgts_web.py
"""
import subprocess
import sys
from pathlib import Path
import socket


def verificar_streamlit():
    """Verifica se o Streamlit está instalado"""
    try:
        import streamlit
        return True
    except ImportError:
        return False


def verificar_porta(porta=8501):
    """Verifica se uma porta está disponível"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', porta))
    sock.close()
    return result != 0  # True se porta está disponível


def main():
    """Função principal"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║        🤖 ROBÔ FGTS DIGITAL - INTERFACE WEB 🤖               ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

    # Verificar Streamlit
    if not verificar_streamlit():
        print("❌ Streamlit não está instalado!")
        print()
        print("Para instalar, execute:")
        print("   pip install streamlit")
        print()
        return 1

    print("✅ Streamlit encontrado")
    print()

    # Caminho do arquivo web
    web_file = Path(__file__).parent / "web_fgts.py"

    if not web_file.exists():
        print(f"❌ Arquivo não encontrado: {web_file}")
        return 1

    print(f"✅ Interface web encontrada: {web_file.name}")
    print()

    # Verificar porta
    porta = 8501
    if not verificar_porta(porta):
        print(f"⚠️  Porta {porta} já está em uso")
        porta = 8502
        print(f"   Tentando porta alternativa: {porta}")
        print()

    # Executar Streamlit
    print("🚀 Iniciando interface web...")
    print()
    print(f"   URL: http://localhost:{porta}")
    print()
    print("💡 Dica: Pressione Ctrl+C para encerrar")
    print()
    print("="*70)
    print()

    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(web_file),
            "--server.port",
            str(porta),
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false"
        ])
    except KeyboardInterrupt:
        print()
        print()
        print("👋 Interface web encerrada")
        return 0
    except Exception as e:
        print(f"❌ Erro ao executar: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
