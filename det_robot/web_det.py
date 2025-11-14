"""
Interface Web Streamlit para o Robô DET
Autor: Paulo Sergio
Versão: 2.0.0
"""

import sys
import platform

# IMPORTANTE: Fix para Python 3.13+ no Windows
# Deve estar ANTES de qualquer import de asyncio ou outras libs async!
if sys.platform == 'win32' and sys.version_info >= (3, 8):
    import asyncio
    try:
        # Para Python 3.13+, usar WindowsSelectorEventLoopPolicy
        if sys.version_info >= (3, 13):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # Para Python 3.8-3.12, usar WindowsProactorEventLoopPolicy se disponível
        elif hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception as e:
        print(f"Aviso: Não foi possível configurar event loop policy: {e}")

import streamlit as st
import asyncio
import json
from pathlib import Path
from datetime import datetime

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


def processar_texto_cnpjs(texto: str) -> list:
    """
    Processa texto com CNPJs e retorna lista de dicionários

    Formatos aceitos:
    - CNPJ (um por linha)
    - CNPJ,Nome da Empresa
    - CNPJ;Nome da Empresa
    """
    empresas = []
    linhas = texto.strip().split('\n')

    for idx, linha in enumerate(linhas, 1):
        linha = linha.strip()
        if not linha or linha.startswith('#'):
            continue

        # Tentar separar CNPJ e nome
        cnpj = ""
        nome = f"Empresa {idx}"

        # Verificar se tem vírgula ou ponto-e-vírgula
        if ',' in linha:
            partes = linha.split(',', 1)
            cnpj = partes[0].strip()
            if len(partes) > 1:
                nome = partes[1].strip()
        elif ';' in linha:
            partes = linha.split(';', 1)
            cnpj = partes[0].strip()
            if len(partes) > 1:
                nome = partes[1].strip()
        else:
            cnpj = linha

        # Limpar CNPJ (remover tudo que não é número)
        cnpj_limpo = ''.join(c for c in cnpj if c.isdigit())

        if len(cnpj_limpo) == 14:
            empresas.append({
                "cnpj": cnpj_limpo,
                "nome": nome
            })
        elif cnpj_limpo:  # Se tem números mas não são 14 dígitos
            st.warning(f"⚠️ CNPJ inválido na linha {idx}: {cnpj} (deve ter 14 dígitos)")

    return empresas


def processar_arquivo_cnpjs(uploaded_file) -> list:
    """Processa arquivo com CNPJs (TXT ou JSON)"""
    try:
        conteudo = uploaded_file.read().decode('utf-8')

        # Se for JSON
        if uploaded_file.name.endswith('.json'):
            dados = json.loads(conteudo)
            if isinstance(dados, list):
                empresas = []
                for item in dados:
                    if isinstance(item, dict) and 'cnpj' in item:
                        cnpj_limpo = ''.join(c for c in str(item['cnpj']) if c.isdigit())
                        if len(cnpj_limpo) == 14:
                            empresas.append({
                                "cnpj": cnpj_limpo,
                                "nome": item.get('nome', f'Empresa {len(empresas)+1}')
                            })
                return empresas

        # Se for TXT, processar como texto
        return processar_texto_cnpjs(conteudo)

    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
        return []


async def executar_robot(empresas: list):
    """Executa o robô para processar empresas"""
    try:
        adicionar_log("Iniciando robô...")

        # Criar instância do robô
        robot = RobotDET(headless=False)

        # Processar empresas
        sucesso = await robot.processar_empresas(empresas)

        if sucesso:
            adicionar_log("✅ Processamento concluído!")
            return robot.dados_resultado
        else:
            adicionar_log("❌ Erro no processamento")
            return None

    except Exception as e:
        adicionar_log(f"❌ Erro: {str(e)}")
        st.error(f"Erro ao executar robô: {str(e)}")
        return None


def run_async(coro):
    """
    Executa uma coroutine de forma segura, garantindo o event loop correto para Python 3.13
    """
    # Re-aplicar o fix antes de criar/obter o event loop
    if sys.platform == 'win32' and sys.version_info >= (3, 13):
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception:
            pass

    # Tentar obter event loop existente
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Executar a coroutine
    return loop.run_until_complete(coro)


