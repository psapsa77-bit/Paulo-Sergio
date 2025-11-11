#!/usr/bin/env python3
"""
Script para iniciar a interface web do Labor Termination Analyzer
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    os.system("streamlit run app.py")
