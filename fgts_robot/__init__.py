"""
Robô de Automação FGTS Digital

Módulo para automação de consultas no portal FGTS Digital usando certificado digital A1.
"""

__version__ = "1.0.0"
__author__ = "Paulo Sergio"

# Import flexível para funcionar como módulo ou script direto
try:
    from .robo_fgts import RoboFGTS
except ImportError:
    from robo_fgts import RoboFGTS

__all__ = ["RoboFGTS"]