def main():
    """Função principal da interface"""

    # Título
    st.title("🤖 Robô DET - Verificador de Mensagens")
    st.markdown("**Portal:** https://det.sit.trabalho.gov.br/")
    st.markdown("**Versão:** 2.0.0")

    st.divider()

    # Sidebar com informações
    with st.sidebar:
        st.header("ℹ️ Informações")
        st.info("""
        **Como usar:**
        1. Digite os CNPJs ou faça upload de arquivo
        2. Clique em "Processar Empresas"
        3. Selecione seu certificado digital
        4. Aguarde os resultados
        """)

        st.header("📋 Formatos Aceitos")
        st.code("""
# Apenas CNPJ
12345678000190

# CNPJ com nome
12345678000190,Minha Empresa
12345678000190;Minha Empresa
        """, language="text")

        st.header("📊 Sistema")
        st.text(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        st.text(f"Sistema: {platform.system()}")

    # Área principal
    tab1, tab2 = st.tabs(["📝 Processar", "📊 Resultados"])

    with tab1:
        st.header("📝 Adicionar Empresas")

        # Método de entrada
        metodo = st.radio(
            "Escolha o método:",
            ["Digitar CNPJs", "Upload de Arquivo"],
            horizontal=True
        )

        empresas = []

        if metodo == "Digitar CNPJs":
            st.markdown("**Digite os CNPJs (um por linha):**")
            texto_cnpjs = st.text_area(
                "CNPJs",
                height=200,
                placeholder="12345678000190\n98765432000188\nou\n12345678000190,Nome da Empresa",
                label_visibility="collapsed"
            )

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("👁️ Visualizar CNPJs"):
                    if texto_cnpjs.strip():
                        empresas = processar_texto_cnpjs(texto_cnpjs)
                        if empresas:
                            st.success(f"✅ {len(empresas)} empresa(s) encontrada(s)")
                            for emp in empresas:
                                st.write(f"- {emp['nome']}: {emp['cnpj']}")
                        else:
                            st.warning("⚠️ Nenhum CNPJ válido encontrado")
                    else:
                        st.warning("⚠️ Digite pelo menos um CNPJ")

        else:  # Upload de Arquivo
            st.markdown("**Faça upload de um arquivo TXT ou JSON:**")
            uploaded_file = st.file_uploader(
                "Escolha um arquivo",
                type=['txt', 'json'],
                label_visibility="collapsed"
            )

            if uploaded_file:
                empresas = processar_arquivo_cnpjs(uploaded_file)
                if empresas:
                    st.success(f"✅ {len(empresas)} empresa(s) carregada(s)")
                    with st.expander("Ver empresas carregadas"):
                        for emp in empresas:
                            st.write(f"- {emp['nome']}: {emp['cnpj']}")
                else:
                    st.error("❌ Nenhuma empresa válida encontrada no arquivo")

            # Botões para download de exemplos
            st.markdown("**📥 Baixar exemplos:**")
            col1, col2 = st.columns(2)

            with col1:
                exemplo_txt = "12345678000190,Empresa Exemplo 1\n98765432000188,Empresa Exemplo 2"
                st.download_button(
                    "📄 Exemplo TXT",
                    exemplo_txt,
                    "exemplo_cnpjs.txt",
                    "text/plain"
                )

            with col2:
                exemplo_json = json.dumps([
                    {"cnpj": "12345678000190", "nome": "Empresa Exemplo 1"},
                    {"cnpj": "98765432000188", "nome": "Empresa Exemplo 2"}
                ], indent=2, ensure_ascii=False)
                st.download_button(
                    "📄 Exemplo JSON",
                    exemplo_json,
                    "exemplo_cnpjs.json",
                    "application/json"
                )

        st.divider()

        # Botão processar
        if st.button("🚀 Processar Empresas", type="primary", use_container_width=True):
            # Obter empresas do método escolhido
            if metodo == "Digitar CNPJs" and texto_cnpjs.strip():
                empresas = processar_texto_cnpjs(texto_cnpjs)

            if not empresas:
                st.error("❌ Nenhuma empresa para processar. Adicione CNPJs primeiro!")
            else:
                st.info(f"🔄 Processando {len(empresas)} empresa(s)...")

                # Executar robô usando nossa função segura
                with st.spinner("Aguarde... O navegador vai abrir para seleção do certificado"):
                    resultado = run_async(executar_robot(empresas))

                if resultado:
                    st.session_state.ultimo_resultado = resultado
                    st.success("✅ Processamento concluído!")
                    st.balloons()

                    # Mostrar resumo
                    st.header("📊 Resumo")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "Total",
                            resultado.get('total_empresas_processadas', 0)
                        )
                    with col2:
                        st.metric(
                            "Com Mensagens",
                            resultado.get('empresas_com_mensagens', 0)
                        )
                    with col3:
                        st.metric(
                            "Sem Mensagens",
                            resultado.get('empresas_sem_mensagens', 0)
                        )
                    with col4:
                        st.metric(
                            "Total Mensagens",
                            resultado.get('total_mensagens_nao_lidas', 0)
                        )

                    # Mostrar resultados por empresa
                    st.header("📋 Resultados por Empresa")
                    for res in resultado.get('resultados_por_empresa', []):
                        with st.expander(f"{res['nome']} - {res['cnpj']}"):
                            if res['sucesso']:
                                if res['total_mensagens'] > 0:
                                    st.warning(f"⚠️ {res['total_mensagens']} mensagem(ns) não lida(s)")
                                    for msg in res['mensagens']:
                                        st.write(f"**Assunto:** {msg.get('assunto', 'N/A')}")
                                        st.write(f"**Data:** {msg.get('data', 'N/A')}")
                                        if msg.get('remetente'):
                                            st.write(f"**Remetente:** {msg['remetente']}")
                                        if msg.get('tem_anexo'):
                                            st.write("📎 Com anexo")
                                        st.divider()
                                else:
                                    st.success("✅ Nenhuma mensagem não lida")
                            else:
                                st.error(f"❌ Erro: {res.get('erro', 'Desconhecido')}")

                    # Informar localização dos arquivos
                    st.info("""
                    📂 **Relatórios salvos em:** `det_robot/resultados/`
                    - Abra o arquivo HTML para visualizar relatório completo
                    - Arquivo JSON para processamento de dados
                    """)

    with tab2:
        st.header("📊 Último Resultado")

        if "ultimo_resultado" in st.session_state:
            resultado = st.session_state.ultimo_resultado

            st.json(resultado)

            # Botão para baixar JSON
            json_str = json.dumps(resultado, indent=2, ensure_ascii=False)
            st.download_button(
                "💾 Baixar Resultado (JSON)",
                json_str,
                f"resultado_det_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )
        else:
            st.info("ℹ️ Nenhum resultado disponível ainda. Processe empresas primeiro.")


if __name__ == "__main__":
    main()
