"""
Extrator de dados de PDFs de rescisão trabalhista
"""

import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
from datetime import date

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
    """Extrator de dados de rescisões trabalhistas em PDF"""

    # Padrões de regex para extração
    PATTERNS = {
        'cpf': r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
        'data': r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',
        'moeda': r'R\$?\s*\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})',
        'valor': r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})',
    }

    # Palavras-chave para identificar campos
    KEYWORDS = {
        'nome': ['nome', 'empregado', 'funcionário', 'trabalhador'],
        'cpf': ['cpf', 'cadastro'],
        'cargo': ['cargo', 'função', 'ocupação'],
        'data_admissao': ['admissão', 'admissao', 'data de admissão', 'inicio'],
        'data_demissao': ['demissão', 'demissao', 'desligamento', 'rescisão', 'rescisao'],
        'salario': ['salário', 'salario', 'remuneração', 'remuneracao'],
        'saldo_salario': ['saldo de salário', 'saldo salário', 'saldo sal'],
        'aviso_previo': ['aviso prévio', 'aviso previo', 'aviso'],
        'ferias_vencidas': ['férias vencidas', 'ferias vencidas'],
        'ferias_proporcionais': ['férias proporcionais', 'ferias proporcionais'],
        'um_terco': ['1/3', 'terço', 'adicional férias', 'adicional ferias'],
        'decimo_terceiro': ['13º', '13o', 'décimo terceiro', 'decimo terceiro'],
        'fgts': ['fgts', 'fundo de garantia'],
        'multa_fgts': ['multa', '40%', 'multa fgts'],
        'inss': ['inss', 'previdência', 'previdencia'],
        'irrf': ['irrf', 'imposto de renda', 'ir'],
    }

    def __init__(self):
        """Inicializa o extrator"""
        self.texto_completo = ""
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
        texto = self._extrair_texto_pdfplumber(pdf_path)

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
        self.dados_extraidos = self._extrair_campos(texto)

        return self.dados_extraidos

    def _extrair_texto_pdfplumber(self, pdf_path: Path) -> str:
        """Extrai texto usando pdfplumber"""
        texto = ""

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                texto += page.extract_text() or ""
                texto += "\n"

        return texto

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

    def _extrair_campos(self, texto: str) -> Dict[str, Any]:
        """Extrai campos específicos do texto"""
        dados = {
            'funcionario': {},
            'tipo_rescisao': '',
            'verbas': {},
            'descontos': {},
        }

        # Normalizar texto
        texto_lower = texto.lower()
        linhas = texto.split('\n')

        # Extrair CPF
        cpf_match = re.search(self.PATTERNS['cpf'], texto)
        if cpf_match:
            dados['funcionario']['cpf'] = cpf_match.group()

        # Extrair datas
        datas = re.findall(self.PATTERNS['data'], texto)
        if len(datas) >= 2:
            dados['funcionario']['data_admissao'] = datas[0]
            dados['funcionario']['data_demissao'] = datas[1] if len(datas) > 1 else datas[0]

        # Extrair valores monetários e associar aos campos
        valores_encontrados = self._extrair_valores_com_contexto(texto)

        # Tentar identificar campos específicos
        for linha in linhas:
            linha_lower = linha.lower()

            # Nome (geralmente primeira linha com texto significativo)
            if not dados['funcionario'].get('nome'):
                if any(kw in linha_lower for kw in self.KEYWORDS['nome']):
                    # Extrair o nome após a palavra-chave
                    for kw in self.KEYWORDS['nome']:
                        if kw in linha_lower:
                            partes = linha.split(kw, 1)
                            if len(partes) > 1:
                                nome_candidato = partes[1].strip(':').strip()
                                if nome_candidato and len(nome_candidato) > 3:
                                    dados['funcionario']['nome'] = nome_candidato
                                    break

            # Cargo
            if not dados['funcionario'].get('cargo'):
                if any(kw in linha_lower for kw in self.KEYWORDS['cargo']):
                    for kw in self.KEYWORDS['cargo']:
                        if kw in linha_lower:
                            partes = linha.split(kw, 1)
                            if len(partes) > 1:
                                cargo = partes[1].strip(':').strip()
                                if cargo and len(cargo) > 2:
                                    dados['funcionario']['cargo'] = cargo
                                    break

            # Salário
            if not dados['funcionario'].get('salario_bruto'):
                if any(kw in linha_lower for kw in self.KEYWORDS['salario']):
                    valor = self._extrair_valor_linha(linha)
                    if valor:
                        dados['funcionario']['salario_bruto'] = valor

        # Atribuir valores encontrados aos campos de verbas e descontos
        for campo, valor in valores_encontrados.items():
            if campo in ['saldo_salario', 'aviso_previo', 'ferias_vencidas',
                        'ferias_proporcionais', 'um_terco', 'decimo_terceiro', 'fgts', 'multa_fgts']:
                dados['verbas'][campo] = valor
            elif campo in ['inss', 'irrf']:
                dados['descontos'][campo] = valor

        # Determinar tipo de rescisão
        dados['tipo_rescisao'] = self._identificar_tipo_rescisao(texto_lower)

        # Preencher campos vazios com valores padrão
        if not dados['funcionario'].get('nome'):
            dados['funcionario']['nome'] = 'Nome não identificado'
        if not dados['funcionario'].get('cpf'):
            dados['funcionario']['cpf'] = '000.000.000-00'
        if not dados['funcionario'].get('cargo'):
            dados['funcionario']['cargo'] = 'Cargo não identificado'
        if not dados['funcionario'].get('data_admissao'):
            dados['funcionario']['data_admissao'] = '01/01/2020'
        if not dados['funcionario'].get('data_demissao'):
            dados['funcionario']['data_demissao'] = date.today().strftime('%d/%m/%Y')
        if not dados['funcionario'].get('salario_bruto'):
            dados['funcionario']['salario_bruto'] = '0.00'

        return dados

    def _extrair_valores_com_contexto(self, texto: str) -> Dict[str, str]:
        """Extrai valores monetários e tenta associar ao campo correto"""
        valores = {}
        linhas = texto.split('\n')

        for linha in linhas:
            linha_lower = linha.lower()

            # Para cada tipo de campo, verificar se está na linha
            for campo, keywords in self.KEYWORDS.items():
                if campo in ['nome', 'cpf', 'cargo', 'data_admissao', 'data_demissao', 'salario']:
                    continue  # Já tratados separadamente

                for keyword in keywords:
                    if keyword in linha_lower:
                        valor = self._extrair_valor_linha(linha)
                        if valor:
                            valores[campo] = valor
                            break

        return valores

    def _extrair_valor_linha(self, linha: str) -> Optional[str]:
        """Extrai valor monetário de uma linha"""
        # Buscar padrão de moeda
        match = re.search(self.PATTERNS['moeda'], linha)
        if match:
            valor_str = match.group()
            # Limpar e normalizar
            valor_str = valor_str.replace('R$', '').replace('R', '').strip()
            valor_str = valor_str.replace('.', '').replace(',', '.')
            return valor_str

        # Buscar padrão de número simples
        match = re.search(self.PATTERNS['valor'], linha)
        if match:
            valor_str = match.group()
            valor_str = valor_str.replace('.', '').replace(',', '.')
            return valor_str

        return None

    def _identificar_tipo_rescisao(self, texto: str) -> str:
        """Identifica o tipo de rescisão pelo texto"""
        texto = texto.lower()

        if 'sem justa causa' in texto or 'dispensa sem justa' in texto:
            return 'sem justa causa'
        elif 'com justa causa' in texto or 'dispensa com justa' in texto:
            return 'com justa causa'
        elif 'pedido' in texto and ('demissão' in texto or 'demissao' in texto):
            return 'pedido de demissao'
        elif 'acordo' in texto or 'comum acordo' in texto:
            return 'acordo'
        else:
            return 'sem justa causa'  # Padrão mais comum

    def obter_texto_completo(self) -> str:
        """Retorna o texto completo extraído do PDF"""
        return self.texto_completo

    def obter_dados_json(self) -> Dict[str, Any]:
        """Retorna dados no formato esperado pelo parser"""
        if not self.dados_extraidos:
            return {}

        return {
            'funcionario': self.dados_extraidos.get('funcionario', {}),
            'tipo_rescisao': self.dados_extraidos.get('tipo_rescisao', 'sem justa causa'),
            'verbas': self.dados_extraidos.get('verbas', {}),
            'descontos': self.dados_extraidos.get('descontos', {}),
            'observacoes': 'Dados extraídos automaticamente de PDF. Verifique a precisão das informações.'
        }
