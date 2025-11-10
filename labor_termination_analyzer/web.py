"""
Interface Web para o Labor Termination Analyzer usando Streamlit
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
    st.markdown("**Análise completa de rescisões trabalhistas com geração de relatórios**")
    st.divider()

    # Sidebar para opções
    with st.sidebar:
        st.header("⚙️ Opções")
        modo = st.radio(
            "Escolha o modo de entrada:",
            ["Upload de Arquivo JSON", "Formulário Manual"],
            help="Escolha como deseja inserir os dados da rescisão"
        )

    rescisao = None

    # Modo de Upload de Arquivo
    if modo == "Upload de Arquivo JSON":
        st.header("📤 Upload de Arquivo JSON")

        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "Faça upload do arquivo JSON com os dados da rescisão",
                type=['json'],
                help="O arquivo deve conter os dados no formato especificado"
            )

        with col2:
            st.info("💡 **Dica**: Use um dos exemplos do repositório ou crie um novo arquivo seguindo o formato documentado.")

            # Botão para baixar exemplo
            exemplo = {
                "funcionario": {
                    "nome": "João da Silva",
                    "cpf": "000.000.000-00",
                    "cargo": "Analista",
                    "data_admissao": "2020-01-01",
                    "data_demissao": "2025-11-10",
                    "salario_bruto": "5000.00"
                },
                "tipo_rescisao": "sem justa causa",
                "verbas": {
                    "saldo_salario": "1666.67",
                    "aviso_previo_indenizado": "5000.00"
                },
                "descontos": {
                    "inss": "500.00"
                }
            }

            st.download_button(
                label="📥 Baixar Exemplo JSON",
                data=json.dumps(exemplo, indent=2, ensure_ascii=False),
                file_name="exemplo_rescisao.json",
                mime="application/json"
            )

        if uploaded_file is not None:
            try:
                # Salvar temporariamente e processar
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
                    tmp.write(uploaded_file.getvalue().decode('utf-8'))
                    tmp_path = tmp.name

                rescisao = RescisaoParser.from_json_file(tmp_path)
                Path(tmp_path).unlink()

                st.success("✅ Arquivo processado com sucesso!")

            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo: {str(e)}")

    # Modo de Formulário Manual
    else:
        st.header("📝 Formulário de Entrada Manual")

        with st.form("formulario_rescisao"):
            st.subheader("👤 Dados do Funcionário")

            col1, col2, col3 = st.columns(3)

            with col1:
                nome = st.text_input("Nome Completo*", value="Maria da Silva")
                cpf = st.text_input("CPF*", value="123.456.789-00")

            with col2:
                cargo = st.text_input("Cargo*", value="Analista")
                salario = st.number_input("Salário Bruto (R$)*", min_value=0.0, value=5000.0, step=100.0)

            with col3:
                data_admissao = st.date_input("Data de Admissão*", value=date(2020, 1, 1))
                data_demissao = st.date_input("Data de Demissão*", value=date.today())

            st.divider()
            st.subheader("📑 Tipo de Rescisão")

            tipo_rescisao = st.selectbox(
                "Selecione o tipo*",
                ["sem justa causa", "com justa causa", "pedido de demissao", "acordo"],
                help="Escolha o tipo de rescisão"
            )

            st.divider()
            st.subheader("💰 Verbas Rescisórias")

            col1, col2, col3 = st.columns(3)

            with col1:
                saldo_salario = st.number_input("Saldo de Salário (R$)", min_value=0.0, value=1666.67, step=10.0)
                aviso_previo = st.number_input("Aviso Prévio Indenizado (R$)", min_value=0.0, value=5000.0, step=100.0)
                ferias_vencidas = st.number_input("Férias Vencidas (R$)", min_value=0.0, value=0.0, step=100.0)

            with col2:
                ferias_proporcionais = st.number_input("Férias Proporcionais (R$)", min_value=0.0, value=4583.33, step=10.0)
                um_terco = st.number_input("1/3 sobre Férias (R$)", min_value=0.0, value=1527.78, step=10.0)
                decimo_terceiro = st.number_input("13º Proporcional (R$)", min_value=0.0, value=4583.33, step=10.0)

            with col3:
                multa_fgts = st.number_input("Multa 40% FGTS (R$)", min_value=0.0, value=11680.0, step=100.0)
                saldo_fgts = st.number_input("Saldo FGTS (R$)", min_value=0.0, value=29200.0, step=100.0)

            st.divider()
            st.subheader("➖ Descontos")

            col1, col2, col3 = st.columns(3)

            with col1:
                inss = st.number_input("INSS (R$)", min_value=0.0, value=835.22, step=10.0)

            with col2:
                irrf = st.number_input("IRRF (R$)", min_value=0.0, value=427.37, step=10.0)

            with col3:
                desc_aviso_previo = st.number_input("Desconto Aviso Prévio (R$)", min_value=0.0, value=0.0, step=10.0)

            st.divider()
            observacoes = st.text_area(
                "Observações",
                value="",
                help="Observações adicionais sobre a rescisão"
            )

            submitted = st.form_submit_button("🔍 Analisar Rescisão", type="primary", use_container_width=True)

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

    # Exibir análise se houver rescisão
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
            st.metric(
                "Total de Verbas",
                totais['total_verbas_formatado'],
                delta=None,
                delta_color="normal"
            )

        with col2:
            st.metric(
                "Total de Descontos",
                totais['total_descontos_formatado'],
                delta=None,
                delta_color="normal"
            )

        with col3:
            st.metric(
                "💰 Valor Líquido a Receber",
                totais['valor_liquido_formatado'],
                delta=None,
                delta_color="normal"
            )

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
            <p><strong>Labor Termination Analyzer</strong> v1.0.0</p>
            <p>Aplicativo para análise de rescisões trabalhistas</p>
            <p><em>Este documento tem caráter informativo e explicativo.</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
