"""
Interface web para o FGTS Digital Robot usando Streamlit.

Execute com:
    streamlit run fgts_digital_robot/web_interface.py --server.port 8502
ou use o launcher:
    python run_fgts_robot.py
"""

from __future__ import annotations

import io
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _importar_streamlit():
    try:
        import streamlit as st
        return st
    except ImportError as exc:
        raise ImportError(
            "Streamlit não está instalado. Execute: pip install streamlit"
        ) from exc


def _formatar_brl(valor) -> str:
    try:
        from decimal import Decimal
        v = float(valor)
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(valor)


# ---------------------------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------------------------

def _inicializar_estado(st):
    defaults = {
        "robot": None,
        "autenticado": False,
        "empresas": [],
        "relatorio": None,
        "erro": None,
        "log_messages": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ---------------------------------------------------------------------------
# Componentes da UI
# ---------------------------------------------------------------------------

def _aba_autenticacao(st):
    st.header("Autenticação com Certificado Digital")

    col1, col2 = st.columns([2, 1])

    with col1:
        cert_file = st.file_uploader(
            "Certificado Digital (.pfx ou .p12)",
            type=["pfx", "p12"],
            help="Selecione seu certificado digital A1",
        )
        senha = st.text_input(
            "Senha do certificado",
            type="password",
            help="Senha do arquivo .pfx/.p12",
        )
        headless = st.checkbox(
            "Modo headless (sem janela do navegador)",
            value=False,
            help="Marque para executar sem abrir o navegador visualmente",
        )

    with col2:
        st.info(
            "**Requisitos:**\n"
            "- Certificado A1 (.pfx ou .p12)\n"
            "- Procuração eletrônica ativa no FGTS Digital\n"
            "- Conexão com a internet"
        )

    if st.button("Autenticar", type="primary", disabled=not cert_file or not senha):
        _executar_autenticacao(st, cert_file, senha, headless)

    if st.session_state.autenticado:
        st.success("Autenticado com sucesso! Navegue pelas abas acima.")
        if st.session_state.robot:
            cert = st.session_state.robot.autenticador.certificado
            if cert:
                with st.expander("Informações do certificado"):
                    st.write(f"**Titular:** {cert.nome_titular or 'N/A'}")
                    st.write(f"**CPF/CNPJ:** {cert.cpf_cnpj or 'N/A'}")
                    st.write(f"**Válido até:** {cert.valido_ate or 'N/A'}")
                    if cert.dias_para_vencer is not None:
                        if cert.dias_para_vencer < 30:
                            st.warning(f"Certificado vence em {cert.dias_para_vencer} dias!")
                        else:
                            st.write(f"**Dias para vencer:** {cert.dias_para_vencer}")


def _executar_autenticacao(st, cert_file, senha: str, headless: bool):
    from .robot import FGTSRobot

    # Encerra sessão anterior se existir
    if st.session_state.robot:
        try:
            st.session_state.robot.fechar()
        except Exception:
            pass
        st.session_state.robot = None
        st.session_state.autenticado = False

    # Salvar certificado em temp file
    with tempfile.NamedTemporaryFile(suffix=f".{cert_file.name.split('.')[-1]}", delete=False) as tmp:
        tmp.write(cert_file.read())
        tmp_path = tmp.name

    with st.spinner("Autenticando… Aguarde o navegador carregar o portal."):
        try:
            robot = FGTSRobot(tmp_path, senha, headless=headless, log_level="INFO")
            robot.autenticar()
            st.session_state.robot = robot
            st.session_state.autenticado = True
            st.session_state.erro = None
        except Exception as exc:
            st.session_state.erro = str(exc)
            st.error(f"Erro na autenticação: {exc}")
        finally:
            # Remove temp file
            try:
                Path(tmp_path).unlink()
            except Exception:
                pass

    if st.session_state.autenticado:
        st.rerun()


def _aba_empresas(st):
    st.header("Empresas com Procuração")

    if not st.session_state.autenticado:
        st.warning("Faça a autenticação primeiro na aba 'Autenticação'.")
        return

    robot = st.session_state.robot

    if st.button("Listar Empresas", type="primary"):
        with st.spinner("Buscando empresas…"):
            try:
                empresas = robot.listar_empresas()
                st.session_state.empresas = empresas
            except Exception as exc:
                st.error(f"Erro ao listar empresas: {exc}")

    empresas = st.session_state.empresas
    if empresas:
        st.success(f"Encontradas {len(empresas)} empresa(s) com procuração.")

        dados = [
            {
                "CNPJ": e.cnpj_formatado,
                "Razão Social": e.razao_social,
                "Nome Fantasia": e.nome_fantasia,
                "Procuração": "Sim" if e.tem_procuracao else "Não",
            }
            for e in empresas
        ]
        st.dataframe(dados, use_container_width=True)
    elif st.session_state.autenticado:
        st.info("Clique em 'Listar Empresas' para carregar a lista.")


def _aba_consultar_guias(st):
    st.header("Consultar Guias FGTS")

    if not st.session_state.autenticado:
        st.warning("Faça a autenticação primeiro na aba 'Autenticação'.")
        return

    robot = st.session_state.robot
    empresas = st.session_state.empresas

    if not empresas:
        st.info("Primeiro vá para a aba 'Empresas' e liste as empresas disponíveis.")
        if st.button("Carregar empresas agora"):
            with st.spinner("Buscando empresas…"):
                try:
                    st.session_state.empresas = robot.listar_empresas()
                    st.rerun()
                except Exception as exc:
                    st.error(f"Erro: {exc}")
        return

    # Seleção de empresas
    st.subheader("Seleção de Empresas")
    todas = st.checkbox("Consultar todas as empresas", value=True)

    cnpjs_selecionados = []
    if not todas:
        opcoes = {f"{e.cnpj_formatado} - {e.razao_social}": e.cnpj for e in empresas}
        selecionados = st.multiselect("Selecione as empresas", list(opcoes.keys()))
        cnpjs_selecionados = [opcoes[s] for s in selecionados]

    # Filtros de status
    st.subheader("Filtros")
    col1, col2 = st.columns(2)

    from .models import StatusGuia
    status_opcoes = {
        "Pendentes": StatusGuia.PENDENTE,
        "Pagas": StatusGuia.PAGA,
        "Vencidas": StatusGuia.VENCIDA,
        "Parceladas": StatusGuia.PARCELADA,
    }

    with col1:
        filtrar = st.checkbox("Filtrar por status", value=False)
    with col2:
        if filtrar:
            status_sel = st.multiselect(
                "Status desejados",
                list(status_opcoes.keys()),
                default=["Pendentes", "Vencidas"],
            )
            filtro_status = [status_opcoes[s] for s in status_sel] if status_sel else None
        else:
            filtro_status = None

    # Executar
    pode_executar = todas or bool(cnpjs_selecionados)
    if st.button("Executar Consulta", type="primary", disabled=not pode_executar):
        with st.spinner("Consultando guias… Isso pode levar alguns minutos."):
            try:
                if todas:
                    relatorio = robot.processar_todas_empresas(filtrar_status=filtro_status)
                else:
                    relatorio = robot.processar_empresas(cnpjs_selecionados, filtrar_status=filtro_status)
                st.session_state.relatorio = relatorio
                st.success(
                    f"Consulta concluída! {relatorio.total_guias} guias encontradas."
                )
            except Exception as exc:
                st.error(f"Erro durante consulta: {exc}")


def _aba_dashboard(st):
    st.header("Dashboard")

    relatorio = st.session_state.relatorio
    if relatorio is None:
        st.info("Execute uma consulta na aba 'Consultar Guias' para ver o dashboard.")
        return

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Guias", relatorio.total_guias)
    with col2:
        st.metric("Pendentes", relatorio.total_pendentes)
    with col3:
        st.metric("Pagas", relatorio.total_pagas)
    with col4:
        st.metric("Vencidas", relatorio.total_vencidas)

    col5, col6 = st.columns(2)
    with col5:
        st.metric("Valor Pendente", _formatar_brl(relatorio.valor_total_pendente))
    with col6:
        st.metric("Valor Pago", _formatar_brl(relatorio.valor_total_pago))

    # Gráfico de pizza por status
    if relatorio.total_guias > 0:
        st.subheader("Distribuição por Status")
        try:
            import plotly.express as px
            from .models import StatusGuia

            contagem = {
                "Pendente": relatorio.total_pendentes,
                "Paga": relatorio.total_pagas,
                "Vencida": relatorio.total_vencidas,
                "Parcelada": relatorio.total_parceladas,
            }
            contagem = {k: v for k, v in contagem.items() if v > 0}

            if contagem:
                fig = px.pie(
                    values=list(contagem.values()),
                    names=list(contagem.keys()),
                    title="Guias por Status",
                )
                st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.info("Instale plotly para ver gráficos: pip install plotly")

    # Tabela de guias
    st.subheader("Tabela de Guias")

    if relatorio.guias:
        dados = [
            {
                "Número": g.numero_guia,
                "CNPJ": g.cnpj_empresa,
                "Tipo": g.tipo.value,
                "Status": g.status.value,
                "Competência": g.competencia,
                "Vencimento": g.data_vencimento.strftime("%d/%m/%Y") if g.data_vencimento else "",
                "Valor Total": float(g.valor_total),
                "Dias Atraso": g.dias_atraso or 0,
            }
            for g in relatorio.guias
        ]
        st.dataframe(dados, use_container_width=True)
    else:
        st.info("Nenhuma guia encontrada com os filtros aplicados.")


def _aba_exportar(st):
    st.header("Exportar Relatório")

    relatorio = st.session_state.relatorio
    if relatorio is None:
        st.info("Execute uma consulta na aba 'Consultar Guias' para exportar.")
        return

    st.write(f"Relatório com **{relatorio.total_guias} guias** de **{len(relatorio.empresas)} empresa(s)**.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Exportar JSON")
        if st.button("Gerar JSON"):
            dados_json = json.dumps(relatorio.to_dict(), ensure_ascii=False, indent=2)
            st.download_button(
                label="Baixar JSON",
                data=dados_json.encode("utf-8"),
                file_name="relatorio_fgts.json",
                mime="application/json",
            )

    with col2:
        st.subheader("Exportar Excel")
        if st.button("Gerar Excel"):
            try:
                import openpyxl  # noqa: F401
                # Gera em memória usando temp file
                with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                robot = st.session_state.robot
                if robot:
                    robot.exportar_relatorio(relatorio, tmp_path, formato="excel")
                    with open(tmp_path, "rb") as f:
                        excel_bytes = f.read()
                    tmp_path.unlink(missing_ok=True)

                    st.download_button(
                        label="Baixar Excel",
                        data=excel_bytes,
                        file_name="relatorio_fgts.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            except ImportError:
                st.error("openpyxl não instalado. Execute: pip install openpyxl")


# ---------------------------------------------------------------------------
# Entrada principal da interface
# ---------------------------------------------------------------------------

def run_interface():
    """Executa a interface Streamlit."""
    st = _importar_streamlit()
    st.set_page_config(
        page_title="FGTS Digital Robot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    _inicializar_estado(st)

    st.title("FGTS Digital Robot")
    st.caption("Automação para consulta de guias FGTS com certificado digital A1")

    # Tabs principais
    tab_auth, tab_emp, tab_guias, tab_dash, tab_export = st.tabs([
        "Autenticação",
        "Empresas",
        "Consultar Guias",
        "Dashboard",
        "Exportar",
    ])

    with tab_auth:
        _aba_autenticacao(st)
    with tab_emp:
        _aba_empresas(st)
    with tab_guias:
        _aba_consultar_guias(st)
    with tab_dash:
        _aba_dashboard(st)
    with tab_export:
        _aba_exportar(st)

    # Sidebar com status
    with st.sidebar:
        st.header("Status")
        if st.session_state.autenticado:
            st.success("Autenticado")
        else:
            st.error("Não autenticado")

        if st.session_state.empresas:
            st.info(f"{len(st.session_state.empresas)} empresa(s) carregada(s)")

        if st.session_state.relatorio:
            r = st.session_state.relatorio
            st.info(f"{r.total_guias} guia(s) consultada(s)")

        if st.session_state.autenticado:
            st.divider()
            if st.button("Desconectar"):
                if st.session_state.robot:
                    try:
                        st.session_state.robot.fechar()
                    except Exception:
                        pass
                for k in ("robot", "autenticado", "empresas", "relatorio"):
                    st.session_state[k] = None if k in ("robot", "relatorio") else (False if k == "autenticado" else [])
                st.rerun()


if __name__ == "__main__":
    run_interface()
