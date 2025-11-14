"""
Robô DET - Verificador de Mensagens do Portal DET
"""

__version__ = "1.0.0"
__author__ = "Paulo Sergio"
__description__ = "Robô para verificar mensagens não lidas no Portal DET"

from .robot_det import RobotDET
from . import config

__all__ = ["RobotDET", "config"]
