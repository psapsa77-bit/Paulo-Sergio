#!/usr/bin/env python3
"""
Exemplos de uso do FGTS Digital Robot.

Configure CERT_PATH e CERT_SENHA antes de executar.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO — altere aqui ou defina as variáveis de ambiente
# ---------------------------------------------------------------------------
CERT_PATH = os.environ.get("FGTS_CERT_PATH", "certificado.pfx")
CERT_SENHA = os.environ.get("FGTS_CERT_SENHA", "sua_senha_aqui")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# ---------------------------------------------------------------------------
# 1. Exemplo básico — processar todas as empresas
# ---------------------------------------------------------------------------

def exemplo_basico():
    """Autentica, processa todas as empresas e exporta relatório JSON."""
    print("\n=== Exemplo 1: Básico — Todas as empresas ===\n")

    from fgts_digital_robot import FGTSRobot

    with FGTSRobot(CERT_PATH, CERT_SENHA) as robot:
        robot.autenticar()
        relatorio = robot.processar_todas_empresas()

        print(f"Total de guias: {relatorio.total_guias}")
        print(f"Pendentes: {relatorio.total_pendentes}")
        print(f"Pagas: {relatorio.total_pagas}")
        print(f"Vencidas: {relatorio.total_vencidas}")
        print(f"Valor pendente: R$ {relatorio.valor_total_pendente}")

        robot.exportar_relatorio(relatorio, "relatorio_completo.json")
        print("Relatório salvo em relatorio_completo.json")


# ---------------------------------------------------------------------------
# 2. Empresa específica
# ---------------------------------------------------------------------------

def exemplo_empresa_especifica():
    """Extrai guias de uma empresa específica por CNPJ."""
    print("\n=== Exemplo 2: Empresa específica ===\n")

    from fgts_digital_robot import FGTSRobot

    robot = FGTSRobot(CERT_PATH, CERT_SENHA)
    robot.autenticar()

    try:
        # Listar e pegar o primeiro CNPJ disponível
        empresas = robot.listar_empresas()
        if not empresas:
            print("Nenhuma empresa encontrada.")
            return

        cnpj_alvo = empresas[0].cnpj
        print(f"Consultando empresa: {empresas[0].razao_social} ({cnpj_alvo})")

        guias = robot.extrair_guias_empresa(cnpj_alvo)

        print(f"\n{len(guias)} guia(s) encontrada(s):")
        for guia in guias[:10]:  # Mostra até 10
            print(
                f"  [{guia.status.value.upper():10}] {guia.numero_guia:20} "
                f"Venc: {guia.data_vencimento or 'N/A'}  "
                f"R$ {guia.valor_total}"
            )
        if len(guias) > 10:
            print(f"  ... e mais {len(guias) - 10} guia(s).")

    finally:
        robot.fechar()


# ---------------------------------------------------------------------------
# 3. Filtrar apenas pendentes e vencidas
# ---------------------------------------------------------------------------

def exemplo_apenas_pendentes():
    """Filtra somente guias pendentes e vencidas."""
    print("\n=== Exemplo 3: Apenas pendentes e vencidas ===\n")

    from fgts_digital_robot import FGTSRobot, StatusGuia

    with FGTSRobot(CERT_PATH, CERT_SENHA) as robot:
        robot.autenticar()

        relatorio = robot.processar_todas_empresas(
            filtrar_status=[StatusGuia.PENDENTE, StatusGuia.VENCIDA]
        )

        print(f"Guias pendentes/vencidas: {relatorio.total_guias}")
        print(f"Valor total a pagar: R$ {relatorio.valor_total_pendente}")

        # Ordenar por valor
        guias_ordenadas = sorted(relatorio.guias, key=lambda g: g.valor_total, reverse=True)
        print("\nTop 5 maiores valores:")
        for g in guias_ordenadas[:5]:
            print(
                f"  CNPJ {g.cnpj_empresa} | Guia {g.numero_guia} | "
                f"R$ {g.valor_total} | {g.status.value}"
            )


# ---------------------------------------------------------------------------
# 4. Exportação em múltiplos formatos
# ---------------------------------------------------------------------------

def exemplo_exportacao_multiplos_formatos():
    """Exporta o relatório em JSON e Excel."""
    print("\n=== Exemplo 4: Exportação em múltiplos formatos ===\n")

    from fgts_digital_robot import FGTSRobot

    with FGTSRobot(CERT_PATH, CERT_SENHA) as robot:
        robot.autenticar()
        relatorio = robot.processar_todas_empresas()

        # JSON
        path_json = robot.exportar_relatorio(relatorio, "relatorio_fgts.json", formato="json")
        print(f"JSON exportado: {path_json}")

        # Excel (requer openpyxl)
        try:
            path_xlsx = robot.exportar_relatorio(relatorio, "relatorio_fgts.xlsx", formato="excel")
            print(f"Excel exportado: {path_xlsx}")
        except ImportError:
            print("openpyxl não instalado. Execute: pip install openpyxl")


# ---------------------------------------------------------------------------
# 5. Análise de guias vencidas com dias de atraso
# ---------------------------------------------------------------------------

def exemplo_guias_vencidas():
    """Analisa guias vencidas e calcula dias de atraso."""
    print("\n=== Exemplo 5: Análise de guias vencidas ===\n")

    from fgts_digital_robot import FGTSRobot, StatusGuia

    with FGTSRobot(CERT_PATH, CERT_SENHA) as robot:
        robot.autenticar()

        relatorio = robot.processar_todas_empresas(
            filtrar_status=[StatusGuia.VENCIDA]
        )

        if not relatorio.guias:
            print("Nenhuma guia vencida encontrada.")
            return

        print(f"Total vencidas: {len(relatorio.guias)}")

        # Agrupar por empresa
        por_empresa: dict = {}
        for g in relatorio.guias:
            por_empresa.setdefault(g.cnpj_empresa, []).append(g)

        for cnpj, guias_emp in por_empresa.items():
            empresa = next((e for e in relatorio.empresas if e.cnpj == cnpj), None)
            nome = empresa.razao_social if empresa else cnpj
            valor = sum(g.valor_total for g in guias_emp)
            max_atraso = max((g.dias_atraso or 0) for g in guias_emp)

            print(
                f"\n  {nome}\n"
                f"    CNPJ: {cnpj}\n"
                f"    Guias vencidas: {len(guias_emp)}\n"
                f"    Valor total: R$ {valor}\n"
                f"    Maior atraso: {max_atraso} dias"
            )


# ---------------------------------------------------------------------------
# 6. Validar certificado sem abrir browser
# ---------------------------------------------------------------------------

def exemplo_validar_certificado():
    """Valida o certificado digital sem iniciar o browser."""
    print("\n=== Exemplo 6: Validar certificado ===\n")

    from fgts_digital_robot import FGTSRobot

    robot = FGTSRobot(CERT_PATH, CERT_SENHA)
    try:
        cert = robot.validar_certificado()
        print(f"Titular: {cert.nome_titular or 'N/A'}")
        print(f"CPF/CNPJ: {cert.cpf_cnpj or 'N/A'}")
        print(f"Válido até: {cert.valido_ate}")
        print(f"Dias para vencer: {cert.dias_para_vencer}")
        print(f"Está válido: {cert.esta_valido}")
    except Exception as exc:
        print(f"Certificado inválido: {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    exemplos = {
        "1": ("Básico — todas as empresas", exemplo_basico),
        "2": ("Empresa específica", exemplo_empresa_especifica),
        "3": ("Apenas pendentes/vencidas", exemplo_apenas_pendentes),
        "4": ("Exportação múltiplos formatos", exemplo_exportacao_multiplos_formatos),
        "5": ("Análise de vencidas", exemplo_guias_vencidas),
        "6": ("Validar certificado", exemplo_validar_certificado),
    }

    print("FGTS Digital Robot — Exemplos\n")
    print("Exemplos disponíveis:")
    for k, (nome, _) in exemplos.items():
        print(f"  {k}. {nome}")

    escolha = input("\nEscolha o exemplo (1-6) ou Enter para rodar todos: ").strip()

    if escolha in exemplos:
        _, func = exemplos[escolha]
        func()
    elif escolha == "":
        for _, (nome, func) in exemplos.items():
            try:
                func()
            except Exception as exc:
                print(f"Erro no exemplo '{nome}': {exc}")
    else:
        print("Opção inválida.")
        sys.exit(1)
