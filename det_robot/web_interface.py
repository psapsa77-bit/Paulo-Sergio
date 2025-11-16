"""
Interface web Streamlit para o DET Robot
"""

import streamlit as st
import time
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional

from .browser import BrowserManager
from .auth import DETAuthenticator
from .scraper import DETScraper
from .storage import DETStorage
from .models import ResultadoExtracao, StatusMensagem, TipoMensagem


def configurar_pagina():
    """Configura a página Streamlit"""
    st.set_page_config(
        page_title="DET Robot - Extrator de Mensagens",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # CSS customizado
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .status-box {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .status-success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }
        .status-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
        }
        .status-error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)


def inicializar_estado():
    """Inicializa variáveis de estado da sessão"""
    if "browser" not in st.session_state:
        st.session_state.browser = None
    if "auth" not in st.session_state:
        st.session_state.auth = None
    if "scraper" not in st.session_state:
        st.session_state.scraper = None
    if "resultado" not in st.session_state:
        st.session_state.resultado = None
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False


def adicionar_log(mensagem: str):
    """Adiciona mensagem ao log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {mensagem}")
    # Manter apenas últimos 100 logs
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]


def sidebar_configuracao():
    """Renderiza sidebar com configurações"""
    st.sidebar.markdown("## ⚙️ Configurações")

    # Navegador
    navegador = st.sidebar.selectbox(
        "Navegador",
        ["auto", "chrome", "chromium", "firefox"],
        index=0,
        help="Navegador a ser usado para automação"
    )

    headless = st.sidebar.checkbox(
        "Modo headless",
        value=False,
        help="Executar sem interface gráfica (mais rápido, mas não visível)"
    )

    # Extração
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Extração")

    apenas_nao_lidas = st.sidebar.checkbox(
        "Apenas mensagens não lidas",
        value=True,
        help="Extrair apenas mensagens que não foram abertas"
    )

    limite = st.sidebar.slider(
        "Limite de mensagens",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
        help="Número máximo de mensagens a extrair"
    )

    # Saída
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 Armazenamento")

    formato = st.sidebar.multiselect(
        "Formatos de saída",
        ["JSON", "CSV", "Excel", "Texto"],
        default=["JSON"],
        help="Formatos para salvar os dados"
    )

    pasta_saida = st.sidebar.text_input(
        "Pasta de saída",
        value="./dados_det",
        help="Pasta onde os dados serão salvos"
    )

    return {
        "navegador": navegador,
        "headless": headless,
        "apenas_nao_lidas": apenas_nao_lidas,
        "limite": limite,
        "formatos": formato,
        "pasta_saida": pasta_saida,
    }


def secao_login():
    """Seção de login"""
    st.markdown("### 🔐 Autenticação")

    col1, col2 = st.columns(2)

    with col1:
        metodo = st.radio(
            "Método de login",
            ["Automático (Gov.br)", "Manual"],
            help="Automático: insere CPF e senha. Manual: você faz login no navegador."
        )

    if metodo == "Automático (Gov.br)":
        with col2:
            cpf = st.text_input(
                "CPF",
                placeholder="000.000.000-00",
                help="CPF cadastrado no Gov.br"
            )
            senha = st.text_input(
                "Senha",
                type="password",
                help="Senha do Gov.br"
            )

        return {
            "metodo": "automatico",
            "cpf": cpf,
            "senha": senha,
        }
    else:
        st.info("No modo manual, o navegador será aberto e você terá 5 minutos para fazer login.")
        return {
            "metodo": "manual",
            "cpf": None,
            "senha": None,
        }


def iniciar_navegador(config: dict):
    """Inicia o navegador"""
    try:
        adicionar_log("Iniciando navegador...")

        browser = BrowserManager(
            navegador=config["navegador"],
            headless=config["headless"],
            log_callback=adicionar_log
        )

        browser.iniciar()
        st.session_state.browser = browser

        adicionar_log(f"Navegador {browser.navegador_usado} iniciado com sucesso")
        return True

    except Exception as e:
        adicionar_log(f"Erro ao iniciar navegador: {e}")
        st.error(f"Erro ao iniciar navegador: {e}")
        return False


def realizar_login(login_info: dict):
    """Realiza login no DET"""
    try:
        if st.session_state.browser is None:
            st.error("Navegador não iniciado")
            return False

        auth = DETAuthenticator(st.session_state.browser, log_callback=adicionar_log)
        st.session_state.auth = auth

        adicionar_log("Acessando página de login...")
        auth.acessar_pagina_login()

        if login_info["metodo"] == "manual":
            adicionar_log("Aguardando login manual...")
            st.info("Por favor, faça login no navegador que foi aberto. Aguardando até 5 minutos...")

            # Criar placeholder para atualização
            status_placeholder = st.empty()

            sucesso = False
            for i in range(60):  # 5 minutos = 300 segundos, checando a cada 5s
                if auth.verificar_autenticacao():
                    sucesso = True
                    break
                status_placeholder.info(f"Aguardando login... ({300 - i*5}s restantes)")
                time.sleep(5)

            status_placeholder.empty()

        else:
            adicionar_log("Realizando login automático...")
            sucesso = auth.login_govbr(login_info["cpf"], login_info["senha"])

        if sucesso:
            st.session_state.autenticado = True
            adicionar_log("Login realizado com sucesso!")
            st.success("Login realizado com sucesso!")
            return True
        else:
            adicionar_log("Falha no login")
            st.error("Falha no login. Verifique suas credenciais.")
            return False

    except Exception as e:
        adicionar_log(f"Erro no login: {e}")
        st.error(f"Erro no login: {e}")
        return False


def executar_extracao(config: dict):
    """Executa a extração de mensagens"""
    try:
        if not st.session_state.autenticado:
            st.error("Usuário não autenticado")
            return None

        scraper = DETScraper(
            st.session_state.browser,
            st.session_state.auth,
            log_callback=adicionar_log
        )
        st.session_state.scraper = scraper

        adicionar_log("Iniciando extração de mensagens...")

        with st.spinner("Extraindo mensagens..."):
            resultado = scraper.executar_extracao_completa(
                apenas_nao_lidas=config["apenas_nao_lidas"],
                limite=config["limite"]
            )

        st.session_state.resultado = resultado

        if resultado.sucesso:
            adicionar_log(f"Extração concluída: {resultado.total_extraido} mensagens")
            st.success(f"Extração concluída! {resultado.total_extraido} mensagens extraídas.")
        else:
            adicionar_log(f"Extração falhou: {resultado.erros}")
            st.error(f"Erros na extração: {', '.join(resultado.erros)}")

        return resultado

    except Exception as e:
        adicionar_log(f"Erro na extração: {e}")
        st.error(f"Erro na extração: {e}")
        return None


def salvar_resultados(resultado: ResultadoExtracao, config: dict):
    """Salva os resultados nos formatos selecionados"""
    storage = DETStorage(config["pasta_saida"], log_callback=adicionar_log)
    arquivos = []

    if "JSON" in config["formatos"]:
        arquivo = storage.salvar_json(resultado)
        arquivos.append(("JSON", arquivo))

    if "CSV" in config["formatos"]:
        arquivo = storage.salvar_csv(resultado)
        arquivos.append(("CSV", arquivo))

    if "Excel" in config["formatos"]:
        arquivo = storage.salvar_excel(resultado)
        arquivos.append(("Excel", arquivo))

    if "Texto" in config["formatos"]:
        arquivo = storage.salvar_relatorio_texto(resultado)
        arquivos.append(("Texto", arquivo))

    return arquivos


def exibir_resultados(resultado: ResultadoExtracao):
    """Exibe os resultados da extração"""
    st.markdown("### 📊 Resultados da Extração")

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Mensagens", resultado.total_extraido)

    with col2:
        nao_lidas = sum(1 for m in resultado.mensagens if m.status == StatusMensagem.NAO_LIDA)
        st.metric("Não Lidas", nao_lidas)

    with col3:
        urgentes = sum(1 for m in resultado.mensagens if m.dias_restantes is not None and m.dias_restantes < 5)
        st.metric("Urgentes (< 5 dias)", urgentes, delta_color="inverse")

    with col4:
        if resultado.tempo_execucao:
            st.metric("Tempo de Execução", f"{resultado.tempo_execucao:.1f}s")

    # Gráficos
    if resultado.mensagens:
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico por tipo
            tipos = {}
            for msg in resultado.mensagens:
                tipo = msg.tipo.value
                tipos[tipo] = tipos.get(tipo, 0) + 1

            fig = px.pie(
                values=list(tipos.values()),
                names=list(tipos.keys()),
                title="Distribuição por Tipo",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gráfico por status
            status = {}
            for msg in resultado.mensagens:
                s = msg.status.value
                status[s] = status.get(s, 0) + 1

            fig = px.bar(
                x=list(status.keys()),
                y=list(status.values()),
                title="Status das Mensagens",
                color=list(status.keys()),
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            st.plotly_chart(fig, use_container_width=True)

        # Tabela de mensagens
        st.markdown("### 📬 Lista de Mensagens")

        # Converter para DataFrame
        dados = []
        for msg in resultado.mensagens:
            dados.append({
                "Assunto": msg.assunto,
                "Tipo": msg.tipo.value,
                "Data": msg.data_envio.strftime("%d/%m/%Y"),
                "Status": msg.status.value,
                "Prazo": msg.prazo_resposta.strftime("%d/%m/%Y") if msg.prazo_resposta else "-",
                "Dias Restantes": msg.dias_restantes if msg.dias_restantes is not None else "-",
            })

        df = pd.DataFrame(dados)

        # Destacar mensagens urgentes
        def destacar_urgentes(row):
            if row["Dias Restantes"] != "-" and int(row["Dias Restantes"]) < 5:
                return ["background-color: #ffcccb"] * len(row)
            return [""] * len(row)

        st.dataframe(
            df.style.apply(destacar_urgentes, axis=1),
            use_container_width=True,
            height=400
        )

    else:
        st.warning("Nenhuma mensagem encontrada")


def exibir_logs():
    """Exibe os logs de execução"""
    with st.expander("📝 Logs de Execução", expanded=False):
        if st.session_state.logs:
            log_text = "\n".join(st.session_state.logs)
            st.code(log_text, language="text")
        else:
            st.info("Nenhum log disponível")


def fechar_navegador():
    """Fecha o navegador se estiver aberto"""
    if st.session_state.browser:
        try:
            st.session_state.browser.fechar()
            adicionar_log("Navegador fechado")
        except:
            pass
        st.session_state.browser = None
        st.session_state.auth = None
        st.session_state.scraper = None
        st.session_state.autenticado = False


def main():
    """Função principal da interface web"""
    configurar_pagina()
    inicializar_estado()

    # Cabeçalho
    st.markdown('<p class="main-header">🤖 DET Robot</p>', unsafe_allow_html=True)
    st.markdown("Extrator automático de mensagens do Domicílio Eletrônico Trabalhista")

    # Sidebar
    config = sidebar_configuracao()

    # Área principal
    tab1, tab2, tab3 = st.tabs(["🚀 Extração", "📁 Histórico", "ℹ️ Sobre"])

    with tab1:
        # Status atual
        if st.session_state.autenticado:
            st.success("✅ Autenticado no DET")
        elif st.session_state.browser:
            st.warning("⚠️ Navegador aberto, mas não autenticado")
        else:
            st.info("ℹ️ Navegador não iniciado")

        # Login
        login_info = secao_login()

        st.markdown("---")

        # Botões de ação
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("1️⃣ Iniciar Navegador", use_container_width=True, disabled=st.session_state.browser is not None):
                iniciar_navegador(config)

        with col2:
            if st.button("2️⃣ Fazer Login", use_container_width=True, disabled=st.session_state.browser is None or st.session_state.autenticado):
                realizar_login(login_info)

        with col3:
            if st.button("3️⃣ Extrair Mensagens", use_container_width=True, disabled=not st.session_state.autenticado):
                resultado = executar_extracao(config)
                if resultado and resultado.sucesso:
                    arquivos = salvar_resultados(resultado, config)
                    st.success("Dados salvos!")
                    for formato, arquivo in arquivos:
                        st.write(f"- {formato}: `{arquivo}`")

        # Botão para fechar
        if st.button("🔴 Fechar Navegador", use_container_width=True):
            fechar_navegador()
            st.info("Navegador fechado")

        st.markdown("---")

        # Resultados
        if st.session_state.resultado:
            exibir_resultados(st.session_state.resultado)

        # Logs
        exibir_logs()

    with tab2:
        st.markdown("### 📁 Extrações Anteriores")

        storage = DETStorage(config["pasta_saida"])
        extracoes = storage.listar_extracoes()

        if extracoes:
            for ext in extracoes[:10]:  # Mostrar últimas 10
                with st.expander(f"📄 {ext['nome']}"):
                    st.write(f"**Data:** {ext['data_modificacao'].strftime('%d/%m/%Y %H:%M')}")
                    st.write(f"**Tamanho:** {ext['tamanho'] / 1024:.1f} KB")

                    if st.button(f"Carregar", key=ext["nome"]):
                        resultado = storage.carregar_json(ext["caminho"])
                        st.session_state.resultado = resultado
                        st.success("Dados carregados!")
                        st.rerun()
        else:
            st.info("Nenhuma extração encontrada na pasta configurada")

    with tab3:
        st.markdown("""
        ### Sobre o DET Robot

        O DET Robot é uma ferramenta de automação para extrair informações de mensagens
        do Domicílio Eletrônico Trabalhista (DET) sem precisar abrir cada mensagem individualmente.

        #### Funcionalidades:
        - ✅ Login via Gov.br (automático ou manual)
        - ✅ Extração de mensagens não lidas
        - ✅ Identificação de prazos e mensagens urgentes
        - ✅ Exportação para JSON, CSV, Excel e Texto
        - ✅ Interface gráfica intuitiva
        - ✅ Usa navegador nativo do sistema

        #### Segurança:
        - Suas credenciais não são armazenadas
        - O navegador é controlado localmente
        - Nenhum dado é enviado para terceiros

        #### Requisitos:
        - Navegador instalado (Chrome, Chromium ou Firefox)
        - Python 3.9+
        - Dependências: selenium, webdriver-manager

        ---
        **Versão:** 1.0.0
        """)


if __name__ == "__main__":
    main()
