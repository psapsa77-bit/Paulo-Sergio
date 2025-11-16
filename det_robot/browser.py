"""
Gerenciador de navegador nativo para o DET Robot
Detecta e usa o navegador instalado no sistema
"""

import subprocess
import shutil
import platform
from typing import Optional, Tuple
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


class BrowserManager:
    """Gerencia a instância do navegador nativo"""

    DET_URL = "https://det.sit.trabalho.gov.br/"
    GOVBR_LOGIN_URL = "https://sso.acesso.gov.br/login"

    def __init__(
        self,
        navegador: str = "auto",
        headless: bool = False,
        timeout: int = 30,
        log_callback=None
    ):
        """
        Inicializa o gerenciador de navegador

        Args:
            navegador: "auto", "chrome", "firefox", "chromium"
            headless: Se True, executa sem interface gráfica
            timeout: Timeout padrão em segundos
            log_callback: Função para logging (opcional)
        """
        self.navegador_preferido = navegador
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        self.navegador_usado = None
        self.log = log_callback or print

    def _detectar_navegador_disponivel(self) -> Tuple[str, Optional[str]]:
        """
        Detecta qual navegador está instalado no sistema

        Returns:
            Tupla (nome_navegador, caminho_executavel)
        """
        sistema = platform.system().lower()

        # Lista de navegadores para tentar (em ordem de preferência)
        navegadores = []

        if sistema == "linux":
            navegadores = [
                ("chrome", ["google-chrome", "google-chrome-stable", "chrome"]),
                ("chromium", ["chromium-browser", "chromium"]),
                ("firefox", ["firefox", "firefox-esr"]),
            ]
        elif sistema == "darwin":  # macOS
            navegadores = [
                ("chrome", ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]),
                ("chromium", ["/Applications/Chromium.app/Contents/MacOS/Chromium"]),
                ("firefox", ["/Applications/Firefox.app/Contents/MacOS/firefox"]),
            ]
        elif sistema == "windows":
            navegadores = [
                ("chrome", [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                ]),
                ("firefox", [
                    r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                ]),
            ]

        # Tentar encontrar cada navegador
        for nome, caminhos in navegadores:
            for caminho in caminhos:
                if shutil.which(caminho) or Path(caminho).exists():
                    self.log(f"Navegador detectado: {nome} em {caminho}")
                    return nome, caminho

        # Se não encontrou nenhum específico, tenta genérico
        if shutil.which("google-chrome"):
            return "chrome", "google-chrome"
        if shutil.which("firefox"):
            return "firefox", "firefox"

        raise RuntimeError(
            "Nenhum navegador compatível encontrado. "
            "Instale Google Chrome, Chromium ou Firefox."
        )

    def _configurar_chrome(self, caminho_executavel: Optional[str] = None) -> webdriver.Chrome:
        """Configura e retorna driver do Chrome/Chromium"""

        options = ChromeOptions()

        # Usar navegador nativo
        if caminho_executavel:
            options.binary_location = caminho_executavel

        # Configurações padrão
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        # Evitar detecção de automação
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        if self.headless:
            options.add_argument("--headless=new")
            self.log("Modo headless ativado")

        # Configurar driver
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = ChromeService(ChromeDriverManager().install())
                self.log("ChromeDriver instalado automaticamente via webdriver-manager")
            else:
                # Tentar usar chromedriver do sistema
                chromedriver_path = shutil.which("chromedriver")
                if chromedriver_path:
                    service = ChromeService(chromedriver_path)
                    self.log(f"Usando chromedriver do sistema: {chromedriver_path}")
                else:
                    # Deixa o Selenium encontrar
                    service = ChromeService()
                    self.log("Tentando usar chromedriver padrão do sistema")

            driver = webdriver.Chrome(service=service, options=options)

            # Configurações anti-detecção
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            return driver

        except Exception as e:
            self.log(f"Erro ao configurar Chrome: {e}")
            raise

    def _configurar_firefox(self, caminho_executavel: Optional[str] = None) -> webdriver.Firefox:
        """Configura e retorna driver do Firefox"""

        options = FirefoxOptions()

        # Usar navegador nativo
        if caminho_executavel:
            options.binary_location = caminho_executavel

        # Configurações padrão
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)

        if self.headless:
            options.add_argument("--headless")
            self.log("Modo headless ativado")

        # Configurar driver
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = FirefoxService(GeckoDriverManager().install())
                self.log("GeckoDriver instalado automaticamente via webdriver-manager")
            else:
                # Tentar usar geckodriver do sistema
                geckodriver_path = shutil.which("geckodriver")
                if geckodriver_path:
                    service = FirefoxService(geckodriver_path)
                    self.log(f"Usando geckodriver do sistema: {geckodriver_path}")
                else:
                    service = FirefoxService()
                    self.log("Tentando usar geckodriver padrão do sistema")

            driver = webdriver.Firefox(service=service, options=options)
            return driver

        except Exception as e:
            self.log(f"Erro ao configurar Firefox: {e}")
            raise

    def iniciar(self) -> webdriver.Remote:
        """
        Inicia o navegador nativo

        Returns:
            Instância do WebDriver
        """
        self.log("Iniciando navegador...")

        # Detectar navegador disponível
        if self.navegador_preferido == "auto":
            nome_navegador, caminho = self._detectar_navegador_disponivel()
        else:
            nome_navegador = self.navegador_preferido
            caminho = None

        # Configurar driver apropriado
        try:
            if nome_navegador in ["chrome", "chromium"]:
                self.driver = self._configurar_chrome(caminho)
                self.navegador_usado = nome_navegador
            elif nome_navegador == "firefox":
                self.driver = self._configurar_firefox(caminho)
                self.navegador_usado = "firefox"
            else:
                raise ValueError(f"Navegador não suportado: {nome_navegador}")

            # Configurar wait
            self.wait = WebDriverWait(self.driver, self.timeout)

            self.log(f"Navegador {self.navegador_usado} iniciado com sucesso")
            return self.driver

        except Exception as e:
            self.log(f"Falha ao iniciar navegador: {e}")
            self.fechar()
            raise

    def acessar_det(self) -> bool:
        """
        Acessa o site do DET

        Returns:
            True se acessou com sucesso
        """
        if not self.driver:
            raise RuntimeError("Navegador não iniciado. Chame iniciar() primeiro.")

        try:
            self.log(f"Acessando DET: {self.DET_URL}")
            self.driver.get(self.DET_URL)

            # Aguardar carregamento da página
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            self.log("Site do DET acessado com sucesso")
            return True

        except TimeoutException:
            self.log("Timeout ao acessar o DET")
            return False
        except Exception as e:
            self.log(f"Erro ao acessar DET: {e}")
            return False

    def aguardar_elemento(self, by: By, valor: str, timeout: Optional[int] = None):
        """
        Aguarda um elemento aparecer na página

        Args:
            by: Tipo de seletor (By.ID, By.CLASS_NAME, etc)
            valor: Valor do seletor
            timeout: Timeout específico (usa padrão se None)

        Returns:
            Elemento encontrado
        """
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait

        return wait.until(EC.presence_of_element_located((by, valor)))

    def aguardar_clicavel(self, by: By, valor: str, timeout: Optional[int] = None):
        """Aguarda elemento ficar clicável"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait

        return wait.until(EC.element_to_be_clickable((by, valor)))

    def capturar_screenshot(self, nome_arquivo: str = "screenshot.png") -> str:
        """
        Captura screenshot da página atual

        Args:
            nome_arquivo: Nome do arquivo para salvar

        Returns:
            Caminho do arquivo salvo
        """
        if not self.driver:
            raise RuntimeError("Navegador não iniciado")

        caminho = Path(nome_arquivo)
        self.driver.save_screenshot(str(caminho))
        self.log(f"Screenshot salvo em: {caminho}")
        return str(caminho)

    def obter_cookies(self) -> list:
        """Retorna cookies da sessão atual"""
        if not self.driver:
            return []
        return self.driver.get_cookies()

    def carregar_cookies(self, cookies: list):
        """Carrega cookies na sessão"""
        if not self.driver:
            raise RuntimeError("Navegador não iniciado")

        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                self.log(f"Erro ao carregar cookie: {e}")

    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            try:
                self.driver.quit()
                self.log("Navegador fechado")
            except Exception as e:
                self.log(f"Erro ao fechar navegador: {e}")
            finally:
                self.driver = None
                self.wait = None

    def __enter__(self):
        """Context manager - entrada"""
        self.iniciar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager - saída"""
        self.fechar()
        return False
