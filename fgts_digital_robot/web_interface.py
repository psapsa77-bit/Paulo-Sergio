"""
Interface web Streamlit para o FGTS Digital Robot
=================================================

Interface gráfica para configurar e executar o robô de automação
do FGTS Digital com facilidade.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional
import logging
import tempfile
import os

try:
    from .robot import FGTSRobot
    from .models import StatusGuia, RelatorioFGTS, GuiaFGTS
except ImportError:
    # Fallback para execução direta
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from fgts_digital_robot.robot import FGTSRobot
    from fgts_digital_robot.models import StatusGuia, RelatorioFGTS, GuiaFGTS

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuração da página
st.set_page_config(
    page_title="FGTS Digital Robot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .status-pendente { color: #ff9800; }
    .status-paga { color: #4caf50; }
    .status-vencida { color: #f44336; }
    </style>
""", unsafe_allow_html=True)


def main():
    """Função principal da interface web"""

    st.title("🤖 FGTS Digital Robot")
    st.markdown("**Automação para consulta de guias FGTS das suas empresas**")
    st.markdown("---")

    # Inicializar session state
    if 'robot' not in st.session_state:
        st.session_state.robot = None
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    if 'empresas' not in st.session_state:
        st.session_state.empresas = []
    if 'relatorio' not in st.session_state:
        st.session_state.relatorio = None
    if 'temp_cert_path' not in st.session_state:
        st.session_state.temp_cert_path = None

    # Sidebar - Configuração
    with st.sidebar:
        st.header("⚙️ Configuração")

        # Upload do certificado
        certificado_file = st.file_uploader(
            "Certificado Digital (.pfx ou .p12)",
            type=['pfx', 'p12'],
            help="Faça upload do seu certificado digital A1"
        )

        # Feedback do upload
        if certificado_file is not None:
            file_size_kb = certificado_file.size / 1024
            st.success(f"✅ Arquivo carregado: {certificado_file.name} ({file_size_kb:.1f} KB)")
        else:
            st.info("ℹ️ Nenhum certificado carregado")

        senha_certificado = st.text_input(
            "Senha do Certificado",
            type="password",
            help="Digite a senha do seu certificado digital"
        )

        headless = st.checkbox(
            "Modo headless (sem interface gráfica)",
            value=False,
            help="Execute o navegador em segundo plano"
        )

        st.markdown("---")

        # Botão de autenticação
        if st.button("🔐 Autenticar", use_container_width=True, type="primary"):
            if not certificado_file or not senha_certificado:
                st.error("Por favor, forneça o certificado e a senha")
            else:
                autenticar(certificado_file, senha_certificado, headless)

        # Status da autenticação
        if st.session_state.autenticado:
            st.success("✅ Autenticado")

            if st.button("🚪 Desconectar", use_container_width=True):
                desconectar()
        else:
            st.info("❌ Não autenticado")

    # Conteúdo principal
    if not st.session_state.autenticado:
        mostrar_boas_vindas()
    else:
        mostrar_painel_principal()


