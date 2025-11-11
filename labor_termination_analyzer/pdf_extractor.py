"""
Extrator de dados de PDFs de rescisão trabalhista - VERSÃO MELHORADA
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from decimal import Decimal
from datetime import date, datetime

import pdfplumber
from PIL import Image

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


class PDFExtractor:
    """Extrator inteligente de dados de rescisões trabalhistas em PDF"""

    # Padrões de regex para extração
    PATTERNS = {
        'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
        'data': r'\b\d{2}[/\-\.]\d{2}[/\-\.]\d{4}\b',
        'moeda': r'R?\$?\s*\d{1,3}(?:[.,]\d{3})*[.,]\d{2}',
        'valor_numerico': r'\d{1,3}(?:[.,]\d{3})*[.,]\d{2}',
    }

    # Palavras-chave expandidas para identificar campos
    KEYWORDS = {
        'nome': [
            'nome', 'empregado', 'funcionário', 'funcionario', 'trabalhador',
            'nome completo', 'nome do empregado', 'nome do funcionário'
        ],
        'cpf': ['cpf', 'cadastro', 'cadastro de pessoa'],
        'cargo': ['cargo', 'função', 'funcao', 'ocupação', 'ocupacao', 'atividade'],
        'data_admissao': [
            'admissão', 'admissao', 'data de admissão', 'data admissão',
            'inicio', 'início', 'data de início', 'entrada'
        ],
        'data_demissao': [
            'demissão', 'demissao', 'desligamento', 'rescisão', 'rescisao',
            'data de demissão', 'data demissão', 'saída', 'saida', 'término', 'termino'
        ],
        'salario': [
            'salário', 'salario', 'remuneração', 'remuneracao',
            'salário bruto', 'salario bruto', 'valor do salário'
        ],
        'saldo_salario': [
            'saldo de salário', 'saldo salário', 'saldo sal',
            'salário dias trabalhados', 'dias trabalhados'
        ],
        'aviso_previo': [
            'aviso prévio', 'aviso previo', 'aviso',
            'aviso prévio indenizado', 'indenização aviso'
        ],
        'ferias_vencidas': [
            'férias vencidas', 'ferias vencidas', 'férias integral',
            'férias não gozadas'
        ],
        'ferias_proporcionais': [
            'férias proporcionais', 'ferias proporcionais',
            'férias proporcional', 'prop férias'
        ],
        'um_terco': [
            '1/3', 'terço', 'adicional férias', 'adicional ferias',
            '1/3 férias', 'um terço', 'terço constitucional'
        ],
        'decimo_terceiro': [
            '13º', '13o', 'décimo terceiro', 'decimo terceiro',
            '13º salário', '13º proporcional', 'décimo terceiro proporcional'
        ],
        'fgts': [
            'fgts', 'fundo de garantia', 'saldo fgts',
            'fundo garantia tempo serviço'
        ],
        'multa_fgts': [
            'multa', '40%', 'multa fgts', '40% fgts',
            'multa 40', 'indenização fgts'
        ],
        'inss': [
            'inss', 'previdência', 'previdencia',
            'contribuição previdenciária', 'inss desconto'
        ],
        'irrf': [
            'irrf', 'imposto de renda', 'ir', 'imposto renda',
            'ir retido', 'imposto retido'
        ],
    }

    def __init__(self):
        """Inicializa o extrator"""
        self.texto_completo = ""
        self.tabelas = []
        self.dados_extraidos = {}

    def extrair_de_pdf(self, pdf_path: Union[str, Path], usar_ocr: bool = False) -> Dict[str, Any]:
        """
        Extrai dados de um PDF de rescisão trabalhista

        Args:
            pdf_path: Caminho para o arquivo PDF
            usar_ocr: Se True, usa OCR para PDFs escaneados

        Returns:
            Dicionário com dados extraídos
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

        # Tentar extração normal primeiro
        texto, tabelas = self._extrair_texto_e_tabelas_pdfplumber(pdf_path)

        # Salvar tabelas
        self.tabelas = tabelas

        # Se não conseguiu extrair muito texto, tentar OCR
        if len(texto.strip()) < 100 and usar_ocr:
            if not OCR_AVAILABLE or not PDF2IMAGE_AVAILABLE:
                raise ImportError(
                    "Para usar OCR, instale: pip install pytesseract pdf2image\n"
                    "E instale o Tesseract OCR no sistema."
                )
            texto = self._extrair_texto_ocr(pdf_path)

        self.texto_completo = texto

        # Extrair dados estruturados
        self.dados_extraidos = self._extrair_campos(texto, tabelas)

        return self.dados_extraidos

    def _extrair_texto_e_tabelas_pdfplumber(self, pdf_path: Path) -> Tuple[str, List]:
        """Extrai texto E tabelas usando pdfplumber"""
        texto = ""
        tabelas = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extrair texto
                page_text = page.extract_text() or ""
                texto += page_text + "\n"

                # Extrair tabelas
                page_tables = page.extract_tables()
                if page_tables:
                    tabelas.extend(page_tables)

        return texto, tabelas

    def _extrair_texto_ocr(self, pdf_path: Path) -> str:
        """Extrai texto usando OCR (para PDFs escaneados)"""
        texto = ""

        # Converter PDF para imagens
        images = convert_from_path(pdf_path)

        # Aplicar OCR em cada página
        for image in images:
            texto += pytesseract.image_to_string(image, lang='por')
            texto += "\n"

        return texto

    def _extrair_campos(self, texto: str, tabelas: List) -> Dict[str, Any]:
        """Extrai campos específicos do texto e tabelas"""
        dados = {
            'funcionario': {},
            'tipo_rescisao': '',
            'verbas': {},
            'descontos': {},
        }

        # Normalizar texto
        texto_lower = texto.lower()
        linhas = texto.split('\n')

        # 1. Extrair de tabelas primeiro (mais estruturado)
        if tabelas:
            self._extrair_de_tabelas(tabelas, dados)

        # 2. Extrair CPF
        cpf_matches = re.findall(self.PATTERNS['cpf'], texto)
        if cpf_matches:
            dados['funcionario']['cpf'] = cpf_matches[0]

        # 3. Extrair datas
        datas = re.findall(self.PATTERNS['data'], texto)
        if len(datas) >= 2:
            # Tentar identificar qual é admissão e qual é demissão
            dados_com_contexto = []
            for i, linha in enumerate(linhas):
                for data in datas:
                    if data in linha:
                        dados_com_contexto.append((data, linha.lower()))

            for data, contexto in dados_com_contexto:
                if any(kw in contexto for kw in self.KEYWORDS['data_admissao']):
                    dados['funcionario']['data_admissao'] = data
                elif any(kw in contexto for kw in self.KEYWORDS['data_demissao']):
                    dados['funcionario']['data_demissao'] = data

            # Se não identificou por contexto, usa as duas primeiras
            if not dados['funcionario'].get('data_admissao') and len(datas) >= 1:
                dados['funcionario']['data_admissao'] = datas[0]
            if not dados['funcionario'].get('data_demissao') and len(datas) >= 2:
                dados['funcionario']['data_demissao'] = datas[1]

        # 4. Extrair campos linha por linha
        for i, linha in enumerate(linhas):
            linha_lower = linha.lower()
            linha_original = linha.strip()

            # Nome
            if not dados['funcionario'].get('nome'):
                if any(kw in linha_lower for kw in self.KEYWORDS['nome']):
                    nome = self._extrair_valor_apos_keyword(linha_original, self.KEYWORDS['nome'])
                    if nome and len(nome) > 3 and not any(char.isdigit() for char in nome):
                        dados['funcionario']['nome'] = nome

            # Cargo
            if not dados['funcionario'].get('cargo'):
                if any(kw in linha_lower for kw in self.KEYWORDS['cargo']):
                    cargo = self._extrair_valor_apos_keyword(linha_original, self.KEYWORDS['cargo'])
                    if cargo and len(cargo) > 2:
                        dados['funcionario']['cargo'] = cargo

            # Salário
            if not dados['funcionario'].get('salario_bruto'):
                if any(kw in linha_lower for kw in self.KEYWORDS['salario']):
                    valor = self._extrair_valor_monetario(linha)
                    if valor:
                        dados['funcionario']['salario_bruto'] = valor

            # Verbas e descontos
            self._extrair_verbas_e_descontos_linha(linha, linha_lower, dados)

        # 5. Determinar tipo de rescisão
        dados['tipo_rescisao'] = self._identificar_tipo_rescisao(texto_lower)

        # 6. Preencher campos vazios com valores padrão
        self._preencher_campos_vazios(dados)

        return dados

    def _extrair_de_tabelas(self, tabelas: List, dados: Dict):
        """Extrai dados das tabelas do PDF"""
        for tabela in tabelas:
            for linha in tabela:
                if not linha or len(linha) < 2:
                    continue

                # Primeira coluna geralmente é o label, segunda o valor
                label = str(linha[0]).lower() if linha[0] else ""
                valor = str(linha[1]) if len(linha) > 1 and linha[1] else ""

                # Tentar identificar o campo
                for campo, keywords in self.KEYWORDS.items():
                    if any(kw in label for kw in keywords):
                        # É uma verba ou desconto?
                        if campo in ['saldo_salario', 'aviso_previo', 'ferias_vencidas',
                                   'ferias_proporcionais', 'um_terco', 'decimo_terceiro',
                                   'fgts', 'multa_fgts']:
                            valor_monetario = self._extrair_valor_monetario(valor)
                            if valor_monetario:
                                dados['verbas'][campo] = valor_monetario

                        elif campo in ['inss', 'irrf']:
                            valor_monetario = self._extrair_valor_monetario(valor)
                            if valor_monetario:
                                dados['descontos'][campo] = valor_monetario

                        elif campo == 'nome':
                            if valor and len(valor) > 3:
                                dados['funcionario']['nome'] = valor.strip()

                        elif campo == 'cargo':
                            if valor and len(valor) > 2:
                                dados['funcionario']['cargo'] = valor.strip()

                        elif campo == 'salario':
                            valor_monetario = self._extrair_valor_monetario(valor)
                            if valor_monetario:
                                dados['funcionario']['salario_bruto'] = valor_monetario

    def _extrair_verbas_e_descontos_linha(self, linha: str, linha_lower: str, dados: Dict):
        """Extrai verbas e descontos de uma linha"""
        # Verificar verbas
        for campo in ['saldo_salario', 'aviso_previo', 'ferias_vencidas',
                     'ferias_proporcionais', 'um_terco', 'decimo_terceiro',
                     'fgts', 'multa_fgts']:
            if campo not in dados['verbas'] or dados['verbas'][campo] == '0.00':
                if any(kw in linha_lower for kw in self.KEYWORDS[campo]):
                    valor = self._extrair_valor_monetario(linha)
                    if valor:
                        dados['verbas'][campo] = valor

        # Verificar descontos
        for campo in ['inss', 'irrf']:
            if campo not in dados['descontos'] or dados['descontos'][campo] == '0.00':
                if any(kw in linha_lower for kw in self.KEYWORDS[campo]):
                    valor = self._extrair_valor_monetario(linha)
                    if valor:
                        dados['descontos'][campo] = valor

    def _extrair_valor_apos_keyword(self, linha: str, keywords: List[str]) -> Optional[str]:
        """Extrai valor que vem após uma palavra-chave"""
        linha_lower = linha.lower()

        for keyword in keywords:
            if keyword in linha_lower:
                # Encontrar posição da keyword
                pos = linha_lower.find(keyword)
                # Pegar o que vem depois
                resto = linha[pos + len(keyword):].strip()

                # Remover caracteres comuns de separação
                resto = resto.lstrip(':').lstrip('-').lstrip('_').strip()

                # Pegar até o próximo separador ou fim da linha
                valor = resto.split('  ')[0]  # Múltiplos espaços
                valor = valor.split('\t')[0]  # Tab
                valor = valor.split('|')[0]   # Pipe

                return valor.strip() if valor else None

        return None

    def _extrair_valor_monetario(self, texto: str) -> Optional[str]:
        """Extrai valor monetário de um texto"""
        # Buscar padrão de moeda
        match = re.search(self.PATTERNS['moeda'], texto)
        if match:
            valor_str = match.group()
            # Limpar e normalizar
            valor_str = re.sub(r'[R$\s]', '', valor_str)
            # Substituir separadores
            if ',' in valor_str and '.' in valor_str:
                # Formato brasileiro: 1.234,56
                valor_str = valor_str.replace('.', '').replace(',', '.')
            elif ',' in valor_str:
                # Pode ser 1234,56 ou 1,234.56
                if valor_str.count(',') == 1 and valor_str.index(',') >= len(valor_str) - 3:
                    # É vírgula decimal: 1234,56
                    valor_str = valor_str.replace(',', '.')
                else:
                    # É vírgula de milhares
                    valor_str = valor_str.replace(',', '')

            try:
                # Validar se é um número válido
                float(valor_str)
                return valor_str
            except ValueError:
                pass

        return None

    def _identificar_tipo_rescisao(self, texto: str) -> str:
        """Identifica o tipo de rescisão pelo texto"""
        texto = texto.lower()

        # Contar menções de cada tipo
        scores = {
            'sem justa causa': 0,
            'com justa causa': 0,
            'pedido de demissao': 0,
            'acordo': 0
        }

        if 'sem justa causa' in texto or 'dispensa sem justa' in texto:
            scores['sem justa causa'] += 3
        if 'com justa causa' in texto or 'dispensa com justa' in texto:
            scores['com justa causa'] += 3
        if 'pedido' in texto and ('demissão' in texto or 'demissao' in texto):
            scores['pedido de demissao'] += 2
        if 'acordo' in texto or 'comum acordo' in texto:
            scores['acordo'] += 2

        # Indicadores indiretos
        if 'multa' in texto and 'fgts' in texto and '40' in texto:
            scores['sem justa causa'] += 1
        if 'seguro desemprego' in texto or 'seguro-desemprego' in texto:
            scores['sem justa causa'] += 1

        # Retornar o tipo com maior score
        tipo = max(scores.items(), key=lambda x: x[1])[0]

        # Se todos zerados, usar padrão
        if scores[tipo] == 0:
            return 'sem justa causa'

        return tipo

    def _preencher_campos_vazios(self, dados: Dict):
        """Preenche campos que não foram identificados com valores padrão"""
        if not dados['funcionario'].get('nome'):
            dados['funcionario']['nome'] = '[Não identificado - Preencha manualmente]'
        if not dados['funcionario'].get('cpf'):
            dados['funcionario']['cpf'] = '000.000.000-00'
        if not dados['funcionario'].get('cargo'):
            dados['funcionario']['cargo'] = '[Não identificado - Preencha manualmente]'
        if not dados['funcionario'].get('data_admissao'):
            dados['funcionario']['data_admissao'] = '01/01/2020'
        if not dados['funcionario'].get('data_demissao'):
            dados['funcionario']['data_demissao'] = date.today().strftime('%d/%m/%Y')
        if not dados['funcionario'].get('salario_bruto'):
            dados['funcionario']['salario_bruto'] = '0.00'

        # Garantir que campos de verbas existam
        for campo in ['saldo_salario', 'aviso_previo_indenizado', 'ferias_vencidas',
                     'ferias_proporcionais', 'um_terco_ferias', 'decimo_terceiro_proporcional',
                     'multa_fgts_40', 'saldo_fgts']:
            campo_key = campo.replace('_indenizado', '').replace('_40', '').replace('_ferias', '')
            if campo_key not in dados['verbas']:
                dados['verbas'][campo_key] = '0.00'

        # Renomear campos para match do parser
        if 'aviso_previo' in dados['verbas']:
            dados['verbas']['aviso_previo_indenizado'] = dados['verbas'].pop('aviso_previo')
        if 'um_terco' in dados['verbas']:
            dados['verbas']['um_terco_ferias'] = dados['verbas'].pop('um_terco')
        if 'decimo_terceiro' in dados['verbas']:
            dados['verbas']['decimo_terceiro_proporcional'] = dados['verbas'].pop('decimo_terceiro')
        if 'multa_fgts' in dados['verbas']:
            dados['verbas']['multa_fgts_40'] = dados['verbas'].pop('multa_fgts')
        if 'fgts' in dados['verbas']:
            dados['verbas']['saldo_fgts'] = dados['verbas'].pop('fgts')

        # Garantir que campos de descontos existam
        for campo in ['inss', 'irrf', 'aviso_previo_indenizado']:
            if campo not in dados['descontos']:
                dados['descontos'][campo] = '0.00'

    def obter_texto_completo(self) -> str:
        """Retorna o texto completo extraído do PDF"""
        return self.texto_completo

    def obter_tabelas(self) -> List:
        """Retorna as tabelas extraídas do PDF"""
        return self.tabelas

    def obter_dados_json(self) -> Dict[str, Any]:
        """Retorna dados no formato esperado pelo parser"""
        if not self.dados_extraidos:
            return {}

        return {
            'funcionario': self.dados_extraidos.get('funcionario', {}),
            'tipo_rescisao': self.dados_extraidos.get('tipo_rescisao', 'sem justa causa'),
            'verbas': self.dados_extraidos.get('verbas', {}),
            'descontos': self.dados_extraidos.get('descontos', {}),
            'observacoes': 'Dados extraídos automaticamente de PDF. ⚠️ IMPORTANTE: Revise todos os valores antes de usar!'
        }
