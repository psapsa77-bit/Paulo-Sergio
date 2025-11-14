"""
Interface Web Streamlit para o Robô DET
Autor: Paulo Sergio
Versão: 1.0.0
"""

import streamlit as st
import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys
import platform

# Fix para Python 3.13+ no Windows
if sys.platform == 'win32' and sys.version_info >= (3, 8):
    try:
        # Para Python 3.13+, usar WindowsSelectorEventLoopPolicy
        if sys.version_info >= (3, 13):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # Para Python 3.8-3.12, usar WindowsProactorEventLoopPolicy se disponível
        elif hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass  # Ignorar erros de configuração do event loop

# Adicionar diretório pai ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from det_robot.robot_det import RobotDET
from det_robot import config


# Configuração da página
st.set_page_config(
    page_title="Robô DET - Verificador de Mensagens",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def adicionar_log(mensagem: str):
    """Adiciona mensagem ao log da sessão"""
    if "logs" not in st.session_state:
        st.session_state.logs = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {mensagem}")


def limpar_logs():
    """Limpa os logs da sessão"""
    st.session_state.logs = []


def carregar_empresas_json():
    """Carrega lista de empresas do arquivo JSON"""
    if config.DADOS_EMPRESAS.exists():
        try:
            with open(config.DADOS_EMPRESAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar empresas: {str(e)}")
            return []
    return []


def salvar_empresas_json(empresas: list):
    """Salva lista de empresas em arquivo JSON"""
    try:
        with open(config.DADOS_EMPRESAS, 'w', encoding='utf-8') as f:
            json.dump(empresas, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar empresas: {str(e)}")
        return False


def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ com pontuação"""
    cnpj = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj


def processar_texto_cnpjs(texto: str) -> list:
    """
    Processa texto com CNPJs e retorna lista de dicionários

    Formatos aceitos:
    - CNPJ (um por linha)
    - CNPJ,Nome da Empresa
    - CNPJ;Nome da Empresa

    Args:
        texto: Texto com CNPJs

    Returns:
        Lista de dicionários com 'cnpj' e 'nome'
    """
    empresas = []
    linhas = texto.strip().split('\n')

    for idx, linha in enumerate(linhas, 1):
        linha = linha.strip()
        if not linha or linha.startswith('#'):  # Ignora linhas vazias e comentários
            continue

        # Tentar separar CNPJ e nome
        partes = None
        if ',' in linha:
            partes = linha.split(',', 1)
        elif ';' in linha:
            partes = linha.split(';', 1)
        elif '\t' in linha:
            partes = linha.split('\t', 1)

        if partes and len(partes) >= 2:
            cnpj_raw = partes[0].strip()
            nome = partes[1].strip()
        else:
            cnpj_raw = linha.strip()
            nome = f"Empresa {idx}"

        # Limpar CNPJ (remover tudo que não é número)
        cnpj = ''.join(filter(str.isdigit, cnpj_raw))

        # Validar CNPJ (14 dígitos)
        if len(cnpj) == 14:
            empresas.append({
                "cnpj": cnpj,
                "nome": nome
            })

    return empresas


def processar_arquivo_upload(arquivo) -> list:
    """
    Processa arquivo TXT ou JSON com CNPJs

    Args:
        arquivo: Arquivo uploaded pelo Streamlit

    Returns:
        Lista de dicionários com 'cnpj' e 'nome'
    """
    try:
        conteudo = arquivo.read().decode('utf-8')

        # Se for JSON
        if arquivo.name.endswith('.json'):
            empresas = json.loads(conteudo)
            if isinstance(empresas, list):
                return empresas

        # Se for TXT ou outro
        return processar_texto_cnpjs(conteudo)

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {str(e)}")
        return []


def main():
    # Inicializar session_state
    if "mensagens_data" not in st.session_state:
        st.session_state.mensagens_data = None
    if "resultados" not in st.session_state:
        st.session_state.resultados = None
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "lista_cnpj_texto" not in st.session_state:
        st.session_state.lista_cnpj_texto = ""
    if "empresas_processadas" not in st.session_state:
        st.session_state.empresas_processadas = []

    # Título principal
    st.title("🤖 Robô DET - Verificador de Mensagens")
    st.markdown("**Automação para verificar mensagens não lidas no Portal DET**")
    st.divider()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")

        st.subheader("🔐 Portal DET")
        st.info(f"🌐 {config.DET_URL}")

        st.divider()

        st.subheader("📁 Diretórios")
        st.text(f"Logs: {config.LOGS_DIR}")
        st.text(f"Resultados: {config.RESULTS_DIR}")

        st.divider()

        st.subheader("🛠️ Opções")
        headless = st.checkbox("Modo Headless", value=False, help="Executar navegador em segundo plano")

        st.divider()

        if st.button("🗑️ Limpar Logs", use_container_width=True):
            limpar_logs()
            st.rerun()

    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["🚀 Processar", "📊 Resultados", "📝 Logs"])

    # TAB 1: Processar
    with tab1:
        st.header("🚀 Processar Verificação de Mensagens")

        # Opções de entrada
        st.subheader("📋 Informar Empresas")

        metodo_input = st.radio(
            "Escolha o método de entrada:",
            ["✍️ Digitar CNPJs", "📁 Upload de Arquivo"],
            horizontal=True
        )

        st.divider()

        empresas_para_processar = []

        if metodo_input == "✍️ Digitar CNPJs":
            st.markdown("""
            **Formatos aceitos:**
            - `CNPJ` (um por linha) - Ex: `12345678000199`
            - `CNPJ,Nome da Empresa` - Ex: `12345678000199,Minha Empresa Ltda`
            - `CNPJ;Nome da Empresa` - Ex: `12345678000199;Minha Empresa Ltda`

            💡 **Dica:** Você pode usar CNPJ com ou sem formatação (pontos e traços)
            """)

            lista_cnpj_texto = st.text_area(
                "Digite os CNPJs (um por linha):",
                value=st.session_state.lista_cnpj_texto,
                height=200,
                placeholder="12345678000199,Empresa Exemplo 1\n98765432000188,Empresa Exemplo 2\n11223344000155",
                help="Digite um CNPJ por linha. Opcionalmente, adicione vírgula e o nome da empresa"
            )

            if lista_cnpj_texto.strip():
                empresas_para_processar = processar_texto_cnpjs(lista_cnpj_texto)
                st.session_state.lista_cnpj_texto = lista_cnpj_texto

                if empresas_para_processar:
                    st.success(f"✅ {len(empresas_para_processar)} empresa(s) identificada(s)")

                    # Preview das empresas
                    with st.expander("👁️ Visualizar empresas identificadas"):
                        for emp in empresas_para_processar:
                            st.text(f"• {emp['nome']} - {formatar_cnpj(emp['cnpj'])}")
                else:
                    st.warning("⚠️ Nenhum CNPJ válido encontrado")

        else:  # Upload de arquivo
            st.markdown("""
            **Formatos aceitos:**
            - **TXT**: Um CNPJ por linha (com ou sem nome)
            - **JSON**: Array de objetos `[{"cnpj": "...", "nome": "..."}]`
            """)

            uploaded_file = st.file_uploader(
                "Selecione o arquivo com os CNPJs:",
                type=['txt', 'json'],
                help="Arquivo TXT ou JSON com lista de CNPJs"
            )

            if uploaded_file:
                empresas_para_processar = processar_arquivo_upload(uploaded_file)

                if empresas_para_processar:
                    st.success(f"✅ {len(empresas_para_processar)} empresa(s) carregada(s) do arquivo")

                    # Preview das empresas
                    with st.expander("👁️ Visualizar empresas do arquivo"):
                        for emp in empresas_para_processar:
                            st.text(f"• {emp['nome']} - {formatar_cnpj(emp['cnpj'])}")
                else:
                    st.warning("⚠️ Nenhum CNPJ válido encontrado no arquivo")

            # Exemplo de arquivo para download
            st.markdown("---")
            st.markdown("**📥 Baixar arquivo de exemplo:**")

            col1, col2 = st.columns(2)

            with col1:
                exemplo_txt = """# Exemplo de arquivo TXT para Robô DET
# Formato: CNPJ,Nome da Empresa (um por linha)

12345678000199,Empresa Exemplo 1 Ltda
98765432000188,Empresa Exemplo 2 S/A
11223344000155,Empresa Exemplo 3

# Você também pode usar apenas o CNPJ:
44556677000199
"""
                st.download_button(
                    label="📄 Exemplo TXT",
                    data=exemplo_txt,
                    file_name="empresas_exemplo.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col2:
                exemplo_json = json.dumps([
                    {"cnpj": "12345678000199", "nome": "Empresa Exemplo 1 Ltda"},
                    {"cnpj": "98765432000188", "nome": "Empresa Exemplo 2 S/A"},
                    {"cnpj": "11223344000155", "nome": "Empresa Exemplo 3"}
                ], ensure_ascii=False, indent=2)

                st.download_button(
                    label="📄 Exemplo JSON",
                    data=exemplo_json,
                    file_name="empresas_exemplo.json",
                    mime="application/json",
                    use_container_width=True
                )

        st.divider()

        # Botão de processar
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if empresas_para_processar:
                if st.button("🚀 INICIAR VERIFICAÇÃO", type="primary", use_container_width=True, key="btn_processar"):
                    limpar_logs()
                    adicionar_log("🤖 Iniciando Robô DET...")
                    adicionar_log(f"📋 {len(empresas_para_processar)} empresa(s) serão processadas")

                    # Salvar empresas processadas
                    st.session_state.empresas_processadas = empresas_para_processar

                    with st.spinner("🔄 Processando... Isso pode levar alguns minutos..."):
                        try:
                            robo = RobotDET(headless=headless)

                            # Executar processamento
                            sucesso = asyncio.run(robo.processar_empresas(empresas_para_processar))

                            if sucesso:
                                adicionar_log("✅ Processamento concluído com sucesso!")
                                st.success("✅ Verificação concluída!")

                                # Salvar dados na sessão
                                st.session_state.mensagens_data = robo.dados_resultado
                                adicionar_log(f"✅ {len(robo.mensagens_encontradas)} mensagem(ns) não lida(s) encontrada(s)")

                                # Buscar arquivo HTML de resultado mais recente
                                arquivos_html = sorted(
                                    config.RESULTS_DIR.glob("mensagens_det_*.html"),
                                    key=lambda x: x.stat().st_mtime,
                                    reverse=True
                                )

                                if arquivos_html:
                                    st.session_state.resultados = arquivos_html[0]
                                    adicionar_log(f"📄 Arquivo HTML gerado: {arquivos_html[0].name}")
                            else:
                                adicionar_log("❌ Processamento falhou")
                                st.error("❌ Processamento falhou. Verifique os logs.")

                        except Exception as e:
                            adicionar_log(f"❌ Erro: {str(e)}")
                            st.error(f"❌ Erro ao processar: {str(e)}")

                    st.rerun()
            else:
                st.info("ℹ️ Informe os CNPJs das empresas para iniciar a verificação")

        st.divider()

        # Logs em tempo real
        if st.session_state.logs:
            st.subheader("📝 Logs da Execução")
            log_container = st.container(height=300)
            with log_container:
                for log in st.session_state.logs:
                    st.text(log)

    # TAB 2: Resultados
    with tab2:
        st.header("📊 Resultados da Verificação")

        # Resumo
        if st.session_state.mensagens_data:
            dados = st.session_state.mensagens_data

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("🏢 Total de Empresas", dados.get('total_empresas_processadas', 0))

            with col2:
                st.metric("📬 Com Mensagens", dados.get('empresas_com_mensagens', 0))

            with col3:
                st.metric("📭 Sem Mensagens", dados.get('empresas_sem_mensagens', 0))

            with col4:
                st.metric("📧 Total de Mensagens", dados.get('total_mensagens_nao_lidas', 0))

            st.divider()

            # Detalhes por empresa
            st.subheader("🏢 Detalhes por Empresa")

            for resultado in dados.get('resultados_por_empresa', []):
                with st.expander(f"📋 {resultado['nome']} - {formatar_cnpj(resultado['cnpj'])}"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.text(f"Status: {resultado['status']}")
                        st.text(f"CNPJ: {formatar_cnpj(resultado['cnpj'])}")

                    with col2:
                        total_msg = resultado.get('total_mensagens', 0)
                        if total_msg > 0:
                            st.error(f"⚠️ {total_msg} mensagem(ns) não lida(s)")
                        else:
                            st.success("✅ Sem mensagens")

                    # Listar mensagens
                    if resultado.get('mensagens'):
                        st.markdown("**📬 Mensagens Não Lidas:**")
                        for msg in resultado['mensagens']:
                            st.markdown(f"- 📧 **{msg.get('assunto', 'Sem assunto')}**")
                            if msg.get('data'):
                                st.markdown(f"  - 📅 {msg['data']}")
                            if msg.get('remetente'):
                                st.markdown(f"  - 👤 {msg['remetente']}")
                            if msg.get('tem_anexo'):
                                st.markdown("  - 📎 Anexo")

            # Downloads
            st.divider()
            st.subheader("📥 Downloads")

            col1, col2 = st.columns(2)

            with col1:
                # Download JSON
                json_str = json.dumps(dados, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 Baixar JSON",
                    data=json_str,
                    file_name=f"mensagens_det_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            with col2:
                # Download HTML (se existir)
                arquivos_html = sorted(
                    config.RESULTS_DIR.glob("mensagens_det_*.html"),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                if arquivos_html:
                    with open(arquivos_html[0], 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="📥 Baixar HTML",
                            data=f.read(),
                            file_name=arquivos_html[0].name,
                            mime="text/html",
                            use_container_width=True
                        )

            st.divider()

        # Arquivo HTML gerado (se existir)
        if st.session_state.resultados and st.session_state.resultados.suffix == '.html':
            st.success(f"📊 Arquivo HTML gerado: {st.session_state.resultados.name}")

            col1, col2 = st.columns(2)

            with col1:
                data_mod = datetime.fromtimestamp(st.session_state.resultados.stat().st_mtime)
                st.metric("Data", data_mod.strftime("%d/%m/%Y %H:%M"))

            with col2:
                tamanho = st.session_state.resultados.stat().st_size / 1024
                st.metric("Tamanho", f"{tamanho:.2f} KB")

            # Preview do HTML
            try:
                with open(st.session_state.resultados, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                st.subheader("Preview do Relatório")
                st.components.v1.html(html_content, height=800, scrolling=True)
            except Exception as e:
                st.warning(f"Não foi possível carregar preview: {str(e)}")

            # Download
            st.divider()

            with open(st.session_state.resultados, 'r', encoding='utf-8') as f:
                st.download_button(
                    label="📥 BAIXAR ARQUIVO HTML",
                    data=f.read(),
                    file_name=st.session_state.resultados.name,
                    mime="text/html",
                    use_container_width=True
                )

        # Mensagem quando não há resultados
        if not st.session_state.mensagens_data and not st.session_state.resultados:
            st.info("📭 Nenhum resultado disponível ainda. Execute uma verificação na aba '🚀 Processar' para visualizar as mensagens.")

            # Listar resultados anteriores (HTML)
            arquivos_anteriores_html = sorted(
                config.RESULTS_DIR.glob("mensagens_det_*.html"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )

            if arquivos_anteriores_html:
                st.subheader("📁 Resultados Anteriores (HTML)")

                for arquivo in arquivos_anteriores_html[:10]:  # Mostrar últimos 10
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.text(arquivo.name)

                    with col2:
                        data_mod = datetime.fromtimestamp(arquivo.stat().st_mtime)
                        st.text(data_mod.strftime("%d/%m/%Y %H:%M"))

                    with col3:
                        with open(arquivo, 'r', encoding='utf-8') as f:
                            st.download_button(
                                "⬇️",
                                data=f.read(),
                                file_name=arquivo.name,
                                mime="text/html",
                                key=f"download_{arquivo.name}"
                            )

    # TAB 3: Logs
    with tab3:
        st.header("📝 Logs do Sistema")

        col1, col2 = st.columns([3, 1])

        with col2:
            if st.button("🔄 Atualizar", use_container_width=True):
                st.rerun()

            if st.button("🗑️ Limpar", use_container_width=True):
                limpar_logs()
                st.rerun()

        # Mostrar logs
        if st.session_state.logs:
            log_container = st.container(height=600)
            with log_container:
                for log in st.session_state.logs:
                    st.text(log)
        else:
            st.info("📭 Nenhum log disponível")

        st.divider()

        # Arquivos de log
        st.subheader("📁 Arquivos de Log")

        arquivos_log = sorted(
            config.LOGS_DIR.glob("det_robot_*.log"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if arquivos_log:
            for arquivo in arquivos_log[:10]:  # Últimos 10
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.text(arquivo.name)

                with col2:
                    data_mod = datetime.fromtimestamp(arquivo.stat().st_mtime)
                    st.text(data_mod.strftime("%d/%m/%Y %H:%M"))

                with col3:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        st.download_button(
                            "⬇️",
                            data=f.read(),
                            file_name=arquivo.name,
                            mime="text/plain",
                            key=f"log_{arquivo.name}"
                        )
        else:
            st.info("📭 Nenhum arquivo de log encontrado")

    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>🤖 Robô DET - Verificador de Mensagens</strong></p>
            <p>Versão 1.0.0 | Portal: https://det.sit.trabalho.gov.br/</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