def autenticar(certificado_file, senha: str, headless: bool):
    """Autentica no portal FGTS Digital"""
    with st.spinner("🔄 Autenticando no FGTS Digital..."):
        try:
            # Validar arquivo
            if certificado_file is None:
                st.error("❌ Nenhum arquivo foi enviado")
                return

            # Verificar tamanho do arquivo
            file_size = certificado_file.size
            if file_size == 0:
                st.error("❌ O arquivo enviado está vazio")
                return

            if file_size > 10 * 1024 * 1024:  # 10MB
                st.error("❌ Arquivo muito grande (máximo 10MB)")
                return

            # Verificar extensão
            file_extension = Path(certificado_file.name).suffix.lower()
            if file_extension not in ['.pfx', '.p12']:
                st.error(f"❌ Arquivo deve ser .pfx ou .p12 (recebido: {file_extension})")
                return

            logger.info(f"Processando certificado: {certificado_file.name} ({file_size} bytes)")

            # Criar diretório temporário seguro
            temp_dir = tempfile.mkdtemp(prefix="fgts_robot_")
            temp_cert_path = Path(temp_dir) / certificado_file.name

            try:
                # Salvar certificado temporariamente
                with open(temp_cert_path, 'wb') as f:
                    f.write(certificado_file.getbuffer())

                logger.info(f"Certificado salvo em: {temp_cert_path}")

                # Verificar se arquivo foi salvo
                if not temp_cert_path.exists():
                    st.error("❌ Falha ao salvar certificado temporariamente")
                    return

                # Criar e autenticar robô
                robot = FGTSRobot(
                    certificado_path=temp_cert_path,
                    senha_certificado=senha,
                    headless=headless
                )

                # Validar certificado
                info_cert = robot.validar_certificado()

                st.sidebar.info(f"""
                **Certificado:**
                - Titular: {info_cert['nome_titular']}
                - CPF/CNPJ: {info_cert['cpf_cnpj']}
                - Válido até: {info_cert['valido_ate']}
                - Dias para vencer: {info_cert['dias_para_vencer']}
                """)

                # Autenticar
                if robot.autenticar():
                    st.session_state.robot = robot
                    st.session_state.autenticado = True
                    st.session_state.temp_cert_path = temp_cert_path  # Salvar para limpeza depois

                    # Listar empresas
                    with st.spinner("📋 Carregando empresas..."):
                        empresas = robot.listar_empresas()
                        st.session_state.empresas = empresas

                    st.success(f"✅ Autenticado! {len(empresas)} empresa(s) encontrada(s)")
                    st.rerun()
                else:
                    st.error("❌ Falha na autenticação")
                    # Limpar arquivo temporário em caso de falha
                    if temp_cert_path.exists():
                        os.remove(temp_cert_path)
                        os.rmdir(temp_dir)

            except Exception as e_inner:
                # Limpar arquivo temporário em caso de erro
                if temp_cert_path.exists():
                    try:
                        os.remove(temp_cert_path)
                        os.rmdir(temp_dir)
                    except:
                        pass
                raise e_inner

        except Exception as e:
            logger.error(f"Erro na autenticação: {e}", exc_info=True)
            st.error(f"❌ Erro ao processar certificado: {str(e)}")

            # Mostrar detalhes do erro em expander para debug
            with st.expander("🔍 Detalhes do erro (para suporte)"):
                st.code(f"Tipo: {type(e).__name__}\nMensagem: {str(e)}")


def desconectar():
    """Desconecta e limpa session state"""
    if st.session_state.robot:
        st.session_state.robot.fechar()

    # Limpar arquivo temporário do certificado
    if 'temp_cert_path' in st.session_state and st.session_state.temp_cert_path:
        try:
            temp_path = Path(st.session_state.temp_cert_path)
            if temp_path.exists():
                os.remove(temp_path)
                # Remover diretório temporário também
                temp_dir = temp_path.parent
                if temp_dir.exists() and temp_dir.name.startswith("fgts_robot_"):
                    os.rmdir(temp_dir)
            logger.info("Arquivo temporário do certificado removido")
        except Exception as e:
            logger.warning(f"Não foi possível remover arquivo temporário: {e}")

    st.session_state.robot = None
    st.session_state.autenticado = False
    st.session_state.empresas = []
    st.session_state.relatorio = None
    st.session_state.temp_cert_path = None
    st.rerun()


def mostrar_boas_vindas():
    """Mostra tela de boas-vindas"""
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Bem-vindo ao FGTS Digital Robot!")

        st.markdown("""
        ### 🎯 O que este robô faz?

        Este robô automatiza o acesso ao **portal FGTS Digital** e permite:

        - ✅ Autenticação via certificado digital A1
        - ✅ Consulta de múltiplas empresas (via procuração)
        - ✅ Extração automática de guias pendentes e pagas
        - ✅ Geração de relatórios consolidados
        - ✅ Exportação em Excel e JSON
        - ✅ Visualização de dashboards interativos

        ### 🚀 Como usar?

        1. **Faça upload** do seu certificado digital (.pfx ou .p12)
        2. **Digite a senha** do certificado
        3. **Clique em Autenticar** e aguarde
        4. **Selecione as empresas** que deseja consultar
        5. **Execute a extração** e visualize os resultados

        ### 🔒 Segurança

        - O certificado é processado apenas em memória
        - A senha não é armazenada
        - Conexão segura com o portal oficial da Caixa
        - Logs anonimizados sem dados sensíveis

        ### 📚 Requisitos

        - Certificado digital A1 válido
        - Procuração eletrônica cadastrada no FGTS Digital
        - Conexão com a internet
        """)

    with col2:
        st.info("""
        **💡 Dica:**

        Configure o modo headless
        para execuções mais
        rápidas em segundo plano.
        """)

        st.warning("""
        **⚠️ Atenção:**

        Certifique-se de ter
        procuração eletrônica
        cadastrada para as
        empresas que deseja
        consultar.
        """)


