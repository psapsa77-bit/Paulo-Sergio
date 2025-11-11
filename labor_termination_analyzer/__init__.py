"""
Labor Termination Analyzer - Analisador de Rescisões Trabalhistas.

Este pacote fornece ferramentas completas para análise de rescisões
trabalhistas brasileiras, incluindo:

- Extração automática de dados de PDFs
- Análise detalhada com explicações e base legal
- Geração de relatórios visuais em HTML/PDF
- Interfaces Web (Streamlit), CLI e API Python

Uso básico:
    >>> from labor_termination_analyzer import RescisaoParser
    >>> rescisao = RescisaoParser.gerar_exemplo()
    >>> print(rescisao.valor_liquido())

Uso com PDF:
    >>> from labor_termination_analyzer import PDFExtractor, RescisaoParser
    >>> extractor = PDFExtractor()
    >>> dados = extractor.extrair_dados('rescisao.pdf')
    >>> rescisao = RescisaoParser.de_dict(dados)

Geração de relatórios:
    >>> from labor_termination_analyzer import HTMLGenerator, PDFGenerator
    >>> html_gen = HTMLGenerator()
    >>> html_gen.gerar_arquivo(rescisao, 'relatorio.html')
    >>>
    >>> pdf_gen = PDFGenerator()
    >>> pdf_gen.gerar_arquivo(rescisao, 'relatorio.pdf')

Análise detalhada:
    >>> from labor_termination_analyzer import RescisaoAnalyzer
    >>> analyzer = RescisaoAnalyzer(rescisao)
    >>> resumo = analyzer.gerar_resumo_completo()
"""

__version__ = "2.0.0"
__author__ = "Labor Termination Analyzer Team"
__license__ = "MIT"

# Importa classes principais para facilitar o uso
from .models import (
    Funcionario,
    Rescisao,
    RescisaoTrabalhista,
    Verbas,
    Descontos,
)

from .parser import RescisaoParser

from .pdf_extractor import PDFExtractor

from .analyzer import RescisaoAnalyzer

from .generators import (
    HTMLGenerator,
    PDFGenerator,
)

# Lista de exportações públicas
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__license__',

    # Models
    'Funcionario',
    'Rescisao',
    'RescisaoTrabalhista',
    'Verbas',
    'Descontos',

    # Parser
    'RescisaoParser',

    # Extractor
    'PDFExtractor',

    # Analyzer
    'RescisaoAnalyzer',

    # Generators
    'HTMLGenerator',
    'PDFGenerator',
]
