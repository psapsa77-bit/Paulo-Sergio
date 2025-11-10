"""
Labor Termination Analyzer
Aplicativo para análise e explicação de rescisões trabalhistas
"""

__version__ = "1.0.0"

from .models import RescisaoTrabalhista, Verbas
from .parser import RescisaoParser
from .analyzer import RescisaoAnalyzer
from .generators import HTMLGenerator, PDFGenerator

__all__ = [
    "RescisaoTrabalhista",
    "Verbas",
    "RescisaoParser",
    "RescisaoAnalyzer",
    "HTMLGenerator",
    "PDFGenerator",
]