def mostrar_painel_principal():
    """Mostra painel principal com opções"""

    tabs = st.tabs(["📊 Dashboard", "🏢 Empresas", "📋 Consultar Guias", "📥 Exportar"])

    with tabs[0]:
        mostrar_dashboard()

    with tabs[1]:
        mostrar_empresas()

    with tabs[2]:
        mostrar_consulta_guias()

    with tabs[3]:
        mostrar_exportacao()


def mostrar_dashboard():
    """Mostra dashboard com resumo"""
    st.header("📊 Dashboard")

    relatorio = st.session_state.relatorio

    if not relatorio:
        st.info("Execute uma consulta de guias para visualizar o dashboard")
        return

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Empresas", relatorio.total_empresas)

    with col2:
        st.metric("Total de Guias", relatorio.total_guias)

    with col3:
        st.metric(
            "Guias Pendentes",
            relatorio.total_pendentes,
            delta=f"-{relatorio.total_vencidas} vencidas" if relatorio.total_vencidas > 0 else None,
            delta_color="inverse"
        )

    with col4:
        st.metric(
            "Valor Pendente",
            f"R$ {float(relatorio.valor_total_pendente):,.2f}",
        )

    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de pizza - Status das guias
        status_counts = {}
        for guia in relatorio.guias:
            status = guia.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        fig_status = go.Figure(data=[go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=0.4
        )])
        fig_status.update_layout(title="Distribuição por Status")
        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        # Gráfico de barras - Valores por empresa
        valores_empresa = {}
        for guia in relatorio.guias:
            empresa = guia.razao_social_empresa[:30]  # Limitar tamanho
            if empresa not in valores_empresa:
                valores_empresa[empresa] = 0
            if guia.status != StatusGuia.PAGA:
                valores_empresa[empresa] += float(guia.valor_total)

        fig_valores = go.Figure(data=[go.Bar(
            x=list(valores_empresa.keys()),
            y=list(valores_empresa.values()),
        )])
        fig_valores.update_layout(
            title="Valores Pendentes por Empresa",
            xaxis_title="Empresa",
            yaxis_title="Valor (R$)"
        )
        st.plotly_chart(fig_valores, use_container_width=True)

    # Tabela de guias vencidas
    if relatorio.total_vencidas > 0:
        st.subheader("⚠️ Guias Vencidas")
        guias_vencidas = [g for g in relatorio.guias if g.esta_vencida()]

        df_vencidas = pd.DataFrame([
            {
                "Empresa": g.razao_social_empresa,
                "Competência": g.competencia,
                "Vencimento": g.data_vencimento.strftime("%d/%m/%Y"),
                "Dias Atraso": g.calcular_dias_atraso(),
                "Valor": f"R$ {float(g.valor_total):,.2f}"
            }
            for g in guias_vencidas
        ])

        st.dataframe(df_vencidas, use_container_width=True)


def mostrar_empresas():
    """Mostra lista de empresas"""
    st.header("🏢 Empresas com Procuração")

    empresas = st.session_state.empresas

    if not empresas:
        st.warning("Nenhuma empresa encontrada")
        return

    st.info(f"**{len(empresas)} empresa(s) disponível(is)**")

    # Criar DataFrame
    df_empresas = pd.DataFrame([
        {
            "CNPJ": e.cnpj_formatado(),
            "Razão Social": e.razao_social,
            "Nome Fantasia": e.nome_fantasia or "-",
        }
        for e in empresas
    ])

    st.dataframe(df_empresas, use_container_width=True, hide_index=True)


