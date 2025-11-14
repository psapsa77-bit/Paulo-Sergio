"""
Configurações do Robô DET - Portal de Mensagens
"""
from pathlib import Path
import os

# Diretórios
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
RESULTS_DIR = BASE_DIR / "results"
CONFIG_DIR = BASE_DIR / "config"

# Criar diretórios se não existirem
LOGS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

# URLs do Portal DET
DET_URL = "https://det.sit.trabalho.gov.br/"
DET_LOGIN_URL = "https://det.sit.trabalho.gov.br/"
DET_MENSAGENS_URL = "https://det.sit.trabalho.gov.br/mensagens"  # Ajustar conforme necessário

# Configurações de Timeout (em segundos)
TIMEOUT_PADRAO = 30
TIMEOUT_LOGIN = 60
TIMEOUT_NAVEGACAO = 30
TIMEOUT_CARREGAMENTO = 45

# Configurações do Playwright
HEADLESS = False  # False para ver o navegador
SLOW_MO = 500  # Milissegundos de delay entre ações (para debugging)

# Configurações de Certificado Digital
CERT_PATH = CONFIG_DIR / "certificado.pfx"
CERT_PASSWORD = os.getenv("CERT_PASSWORD", "")

# Configurações de Log
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configurações de Retry
MAX_TENTATIVAS = 3
DELAY_ENTRE_TENTATIVAS = 2  # segundos

# Seletores CSS/XPath do Portal DET (ajustar após análise do site)
SELETORES = {
    # Login
    "btn_certificado": "//button[contains(text(), 'Certificado Digital')]",
    "select_certificado": "select[name='certificate']",

    # Menu de Mensagens
    "menu_mensagens": "//a[contains(text(), 'Mensagens')]",
    "link_mensagens": "a[href*='mensagens']",

    # Caixa de Entrada
    "mensagens_nao_lidas": ".mensagem.nao-lida",
    "contador_mensagens": ".badge-mensagens",
    "lista_mensagens": ".lista-mensagens",
    "mensagem_item": ".mensagem-item",

    # Detalhes da Mensagem
    "mensagem_assunto": ".mensagem-assunto",
    "mensagem_data": ".mensagem-data",
    "mensagem_remetente": ".mensagem-remetente",
    "mensagem_conteudo": ".mensagem-conteudo",

    # Status
    "indicador_nao_lida": ".badge-nao-lida",
    "icone_anexo": ".icone-anexo",
}

# Configurações de Empresa
DADOS_EMPRESAS = CONFIG_DIR / "empresas.json"

# Cores para logs no terminal
class Cores:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
