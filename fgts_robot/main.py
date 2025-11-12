#!/usr/bin/env python3
"""
Script principal do Robô FGTS Digital

Exemplo de uso:
    python main.py
    python main.py --cnpjs 12345678000190 98765432000110
    python main.py --arquivo lista_cnpjs.txt
"""
import argparse
import sys
from pathlib import Path
from typing import List

# Adicionar diretório atual ao path para imports funcionarem
sys.path.insert(0, str(Path(__file__).parent))

from robo_fgts import RoboFGTS
import config


def ler_cnpjs_arquivo(caminho: str) -> List[str]:
    """
    Lê lista de CNPJs de um arquivo de texto

    Args:
        caminho: Caminho para o arquivo

    Returns:
        Lista de CNPJs
    """
    try:
        arquivo = Path(caminho)
        if not arquivo.exists():
            print(f"❌ Arquivo não encontrado: {caminho}")
            return []

        with open(arquivo, "r", encoding="utf-8") as f:
            cnpjs = [
                linha.strip()
                for linha in f
                if linha.strip() and not linha.strip().startswith("#")
            ]

        return cnpjs

    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {str(e)}")
        return []


def validar_cnpj(cnpj: str) -> bool:
    """
    Validação básica de CNPJ

    Args:
        cnpj: CNPJ a validar

    Returns:
        bool: True se válido (formato básico)
    """
    # Remove formatação
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()

    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14 or not cnpj_limpo.isdigit():
        return False

    return True


def exibir_banner():
    """Exibe banner do programa"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           🤖 ROBÔ DE AUTOMAÇÃO FGTS DIGITAL 🤖               ║
║                                                               ║
║                    Versão 1.0.0                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def exibir_configuracoes():
    """Exibe configurações atuais"""
    print("\n📋 Configurações:")
    print(f"   • Certificado: {config.CERT_PATH}")
    print(f"   • Modo headless: {'Sim' if config.HEADLESS else 'Não'}")
    print(f"   • Timeout: {config.BROWSER_TIMEOUT}ms")
    print(f"   • Diretório de resultados: {config.RESULTS_DIR}")
    print(f"   • Diretório de logs: {config.LOGS_DIR}")


def confirmar_execucao(cnpjs: List[str]) -> bool:
    """
    Solicita confirmação do usuário

    Args:
        cnpjs: Lista de CNPJs que serão processados

    Returns:
        bool: True se usuário confirmou
    """
    print(f"\n📊 Total de empresas a processar: {len(cnpjs)}")
    print("\nEmpresas:")
    for i, cnpj in enumerate(cnpjs, 1):
        print(f"   {i}. {cnpj}")

    resposta = input("\n❓ Deseja continuar? (s/n): ").strip().lower()
    return resposta in ("s", "sim", "y", "yes")


def main():
    """Função principal"""
    # Exibir banner
    exibir_banner()

    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description="Robô de automação para consulta FGTS Digital",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Modo interativo (solicita CNPJs)
  python main.py

  # Processar CNPJs específicos
  python main.py --cnpjs 12345678000190 98765432000110

  # Processar CNPJs de um arquivo
  python main.py --arquivo lista_cnpjs.txt

  # Modo headless
  python main.py --cnpjs 12345678000190 --headless

  # Especificar certificado
  python main.py --cert certificados/meu_cert.pfx --senha minha_senha
        """
    )

    parser.add_argument(
        "--cnpjs",
        nargs="+",
        help="Lista de CNPJs para processar"
    )

    parser.add_argument(
        "--arquivo",
        "-a",
        help="Arquivo com lista de CNPJs (um por linha)"
    )

    parser.add_argument(
        "--cert",
        help="Caminho para o certificado .pfx"
    )

    parser.add_argument(
        "--senha",
        help="Senha do certificado"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executar em modo headless (sem interface gráfica)"
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help="Exibir configurações atuais e sair"
    )

    parser.add_argument(
        "--sim",
        "-y",
        action="store_true",
        help="Confirmar automaticamente (não solicitar confirmação)"
    )

    args = parser.parse_args()

    # Se solicitado, exibir configurações e sair
    if args.config:
        exibir_configuracoes()
        return 0

    # Obter lista de CNPJs
    cnpjs = []

    if args.cnpjs:
        cnpjs = args.cnpjs
    elif args.arquivo:
        cnpjs = ler_cnpjs_arquivo(args.arquivo)
    else:
        # Modo interativo
        print("\n📝 Modo interativo")
        print("   Digite os CNPJs (um por linha)")
        print("   Digite 'fim' quando terminar\n")

        while True:
            cnpj = input("CNPJ: ").strip()
            if cnpj.lower() in ("fim", "end", "exit", "quit"):
                break
            if cnpj:
                cnpjs.append(cnpj)

    # Validar CNPJs
    if not cnpjs:
        print("\n❌ Nenhum CNPJ fornecido!")
        parser.print_help()
        return 1

    # Validar formato dos CNPJs
    cnpjs_validos = []
    for cnpj in cnpjs:
        if validar_cnpj(cnpj):
            cnpjs_validos.append(cnpj)
        else:
            print(f"⚠️  CNPJ inválido ignorado: {cnpj}")

    if not cnpjs_validos:
        print("\n❌ Nenhum CNPJ válido encontrado!")
        return 1

    # Exibir configurações
    exibir_configuracoes()

    # Confirmar execução (se não for auto-confirmação)
    if not args.sim:
        if not confirmar_execucao(cnpjs_validos):
            print("\n❌ Execução cancelada pelo usuário")
            return 0

    # Inicializar robô
    print("\n🚀 Iniciando robô...\n")

    try:
        robo = RoboFGTS(
            cert_path=args.cert,
            cert_password=args.senha,
            headless=args.headless
        )

        # Processar clientes
        sucesso = robo.processar_clientes(cnpjs_validos)

        if sucesso:
            print("\n✅ Processamento concluído com sucesso!")
            print(f"📂 Resultados salvos em: {config.RESULTS_DIR}")
            return 0
        else:
            print("\n❌ Processamento falhou. Verifique os logs.")
            print(f"📂 Logs em: {config.LOGS_DIR}")
            return 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        return 130

    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        print(f"📂 Verifique os logs em: {config.LOGS_DIR}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
