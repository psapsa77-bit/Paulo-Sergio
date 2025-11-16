"""
DET Robot - Robô para automação do Domicílio Eletrônico Trabalhista
"""

__version__ = "1.0.0"
__author__ = "Paulo Sergio"

from .models import MensagemDET, EmpregadorDET, ResultadoExtracao
from .browser import BrowserManager
from .auth import DETAuthenticator
from .scraper import DETScraper
from .storage import DETStorage

__all__ = [
    "MensagemDET",
    "EmpregadorDET",
    "ResultadoExtracao",
    "BrowserManager",
    "DETAuthenticator",
    "DETScraper",
    "DETStorage",
]
