"""
Extrator de dados de PDFs de rescisões trabalhistas.

Este módulo extrai automaticamente informações de PDFs usando
PyPDF2 para PDFs digitais e OCR (pytesseract) para PDFs escaneados.
"""

import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, Union, Any
import logging

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from .parser import RescisaoParser


logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Extrator de dados de PDFs de rescisões trabalhistas.

    Suporta extração de PDFs digitais e escaneados (com OCR).
    """

    # Palavras-chave para identificar campos
    KEYWORDS = {
        'nome': [
            r'nome\s*(?:do\s*)?(?:empregado|funcion[aá]rio|trabalhador)',
            r'empregado\s*:\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+)',
            r'nome\s*:\s*([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+)',
        ],
        'cpf': [
            r'cpf\s*[:\-]?\s*(\d{3}\.?\d{3}\.?\d{3}[\-\.]?\d{2})',
            r'(\d{3}\.?\d{3}\.?\d{3}[\-\.]?\d{2})',
        ],
        'cargo': [
            r'cargo\s*[:\-]?\s*([A-Za-zÀ-ú\s]+)',
            r'fun[çc][ãa]o\s*[:\-]?\s*([A-Za-zÀ-ú\s]+)',
        ],
        'admissao': [
            r'admiss[ãa]o\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'data\s*(?:de\s*)?admiss[ãa]o\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ],
        'demissao': [
            r'demiss[ãa]o\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'rescis[ãa]o\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'data\s*(?:de\s*)?(?:demiss[ãa]o|rescis[ãa]o)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ],
        'salario': [
            r'sal[aá]rio\s*(?:bruto)?\s*[:\-]?\s*r?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'remunera[çc][ãa]o\s*[:\-]?\s*r?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
        ],
    }

    # Palavras-chave para verbas rescisórias
    VERBAS_KEYWORDS = {
        'Saldo de Salário': [
            r'saldo\s*(?:de\s*)?sal[aá]rio',
            r'sal[aá]rio\s*(?:do\s*)?m[eê]s',
        ],
        'Aviso Prévio Indenizado': [
            r'aviso\s*pr[ée]vio\s*indenizado',
            r'aviso\s*pr[ée]vio',
        ],
        'Férias Vencidas': [
            r'f[ée]rias\s*vencidas',
            r'f[ée]rias\s*(?:integrais|integral)',
        ],
        'Férias Proporcionais': [
            r'f[ée]rias\s*proporcionais',
            r'f[ée]rias\s*prop',
        ],
        '1/3 Férias': [
            r'1\/3\s*(?:de\s*)?f[ée]rias',
            r'ter[çc]o\s*(?:de\s*)?f[ée]rias',
            r'adi[çc]ional\s*(?:de\s*)?f[ée]rias',
        ],
        '13º Salário': [
            r'13[ºo]\s*sal[aá]rio',
            r'd[ée]cimo\s*terceiro',
            r'gratifica[çc][ãa]o\s*natalina',
        ],
        'Multa 40% FGTS': [
            r'multa\s*(?:de\s*)?40%?\s*(?:do\s*)?fgts',
            r'40%\s*fgts',
            r'multa\s*fgts',
        ],
        'Saque FGTS': [
            r'saque\s*fgts',
            r'fgts\s*a\s*sacar',
        ],
    }

    # Palavras-chave para descontos
    DESCONTOS_KEYWORDS = {
        'INSS': [
            r'inss',
            r'previd[eê]ncia\s*social',
        ],
        'IRRF': [
            r'irrf',
            r'imposto\s*de\s*renda',
            r'ir\s*(?:retido\s*)?(?:na\s*)?fonte',
        ],
        'Aviso Prévio Descontado': [
            r'aviso\s*pr[ée]vio\s*(?:n[ãa]o\s*)?(?:cumprido|trabalhado)',
            r'desconto\s*aviso\s*pr[ée]vio',
        ],
        'Vale Transporte': [
            r'vale\s*transporte',
            r'vt',
        ],
        'Vale Refeição': [
            r'vale\s*(?:refei[çc][ãa]o|alimenta[çc][ãa]o)',
            r'vr|va',
        ],
    }

    # Tipos de rescisão
    TIPOS_RESCISAO = {
        'sem justa causa': [
            r'sem\s*justa\s*causa',
            r'dispensa\s*(?:imotivada|sem\s*justa\s*causa)',
        ],
        'com justa causa': [
            r'com\s*justa\s*causa',
            r'justa\s*causa',
        ],
        'pedido de demissao': [
            r'pedido\s*(?:de\s*)?demiss[ãa]o',
            r'demiss[ãa]o\s*(?:a\s*)?pedido',
        ],
        'acordo': [
            r'acordo',
            r'rescis[ãa]o\s*por\s*acordo',
            r'demiss[ãa]o\s*consensual',
        ],
    }

    def __init__(self, usar_ocr: bool = False):
        """
        Inicializa o extrator.

        Args:
            usar_ocr: Se True, tenta usar OCR para PDFs escaneados
        """
        self.usar_ocr = usar_ocr

        if not PYPDF2_AVAILABLE:
            logger.warning("PyPDF2 não disponível. Instale com: pip install PyPDF2")

        if usar_ocr and not OCR_AVAILABLE:
            logger.warning(
                "Bibliotecas de OCR não disponíveis. "
                "Instale com: pip install pytesseract pdf2image"
            )

    def extrair_texto_pdf(self, caminho: Union[str, Path]) -> str:
        """
        Extrai texto de um PDF.

        Args:
            caminho: Caminho para o arquivo PDF

        Returns:
            Texto extraído do PDF

        Raises:
            FileNotFoundError: Se o arquivo não existir
            RuntimeError: Se não houver biblioteca disponível
        """
        caminho_path = Path(caminho)

        if not caminho_path.exists():
            raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')

        texto = ""

        # Tenta extrair com PyPDF2 primeiro
        if PYPDF2_AVAILABLE:
            try:
                with open(caminho_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for pagina in reader.pages:
                        texto += pagina.extract_text() + "\n"
            except Exception as e:
                logger.error(f'Erro ao extrair com PyPDF2: {e}')

        # Se o texto está vazio e OCR está habilitado, tenta OCR
        if not texto.strip() and self.usar_ocr and OCR_AVAILABLE:
            try:
                logger.info("Tentando OCR...")
                imagens = convert_from_path(caminho_path)
                for imagem in imagens:
                    texto += pytesseract.image_to_string(imagem, lang='por') + "\n"
            except Exception as e:
                logger.error(f'Erro ao fazer OCR: {e}')

        if not texto.strip():
            raise RuntimeError(
                'Não foi possível extrair texto do PDF. '
                'Tente habilitar OCR ou converta o PDF para formato digital.'
            )

        return texto

    def extrair_com_regex(self, texto: str, patterns: list[str]) -> Optional[str]:
        """
        Extrai informação do texto usando múltiplos padrões regex.

        Args:
            texto: Texto para buscar
            patterns: Lista de padrões regex

        Returns:
            Primeiro match encontrado ou None
        """
        texto_lower = texto.lower()

        for pattern in patterns:
            match = re.search(pattern, texto_lower, re.IGNORECASE)
            if match:
                grupos = match.groups()
                if grupos:
                    return grupos[0].strip()
                return match.group(0).strip()

        return None

    def extrair_valores_monetarios(self, texto: str) -> dict[str, Decimal]:
        """
        Extrai todos os valores monetários do texto.

        Args:
            texto: Texto para buscar

        Returns:
            Dicionário com valores encontrados
        """
        valores = {}

        # Busca verbas
        for nome_verba, patterns in self.VERBAS_KEYWORDS.items():
            for pattern in patterns:
                # Busca o padrão seguido de um valor
                match = re.search(
                    pattern + r'[:\s]*r?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
                    texto,
                    re.IGNORECASE
                )
                if match:
                    try:
                        valor_str = match.group(1)
                        valor = RescisaoParser.converter_decimal(valor_str)
                        valores[nome_verba] = valor
                        break
                    except Exception as e:
                        logger.debug(f'Erro ao converter valor de {nome_verba}: {e}')

        return valores

    def extrair_dados(self, caminho: Union[str, Path]) -> dict[str, Any]:
        """
        Extrai todos os dados estruturados de um PDF.

        Args:
            caminho: Caminho para o arquivo PDF

        Returns:
            Dicionário com dados extraídos

        Raises:
            FileNotFoundError: Se o arquivo não existir
        """
        # Extrai texto
        texto = self.extrair_texto_pdf(caminho)

        dados = {
            'funcionario': {},
            'verbas': {},
            'descontos': {},
        }

        # Extrai dados do funcionário
        nome = self.extrair_com_regex(texto, self.KEYWORDS['nome'])
        if nome:
            # Remove caracteres especiais e normaliza
            nome = re.sub(r'\s+', ' ', nome).strip().title()
            dados['funcionario']['nome'] = nome

        cpf = self.extrair_com_regex(texto, self.KEYWORDS['cpf'])
        if cpf:
            dados['funcionario']['cpf'] = cpf

        cargo = self.extrair_com_regex(texto, self.KEYWORDS['cargo'])
        if cargo:
            cargo = re.sub(r'\s+', ' ', cargo).strip().title()
            dados['funcionario']['cargo'] = cargo

        # Extrai datas
        data_admissao = self.extrair_com_regex(texto, self.KEYWORDS['admissao'])
        if data_admissao:
            try:
                dados['funcionario']['data_admissao'] = RescisaoParser.converter_data(data_admissao)
            except ValueError:
                pass

        data_demissao = self.extrair_com_regex(texto, self.KEYWORDS['demissao'])
        if data_demissao:
            try:
                dados['funcionario']['data_demissao'] = RescisaoParser.converter_data(data_demissao)
            except ValueError:
                pass

        # Extrai salário
        salario = self.extrair_com_regex(texto, self.KEYWORDS['salario'])
        if salario:
            try:
                dados['funcionario']['salario_bruto'] = RescisaoParser.converter_decimal(salario)
            except ValueError:
                pass

        # Extrai tipo de rescisão
        for tipo, patterns in self.TIPOS_RESCISAO.items():
            if self.extrair_com_regex(texto, patterns):
                dados['tipo_rescisao'] = tipo
                break

        # Extrai verbas e descontos
        valores = self.extrair_valores_monetarios(texto)

        # Separa verbas de descontos
        for nome, valor in valores.items():
            if any(nome.startswith(desc) for desc in self.DESCONTOS_KEYWORDS.keys()):
                dados['descontos'][nome] = valor
            else:
                dados['verbas'][nome] = valor

        # Busca descontos explicitamente
        for nome_desconto, patterns in self.DESCONTOS_KEYWORDS.items():
            for pattern in patterns:
                match = re.search(
                    pattern + r'[:\s]*r?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
                    texto,
                    re.IGNORECASE
                )
                if match:
                    try:
                        valor_str = match.group(1)
                        valor = RescisaoParser.converter_decimal(valor_str)
                        dados['descontos'][nome_desconto] = valor
                        break
                    except Exception as e:
                        logger.debug(f'Erro ao converter desconto {nome_desconto}: {e}')

        return dados

    def extrair_e_validar(self, caminho: Union[str, Path]) -> tuple[dict[str, Any], list[str]]:
        """
        Extrai dados e retorna também lista de campos não encontrados.

        Args:
            caminho: Caminho para o arquivo PDF

        Returns:
            Tupla (dados_extraidos, campos_faltantes)
        """
        dados = self.extrair_dados(caminho)
        campos_faltantes = []

        # Verifica campos obrigatórios do funcionário
        campos_obrigatorios = ['nome', 'cpf', 'cargo', 'data_admissao', 'data_demissao', 'salario_bruto']

        for campo in campos_obrigatorios:
            if campo not in dados['funcionario'] or not dados['funcionario'][campo]:
                campos_faltantes.append(f'funcionario.{campo}')

        if 'tipo_rescisao' not in dados:
            campos_faltantes.append('tipo_rescisao')

        if not dados['verbas']:
            campos_faltantes.append('verbas (nenhuma encontrada)')

        return dados, campos_faltantes
