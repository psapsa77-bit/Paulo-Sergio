"""
Arquivo de configuração do Robô FGTS Digital
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
CERT_DIR = BASE_DIR / "certificados"
RESULTS_DIR = BASE_DIR / "resultados"
LOGS_DIR = BASE_DIR / "logs"

# Criar diretórios se não existirem
for directory in [CERT_DIR, RESULTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configurações de Certificado
CERT_PATH = os.getenv("CERT_PATH", str(CERT_DIR / "certificado.pfx"))
CERT_PASSWORD = os.getenv("CERT_PASSWORD", "")

# Configurações do Navegador
HEADLESS = os.getenv("HEADLESS", "False").lower() in ("true", "1", "yes")
BROWSER_TIMEOUT = int(os.getenv("TIMEOUT", "30000"))  # 30 segundos padrão
SLOW_MO = int(os.getenv("SLOW_MO", "100"))  # Delay em ms entre ações

# Configurações de CAPTCHA
CAPTCHA_MANUAL_MODE = os.getenv("CAPTCHA_MANUAL", "True").lower() in ("true", "1", "yes")
CAPTCHA_TIMEOUT = int(os.getenv("CAPTCHA_TIMEOUT", "300"))  # 5 minutos para resolver manualmente
CAPTCHA_2CAPTCHA_KEY = os.getenv("2CAPTCHA_API_KEY", "")  # Chave API do 2Captcha (opcional)
CAPTCHA_CHECK_INTERVAL = 2  # Verificar a cada 2 segundos se CAPTCHA foi resolvido

# URLs do FGTS Digital
FGTS_URL_BASE = "https://fgtsdigital.sistema.gov.br"
FGTS_URL_LOGIN = f"{FGTS_URL_BASE}/portal"
FGTS_URL_CONSULTA_GUIAS = f"{FGTS_URL_BASE}/portal/guias"

# Timeouts específicos (em milissegundos)
TIMEOUT_PAGE_LOAD = 60000  # 60 segundos para carregamento de página
TIMEOUT_ELEMENT = 30000    # 30 segundos para esperar elemento
TIMEOUT_DOWNLOAD = 120000  # 2 minutos para downloads

# Configurações de Retry
MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos

# Delays aleatórios (em segundos) - para simular comportamento humano
DELAY_MIN = 1
DELAY_MAX = 3

# Seletores do Site (usando múltiplas estratégias)
SELECTORS = {
    "inicial": {
        # Botões comuns na tela inicial de portais gov.br
        "btn_acessar": [
            "button:has-text('Acessar')",
            "a:has-text('Acessar')",
            "//button[contains(text(), 'Acessar')]",
            "//a[contains(text(), 'Acessar')]"
        ],
        "btn_entrar": [
            "button:has-text('Entrar')",
            "a:has-text('Entrar')",
            "//button[contains(text(), 'Entrar')]",
            "//a[contains(text(), 'Entrar')]"
        ],
        "btn_login": [
            "button:has-text('Login')",
            "a:has-text('Login')",
            "//button[contains(text(), 'Login')]",
            "//a[contains(text(), 'Login')]",
            "#login",
            ".btn-login"
        ],
        "btn_gov_br": [
            "button:has-text('gov.br')",
            "a:has-text('gov.br')",
            "//button[contains(text(), 'gov.br')]",
            "//a[contains(text(), 'gov.br')]"
        ]
    },
    "login": {
        "btn_certificado": [
            "button:has-text('Certificado Digital')",
            "a:has-text('Certificado Digital')",
            "//button[contains(text(), 'Certificado')]",
            "//a[contains(text(), 'Certificado')]",
            "#btn-certificado-digital",
            "[data-testid*='certificado']",
            ".btn-certificado"
        ],
        "select_certificado": [
            "select#certificado",
            "//select[@id='certificado']",
            "[name='certificado']"
        ],
        "btn_entrar": [
            "button:has-text('Entrar')",
            "//button[contains(text(), 'Entrar')]",
            "#btn-login",
            "button[type='submit']"
        ]
    },
    "empresas": {
        "dropdown_empresa": [
            "select#empresa",
            "//select[@id='empresa']",
            "[name='empresa']"
        ],
        "btn_selecionar": [
            "button:has-text('Selecionar')",
            "//button[contains(text(), 'Selecionar')]"
        ]
    },
    "guias": {
        "link_guias": [
            "a:has-text('Guias')",
            "//a[contains(text(), 'Guias')]",
            "nav a[href*='guias']"
        ],
        "tabela_guias": [
            "table.guias",
            "//table[contains(@class, 'guias')]",
            "#tabela-guias"
        ],
        "linha_guia": [
            "table.guias tbody tr",
            "//table[contains(@class, 'guias')]//tbody//tr"
        ],
        "btn_proxima_pagina": [
            "button:has-text('Próxima')",
            "//button[contains(text(), 'Próxima')]",
            ".pagination .next"
        ]
    },
    "logout": {
        "btn_sair": [
            "button:has-text('Sair')",
            "//button[contains(text(), 'Sair')]",
            "#btn-logout"
        ]
    },
    "captcha": {
        # Detectar diferentes tipos de CAPTCHA
        "recaptcha_v2": [
            "iframe[src*='recaptcha']",
            ".g-recaptcha",
            "#recaptcha",
            "[data-sitekey]"
        ],
        "recaptcha_v3": [
            "script[src*='recaptcha/api.js']",
            "[data-callback]"
        ],
        "hcaptcha": [
            "iframe[src*='hcaptcha']",
            ".h-captcha",
            "#hcaptcha"
        ],
        "captcha_image": [
            "img[alt*='captcha' i]",
            "img[src*='captcha' i]",
            "#captcha-image",
            ".captcha-img"
        ],
        "captcha_input": [
            "input[name*='captcha' i]",
            "input[placeholder*='captcha' i]",
            "#captcha",
            ".captcha-input"
        ],
        "captcha_frame": [
            "iframe[title*='captcha' i]",
            "iframe[name*='captcha' i]"
        ]
    }
}

# Configurações de Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configurações de Excel
EXCEL_ENGINE = "openpyxl"
EXCEL_COLUMNS = [
    "CNPJ",
    "Empresa",
    "Competência",
    "Status",
    "Valor",
    "Vencimento",
    "Código Barras",
    "Data Consulta"
]

# User Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Configurações de Screenshot em erro
SCREENSHOT_ON_ERROR = True
SCREENSHOT_DIR = LOGS_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
