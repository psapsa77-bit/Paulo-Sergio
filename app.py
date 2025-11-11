"""
Script de entrada para a interface web
Este arquivo resolve problemas de imports relativos ao executar com Streamlit
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Importar e executar a aplicação
from labor_termination_analyzer.web import main

if __name__ == "__main__":
    main()
