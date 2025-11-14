"""
Interface Web do Robô FGTS Digital - Streamlit

Interface gráfica para facilitar o uso do robô de automação FGTS.
"""
import streamlit as st
import sys
from pathlib import Path
import asyncio
from datetime import datetime
import pandas as pd
import time
import io

# Adicionar diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from robo_fgts import RoboFGTS
import config


# Configuração da página
st.set_page_config(
    page_title="Robô FGTS Digital",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #1f4788 0%, #4a90e2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        color: #0c5460;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f4788;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #4a90e2;
    }
    </style>
""", unsafe_allow_html=True)


def inicializar_sessao():
    """Inicializa variáveis de sessão"""
    if 'processamento_iniciado' not in st.session_state:
        st.session_state.processamento_iniciado = False
    if 'resultados' not in st.session_state:
        st.session_state.resultados = None
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'competencias_data' not in st.session_state:
        st.session_state.competencias_data = None


def validar_cnpj(cnpj: str) -> bool:
    """Valida formato básico do CNPJ"""
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
    return len(cnpj_limpo) == 14 and cnpj_limpo.isdigit()


def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ para exibição"""
    cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
    if len(cnpj_limpo) == 14:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    return cnpj


def adicionar_log(mensagem: str):
    """Adiciona mensagem ao log da sessão"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {mensagem}")


def verificar_configuracao():
    """Verifica se a configuração está completa"""
    problemas = []

    # Verificar certificado
    cert_path = Path(config.CERT_PATH)
    if not cert_path.exists():
        problemas.append(f"❌ Certificado não encontrado: {config.CERT_PATH}")
    else:
        problemas.append(f"✅ Certificado encontrado: {cert_path.name}")

    # Verificar senha
    if not config.CERT_PASSWORD:
        problemas.append("⚠️ Senha do certificado não configurada no .env")
    else:
        problemas.append("✅ Senha do certificado configurada")

    # Verificar diretórios
    for dir_name, dir_path in [
        ("Certificados", config.CERT_DIR),
        ("Resultados", config.RESULTS_DIR),
        ("Logs", config.LOGS_DIR)
    ]:
        if dir_path.exists():
            problemas.append(f"✅ Diretório {dir_name}: OK")
        else:
            problemas.append(f"❌ Diretório {dir_name} não existe")

    return problemas


def main():
    """Função principal da interface web"""

    inicializar_sessao()

    # Header
    st.markdown('<h1 class="main-header">🤖 Robô FGTS Digital</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Automação de Consulta de Guias FGTS com Certificado Digital</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")

        # Upload de certificado
        st.subheader("📜 Certificado Digital")
        cert_file = st.file_uploader(
            "Fazer upload do certificado (.pfx)",
            type=['pfx'],
            help="Selecione seu certificado digital A1 no formato .pfx"
        )

        if cert_file:
            # Salvar certificado temporariamente
            cert_path = config.CERT_DIR / cert_file.name
            with open(cert_path, 'wb') as f:
                f.write(cert_file.read())
            st.success(f"✅ Certificado carregado: {cert_file.name}")
            cert_path_str = str(cert_path)
        else:
            cert_path_str = config.CERT_PATH

        cert_password = st.text_input(
            "Senha do certificado",
            type="password",
            value=config.CERT_PASSWORD,
            help="Digite a senha do seu certificado digital"
        )

        st.divider()

        # Configurações avançadas
        with st.expander("🔧 Configurações Avançadas"):
            headless = st.checkbox(
                "Modo Headless (sem interface gráfica)",
                value=config.HEADLESS,
                help="Execute o navegador em modo invisível"
            )

            timeout = st.number_input(
                "Timeout (ms)",
                min_value=10000,
                max_value=120000,
                value=config.BROWSER_TIMEOUT,
                step=5000,
                help="Tempo máximo de espera por elementos"
            )

            log_level = st.selectbox(
                "Nível de Log",
                options=["DEBUG", "INFO", "WARNING", "ERROR"],
                index=1,
                help="Detalhamento dos logs"
            )

        st.divider()

        # Status da configuração
        st.subheader("📋 Status do Sistema")
        status = verificar_configuracao()
        for item in status:
            if "✅" in item:
                st.success(item)
            elif "⚠️" in item:
                st.warning(item)
            elif "❌" in item:
                st.error(item)

        st.divider()

        # Sobre
        with st.expander("ℹ️ Sobre"):
            st.markdown(f"""
            **Robô FGTS Digital v{1.0}**

            Robô de automação para consulta de guias FGTS no portal FGTS Digital.

            **Funcionalidades:**
            - Autenticação com certificado A1
            - Consulta de múltiplas empresas
            - Extração de guias (pagas e pendentes)
            - Exportação para Excel

            **Desenvolvido por:** Paulo Sergio
            """)

    # Conteúdo principal
    tab1, tab2, tab3 = st.tabs(["🚀 Processar", "📊 Resultados", "📝 Logs"])

    with tab1:
        st.header("Processamento de Guias FGTS")

        # Método de entrada de CNPJs
        metodo = st.radio(
            "Como você deseja fornecer os CNPJs?",
            options=["Digitação Manual", "Upload de Arquivo", "Área de Texto"],
            horizontal=True
        )

        cnpjs_lista = []

        if metodo == "Digitação Manual":
            st.subheader("Digite os CNPJs")

            col1, col2 = st.columns([3, 1])

            with col1:
                # Input dinâmico de CNPJs
                num_cnpjs = st.number_input("Quantos CNPJs deseja processar?", min_value=1, max_value=50, value=1)

            for i in range(num_cnpjs):
                cnpj = st.text_input(
                    f"CNPJ {i+1}",
                    key=f"cnpj_{i}",
                    placeholder="00.000.000/0000-00",
                    help="Digite o CNPJ no formato: 00.000.000/0000-00"
                )
                if cnpj and validar_cnpj(cnpj):
                    cnpjs_lista.append(cnpj.replace(".", "").replace("/", "").replace("-", ""))

        elif metodo == "Upload de Arquivo":
            st.subheader("Upload de Arquivo")
            st.info("📄 Faça upload de um arquivo .txt com um CNPJ por linha")

            arquivo = st.file_uploader("Selecione o arquivo", type=['txt'])
            if arquivo:
                conteudo = arquivo.read().decode('utf-8')
                linhas = conteudo.split('\n')
                for linha in linhas:
                    cnpj = linha.strip()
                    if cnpj and not cnpj.startswith('#') and validar_cnpj(cnpj):
                        cnpjs_lista.append(cnpj.replace(".", "").replace("/", "").replace("-", ""))

                st.success(f"✅ {len(cnpjs_lista)} CNPJs válidos encontrados no arquivo")

        else:  # Área de Texto
            st.subheader("Cole os CNPJs")
            st.info("📝 Cole os CNPJs, um por linha")

            texto = st.text_area(
                "CNPJs",
                height=200,
                placeholder="00.000.000/0000-00\n11.111.111/1111-11\n22.222.222/2222-22"
            )

            if texto:
                linhas = texto.split('\n')
                for linha in linhas:
                    cnpj = linha.strip()
                    if cnpj and not cnpj.startswith('#') and validar_cnpj(cnpj):
                        cnpjs_lista.append(cnpj.replace(".", "").replace("/", "").replace("-", ""))

                if cnpjs_lista:
                    st.success(f"✅ {len(cnpjs_lista)} CNPJs válidos identificados")

        # Exibir CNPJs que serão processados
        if cnpjs_lista:
            st.divider()
            st.subheader("CNPJs que serão processados:")

            col1, col2, col3 = st.columns(3)
            for i, cnpj in enumerate(cnpjs_lista):
                with [col1, col2, col3][i % 3]:
                    st.code(formatar_cnpj(cnpj))

            st.divider()

            # Botão de processar
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                processar = st.button(
                    f"🚀 PROCESSAR {len(cnpjs_lista)} EMPRESA(S)",
                    type="primary",
                    use_container_width=True
                )

            if processar:
                if not cert_password:
                    st.error("❌ Por favor, configure a senha do certificado na barra lateral")
                else:
                    with st.spinner("🔄 Processando... Isso pode levar alguns minutos..."):
                        try:
                            adicionar_log("Iniciando robô FGTS...")
                            adicionar_log(f"Processando {len(cnpjs_lista)} empresa(s)")

                            # Criar instância do robô
                            robo = RoboFGTS(
                                cert_path=cert_path_str,
                                cert_password=cert_password,
                                headless=headless
                            )

                            # Processar
                            adicionar_log("Robô inicializado, executando automação...")

                            # Progress bar
                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            for i, cnpj in enumerate(cnpjs_lista):
                                status_text.text(f"Processando {i+1}/{len(cnpjs_lista)}: {formatar_cnpj(cnpj)}")
                                progress_bar.progress((i + 1) / len(cnpjs_lista))
                                time.sleep(0.5)  # Simular processamento

                            sucesso = robo.processar_clientes(cnpjs_lista)

                            if sucesso:
                                adicionar_log("✅ Processamento concluído com sucesso!")
                                st.success("✅ Processamento concluído com sucesso!")
                                st.balloons()

                                # Armazenar dados de competências na sessão
                                if robo.dados_resultado:
                                    st.session_state.competencias_data = robo.dados_resultado
                                    adicionar_log(f"✅ {len(robo.competencias_encontradas)} competências encontradas")

                                # Buscar arquivo de resultado mais recente
                                arquivos_resultado = sorted(
                                    config.RESULTS_DIR.glob("*.xlsx"),
                                    key=lambda x: x.stat().st_mtime,
                                    reverse=True
                                )

                                if arquivos_resultado:
                                    st.session_state.resultados = arquivos_resultado[0]
                                    adicionar_log(f"Arquivo gerado: {arquivos_resultado[0].name}")
                            else:
                                adicionar_log("❌ Processamento falhou")
                                st.error("❌ Processamento falhou. Verifique os logs.")

                        except Exception as e:
                            adicionar_log(f"❌ Erro: {str(e)}")
                            st.error(f"❌ Erro durante processamento: {str(e)}")
        else:
            st.info("👆 Digite os CNPJs acima para começar")

    with tab2:
        st.header("Resultados")

        # Exibir competências encontradas (resultado principal)
        if st.session_state.competencias_data:
            st.success("🎉 Competências em Aberto Encontradas!")
            st.divider()

            dados = st.session_state.competencias_data

            # Métricas principais
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "📅 Total de Competências",
                    dados['total_competencias'],
                    help="Número de competências em aberto encontradas"
                )

            with col2:
                st.metric(
                    "🏢 CNPJs Processados",
                    len(dados['cnpjs_processados']),
                    help="Número de empresas processadas"
                )

            with col3:
                st.metric(
                    "🕐 Data/Hora",
                    dados['timestamp'].split()[1],
                    help="Horário do processamento"
                )

            st.divider()

            # Lista de CNPJs processados
            st.subheader("🏢 Empresas Processadas")
            for cnpj in dados['cnpjs_processados']:
                st.code(formatar_cnpj(cnpj))

            st.divider()

            # Lista de competências
            st.subheader("📅 Competências em Aberto")

            # Exibir em colunas para melhor visualização
            num_cols = 4
            cols = st.columns(num_cols)

            for i, comp in enumerate(dados['competencias_em_aberto']):
                with cols[i % num_cols]:
                    st.markdown(f"""
                    <div class="info-box" style="text-align: center; font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
                        📆 {comp}
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            # Download dos dados
            st.subheader("💾 Exportar Resultados")

            col1, col2 = st.columns(2)

            with col1:
                # Download JSON
                import json
                json_str = json.dumps(dados, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 Baixar JSON",
                    data=json_str,
                    file_name=f"competencias_{dados['timestamp'].replace(' ', '_').replace(':', '-')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col2:
                # Download Excel (se existir)
                arquivos_excel = sorted(
                    config.LOGS_DIR.glob("competencias_em_aberto_*.xlsx"),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                if arquivos_excel:
                    with open(arquivos_excel[0], 'rb') as f:
                        st.download_button(
                            label="📥 Baixar Excel",
                            data=f.read(),
                            file_name=arquivos_excel[0].name,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

            st.divider()

        # Arquivos Excel antigos (se existirem)
        if st.session_state.resultados:
            st.success(f"📊 Arquivo gerado: {st.session_state.resultados.name}")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Arquivo", st.session_state.resultados.name)

            with col2:
                tamanho = st.session_state.resultados.stat().st_size / 1024
                st.metric("Tamanho", f"{tamanho:.2f} KB")

            # Preview do Excel
            try:
                df = pd.read_excel(st.session_state.resultados, sheet_name=0)
                st.subheader("Preview dos Dados")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.warning(f"Não foi possível carregar preview: {str(e)}")

            # Download
            st.divider()

            with open(st.session_state.resultados, 'rb') as f:
                st.download_button(
                    label="📥 BAIXAR ARQUIVO EXCEL",
                    data=f.read(),
                    file_name=st.session_state.resultados.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        # Mensagem quando não há resultados
        if not st.session_state.competencias_data and not st.session_state.resultados:
            st.info("📭 Nenhum resultado disponível ainda. Execute um processamento na aba '🚀 Processar' para visualizar as competências em aberto.")

            # Listar resultados anteriores
            arquivos_anteriores = sorted(
                config.RESULTS_DIR.glob("*.xlsx"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )

            if arquivos_anteriores:
                st.subheader("📁 Resultados Anteriores")

                for arquivo in arquivos_anteriores[:10]:  # Mostrar últimos 10
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.text(arquivo.name)

                    with col2:
                        data_mod = datetime.fromtimestamp(arquivo.stat().st_mtime)
                        st.text(data_mod.strftime("%d/%m/%Y %H:%M"))

                    with col3:
                        with open(arquivo, 'rb') as f:
                            st.download_button(
                                "⬇️",
                                data=f.read(),
                                file_name=arquivo.name,
                                key=f"download_{arquivo.name}"
                            )

    with tab3:
        st.header("Logs do Sistema")

        if st.session_state.logs:
            st.text_area(
                "Logs de Execução",
                value="\n".join(st.session_state.logs),
                height=400,
                disabled=True
            )

            if st.button("🗑️ Limpar Logs"):
                st.session_state.logs = []
                st.rerun()
        else:
            st.info("📝 Nenhum log disponível ainda")

        # Logs de arquivo
        st.divider()
        st.subheader("📂 Arquivos de Log")

        arquivos_log = sorted(
            config.LOGS_DIR.glob("*.log"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if arquivos_log:
            log_selecionado = st.selectbox(
                "Selecione um arquivo de log",
                options=[f.name for f in arquivos_log[:10]]
            )

            if log_selecionado:
                log_path = config.LOGS_DIR / log_selecionado
                with open(log_path, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    st.text_area(
                        "Conteúdo do Log",
                        value=conteudo,
                        height=400,
                        disabled=True
                    )
        else:
            st.info("Nenhum arquivo de log encontrado")


if __name__ == "__main__":
    main()