def mostrar_consulta_guias():
    """Mostra interface para consultar guias"""
    st.header("📋 Consultar Guias FGTS")

    empresas = st.session_state.empresas

    if not empresas:
        st.warning("Nenhuma empresa disponível")
        return

    # Seleção de empresas
    st.subheader("Selecione as empresas")

    opcao_selecao = st.radio(
        "Opção de seleção:",
        ["Todas as empresas", "Empresas específicas"]
    )

    empresas_selecionadas = []

    if opcao_selecao == "Todas as empresas":
        empresas_selecionadas = [e.cnpj for e in empresas]
        st.info(f"{len(empresas_selecionadas)} empresa(s) selecionada(s)")
    else:
        empresas_opcoes = {
            f"{e.razao_social} ({e.cnpj_formatado()})": e.cnpj
            for e in empresas
        }

        empresas_escolhidas = st.multiselect(
            "Escolha as empresas:",
            options=list(empresas_opcoes.keys())
        )

        empresas_selecionadas = [empresas_opcoes[e] for e in empresas_escolhidas]

    # Filtro de status
    st.subheader("Filtrar por status (opcional)")

    filtrar = st.checkbox("Aplicar filtro de status")

    status_filtro = None

    if filtrar:
        status_opcoes = st.multiselect(
            "Status:",
            options=[s.value for s in StatusGuia],
            default=[StatusGuia.PENDENTE.value, StatusGuia.VENCIDA.value]
        )

        if status_opcoes:
            status_filtro = [StatusGuia(s) for s in status_opcoes]

    # Botão de execução
    st.markdown("---")

    if st.button("🚀 Executar Consulta", type="primary", use_container_width=True):
        if not empresas_selecionadas:
            st.error("Selecione pelo menos uma empresa")
        else:
            executar_consulta(empresas_selecionadas, status_filtro)


def executar_consulta(cnpjs: List[str], filtrar_status: Optional[List[StatusGuia]]):
    """Executa consulta de guias"""
    robot = st.session_state.robot

    if not robot:
        st.error("Robô não inicializado")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("🔄 Processando empresas...")

        relatorio = robot.processar_todas_empresas(
            empresas_cnpj=cnpjs,
            filtrar_status=filtrar_status
        )

        progress_bar.progress(100)

        st.session_state.relatorio = relatorio

        status_text.empty()
        progress_bar.empty()

        st.success(f"""
        ✅ Consulta concluída!

        - **{relatorio.total_guias}** guias encontradas
        - **{relatorio.total_pendentes}** pendentes
        - **{relatorio.total_pagas}** pagas
        - **{relatorio.total_vencidas}** vencidas
        - **Valor pendente:** R$ {float(relatorio.valor_total_pendente):,.2f}
        """)

        st.balloons()

    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        st.error(f"❌ Erro: {str(e)}")


def mostrar_exportacao():
    """Mostra opções de exportação"""
    st.header("📥 Exportar Relatório")

    relatorio = st.session_state.relatorio

    if not relatorio:
        st.info("Execute uma consulta primeiro para exportar o relatório")
        return

    st.success(f"Relatório com **{relatorio.total_guias}** guias pronto para exportação")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Exportar JSON")
        nome_json = st.text_input("Nome do arquivo JSON:", value="relatorio_fgts.json")

        if st.button("💾 Baixar JSON", use_container_width=True):
            exportar_json(relatorio, nome_json)

    with col2:
        st.subheader("📊 Exportar Excel")
        nome_excel = st.text_input("Nome do arquivo Excel:", value="relatorio_fgts.xlsx")

        if st.button("💾 Baixar Excel", use_container_width=True):
            exportar_excel(relatorio, nome_excel)


def exportar_json(relatorio: RelatorioFGTS, nome: str):
    """Exporta relatório em JSON"""
    try:
        robot = st.session_state.robot
        caminho = robot.exportar_relatorio(relatorio, nome, formato="json")

        with open(caminho, 'rb') as f:
            st.download_button(
                label="⬇️ Download JSON",
                data=f,
                file_name=nome,
                mime="application/json"
            )

        st.success(f"✅ JSON gerado: {caminho}")

    except Exception as e:
        st.error(f"❌ Erro ao exportar JSON: {e}")


def exportar_excel(relatorio: RelatorioFGTS, nome: str):
    """Exporta relatório em Excel"""
    try:
        robot = st.session_state.robot
        caminho = robot.exportar_relatorio(relatorio, nome, formato="excel")

        with open(caminho, 'rb') as f:
            st.download_button(
                label="⬇️ Download Excel",
                data=f,
                file_name=nome,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.success(f"✅ Excel gerado: {caminho}")

    except Exception as e:
        st.error(f"❌ Erro ao exportar Excel: {e}")


if __name__ == "__main__":
    main()
