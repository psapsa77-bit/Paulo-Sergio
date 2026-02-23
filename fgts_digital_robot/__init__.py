"""
FGTS Digital Robot
==================
Automação para consulta de guias FGTS Digital com certificado digital A1.

Uso rápido::

    from fgts_digital_robot import FGTSRobot, StatusGuia

    with FGTSRobot("certificado.pfx", "senha123") as robot:
        robot.autenticar()
        relatorio = robot.processar_todas_empresas()
        robot.exportar_relatorio(relatorio, "relatorio.xlsx", formato="excel")
"""

from .models import (
    CertificadoDigital,
    EmpresaFGTS,
    GuiaFGTS,
    RelatorioFGTS,
    StatusGuia,
    TipoGuia,
)
from .robot import FGTSRobot

__all__ = [
    "FGTSRobot",
    "CertificadoDigital",
    "EmpresaFGTS",
    "GuiaFGTS",
    "RelatorioFGTS",
    "StatusGuia",
    "TipoGuia",
]

__version__ = "1.0.0"
__author__ = "Paulo Sergio"
