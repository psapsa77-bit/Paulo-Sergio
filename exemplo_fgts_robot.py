#!/usr/bin/env python3
"""
Exemplo de uso do FGTS Digital Robot via código Python
=======================================================

Este script demonstra como usar o robô programaticamente.
"""

from pathlib import Path
from fgts_digital_robot import FGTSRobot, StatusGuia


def exemplo_basico():
    """Exemplo básico de uso do robô"""

    print("🤖 FGTS Digital Robot - Exemplo Básico")
    print("=" * 60)

    # Configurar certificado
    certificado_path = "certificado.pfx"  # Altere para o caminho do seu certificado
    senha = "sua_senha_aqui"              # Altere para sua senha

    # Verificar se certificado existe
    if not Path(certificado_path).exists():
        print(f"❌ Certificado não encontrado: {certificado_path}")
        print("Por favor, altere o caminho no script")
        return

    try:
        # Criar robô usando context manager (fecha automaticamente)
        with FGTSRobot(certificado_path, senha, headless=False) as robot:

            print("\n1️⃣ Validando certificado...")
            info_cert = robot.validar_certificado()
            print(f"   ✅ Titular: {info_cert['nome_titular']}")
            print(f"   ✅ Válido até: {info_cert['valido_ate']}")
            print(f"   ✅ Dias para vencer: {info_cert['dias_para_vencer']}")

            print("\n2️⃣ Autenticando no portal...")
            robot.autenticar()
            print("   ✅ Autenticado com sucesso!")

            print("\n3️⃣ Listando empresas...")
            empresas = robot.listar_empresas()
            print(f"   ✅ Encontradas {len(empresas)} empresa(s):")
            for i, empresa in enumerate(empresas, 1):
                print(f"      {i}. {empresa.razao_social} - {empresa.cnpj_formatado()}")

            if not empresas:
                print("   ⚠️ Nenhuma empresa encontrada")
                return

            print("\n4️⃣ Processando empresas...")
            relatorio = robot.processar_todas_empresas()

            print(f"\n✅ Processamento concluído!")
            print(f"   📊 Estatísticas:")
            print(f"   - Total de guias: {relatorio.total_guias}")
            print(f"   - Pendentes: {relatorio.total_pendentes}")
            print(f"   - Pagas: {relatorio.total_pagas}")
            print(f"   - Vencidas: {relatorio.total_vencidas}")
            print(f"   - Valor pendente: R$ {relatorio.valor_total_pendente:,.2f}")
            print(f"   - Valor pago: R$ {relatorio.valor_total_pago:,.2f}")
            print(f"   - Tempo de execução: {relatorio.tempo_execucao_segundos:.2f}s")

            print("\n5️⃣ Exportando relatórios...")

            # Exportar JSON
            json_path = robot.exportar_relatorio(relatorio, "relatorio_fgts.json", formato="json")
            print(f"   ✅ JSON: {json_path.absolute()}")

            # Exportar Excel
            excel_path = robot.exportar_relatorio(relatorio, "relatorio_fgts.xlsx", formato="excel")
            print(f"   ✅ Excel: {excel_path.absolute()}")

            print("\n🎉 Processo concluído com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        raise


def exemplo_empresa_especifica():
    """Exemplo consultando apenas uma empresa específica"""

    print("🤖 FGTS Digital Robot - Consulta Empresa Específica")
    print("=" * 60)

    certificado_path = "certificado.pfx"
    senha = "sua_senha_aqui"
    cnpj_alvo = "12345678000190"  # Altere para o CNPJ desejado

    try:
        with FGTSRobot(certificado_path, senha, headless=True) as robot:

            print("Autenticando...")
            robot.autenticar()

            print("Listando empresas...")
            robot.listar_empresas()

            print(f"Extraindo guias da empresa {cnpj_alvo}...")
            guias = robot.extrair_guias_empresa(cnpj_alvo)

            print(f"\n✅ {len(guias)} guia(s) encontrada(s):")

            for guia in guias:
                print(f"\n  Guia: {guia.numero_guia}")
                print(f"  Tipo: {guia.tipo.value}")
                print(f"  Status: {guia.status.value}")
                print(f"  Competência: {guia.competencia}")
                print(f"  Vencimento: {guia.data_vencimento.strftime('%d/%m/%Y')}")
                print(f"  Valor: R$ {guia.valor_total:,.2f}")

                if guia.esta_vencida():
                    print(f"  ⚠️ VENCIDA há {guia.calcular_dias_atraso()} dias!")

    except Exception as e:
        print(f"❌ Erro: {e}")
        raise


def exemplo_filtrar_pendentes():
    """Exemplo filtrando apenas guias pendentes"""

    print("🤖 FGTS Digital Robot - Apenas Guias Pendentes")
    print("=" * 60)

    certificado_path = "certificado.pfx"
    senha = "sua_senha_aqui"

    try:
        with FGTSRobot(certificado_path, senha) as robot:

            robot.autenticar()

            # Processar apenas guias pendentes e vencidas
            relatorio = robot.processar_todas_empresas(
                filtrar_status=[StatusGuia.PENDENTE, StatusGuia.VENCIDA]
            )

            print(f"\n📋 Guias Pendentes/Vencidas:")
            print(f"   Total: {relatorio.total_guias}")
            print(f"   Valor: R$ {relatorio.valor_total_geral:,.2f}")

            # Agrupar por empresa
            por_empresa = relatorio.agrupar_por_empresa()

            for cnpj, guias in por_empresa.items():
                empresa = next((e for e in relatorio.empresas if e.cnpj == cnpj), None)
                if empresa:
                    print(f"\n  🏢 {empresa.razao_social}")
                    print(f"     CNPJ: {empresa.cnpj_formatado()}")
                    print(f"     Guias: {len(guias)}")

                    valor_total = sum(g.valor_total for g in guias)
                    print(f"     Valor: R$ {valor_total:,.2f}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        raise


if __name__ == "__main__":
    print("Escolha um exemplo:")
    print("1. Exemplo básico (todas as empresas)")
    print("2. Empresa específica")
    print("3. Filtrar apenas pendentes")

    escolha = input("\nOpção (1-3): ").strip()

    if escolha == "1":
        exemplo_basico()
    elif escolha == "2":
        exemplo_empresa_especifica()
    elif escolha == "3":
        exemplo_filtrar_pendentes()
    else:
        print("Opção inválida")
