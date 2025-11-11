"""
FGTS Digital Robot - Automação para consulta de guias FGTS
============================================================

Este módulo fornece automação para acessar o portal FGTS Digital,
autenticar via certificado digital e extrair informações sobre guias
pendentes e pagas das empresas.

Funcionalidades:
- Autenticação com certificado digital A1 (.pfx)
- Alternância entre múltiplas empresas via procuração
- Extração de guias pendentes e pagas
- Exportação de relatórios em JSON/Excel
- Interface web integrada com Streamlit

Exemplo de uso:
    from fgts_digital_robot import FGTSRobot

    robot = FGTSRobot(
        certificado_path="certificado.pfx",
        senha_certificado="senha123"
    )

    robot.autenticar()
    empresas = robot.listar_empresas()
    guias = robot.extrair_guias(cnpj="12345678000190")
    robot.exportar_relatorio(guias, formato="excel")

Autor: Paulo Sergio
Versão: 1.0.0
Data: 2025-01-11
"""

from .models import (
    CertificadoDigital,
    EmpresaFGTS,
    GuiaFGTS,
    StatusGuia,
    TipoGuia,
    RelatorioFGTS
)

from .authenticator import FGTSAuthenticator
from .navigator import FGTSNavigator
from .extractor import FGTSExtractor
from .robot import FGTSRobot

__version__ = "1.0.0"
__author__ = "Paulo Sergio"
__all__ = [
    "CertificadoDigital",
    "EmpresaFGTS",
    "GuiaFGTS",
    "StatusGuia",
    "TipoGuia",
    "RelatorioFGTS",
    "FGTSAuthenticator",
    "FGTSNavigator",
    "FGTSExtractor",
    "FGTSRobot",
]
