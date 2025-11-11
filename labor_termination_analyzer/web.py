"""
Interface Web SIMPLIFICADA para o Labor Termination Analyzer
Foco em PDF/TXT com formulário editável
"""

import streamlit as st
import json
import tempfile
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal
import plotly.graph_objects as go

from .models import RescisaoTrabalhista, Funcionario, Verbas, Descontos
from .parser import RescisaoParser
from .analyzer import RescisaoAnalyzer
from .generators import HTMLGenerator, PDFGenerator
from .pdf_extractor import PDFExtractor


def formatar_moeda(valor: Decimal) -> str:
    """Formata valor para moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def criar_grafico_verbas(resumo: dict):
    """Cria gráfico de pizza das verbas"""
    verbas = resumo['verbas']

    if not verbas:
        return None

    labels = [v['titulo'] for v in verbas]
    values = [float(v['valor']) for v in verbas]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12', '#1abc9c', '#34495e', '#16a085']
    )])

    fig.update_layout(
        title_text="Composição das Verbas Rescisórias",
        height=400
    )

    return fig


def criar_grafico_totais(resumo: dict):
    """Cria gráfico de barras dos totais"""
    totais = resumo['totais']

    fig = go.Figure(data=[
        go.Bar(
            x=['Total Verbas', 'Total Descontos', 'Valor Líquido'],
            y=[
                float(totais['total_verbas']),
                float(totais['total_descontos']),
                float(totais['valor_liquido'])
            ],
            marker_color=['#2ecc71', '#e74c3c', '#3498db']
        )
    ])

    fig.update_layout(
        title_text="Resumo Financeiro",
        yaxis_title="Valor (R$)",
        height=400
    )

    return fig


def extrair_texto_arquivo(uploaded_file, usar_ocr=False):
    """Extrai texto de PDF ou TXT"""
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == 'txt':
        # Arquivo TXT - simples
        return uploaded_file.getvalue().decode('utf-8'), {}

    elif file_type == 'pdf':
        # Arquivo PDF - usar extrator
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        extractor = PDFExtractor()
        dados_extraidos = extractor.extrair_de_pdf(tmp_path, usar_ocr=usar_ocr)
        texto_completo = extractor.obter_texto_completo()

        Path(tmp_path).unlink()

        return texto_completo, dados_extraidos

    return "", {}


def main():
    """Função principal da interface web"""

    st.set_page_config(
        page_title="Labor Termination Analyzer",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Cabeçalho
    st.title("📋 Labor Termination Analyzer")
    st.markdown("**Análise de rescisões trabalhistas com geração de relatórios**")
    st.divider()

    # Sidebar para opções
    with st.sidebar:
        st.header("⚙️ Modo de Entrada")
        modo = st.radio(
            "Escolha como inserir dados:",
            ["📄 Upload de Arquivo (PDF/TXT)", "✍️ Formulário em Branco"],
            help="Upload extrai dados automaticamente e permite edição"
        )

    rescisao = None

    # ============================================================================
    # MODO 1: UPLOAD DE ARQUIVO (PDF/TXT) COM FORMULÁRIO PRÉ-PREENCHIDO
    # ============================================================================
    if modo == "📄 Upload de Arquivo (PDF/TXT)":
        st.header("📄 Upload de Arquivo de Rescisão")

        st.info(
            "💡 **Como funciona:**\n\n"
            "1. Faça upload do PDF ou TXT da rescisão\n"
            "2. O sistema extrai o texto e tenta identificar os dados\n"
            "3. Um formulário aparece PRÉ-PREENCHIDO\n"
            "4. Você EDITA o que estiver errado\n"
            "5. Clica em Analisar!"
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Escolha o arquivo (PDF ou TXT)",
                type=['pdf', 'txt'],
                help="PDF com texto ou arquivo TXT simples"
            )

        with col2:
            usar_ocr = st.checkbox(
                "PDF Escaneado?",
                value=False,
                help="Marque apenas se o PDF for imagem escaneada"
            )

        if uploaded_file is not None:
            try:
                with st.spinner("📖 Extraindo texto do arquivo..."):
                    texto_completo, dados_extraidos = extrair_texto_arquivo(uploaded_file, usar_ocr)

                # Mostrar texto extraído para referência
                with st.expander("📄 Ver texto completo extraído do arquivo", expanded=False):
                    st.text_area(
                        "Texto do arquivo (use como referência para preencher o formulário)",
                        texto_completo,
                        height=300
                    )

                # FORMULÁRIO PRÉ-PREENCHIDO
                st.success("✅ Arquivo carregado! Revise e corrija os dados abaixo:")

                # Pegar dados extraídos ou valores padrão
                func_data = dados_extraidos.get('funcionario', {}) if dados_extraidos else {}
                verbas_data = dados_extraidos.get('verbas', {}) if dados_extraidos else {}
                descontos_data = dados_extraidos.get('descontos', {}) if dados_extraidos else {}
                tipo_resc = dados_extraidos.get('tipo_rescisao', 'sem justa causa') if dados_extraidos else 'sem justa causa'

                with st.form("formulario_pdf"):
                    st.subheader("👤 Dados do Funcionário")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        nome = st.text_input(
                            "Nome Completo*",
                            value=func_data.get('nome', ''),
                            help="Corrija se necessário"
                        )
                        cpf = st.text_input(
                            "CPF*",
                            value=func_data.get('cpf', ''),
                            help="Formato: 000.000.000-00"
                        )

                    with col2:
                        cargo = st.text_input(
                            "Cargo*",
                            value=func_data.get('cargo', ''),
                            help="Ex: Analista, Gerente"
                        )
                        salario = st.number_input(
                            "Salário Bruto (R$)*",
                            min_value=0.0,
                            value=float(func_data.get('salario_bruto', '0').replace(',', '.')) if func_data.get('salario_bruto') else 0.0,
                            step=100.0
                        )

                    with col3:
                        # Parse de datas
                        data_adm_str = func_data.get('data_admissao', '01/01/2020')
                        data_dem_str = func_data.get('data_demissao', date.today().strftime('%d/%m/%Y'))

                        try:
                            data_adm = datetime.strptime(data_adm_str, '%d/%m/%Y').date()
                        except:
                            data_adm = date(2020, 1, 1)

                        try:
                            data_dem = datetime.strptime(data_dem_str, '%d/%m/%Y').date()
                        except:
                            data_dem = date.today()

                        data_admissao = st.date_input("Data de Admissão*", value=data_adm)
                        data_demissao = st.date_input("Data de Demissão*", value=data_dem)

                    st.divider()
                    st.subheader("📑 Tipo de Rescisão")

                    tipo_rescisao = st.selectbox(
                        "Selecione o tipo*",
                        ["sem justa causa", "com justa causa", "pedido de demissao", "acordo"],
                        index=["sem justa causa", "com justa causa", "pedido de demissao", "acordo"].index(tipo_resc) if tipo_resc in ["sem justa causa", "com justa causa", "pedido de demissao", "acordo"] else 0
                    )

                    st.divider()
                    st.subheader("💰 Verbas Rescisórias")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        saldo_salario = st.number_input(
                            "Saldo de Salário (R$)",
                            min_value=0.0,
                            value=float(verbas_data.get('saldo_salario', '0').replace(',', '.')) if verbas_data.get('saldo_salario') else 0.0,
                            step=10.0
                        )
                        aviso_previo = st.number_input(
                            "Aviso Prévio Indenizado (R$)",
                            min_value=0.0,
                            value=float(verbas_data.get('aviso_previo_indenizado', '0').replace(',', '.')) if verbas_data.get('aviso_previo_indenizado') else 0.0,
                            step=100.0
                        )
                        ferias_vencidas = st.number_input(
                            "Férias Vencidas (R$)",
                            min_value=0.0,
                            value=float(verbas_data.get('ferias_vencidas', '0').replace(',', '.')) if verbas_data.get('ferias_vencidas') else 0.0,
                            step=100.0
                        )

                    with col2:
                        ferias_proporcionais = st.number_input(
                            "Férias Proporcionais (R$)",
                            min_value=0.0,
                            value=float(verbas_data.get('ferias_proporcionais', '0').replace(',', '.')) if verbas_data.get('ferias_proporcionais') else 0.0,
                            step=10.0
                        )
                        um_terco = st.number_input(
                            "1/3 sobre Férias (R$)",
                            min_value=0.0,
                            value=float(verbas_data.get('um_terco_ferias', '0').replace(',', '.')) if verbas_data.get('um_terco_ferias') else 0.0,
                            step=10.0
                        )
                        decimo_terceiro = st.number_input(
                            "13º Proporcional (R$)",
                            min_value=0.0,
                            value=float(verbas_data.get('decimo_terceiro_proporcional', '0').replace(',', '.')) if verbas_data.get('decimo_terceiro_proporcional') else 0.0,
                            step=10.0
                        )

                    with col3:
                        multa_fgts = st.number_input(
                            "Multa 40% FGTS (R$)",
                            min_value=0.0,
                            value=float(verbas_data.get('multa_fgts_40', '0').replace(',', '.')) if verbas_data.get('multa_fgts_40') else 0.0,
                            step=100.0
                        )
                        saldo_fgts = st.number_input(
                            "Saldo FGTS (R$)",
                            min_value=0.0,
                            value=float(verbas_data.get('saldo_fgts', '0').replace(',', '.')) if verbas_data.get('saldo_fgts') else 0.0,
                            step=100.0
                        )

                    st.divider()
                    st.subheader("➖ Descontos")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        inss = st.number_input(
                            "INSS (R$)",
                            min_value=0.0,
                            value=float(descontos_data.get('inss', '0').replace(',', '.')) if descontos_data.get('inss') else 0.0,
                            step=10.0
                        )

                    with col2:
                        irrf = st.number_input(
                            "IRRF (R$)",
                            min_value=0.0,
                            value=float(descontos_data.get('irrf', '0').replace(',', '.')) if descontos_data.get('irrf') else 0.0,
                            step=10.0
                        )

                    with col3:
                        desc_aviso_previo = st.number_input(
                            "Desconto Aviso Prévio (R$)",
                            min_value=0.0,
                            value=float(descontos_data.get('aviso_previo_indenizado', '0').replace(',', '.')) if descontos_data.get('aviso_previo_indenizado') else 0.0,
                            step=10.0
                        )

                    st.divider()
                    observacoes = st.text_area(
                        "Observações",
                        value="Dados extraídos de arquivo e revisados.",
                        help="Observações adicionais"
                    )

                    submitted = st.form_submit_button(
                        "🔍 Analisar Rescisão",
                        type="primary",
                        use_container_width=True
                    )

                    if submitted:
                        try:
                            # Criar objeto Rescisao
                            funcionario = Funcionario(
                                nome=nome,
                                cpf=cpf,
                                cargo=cargo,
                                data_admissao=data_admissao,
                                data_demissao=data_demissao,
                                salario_bruto=Decimal(str(salario))
                            )

                            verbas = Verbas(
                                saldo_salario=Decimal(str(saldo_salario)),
                                aviso_previo_indenizado=Decimal(str(aviso_previo)),
                                ferias_vencidas=Decimal(str(ferias_vencidas)),
                                ferias_proporcionais=Decimal(str(ferias_proporcionais)),
                                um_terco_ferias=Decimal(str(um_terco)),
                                decimo_terceiro_proporcional=Decimal(str(decimo_terceiro)),
                                multa_fgts_40=Decimal(str(multa_fgts)),
                                saldo_fgts=Decimal(str(saldo_fgts))
                            )

                            descontos = Descontos(
                                inss=Decimal(str(inss)),
                                irrf=Decimal(str(irrf)),
                                aviso_previo_indenizado=Decimal(str(desc_aviso_previo))
                            )

                            rescisao = RescisaoTrabalhista(
                                funcionario=funcionario,
                                tipo_rescisao=tipo_rescisao,
                                verbas=verbas,
                                descontos=descontos,
                                observacoes=observacoes if observacoes else None
                            )

                            st.success("✅ Dados validados com sucesso!")

                        except Exception as e:
                            st.error(f"❌ Erro ao processar dados: {str(e)}")

            except Exception as e:
                st.error(f"❌ Erro ao ler arquivo: {str(e)}")
                st.info("💡 Tente outro arquivo ou use o Formulário em Branco")

    # ============================================================================
    # MODO 2: FORMULÁRIO EM BRANCO
    # ============================================================================
    else:
        st.header("✍️ Formulário em Branco")

        with st.form("formulario_manual"):
            st.subheader("👤 Dados do Funcionário")

            col1, col2, col3 = st.columns(3)

            with col1:
                nome = st.text_input("Nome Completo*", value="")
                cpf = st.text_input("CPF*", value="")

            with col2:
                cargo = st.text_input("Cargo*", value="")
                salario = st.number_input("Salário Bruto (R$)*", min_value=0.0, value=0.0, step=100.0)

            with col3:
                data_admissao = st.date_input("Data de Admissão*", value=date(2020, 1, 1))
                data_demissao = st.date_input("Data de Demissão*", value=date.today())

            st.divider()
            st.subheader("📑 Tipo de Rescisão")

            tipo_rescisao = st.selectbox(
                "Selecione o tipo*",
                ["sem justa causa", "com justa causa", "pedido de demissao", "acordo"]
            )

            st.divider()
            st.subheader("💰 Verbas Rescisórias")

            col1, col2, col3 = st.columns(3)

            with col1:
                saldo_salario = st.number_input("Saldo de Salário (R$)", min_value=0.0, value=0.0, step=10.0)
                aviso_previo = st.number_input("Aviso Prévio Indenizado (R$)", min_value=0.0, value=0.0, step=100.0)
                ferias_vencidas = st.number_input("Férias Vencidas (R$)", min_value=0.0, value=0.0, step=100.0)

            with col2:
                ferias_proporcionais = st.number_input("Férias Proporcionais (R$)", min_value=0.0, value=0.0, step=10.0)
                um_terco = st.number_input("1/3 sobre Férias (R$)", min_value=0.0, value=0.0, step=10.0)
                decimo_terceiro = st.number_input("13º Proporcional (R$)", min_value=0.0, value=0.0, step=10.0)

            with col3:
                multa_fgts = st.number_input("Multa 40% FGTS (R$)", min_value=0.0, value=0.0, step=100.0)
                saldo_fgts = st.number_input("Saldo FGTS (R$)", min_value=0.0, value=0.0, step=100.0)

            st.divider()
            st.subheader("➖ Descontos")

            col1, col2, col3 = st.columns(3)

            with col1:
                inss = st.number_input("INSS (R$)", min_value=0.0, value=0.0, step=10.0)

            with col2:
                irrf = st.number_input("IRRF (R$)", min_value=0.0, value=0.0, step=10.0)

            with col3:
                desc_aviso_previo = st.number_input("Desconto Aviso Prévio (R$)", min_value=0.0, value=0.0, step=10.0)

            st.divider()
            observacoes = st.text_area("Observações", value="")

            submitted = st.form_submit_button("🔍 Analisar Rescisão", type="primary", use_container_width=True)

            if submitted:
                try:
                    funcionario = Funcionario(
                        nome=nome,
                        cpf=cpf,
                        cargo=cargo,
                        data_admissao=data_admissao,
                        data_demissao=data_demissao,
                        salario_bruto=Decimal(str(salario))
                    )

                    verbas = Verbas(
                        saldo_salario=Decimal(str(saldo_salario)),
                        aviso_previo_indenizado=Decimal(str(aviso_previo)),
                        ferias_vencidas=Decimal(str(ferias_vencidas)),
                        ferias_proporcionais=Decimal(str(ferias_proporcionais)),
                        um_terco_ferias=Decimal(str(um_terco)),
                        decimo_terceiro_proporcional=Decimal(str(decimo_terceiro)),
                        multa_fgts_40=Decimal(str(multa_fgts)),
                        saldo_fgts=Decimal(str(saldo_fgts))
                    )

                    descontos = Descontos(
                        inss=Decimal(str(inss)),
                        irrf=Decimal(str(irrf)),
                        aviso_previo_indenizado=Decimal(str(desc_aviso_previo))
                    )

                    rescisao = RescisaoTrabalhista(
                        funcionario=funcionario,
                        tipo_rescisao=tipo_rescisao,
                        verbas=verbas,
                        descontos=descontos,
                        observacoes=observacoes if observacoes else None
                    )

                    st.success("✅ Dados validados com sucesso!")

                except Exception as e:
                    st.error(f"❌ Erro ao processar dados: {str(e)}")

    # ============================================================================
    # EXIBIR ANÁLISE
    # ============================================================================
    if rescisao is not None:
        st.divider()
        st.header("📊 Análise da Rescisão")

        # Criar análise
        analyzer = RescisaoAnalyzer(rescisao)
        resumo = analyzer.gerar_resumo_completo()

        # Informações do Funcionário
        with st.expander("👤 Informações do Funcionário", expanded=True):
            func = resumo['funcionario']

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Nome", func['nome'])
                st.metric("CPF", func['cpf'])

            with col2:
                st.metric("Cargo", func['cargo'])
                st.metric("Salário Bruto", func['salario_bruto'])

            with col3:
                st.metric("Admissão", func['data_admissao'])
                st.metric("Demissão", func['data_demissao'])

            with col4:
                st.metric("Tempo de Serviço", func['tempo_servico'])

        # Tipo de Rescisão
        tipo = resumo['tipo_rescisao']
        st.info(f"**📑 {tipo['nome']}**\n\n{tipo['descricao']}")

        if tipo.get('direitos'):
            with st.expander("✅ Direitos do Trabalhador neste Tipo de Rescisão"):
                for direito in tipo['direitos']:
                    st.markdown(f"- {direito}")

        # Verbas
        st.subheader("💰 Verbas Rescisórias")

        if resumo['verbas']:
            # Gráfico de verbas
            fig_verbas = criar_grafico_verbas(resumo)
            if fig_verbas:
                st.plotly_chart(fig_verbas, use_container_width=True)

            # Detalhes das verbas
            for verba in resumo['verbas']:
                with st.expander(f"**{verba['titulo']}** - {verba['valor_formatado']}", expanded=False):
                    st.markdown(f"**Descrição:** {verba['descricao']}")
                    st.info(f"**Cálculo:** {verba['calculo']}")

        # Descontos
        if resumo['descontos']:
            st.subheader("➖ Descontos")

            for desconto in resumo['descontos']:
                with st.expander(f"**{desconto['titulo']}** - {desconto['valor_formatado']}", expanded=False):
                    st.markdown(f"**Descrição:** {desconto['descricao']}")
                    st.info(f"**Cálculo:** {desconto['calculo']}")

        # Totais
        st.divider()
        st.subheader("💵 Resumo Financeiro")

        totais = resumo['totais']

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Verbas", totais['total_verbas_formatado'])

        with col2:
            st.metric("Total de Descontos", totais['total_descontos_formatado'])

        with col3:
            st.metric("💰 Valor Líquido a Receber", totais['valor_liquido_formatado'])

        # Gráfico de totais
        fig_totais = criar_grafico_totais(resumo)
        st.plotly_chart(fig_totais, use_container_width=True)

        # Observações
        if resumo['observacoes']:
            st.warning(f"**⚠️ Observações**\n\n{resumo['observacoes']}")

        # Botões de Download
        st.divider()
        st.subheader("📥 Gerar Relatórios")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Gerar HTML
            try:
                html_gen = HTMLGenerator()

                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
                    html_path = html_gen.gerar(rescisao, tmp.name)

                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()

                    st.download_button(
                        label="📄 Baixar Relatório HTML",
                        data=html_content,
                        file_name=f"rescisao_{resumo['funcionario']['nome'].replace(' ', '_')}.html",
                        mime="text/html",
                        use_container_width=True
                    )

                    Path(html_path).unlink()
            except Exception as e:
                st.error(f"Erro ao gerar HTML: {str(e)}")

        with col2:
            # Gerar PDF
            try:
                pdf_gen = PDFGenerator()

                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    pdf_path = pdf_gen.gerar(rescisao, tmp.name)

                    with open(pdf_path, 'rb') as f:
                        pdf_content = f.read()

                    st.download_button(
                        label="📑 Baixar Relatório PDF",
                        data=pdf_content,
                        file_name=f"rescisao_{resumo['funcionario']['nome'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                    Path(pdf_path).unlink()
            except RuntimeError as e:
                # Erro específico de WeasyPrint não disponível
                st.warning("⚠️ **PDF não disponível no Windows**")
                st.info(
                    "💡 **SOLUÇÃO RÁPIDA:**\n\n"
                    "1. Baixe o relatório **HTML** (botão ao lado)\n"
                    "2. Abra o HTML no navegador\n"
                    "3. Pressione **Ctrl+P**\n"
                    "4. Escolha **'Salvar como PDF'**"
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {str(e)}")

        with col3:
            # Exportar JSON
            json_data = {
                "funcionario": {
                    "nome": rescisao.funcionario.nome,
                    "cpf": rescisao.funcionario.cpf,
                    "cargo": rescisao.funcionario.cargo,
                    "data_admissao": rescisao.funcionario.data_admissao.isoformat(),
                    "data_demissao": rescisao.funcionario.data_demissao.isoformat(),
                    "salario_bruto": str(rescisao.funcionario.salario_bruto)
                },
                "tipo_rescisao": rescisao.tipo_rescisao,
                "verbas": {k: str(v) for k, v in rescisao.verbas.model_dump().items() if k != "outras_verbas"},
                "descontos": {k: str(v) for k, v in rescisao.descontos.model_dump().items() if k != "outros_descontos"},
                "observacoes": rescisao.observacoes
            }

            st.download_button(
                label="💾 Exportar JSON",
                data=json.dumps(json_data, indent=2, ensure_ascii=False),
                file_name=f"rescisao_{resumo['funcionario']['nome'].replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )

    # Rodapé
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>Labor Termination Analyzer</strong> v1.1.0</p>
            <p>📄 PDF/TXT → Formulário Editável → Relatório Profissional</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
