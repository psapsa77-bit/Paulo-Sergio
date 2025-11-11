"""
Interface Web com Streamlit para análise de rescisões trabalhistas.

Interface gráfica completa e intuitiva para usuários não-técnicos.
"""

import streamlit as st
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import json
import tempfile
from typing import Optional, Any

# Imports locais
from .models import Funcionario, Rescisao
from .parser import RescisaoParser
from .pdf_extractor import PDFExtractor
from .analyzer import RescisaoAnalyzer
from .generators import HTMLGenerator, PDFGenerator


def configurar_pagina():
    """Configura a página Streamlit."""
    st.set_page_config(
        page_title="Analisador de Rescisões Trabalhistas",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS customizado
    st.markdown("""
        <style>
        .main-title {
            font-size: 3em;
            color: #2c3e50;
            text-align: center;
            margin-bottom: 0.5em;
        }
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 2em;
        }
        .stButton>button {
            width: 100%;
            background-color: #3498db;
            color: white;
            font-weight: bold;
            padding: 0.75em;
            border-radius: 8px;
        }
        .success-box {
            padding: 1em;
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            border-radius: 4px;
            margin: 1em 0;
        }
        .warning-box {
            padding: 1em;
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            margin: 1em 0;
        }
        .error-box {
            padding: 1em;
            background-color: #f8d7da;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
            margin: 1em 0;
        }
        </style>
    """, unsafe_allow_html=True)


def extrair_de_pdf(arquivo_pdf, usar_ocr: bool = False) -> tuple[Optional[dict], list[str]]:
    """
    Extrai dados de um PDF.

    Returns:
        Tupla (dados_extraidos, campos_faltantes)
    """
    try:
        # Salva arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(arquivo_pdf.read())
            tmp_path = tmp.name

        # Extrai dados
        extractor = PDFExtractor(usar_ocr=usar_ocr)
        dados, campos_faltantes = extractor.extrair_e_validar(tmp_path)

        # Remove arquivo temporário
        Path(tmp_path).unlink()

        return dados, campos_faltantes

    except Exception as e:
        st.error(f'Erro ao extrair PDF: {e}')
        return None, []


def formulario_funcionario(dados_iniciais: dict = None) -> Optional[Funcionario]:
    """
    Exibe formulário para dados do funcionário.

    Args:
        dados_iniciais: Dados pré-preenchidos (opcional)

    Returns:
        Objeto Funcionario ou None se inválido
    """
    dados = dados_iniciais or {}

    col1, col2, col3 = st.columns(3)

    with col1:
        nome = st.text_input(
            'Nome Completo *',
            value=dados.get('nome', ''),
            help='Nome completo do funcionário'
        )

        cpf = st.text_input(
            'CPF *',
            value=dados.get('cpf', ''),
            help='CPF no formato XXX.XXX.XXX-XX',
            placeholder='000.000.000-00'
        )

    with col2:
        cargo = st.text_input(
            'Cargo *',
            value=dados.get('cargo', ''),
            help='Cargo ou função exercida'
        )

        salario_str = st.text_input(
            'Salário Bruto (R$) *',
            value=str(dados.get('salario_bruto', '')),
            help='Salário mensal bruto',
            placeholder='0000.00'
        )

    with col3:
        data_admissao_default = dados.get('data_admissao', date.today())
        if isinstance(data_admissao_default, str):
            data_admissao_default = datetime.strptime(data_admissao_default, '%Y-%m-%d').date()

        data_admissao = st.date_input(
            'Data de Admissão *',
            value=data_admissao_default,
            help='Data de entrada na empresa'
        )

        data_demissao_default = dados.get('data_demissao', date.today())
        if isinstance(data_demissao_default, str):
            data_demissao_default = datetime.strptime(data_demissao_default, '%Y-%m-%d').date()

        data_demissao = st.date_input(
            'Data de Demissão *',
            value=data_demissao_default,
            help='Data de saída da empresa'
        )

    # Validação básica
    if not all([nome, cpf, cargo, salario_str]):
        return None

    try:
        salario = Decimal(salario_str.replace(',', '.'))
        funcionario = Funcionario(
            nome=nome,
            cpf=cpf,
            cargo=cargo,
            data_admissao=data_admissao,
            data_demissao=data_demissao,
            salario_bruto=salario
        )
        return funcionario
    except Exception as e:
        st.error(f'Erro nos dados do funcionário: {e}')
        return None


def formulario_verbas_descontos(dados_iniciais: dict = None) -> tuple[dict[str, Decimal], dict[str, Decimal]]:
    """
    Exibe formulários para verbas e descontos.

    Returns:
        Tupla (verbas, descontos)
    """
    dados = dados_iniciais or {'verbas': {}, 'descontos': {}}

    # Verbas
    st.subheader('💰 Verbas Rescisórias (Valores a Receber)')

    verbas_padrao = [
        'Saldo de Salário',
        'Aviso Prévio Indenizado',
        'Férias Vencidas + 1/3',
        'Férias Proporcionais + 1/3',
        '13º Salário Proporcional',
        'Multa 40% FGTS',
    ]

    verbas = {}
    cols_verbas = st.columns(3)

    for i, verba_nome in enumerate(verbas_padrao):
        with cols_verbas[i % 3]:
            valor_inicial = dados.get('verbas', {}).get(verba_nome, '')
            valor_str = st.text_input(
                f'{verba_nome} (R$)',
                value=str(valor_inicial) if valor_inicial else '',
                key=f'verba_{i}',
                placeholder='0.00'
            )
            if valor_str:
                try:
                    verbas[verba_nome] = Decimal(valor_str.replace(',', '.'))
                except:
                    pass

    # Verbas adicionais
    with st.expander('➕ Adicionar Outras Verbas'):
        num_verbas_extras = st.number_input('Número de verbas adicionais', min_value=0, max_value=10, value=0)
        for i in range(num_verbas_extras):
            col1, col2 = st.columns([2, 1])
            with col1:
                nome_extra = st.text_input(f'Nome da verba {i+1}', key=f'verba_extra_nome_{i}')
            with col2:
                valor_extra = st.text_input(f'Valor (R$) {i+1}', key=f'verba_extra_valor_{i}', placeholder='0.00')

            if nome_extra and valor_extra:
                try:
                    verbas[nome_extra] = Decimal(valor_extra.replace(',', '.'))
                except:
                    pass

    st.divider()

    # Descontos
    st.subheader('➖ Descontos')

    descontos_padrao = [
        'INSS',
        'IRRF',
        'Aviso Prévio Descontado',
    ]

    descontos = {}
    cols_descontos = st.columns(3)

    for i, desconto_nome in enumerate(descontos_padrao):
        with cols_descontos[i % 3]:
            valor_inicial = dados.get('descontos', {}).get(desconto_nome, '')
            valor_str = st.text_input(
                f'{desconto_nome} (R$)',
                value=str(valor_inicial) if valor_inicial else '',
                key=f'desconto_{i}',
                placeholder='0.00'
            )
            if valor_str:
                try:
                    descontos[desconto_nome] = Decimal(valor_str.replace(',', '.'))
                except:
                    pass

    # Descontos adicionais
    with st.expander('➕ Adicionar Outros Descontos'):
        num_descontos_extras = st.number_input('Número de descontos adicionais', min_value=0, max_value=10, value=0)
        for i in range(num_descontos_extras):
            col1, col2 = st.columns([2, 1])
            with col1:
                nome_extra = st.text_input(f'Nome do desconto {i+1}', key=f'desconto_extra_nome_{i}')
            with col2:
                valor_extra = st.text_input(f'Valor (R$) {i+1}', key=f'desconto_extra_valor_{i}', placeholder='0.00')

            if nome_extra and valor_extra:
                try:
                    descontos[nome_extra] = Decimal(valor_extra.replace(',', '.'))
                except:
                    pass

    return verbas, descontos


def exibir_analise(rescisao: Rescisao):
    """Exibe análise completa da rescisão."""
    analyzer = RescisaoAnalyzer(rescisao)
    resumo = analyzer.gerar_resumo_completo()

    # Totais em destaque
    st.markdown('### 💰 Resumo Financeiro')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label='Total de Verbas',
            value=f"R$ {resumo['totais']['verbas']:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'),
            delta=None,
            delta_color='normal'
        )

    with col2:
        st.metric(
            label='Total de Descontos',
            value=f"R$ {resumo['totais']['descontos']:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'),
            delta=None,
            delta_color='inverse'
        )

    with col3:
        st.metric(
            label='VALOR LÍQUIDO',
            value=f"R$ {resumo['totais']['liquido']:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.'),
            delta=None,
            delta_color='normal'
        )

    st.divider()

    # Gráficos
    try:
        import plotly.graph_objects as go
        import plotly.express as px

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de pizza - Verbas
            if resumo['verbas']:
                st.markdown('#### Distribuição de Verbas')
                labels_verbas = [v['nome'] for v in resumo['verbas']]
                values_verbas = [float(v['valor']) for v in resumo['verbas']]

                fig_verbas = go.Figure(data=[go.Pie(
                    labels=labels_verbas,
                    values=values_verbas,
                    hole=.3,
                    marker=dict(colors=px.colors.sequential.Greens_r)
                )])
                fig_verbas.update_layout(height=400)
                st.plotly_chart(fig_verbas, use_container_width=True)

        with col2:
            # Gráfico de barras - Comparativo
            st.markdown('#### Comparativo Verbas vs Descontos')
            categorias = []
            valores = []

            for verba in resumo['verbas']:
                categorias.append(verba['nome'])
                valores.append(float(verba['valor']))

            for desconto in resumo['descontos']:
                categorias.append(f"{desconto['nome']} (Desconto)")
                valores.append(-float(desconto['valor']))

            fig_comparativo = go.Figure(data=[
                go.Bar(
                    x=categorias,
                    y=valores,
                    marker_color=['green' if v > 0 else 'red' for v in valores]
                )
            ])
            fig_comparativo.update_layout(
                height=400,
                xaxis_tickangle=-45,
                showlegend=False,
                yaxis_title='Valor (R$)'
            )
            st.plotly_chart(fig_comparativo, use_container_width=True)

    except ImportError:
        st.warning('Plotly não disponível para gráficos interativos.')

    st.divider()

    # Tipo de rescisão e direitos
    st.markdown('### 📋 Tipo de Rescisão e Direitos')

    direitos = resumo['direitos_tipo_rescisao']

    st.info(f"**{direitos['nome']}**: {direitos['descricao']}")

    if direitos.get('direitos'):
        with st.expander('✅ Direitos neste tipo de rescisão', expanded=True):
            for direito in direitos['direitos']:
                st.write(f"- {direito}")

    if direitos.get('perdas'):
        with st.expander('⚠️ Perdas neste tipo de rescisão'):
            for perda in direitos['perdas']:
                st.write(f"- {perda}")

    if direitos.get('observacoes'):
        with st.expander('📌 Observações importantes'):
            for obs in direitos['observacoes']:
                st.write(f"- {obs}")

    st.divider()

    # Verbas detalhadas
    st.markdown('### 💵 Verbas Detalhadas com Explicações')

    for verba in resumo['verbas']:
        with st.expander(f"{verba['nome']} - R$ {float(verba['valor']):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')):
            expl = verba['explicacao']

            st.markdown(f"**💡 O que é?**")
            st.write(expl['o_que_e'])

            st.markdown(f"**📚 Base Legal**")
            st.write(expl['base_legal'])

            st.markdown(f"**🧮 Como é calculado**")
            st.code(expl['calculo'])

            st.markdown(f"**📋 Quando se aplica**")
            st.write(expl['quando_aplica'])

    # Descontos detalhados
    if resumo['descontos']:
        st.markdown('### ➖ Descontos Detalhados com Explicações')

        for desconto in resumo['descontos']:
            with st.expander(f"{desconto['nome']} - R$ {float(desconto['valor']):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')):
                expl = desconto['explicacao']

                st.markdown(f"**💡 O que é?**")
                st.write(expl['o_que_e'])

                st.markdown(f"**📚 Base Legal**")
                st.write(expl['base_legal'])

                st.markdown(f"**🧮 Como é calculado**")
                st.code(expl['calculo'])

                st.markdown(f"**📋 Quando se aplica**")
                st.write(expl['quando_aplica'])

    # Alertas
    if resumo['alertas']:
        st.markdown('### ⚠️ Verificações e Alertas')

        for alerta in resumo['alertas']:
            tipo_icon = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❌'}
            icon = tipo_icon.get(alerta['tipo'], 'ℹ️')

            if alerta['tipo'] == 'error':
                st.error(f"{icon} **{alerta['campo']}**: {alerta['mensagem']}")
            elif alerta['tipo'] == 'warning':
                st.warning(f"{icon} **{alerta['campo']}**: {alerta['mensagem']}")
            else:
                st.info(f"{icon} **{alerta['campo']}**: {alerta['mensagem']}")

    # Observações
    if resumo['observacoes']:
        st.markdown('### 📝 Observações')
        st.info(resumo['observacoes'])


def main():
    """Função principal da aplicação Streamlit."""
    configurar_pagina()

    # Cabeçalho
    st.markdown('<h1 class="main-title">📋 Analisador de Rescisões Trabalhistas</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análise completa com explicações detalhadas e base legal</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header('⚙️ Opções')

        modo = st.radio(
            'Como deseja iniciar?',
            ['📄 Upload de Arquivo (PDF/JSON)', '✍️ Formulário Manual'],
            help='Escolha se quer importar dados ou preencher manualmente'
        )

        st.divider()

        # Tipo de rescisão
        tipo_rescisao = st.selectbox(
            'Tipo de Rescisão *',
            ['sem justa causa', 'com justa causa', 'pedido de demissao', 'acordo'],
            help='Selecione o tipo de rescisão contratual'
        )

        observacoes = st.text_area(
            'Observações',
            help='Observações adicionais sobre a rescisão',
            placeholder='Digite observações adicionais...'
        )

        st.divider()
        st.caption('Labor Termination Analyzer v2.0')

    # Área principal
    dados_extraidos = None

    if modo == '📄 Upload de Arquivo (PDF/JSON)':
        st.header('📤 Upload de Arquivo')

        tipo_arquivo = st.radio('Tipo de arquivo:', ['PDF', 'JSON'], horizontal=True)

        if tipo_arquivo == 'PDF':
            usar_ocr = st.checkbox(
                'Usar OCR (para PDFs escaneados)',
                help='Ativa reconhecimento óptico de caracteres para PDFs escaneados'
            )

            arquivo_pdf = st.file_uploader(
                'Selecione o arquivo PDF',
                type=['pdf'],
                help='Faça upload do PDF da rescisão trabalhista'
            )

            if arquivo_pdf:
                with st.spinner('Extraindo dados do PDF...'):
                    dados, campos_faltantes = extrair_de_pdf(arquivo_pdf, usar_ocr)

                    if dados:
                        st.success('✅ Dados extraídos com sucesso!')

                        if campos_faltantes:
                            st.warning(f'⚠️ Alguns campos não foram encontrados: {", ".join(campos_faltantes)}')
                            st.info('💡 Revise e complete os campos abaixo conforme necessário.')

                        dados_extraidos = dados
                    else:
                        st.error('❌ Não foi possível extrair dados do PDF.')

        else:  # JSON
            arquivo_json = st.file_uploader(
                'Selecione o arquivo JSON',
                type=['json'],
                help='Faça upload do arquivo JSON com dados da rescisão'
            )

            if arquivo_json:
                try:
                    conteudo = arquivo_json.read().decode('utf-8')
                    dados = json.loads(conteudo)
                    st.success('✅ JSON carregado com sucesso!')
                    dados_extraidos = dados
                except Exception as e:
                    st.error(f'❌ Erro ao ler JSON: {e}')

    # Formulário
    st.header('📝 Dados da Rescisão')

    with st.form('formulario_rescisao'):
        st.subheader('👤 Dados do Funcionário')

        funcionario_data = dados_extraidos.get('funcionario', {}) if dados_extraidos else {}
        funcionario = formulario_funcionario(funcionario_data)

        st.divider()

        verbas_descontos_data = dados_extraidos if dados_extraidos else {}
        verbas, descontos = formulario_verbas_descontos(verbas_descontos_data)

        # Botão de análise
        submitted = st.form_submit_button('🔍 Analisar Rescisão', use_container_width=True)

        if submitted:
            if funcionario and (verbas or descontos):
                try:
                    # Cria objeto Rescisao
                    rescisao = Rescisao(
                        funcionario=funcionario,
                        tipo_rescisao=tipo_rescisao,
                        verbas=verbas,
                        descontos=descontos,
                        observacoes=observacoes if observacoes else None
                    )

                    # Salva no session state
                    st.session_state['rescisao'] = rescisao
                    st.session_state['analise_realizada'] = True

                    st.success('✅ Rescisão analisada com sucesso!')

                except Exception as e:
                    st.error(f'❌ Erro ao criar rescisão: {e}')
            else:
                st.error('❌ Por favor, preencha todos os campos obrigatórios.')

    # Exibe análise se disponível
    if st.session_state.get('analise_realizada') and 'rescisao' in st.session_state:
        st.divider()
        st.header('📊 Análise Completa')

        rescisao = st.session_state['rescisao']

        # Exibe análise
        exibir_analise(rescisao)

        # Downloads
        st.divider()
        st.header('💾 Downloads')

        col1, col2, col3 = st.columns(3)

        with col1:
            # Download HTML
            try:
                html_gen = HTMLGenerator()
                html_content = html_gen.gerar(rescisao)

                st.download_button(
                    label='📄 Baixar Relatório HTML',
                    data=html_content,
                    file_name='rescisao_analise.html',
                    mime='text/html',
                    use_container_width=True
                )
            except Exception as e:
                st.error(f'Erro ao gerar HTML: {e}')

        with col2:
            # Download PDF
            if PDFGenerator.esta_disponivel():
                try:
                    pdf_gen = PDFGenerator()
                    pdf_bytes = pdf_gen.gerar(rescisao)

                    st.download_button(
                        label='📑 Baixar Relatório PDF',
                        data=pdf_bytes,
                        file_name='rescisao_analise.pdf',
                        mime='application/pdf',
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f'Erro ao gerar PDF: {e}')
            else:
                st.warning(PDFGenerator.obter_mensagem_erro())

        with col3:
            # Download JSON
            json_str = RescisaoParser.para_json(rescisao, indent=2)

            st.download_button(
                label='💾 Baixar Dados JSON',
                data=json_str,
                file_name='rescisao_dados.json',
                mime='application/json',
                use_container_width=True
            )


if __name__ == '__main__':
    main()
