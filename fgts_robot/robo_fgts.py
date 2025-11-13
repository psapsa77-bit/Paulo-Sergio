"""
Classe principal do Robô de Automação FGTS Digital
"""
import asyncio
import logging
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Error as PlaywrightError
import pandas as pd

# Import flexível para funcionar como módulo ou script direto
try:
    from . import config
except ImportError:
    import config


class RoboFGTS:
    """Robô de automação para consulta de guias FGTS Digital"""

    def __init__(
        self,
        cert_path: Optional[str] = None,
        cert_password: Optional[str] = None,
        headless: Optional[bool] = None
    ):
        """
        Inicializa o robô FGTS

        Args:
            cert_path: Caminho para o certificado .pfx (opcional, usa config se não fornecido)
            cert_password: Senha do certificado (opcional, usa config se não fornecido)
            headless: Modo headless do navegador (opcional, usa config se não fornecido)
        """
        self.cert_path = cert_path or config.CERT_PATH
        self.cert_password = cert_password or config.CERT_PASSWORD
        self.headless = headless if headless is not None else config.HEADLESS

        # Configurar logging
        self._setup_logging()

        # Variáveis de controle
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.dados_extraidos: List[Dict[str, Any]] = []

        self.logger.info("Robô FGTS inicializado")

    def _setup_logging(self):
        """Configura o sistema de logging"""
        log_file = config.LOGS_DIR / f"fgts_robot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # Configurar logger
        self.logger = logging.getLogger("RoboFGTS")
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))

        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)

        # Adicionar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Log file: {log_file}")

    def _validar_certificado(self) -> bool:
        """
        Valida se o certificado existe e é válido

        Returns:
            bool: True se válido, False caso contrário
        """
        try:
            cert_file = Path(self.cert_path)
            if not cert_file.exists():
                self.logger.error(f"Certificado não encontrado: {self.cert_path}")
                return False

            # Tentar carregar o certificado
            with open(cert_file, "rb") as f:
                cert_data = f.read()

            # Validar formato PKCS12
            private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
                cert_data,
                self.cert_password.encode() if self.cert_password else None,
                backend=default_backend()
            )

            # Armazenar para uso posterior
            self._cert_key = private_key
            self._cert_certificate = certificate
            self._cert_additional = additional_certificates

            self.logger.info("Certificado validado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao validar certificado: {str(e)}")
            return False

    def _preparar_certificado_pem(self) -> tuple:
        """
        Converte certificado .pfx para arquivos .pem temporários

        O Playwright precisa de certificado e chave em arquivos PEM separados.

        Returns:
            tuple: (cert_path, key_path) com caminhos dos arquivos temporários
        """
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography import x509

            # Caminhos dos arquivos temporários
            temp_cert_path = config.CERT_DIR / "temp_cert.pem"
            temp_key_path = config.CERT_DIR / "temp_key.pem"

            # Obter informações do certificado
            cert_subject = self._cert_certificate.subject
            cert_issuer = self._cert_certificate.issuer
            cert_not_before = self._cert_certificate.not_valid_before
            cert_not_after = self._cert_certificate.not_valid_after

            self.logger.info("Informações do certificado:")
            self.logger.info(f"  - Titular: {cert_subject.rfc4514_string()}")
            self.logger.info(f"  - Emissor: {cert_issuer.rfc4514_string()}")
            self.logger.info(f"  - Válido de: {cert_not_before}")
            self.logger.info(f"  - Válido até: {cert_not_after}")

            # Verificar validade
            from datetime import datetime
            now = datetime.now()
            if now < cert_not_before:
                self.logger.warning(f"⚠️ Certificado ainda não é válido! Inicia em {cert_not_before}")
            elif now > cert_not_after:
                self.logger.error(f"❌ Certificado expirado! Validade: {cert_not_after}")
                raise ValueError("Certificado digital está expirado!")
            else:
                dias_restantes = (cert_not_after - now).days
                self.logger.info(f"  - Status: ✓ Válido ({dias_restantes} dias restantes)")

            # Escrever certificado em formato PEM
            cert_pem = self._cert_certificate.public_bytes(
                encoding=serialization.Encoding.PEM
            )
            with open(temp_cert_path, 'wb') as f:
                f.write(cert_pem)

            # Escrever chave privada em formato PEM
            key_pem = self._cert_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            with open(temp_key_path, 'wb') as f:
                f.write(key_pem)

            # Verificar se arquivos foram criados
            if not temp_cert_path.exists():
                raise FileNotFoundError(f"Falha ao criar certificado PEM: {temp_cert_path}")
            if not temp_key_path.exists():
                raise FileNotFoundError(f"Falha ao criar chave PEM: {temp_key_path}")

            cert_size = temp_cert_path.stat().st_size
            key_size = temp_key_path.stat().st_size

            self.logger.info(f"Arquivos PEM criados:")
            self.logger.info(f"  - Certificado: {temp_cert_path} ({cert_size} bytes)")
            self.logger.info(f"  - Chave: {temp_key_path} ({key_size} bytes)")

            return str(temp_cert_path), str(temp_key_path)

        except Exception as e:
            self.logger.error(f"❌ Erro ao preparar certificado PEM: {str(e)}")
            raise

    def _limpar_certificados_temporarios(self):
        """Remove arquivos temporários de certificado"""
        try:
            temp_cert = config.CERT_DIR / "temp_cert.pem"
            temp_key = config.CERT_DIR / "temp_key.pem"

            if temp_cert.exists():
                temp_cert.unlink()
                self.logger.debug("Certificado temporário removido")

            if temp_key.exists():
                temp_key.unlink()
                self.logger.debug("Chave temporária removida")

        except Exception as e:
            self.logger.warning(f"Erro ao limpar certificados temporários: {str(e)}")

    async def _iniciar_navegador(self):
        """Inicializa o navegador Playwright com configurações de certificado"""
        try:
            self.logger.info("Iniciando navegador...")
            self.logger.info(f"Tipo de navegador: {config.BROWSER_TYPE}")

            playwright = await async_playwright().start()

            # Selecionar o tipo de navegador
            if config.BROWSER_TYPE == "chrome":
                self.logger.info("🌐 Usando Google Chrome instalado (tem acesso aos certificados do sistema)")
                browser_launcher = playwright.chromium
                channel = "chrome"
            elif config.BROWSER_TYPE == "msedge":
                self.logger.info("🌐 Usando Microsoft Edge instalado (tem acesso aos certificados do sistema)")
                browser_launcher = playwright.chromium
                channel = "msedge"
            elif config.BROWSER_TYPE == "firefox":
                self.logger.warning("⚠️ Firefox não suporta bem certificados digitais. Use Chrome ou Edge.")
                browser_launcher = playwright.firefox
                channel = None
            else:  # chromium (padrão)
                self.logger.warning("⚠️ Chromium empacotado NÃO tem acesso aos certificados do sistema!")
                self.logger.warning("⚠️ Configure BROWSER_TYPE=chrome ou BROWSER_TYPE=msedge no .env")
                browser_launcher = playwright.chromium
                channel = None

            # Argumentos do navegador
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]

            # Lançar navegador
            if channel:
                # Usar navegador instalado (Chrome/Edge)
                self.browser = await browser_launcher.launch(
                    headless=self.headless,
                    slow_mo=config.SLOW_MO,
                    channel=channel,
                    args=browser_args
                )
            else:
                # Usar Chromium empacotado (com certificados via arquivos PEM)
                self.browser = await browser_launcher.launch(
                    headless=self.headless,
                    slow_mo=config.SLOW_MO,
                    args=browser_args
                )

            # Criar contexto do navegador
            context_options = {
                "user_agent": config.USER_AGENT,
                "viewport": {"width": 1920, "height": 1080},
                "locale": "pt-BR",
                "timezone_id": "America/Sao_Paulo",
                "accept_downloads": True,
                "ignore_https_errors": False
            }

            # Se estiver usando Chromium empacotado, configurar certificados manualmente
            if config.BROWSER_TYPE == "chromium":
                self.logger.info("Configurando certificado manualmente para Chromium...")
                cert_path, key_path = self._preparar_certificado_pem()

                self.logger.info(f"Certificado preparado:")
                self.logger.info(f"  - Cert: {cert_path}")
                self.logger.info(f"  - Key: {key_path}")

                # Configurar certificado para múltiplas origens
                client_certs = [
                    {
                        "origin": "https://fgtsdigital.sistema.gov.br",
                        "certPath": cert_path,
                        "keyPath": key_path
                    },
                    {
                        "origin": "https://*.sistema.gov.br",
                        "certPath": cert_path,
                        "keyPath": key_path
                    },
                    {
                        "origin": "https://login.acesso.gov.br",
                        "certPath": cert_path,
                        "keyPath": key_path
                    }
                ]
                context_options["client_certificates"] = client_certs
                self.logger.info(f"✓ Certificado configurado para {len(client_certs)} origens")
            else:
                # Chrome/Edge usam certificados do sistema automaticamente
                self.logger.info("✓ Navegador usará certificados instalados no sistema Windows")
                self.logger.info("📌 Certifique-se de que seu certificado .pfx está instalado no Windows!")

            self.context = await self.browser.new_context(**context_options)

            # Criar página
            self.page = await self.context.new_page()
            self.page.set_default_timeout(config.TIMEOUT_ELEMENT)

            self.logger.info("Navegador iniciado com sucesso")

        except Exception as e:
            self.logger.error(f"Erro ao iniciar navegador: {str(e)}")
            raise

    async def _fechar_navegador(self):
        """Fecha o navegador e libera recursos"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()

            self.logger.info("Navegador fechado")

            # Limpar certificados temporários
            self._limpar_certificados_temporarios()

        except Exception as e:
            self.logger.warning(f"Erro ao fechar navegador: {str(e)}")

    async def _screenshot_erro(self, nome: str = "erro"):
        """Captura screenshot em caso de erro"""
        if config.SCREENSHOT_ON_ERROR and self.page:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = config.SCREENSHOT_DIR / f"{nome}_{timestamp}.png"
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                self.logger.info(f"Screenshot salvo: {screenshot_path}")
            except Exception as e:
                self.logger.warning(f"Erro ao capturar screenshot: {str(e)}")

    async def _aguardar_elemento(
        self,
        seletores: List[str],
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """
        Aguarda um elemento usando múltiplas estratégias de seletor

        Args:
            seletores: Lista de seletores para tentar
            timeout: Timeout em ms (usa padrão se não fornecido)

        Returns:
            Seletor que funcionou ou None
        """
        timeout = timeout or config.TIMEOUT_ELEMENT

        for seletor in seletores:
            try:
                await self.page.wait_for_selector(seletor, timeout=timeout, state="visible")
                self.logger.debug(f"Elemento encontrado com seletor: {seletor}")
                return seletor
            except PlaywrightError:
                continue

        return None

    async def _clicar_com_retry(
        self,
        seletores: List[str],
        max_tentativas: int = 3
    ) -> bool:
        """
        Clica em um elemento com retry

        Args:
            seletores: Lista de seletores para tentar
            max_tentativas: Número máximo de tentativas

        Returns:
            bool: True se conseguiu clicar, False caso contrário
        """
        for tentativa in range(max_tentativas):
            try:
                seletor = await self._aguardar_elemento(seletores)
                if seletor:
                    await self.page.click(seletor)
                    self.logger.debug(f"Clique realizado com sucesso: {seletor}")
                    await self._delay_aleatorio()
                    return True
            except Exception as e:
                self.logger.warning(f"Tentativa {tentativa + 1} falhou: {str(e)}")
                if tentativa < max_tentativas - 1:
                    await asyncio.sleep(config.RETRY_DELAY)

        return False

    async def _delay_aleatorio(self):
        """Adiciona um delay aleatório para simular comportamento humano"""
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        await asyncio.sleep(delay)

    async def _navegar_tela_inicial(self) -> bool:
        """
        Navega pela tela inicial do portal clicando em botões necessários

        Muitos portais gov.br têm uma tela inicial com botões como "Acessar", "Entrar", etc.
        antes de chegar na tela de login com certificado.

        Returns:
            bool: True se navegação bem-sucedida ou não necessária
        """
        try:
            self.logger.info("Verificando se há navegação inicial necessária...")

            # Aguardar um pouco para a página carregar completamente
            await asyncio.sleep(2)

            # Lista de botões comuns em telas iniciais
            botoes_iniciais = [
                ("Acessar", config.SELECTORS["inicial"]["btn_acessar"]),
                ("Entrar", config.SELECTORS["inicial"]["btn_entrar"]),
                ("Login", config.SELECTORS["inicial"]["btn_login"]),
                ("gov.br", config.SELECTORS["inicial"]["btn_gov_br"])
            ]

            # Tentar clicar em cada tipo de botão (se existir)
            for nome_botao, seletores in botoes_iniciais:
                seletor = await self._aguardar_elemento(seletores, timeout=3000)

                if seletor:
                    self.logger.info(f"Encontrado botão '{nome_botao}', clicando...")
                    try:
                        await self.page.click(seletor)
                        await self._delay_aleatorio()

                        # Aguardar navegação
                        await asyncio.sleep(2)

                        url_atual = self.page.url
                        self.logger.info(f"Após clicar em '{nome_botao}', URL: {url_atual}")

                        # Se a URL mudou significativamente, provável que avançamos
                        break

                    except Exception as e:
                        self.logger.warning(f"Erro ao clicar em '{nome_botao}': {str(e)}")
                        continue

            self.logger.info("Navegação inicial concluída")
            return True

        except Exception as e:
            self.logger.warning(f"Erro durante navegação inicial: {str(e)}")
            # Não falhar aqui, pois pode ser que não haja tela inicial
            return True

    async def _detectar_captcha(self) -> Optional[str]:
        """
        Detecta se há CAPTCHA na página atual

        Returns:
            str: Tipo de CAPTCHA detectado ('recaptcha_v2', 'hcaptcha', 'image', etc.) ou None
        """
        try:
            self.logger.debug("Verificando se há CAPTCHA na página...")

            # Verificar cada tipo de CAPTCHA
            tipos_captcha = {
                "recaptcha_v2": config.SELECTORS["captcha"]["recaptcha_v2"],
                "hcaptcha": config.SELECTORS["captcha"]["hcaptcha"],
                "captcha_image": config.SELECTORS["captcha"]["captcha_image"],
                "captcha_frame": config.SELECTORS["captcha"]["captcha_frame"]
            }

            for tipo, seletores in tipos_captcha.items():
                seletor = await self._aguardar_elemento(seletores, timeout=2000)
                if seletor:
                    self.logger.info(f"✋ CAPTCHA detectado: {tipo}")
                    return tipo

            # Também verificar no HTML se há referências a CAPTCHA
            page_content = await self.page.content()
            if any(keyword in page_content.lower() for keyword in ['recaptcha', 'hcaptcha', 'captcha']):
                self.logger.info("✋ CAPTCHA detectado via análise de HTML")
                return "captcha_generic"

            return None

        except Exception as e:
            self.logger.debug(f"Erro ao detectar CAPTCHA: {str(e)}")
            return None

    async def _verificar_captcha_resolvido(self, tipo_captcha: str) -> bool:
        """
        Verifica se o CAPTCHA foi resolvido pelo usuário

        Args:
            tipo_captcha: Tipo de CAPTCHA que foi detectado

        Returns:
            bool: True se CAPTCHA foi resolvido, False caso contrário
        """
        try:
            # Para reCAPTCHA v2: Verificar se há token de resposta
            if tipo_captcha == "recaptcha_v2":
                # reCAPTCHA cria um textarea com a resposta quando resolvido
                token = await self.page.evaluate("""
                    () => {
                        const response = document.getElementById('g-recaptcha-response');
                        return response ? response.value : '';
                    }
                """)

                if token and len(token) > 0:
                    self.logger.debug(f"Token reCAPTCHA encontrado (tamanho: {len(token)})")
                    return True

            # Para hCaptcha: Verificar token de resposta
            elif tipo_captcha == "hcaptcha":
                token = await self.page.evaluate("""
                    () => {
                        const response = document.querySelector('[name=h-captcha-response]');
                        return response ? response.value : '';
                    }
                """)

                if token and len(token) > 0:
                    self.logger.debug(f"Token hCaptcha encontrado (tamanho: {len(token)})")
                    return True

            # Para CAPTCHA de imagem: Verificar se input foi preenchido
            elif tipo_captcha == "captcha_image":
                input_seletor = await self._aguardar_elemento(
                    config.SELECTORS["captcha"]["captcha_input"],
                    timeout=2000
                )
                if input_seletor:
                    valor = await self.page.input_value(input_seletor)
                    if valor and len(valor) > 0:
                        self.logger.debug(f"Input de CAPTCHA preenchido: {valor}")
                        return True

            # Verificação genérica: Se o CAPTCHA sumiu da página
            tipo_atual = await self._detectar_captcha()
            if tipo_atual is None:
                self.logger.debug("CAPTCHA não detectado mais na página")
                return True

            # Verificação adicional: Se a URL mudou (navegou após resolver)
            url_atual = self.page.url
            if "login" not in url_atual.lower() and "auth" not in url_atual.lower():
                self.logger.debug(f"URL mudou para: {url_atual}")
                return True

            return False

        except Exception as e:
            self.logger.debug(f"Erro ao verificar CAPTCHA resolvido: {str(e)}")
            # Em caso de erro, verificar se CAPTCHA sumiu
            tipo_atual = await self._detectar_captcha()
            return tipo_atual is None

    async def _resolver_captcha_manual(self, tipo_captcha: str, timeout: int = None) -> bool:
        """
        Aguarda resolução manual do CAPTCHA pelo usuário

        Args:
            tipo_captcha: Tipo de CAPTCHA detectado
            timeout: Tempo máximo de espera em segundos (padrão: config.CAPTCHA_TIMEOUT)

        Returns:
            bool: True se CAPTCHA foi resolvido, False se timeout
        """
        try:
            timeout = timeout or config.CAPTCHA_TIMEOUT

            self.logger.warning("=" * 70)
            self.logger.warning("🔴 CAPTCHA DETECTADO - AÇÃO NECESSÁRIA!")
            self.logger.warning("=" * 70)
            self.logger.warning(f"Tipo: {tipo_captcha}")
            self.logger.warning(f"")
            self.logger.warning(f"📋 INSTRUÇÕES:")
            self.logger.warning(f"  1. Vá até a janela do navegador que foi aberta")
            self.logger.warning(f"  2. Resolva o CAPTCHA manualmente")
            self.logger.warning(f"  3. Aguarde - o robô continuará automaticamente")
            self.logger.warning(f"")
            self.logger.warning(f"⏱️  Tempo limite: {timeout} segundos ({timeout//60} minutos)")
            self.logger.warning("=" * 70)

            # Se estiver em modo headless, avisar que não é possível
            if self.headless:
                self.logger.error("❌ ERRO: CAPTCHA detectado em modo HEADLESS!")
                self.logger.error("Configure HEADLESS=False no arquivo .env para resolver CAPTCHA manualmente")
                return False

            inicio = time.time()
            tentativas = 0

            while time.time() - inicio < timeout:
                tentativas += 1
                tempo_decorrido = int(time.time() - inicio)
                tempo_restante = timeout - tempo_decorrido

                # Log a cada 10 segundos
                if tentativas % 5 == 0:  # A cada 10 segundos (2s * 5)
                    self.logger.info(f"⏳ Aguardando resolução do CAPTCHA... ({tempo_restante}s restantes)")

                # Verificar se CAPTCHA foi resolvido
                if await self._verificar_captcha_resolvido(tipo_captcha):
                    self.logger.info("✅ CAPTCHA resolvido com sucesso!")
                    await asyncio.sleep(2)  # Aguardar processamento
                    return True

                await asyncio.sleep(config.CAPTCHA_CHECK_INTERVAL)

            self.logger.error(f"⏰ Timeout: CAPTCHA não foi resolvido em {timeout} segundos")
            return False

        except Exception as e:
            self.logger.error(f"❌ Erro ao aguardar resolução manual do CAPTCHA: {str(e)}")
            return False

    async def _resolver_captcha_2captcha(self, tipo_captcha: str) -> bool:
        """
        Resolve CAPTCHA automaticamente usando o serviço 2Captcha

        Args:
            tipo_captcha: Tipo de CAPTCHA detectado

        Returns:
            bool: True se resolvido com sucesso, False caso contrário
        """
        try:
            if not config.CAPTCHA_2CAPTCHA_KEY:
                self.logger.warning("Chave 2Captcha não configurada. Use resolução manual.")
                return False

            self.logger.info("🤖 Tentando resolver CAPTCHA automaticamente com 2Captcha...")

            # Importar biblioteca 2captcha (lazy import)
            try:
                from twocaptcha import TwoCaptcha
            except ImportError:
                self.logger.error("Biblioteca 'twocaptcha' não instalada!")
                self.logger.error("Execute: pip install 2captcha-python")
                return False

            solver = TwoCaptcha(config.CAPTCHA_2CAPTCHA_KEY)

            # Obter URL da página atual
            url_atual = self.page.url

            # Resolver baseado no tipo
            if tipo_captcha == "recaptcha_v2":
                # Encontrar sitekey
                sitekey_element = await self._aguardar_elemento(["[data-sitekey]"], timeout=5000)
                if not sitekey_element:
                    self.logger.error("Não foi possível encontrar sitekey do reCAPTCHA")
                    return False

                sitekey = await self.page.get_attribute(sitekey_element, "data-sitekey")
                self.logger.info(f"Resolvendo reCAPTCHA v2 (sitekey: {sitekey[:20]}...)")

                result = solver.recaptcha(sitekey=sitekey, url=url_atual)

                # Injetar resposta do CAPTCHA
                await self.page.evaluate(f"""
                    document.getElementById('g-recaptcha-response').innerHTML = '{result["code"]}';
                """)

                self.logger.info("✅ CAPTCHA resolvido automaticamente!")
                return True

            elif tipo_captcha == "hcaptcha":
                # Similar ao reCAPTCHA
                sitekey_element = await self._aguardar_elemento(["[data-sitekey]"], timeout=5000)
                if not sitekey_element:
                    return False

                sitekey = await self.page.get_attribute(sitekey_element, "data-sitekey")
                result = solver.hcaptcha(sitekey=sitekey, url=url_atual)

                await self.page.evaluate(f"""
                    document.querySelector('[name=h-captcha-response]').innerHTML = '{result["code"]}';
                """)

                self.logger.info("✅ hCaptcha resolvido automaticamente!")
                return True

            else:
                self.logger.warning(f"Tipo de CAPTCHA '{tipo_captcha}' não suportado para resolução automática")
                return False

        except Exception as e:
            self.logger.error(f"❌ Erro ao resolver CAPTCHA com 2Captcha: {str(e)}")
            return False

    async def _lidar_com_captcha(self) -> bool:
        """
        Detecta e resolve CAPTCHA (manual ou automaticamente)

        Returns:
            bool: True se não há CAPTCHA ou foi resolvido, False caso contrário
        """
        try:
            # Detectar CAPTCHA
            self.logger.debug("Verificando presença de CAPTCHA...")
            tipo_captcha = await self._detectar_captcha()

            if tipo_captcha is None:
                # Sem CAPTCHA, pode prosseguir
                self.logger.debug("✓ Nenhum CAPTCHA detectado na página")
                return True

            # CAPTCHA detectado - escolher método de resolução
            self.logger.info(f"CAPTCHA detectado do tipo: {tipo_captcha}")

            if config.CAPTCHA_MANUAL_MODE or not config.CAPTCHA_2CAPTCHA_KEY:
                # Resolução manual
                self.logger.info("Modo de resolução: MANUAL")
                sucesso = await self._resolver_captcha_manual(tipo_captcha)

                if sucesso:
                    self.logger.info("✓ Continuando após resolução de CAPTCHA...")
                    return True
                else:
                    self.logger.warning("⚠️ CAPTCHA não foi resolvido, mas continuando mesmo assim...")
                    # Continuar mesmo se não conseguiu confirmar resolução
                    # Pode ser que o usuário resolveu mas a detecção falhou
                    return True
            else:
                # Tentar resolução automática
                self.logger.info("Modo de resolução: AUTOMÁTICO (2Captcha)")
                sucesso = await self._resolver_captcha_2captcha(tipo_captcha)

                # Se falhar, tentar manual como fallback
                if not sucesso:
                    self.logger.warning("Resolução automática falhou. Tentando manual...")
                    sucesso = await self._resolver_captcha_manual(tipo_captcha)

                    if not sucesso:
                        self.logger.warning("⚠️ CAPTCHA não foi resolvido, mas continuando mesmo assim...")
                        return True

                return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao lidar com CAPTCHA: {str(e)}")
            self.logger.warning("Continuando mesmo com erro na detecção de CAPTCHA...")
            # Não bloquear por causa de erro na detecção
            return True

    async def _fazer_login(self) -> bool:
        """
        Realiza login no FGTS Digital usando certificado

        Returns:
            bool: True se login bem-sucedido, False caso contrário
        """
        try:
            self.logger.info(f"Acessando FGTS Digital: {config.FGTS_URL_LOGIN}")

            # Tentar acessar a página
            try:
                response = await self.page.goto(
                    config.FGTS_URL_LOGIN,
                    wait_until="networkidle",
                    timeout=config.TIMEOUT_PAGE_LOAD
                )

                # Verificar status da resposta
                if response:
                    self.logger.info(f"Página carregada - Status: {response.status}")
                    if response.status >= 400:
                        self.logger.error(f"Erro HTTP {response.status} ao acessar o portal")
                        await self._screenshot_erro("acesso_portal_erro_http")
                        return False
                else:
                    self.logger.warning("Resposta vazia ao carregar página")

                # Verificar URL atual
                url_atual = self.page.url
                self.logger.info(f"URL atual: {url_atual}")

            except PlaywrightError as e:
                self.logger.error(f"Erro ao acessar portal FGTS: {str(e)}")
                self.logger.error(f"Verifique se a URL está correta: {config.FGTS_URL_LOGIN}")
                await self._screenshot_erro("acesso_portal_falhou")
                return False

            # Aguardar página carregar completamente
            await asyncio.sleep(2)

            # Navegar pela tela inicial (se houver botões de navegação)
            self.logger.info("Verificando se há navegação inicial necessária...")
            await self._navegar_tela_inicial()

            # Aguardar um pouco para página processar
            self.logger.debug("Aguardando página processar...")
            await asyncio.sleep(2)

            # ========================================================================
            # PASSO 1: PROCURAR E CLICAR NO BOTÃO DE CERTIFICADO DIGITAL
            # ========================================================================
            self.logger.info("=" * 70)
            self.logger.info("PASSO 1: Procurando botão de certificado digital...")
            self.logger.info("=" * 70)
            self.logger.debug(f"Seletores a serem tentados: {config.SELECTORS['login']['btn_certificado']}")

            # Logar URL atual antes de procurar botão
            url_antes_botao = self.page.url
            self.logger.info(f"URL antes de procurar botão: {url_antes_botao}")

            if not await self._clicar_com_retry(config.SELECTORS["login"]["btn_certificado"]):
                self.logger.error("❌ Botão de certificado digital não encontrado na página")
                self.logger.error("Possíveis causas:")
                self.logger.error("  1. A estrutura do site mudou")
                self.logger.error("  2. Ainda está em uma tela anterior")
                self.logger.error("  3. Já passou da tela de login")
                self.logger.error("  4. Portal FGTS está fora do ar ou URL incorreta")

                # Screenshot para debug
                await self._screenshot_erro("login_botao_cert")

                # Logar URL atual
                url_atual = self.page.url
                self.logger.error(f"URL atual: {url_atual}")

                # Logar título da página
                titulo = await self.page.title()
                self.logger.error(f"Título da página: {titulo}")

                # Logar conteúdo da página para debug (primeiros 1000 chars)
                page_content = await self.page.content()
                self.logger.debug(f"Conteúdo da página (primeiros 1000 chars):")
                self.logger.debug(page_content[:1000])

                # Verificar se há botões visíveis na página
                botoes = await self.page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button, a[role="button"]'));
                        return buttons.map(b => ({
                            text: b.innerText?.substring(0, 50) || '',
                            id: b.id || '',
                            class: b.className || ''
                        })).slice(0, 10);
                    }
                """)
                self.logger.debug(f"Botões encontrados na página: {botoes}")

                return False

            self.logger.info("✓ Botão de certificado digital clicado com sucesso!")

            # ========================================================================
            # PASSO 2: VERIFICAR SE APARECEU CAPTCHA OU SELEÇÃO DE CERTIFICADO
            # ========================================================================
            self.logger.info("=" * 70)
            self.logger.info("PASSO 2: Verificando o que apareceu após clicar no botão...")
            self.logger.info("=" * 70)

            # Aguardar um pouco para a página processar o clique
            await asyncio.sleep(3)

            # Verificar se há CAPTCHA
            self.logger.info("Verificando se há CAPTCHA...")
            if not await self._lidar_com_captcha():
                self.logger.error("Falha ao resolver CAPTCHA após clicar no botão")
                await self._screenshot_erro("captcha_apos_botao")
                # Continuar mesmo assim
                self.logger.warning("Continuando mesmo com problema no CAPTCHA...")

            # Aguardar seleção de certificado
            # O Chrome/Edge abrirá uma janela popup pedindo para selecionar o certificado
            self.logger.info("=" * 70)
            self.logger.info("⏳ AGUARDANDO SELEÇÃO DE CERTIFICADO")
            self.logger.info("=" * 70)
            self.logger.info("📌 Se uma janela popup aparecer, selecione seu certificado e clique em OK")
            self.logger.info("📌 Se estiver usando Chrome/Edge, o certificado deve aparecer automaticamente")
            self.logger.info("=" * 70)

            await asyncio.sleep(5)  # Tempo para usuário selecionar certificado se necessário

            # Verificar se houve seleção de certificado no navegador
            await self._delay_aleatorio()

            # ========================================================================
            # PASSO 3: SELECIONAR PERFIL "SOU PROCURADOR"
            # ========================================================================
            self.logger.info("=" * 70)
            self.logger.info("PASSO 3: Verificando seleção de perfil...")
            self.logger.info("=" * 70)

            # Após selecionar certificado, aparece pop-up perguntando:
            # "Meu Perfil" ou "Sou Procurador"
            # Precisamos clicar em "Sou Procurador" para acessar empresas via procuração
            try:
                await self._selecionar_perfil_procurador()
            except Exception as e:
                self.logger.warning(f"Erro ao selecionar perfil de procurador: {str(e)}")
                # Continua mesmo se falhar - pode ser que já tenha selecionado

            # Aguardar carregamento da página inicial
            await asyncio.sleep(3)

            # ========================================================================
            # PASSO 4: VERIFICAR SE HÁ CAPTCHA APÓS AUTENTICAÇÃO
            # ========================================================================
            self.logger.info("Verificando se há CAPTCHA após autenticação...")
            if not await self._lidar_com_captcha():
                self.logger.warning("Problema ao verificar CAPTCHA pós-login, mas continuando...")

            # Verificar se login foi bem-sucedido (procurar elemento da página logada)
            try:
                await self.page.wait_for_load_state("networkidle", timeout=10000)
                url_pos_login = self.page.url
                self.logger.info(f"Login realizado - URL: {url_pos_login}")

                # Verificar se realmente logou (URL mudou?)
                if url_pos_login != config.FGTS_URL_LOGIN:
                    self.logger.info("✓ Login realizado com sucesso")
                    return True
                else:
                    self.logger.warning("URL não mudou após login - verificando se logou...")
                    # Tentar verificar de outra forma (procurar elemento que só existe quando logado)
                    await asyncio.sleep(2)
                    return True

            except Exception as e:
                self.logger.error(f"Timeout aguardando página após login: {str(e)}")
                await self._screenshot_erro("login_timeout")
                return False

        except Exception as e:
            self.logger.error(f"Erro crítico durante login: {str(e)}")
            self.logger.error(f"Tipo do erro: {type(e).__name__}")
            await self._screenshot_erro("login_erro_critico")
            return False

    async def _fechar_popups(self) -> bool:
        """
        Detecta e fecha pop-ups, modais e avisos que aparecem após login

        Returns:
            bool: True se processou (fechou ou não havia pop-ups)
        """
        try:
            self.logger.info("=" * 70)
            self.logger.info("🔍 Verificando pop-ups, modais e avisos...")
            self.logger.info("=" * 70)

            await asyncio.sleep(2)  # Aguardar pop-ups aparecerem

            # Lista de seletores comuns de pop-ups/modais
            seletores_popup = [
                # Botões de fechar (X)
                "button[aria-label='Close']",
                "button[aria-label='Fechar']",
                "button.close",
                "button.modal-close",
                "[data-dismiss='modal']",
                ".modal-header .close",

                # Botões de OK/Entendi/Continuar
                "button:has-text('OK')",
                "button:has-text('Entendi')",
                "button:has-text('Continuar')",
                "button:has-text('Aceitar')",
                "button:has-text('Concordo')",

                # Overlays/modais
                ".modal.show button",
                ".popup button",
                ".dialog button",
                "[role='dialog'] button"
            ]

            popups_fechados = 0

            for seletor in seletores_popup:
                try:
                    # Tentar encontrar elemento (não aguardar muito)
                    elementos = await self.page.query_selector_all(seletor)

                    for elemento in elementos:
                        # Verificar se elemento está visível
                        is_visible = await elemento.is_visible()
                        if is_visible:
                            texto = await elemento.inner_text()
                            self.logger.info(f"Encontrado pop-up/modal: '{texto[:50]}' (seletor: {seletor})")

                            # Tentar clicar
                            await elemento.click()
                            popups_fechados += 1
                            self.logger.info(f"✓ Pop-up fechado: '{texto[:50]}'")
                            await asyncio.sleep(1)

                except Exception as e:
                    # Ignorar erros (elemento pode não existir ou desaparecer)
                    continue

            if popups_fechados > 0:
                self.logger.info(f"✓ Total de pop-ups fechados: {popups_fechados}")
            else:
                self.logger.info("✓ Nenhum pop-up detectado")

            return True

        except Exception as e:
            self.logger.warning(f"Erro ao verificar pop-ups: {str(e)}")
            return True  # Não bloquear por causa disso

    async def _selecionar_perfil_procurador(self) -> bool:
        """
        Detecta e seleciona o perfil de acesso após login com certificado

        Após login, o portal pode mostrar um pop-up perguntando:
        - "Meu Perfil" (acesso como pessoa/empresa do certificado)
        - "Sou Procurador" (acesso via procuração eletrônica)

        Returns:
            bool: True se selecionou ou não havia pop-up
        """
        try:
            self.logger.info("=" * 70)
            self.logger.info("👤 Verificando seleção de perfil de acesso...")
            self.logger.info("=" * 70)

            await asyncio.sleep(2)  # Aguardar pop-up aparecer

            # Seletores para o pop-up de seleção de perfil
            seletores_popup_perfil = [
                # Texto específico do pop-up
                "text='Selecione o tipo de acesso'",
                "text='Como deseja acessar?'",
                "text='Escolha seu perfil'",

                # Container do modal
                "[role='dialog']:has-text('perfil')",
                ".modal:has-text('meu perfil')",
                ".modal:has-text('procurador')",
                ".dialog:has-text('acesso')"
            ]

            # Verificar se o pop-up existe
            popup_encontrado = False
            for seletor in seletores_popup_perfil:
                try:
                    elemento = await self.page.query_selector(seletor)
                    if elemento and await elemento.is_visible():
                        popup_encontrado = True
                        self.logger.info("✓ Pop-up de seleção de perfil detectado!")
                        break
                except:
                    continue

            if not popup_encontrado:
                # Verificar de forma genérica procurando pelos textos
                textos_na_pagina = await self.page.evaluate("""
                    () => {
                        const texto = document.body.innerText.toLowerCase();
                        return {
                            temPerfil: texto.includes('meu perfil') || texto.includes('perfil'),
                            temProcurador: texto.includes('procurador') || texto.includes('procuração'),
                            temSelecione: texto.includes('selecione') && (texto.includes('acesso') || texto.includes('perfil'))
                        };
                    }
                """)

                if textos_na_pagina['temPerfil'] or textos_na_pagina['temProcurador']:
                    popup_encontrado = True
                    self.logger.info("✓ Pop-up de seleção detectado via análise de texto!")

            if not popup_encontrado:
                self.logger.info("ℹ️  Pop-up de seleção de perfil não detectado (pode já estar na tela correta)")
                return True

            # ========================================================================
            # Clicar em "Definir" para confirmar perfil
            # ========================================================================
            # NOTA: "Meu Perfil" já vem selecionado por padrão, basta confirmar
            self.logger.info("")
            self.logger.info("🔍 Procurando botão 'Definir' para confirmar perfil...")

            seletores_definir = [
                # Botões com texto
                "button:has-text('Definir')",
                "button:has-text('definir')",
                "a:has-text('Definir')",

                # Botões de confirmação comuns
                "button:has-text('Confirmar')",
                "button:has-text('OK')",
                "button:has-text('Continuar')",

                # XPath
                "//button[contains(text(), 'Definir')]",
                "//button[contains(text(), 'Confirmar')]",

                # IDs e classes
                "#btn-definir",
                ".btn-definir",
                "button[type='submit']"
            ]

            definir_clicado = False

            for seletor in seletores_definir:
                try:
                    elemento = await self.page.query_selector(seletor)
                    if elemento and await elemento.is_visible():
                        texto = await elemento.inner_text()
                        self.logger.info(f"✓ Encontrado botão: '{texto.strip()}'")

                        # Clicar
                        await elemento.click()
                        definir_clicado = True
                        self.logger.info("✅ Clicado em 'Definir'!")

                        # Aguardar navegação
                        await asyncio.sleep(3)

                        url_apos = self.page.url
                        self.logger.info(f"📍 URL após seleção: {url_apos}")
                        break

                except Exception as e:
                    continue

            if not definir_clicado:
                # Tentar via JavaScript
                self.logger.info("Tentando clicar em 'Definir' via JavaScript...")
                resultado = await self.page.evaluate("""
                    () => {
                        const elementos = document.querySelectorAll('button, a, [type="submit"]');
                        for (const el of elementos) {
                            const texto = el.innerText.toLowerCase();
                            if (texto.includes('definir') || texto.includes('confirmar') || texto.includes('continuar')) {
                                el.click();
                                return { success: true, texto: el.innerText };
                            }
                        }
                        return { success: false };
                    }
                """)

                if resultado.get('success'):
                    self.logger.info(f"✓ Clicado via JavaScript em: '{resultado.get('texto')}'")
                    await asyncio.sleep(3)
                else:
                    self.logger.warning("⚠️  Não foi possível encontrar botão 'Definir'")
                    await self._screenshot_erro("definir_nao_encontrado")

                    # Listar opções disponíveis
                    opcoes = await self.page.evaluate("""
                        () => {
                            const opcoes = [];
                            document.querySelectorAll('button, a').forEach(el => {
                                if (el.offsetParent !== null && el.innerText.trim()) {
                                    opcoes.push(el.innerText.trim().substring(0, 50));
                                }
                            });
                            return opcoes.slice(0, 10);
                        }
                    """)

                    self.logger.warning("Botões disponíveis na tela:")
                    for i, opcao in enumerate(opcoes, 1):
                        self.logger.warning(f"  {i}. {opcao}")

            self.logger.info("=" * 70)
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao selecionar perfil: {str(e)}")
            self.logger.exception("Traceback:")
            await self._screenshot_erro("erro_selecao_perfil")
            # Continuar mesmo com erro
            return True

    async def _explorar_pagina_inicial(self) -> dict:
        """
        Explora e mapeia a estrutura da página inicial após login

        Returns:
            dict: Informações sobre a estrutura da página
        """
        try:
            self.logger.info("=" * 70)
            self.logger.info("🗺️  EXPLORANDO ESTRUTURA DO SITE...")
            self.logger.info("=" * 70)

            await asyncio.sleep(2)

            info = {
                "url": self.page.url,
                "titulo": await self.page.title(),
                "menus": [],
                "links": [],
                "botoes": [],
                "tabelas": [],
                "formularios": []
            }

            self.logger.info(f"📍 URL atual: {info['url']}")
            self.logger.info(f"📄 Título: {info['titulo']}")
            self.logger.info("")

            # 1. MAPEAR MENUS E NAVEGAÇÃO
            self.logger.info("🔍 Mapeando menus de navegação...")
            menus = await self.page.evaluate("""
                () => {
                    const menus = [];
                    const nav = document.querySelectorAll('nav a, nav button, [role="navigation"] a');
                    nav.forEach((el, index) => {
                        if (el.innerText && el.innerText.trim()) {
                            menus.push({
                                texto: el.innerText.trim().substring(0, 50),
                                href: el.href || '',
                                id: el.id || '',
                                class: el.className || ''
                            });
                        }
                    });
                    return menus.slice(0, 20);  // Limitar a 20 itens
                }
            """)
            info["menus"] = menus

            if menus:
                self.logger.info(f"✓ Encontrados {len(menus)} itens de menu:")
                for i, menu in enumerate(menus[:10], 1):
                    self.logger.info(f"  {i}. {menu['texto']}")
                if len(menus) > 10:
                    self.logger.info(f"  ... e mais {len(menus) - 10} itens")
            else:
                self.logger.info("⚠️  Nenhum menu encontrado")

            self.logger.info("")

            # 2. MAPEAR LINKS PRINCIPAIS
            self.logger.info("🔍 Mapeando links principais...")
            links = await self.page.evaluate("""
                () => {
                    const links = [];
                    const principais = document.querySelectorAll('main a, .content a, #content a');
                    principais.forEach((el) => {
                        if (el.innerText && el.innerText.trim() && el.href) {
                            links.push({
                                texto: el.innerText.trim().substring(0, 50),
                                href: el.href
                            });
                        }
                    });
                    return links.slice(0, 15);
                }
            """)
            info["links"] = links

            if links:
                self.logger.info(f"✓ Encontrados {len(links)} links:")
                for i, link in enumerate(links[:10], 1):
                    self.logger.info(f"  {i}. {link['texto']} → {link['href']}")
            else:
                self.logger.info("⚠️  Nenhum link principal encontrado")

            self.logger.info("")

            # 3. MAPEAR BOTÕES
            self.logger.info("🔍 Mapeando botões...")
            botoes = await self.page.evaluate("""
                () => {
                    const botoes = [];
                    document.querySelectorAll('button, [role="button"]').forEach((btn) => {
                        if (btn.innerText && btn.innerText.trim()) {
                            botoes.push({
                                texto: btn.innerText.trim().substring(0, 50),
                                id: btn.id || '',
                                class: btn.className || '',
                                type: btn.type || ''
                            });
                        }
                    });
                    return botoes.slice(0, 15);
                }
            """)
            info["botoes"] = botoes

            if botoes:
                self.logger.info(f"✓ Encontrados {len(botoes)} botões:")
                for i, btn in enumerate(botoes[:10], 1):
                    self.logger.info(f"  {i}. {btn['texto']}")
            else:
                self.logger.info("⚠️  Nenhum botão encontrado")

            self.logger.info("")

            # 4. MAPEAR TABELAS
            self.logger.info("🔍 Procurando tabelas de dados...")
            tabelas = await self.page.evaluate("""
                () => {
                    const tabelas = [];
                    document.querySelectorAll('table').forEach((table, index) => {
                        const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim());
                        const rows = table.querySelectorAll('tbody tr').length;

                        if (headers.length > 0 || rows > 0) {
                            tabelas.push({
                                index: index,
                                headers: headers.slice(0, 10),
                                rows: rows,
                                id: table.id || '',
                                class: table.className || ''
                            });
                        }
                    });
                    return tabelas;
                }
            """)
            info["tabelas"] = tabelas

            if tabelas:
                self.logger.info(f"✓ Encontradas {len(tabelas)} tabelas:")
                for i, tab in enumerate(tabelas, 1):
                    self.logger.info(f"  {i}. Tabela com {tab['rows']} linhas")
                    if tab['headers']:
                        self.logger.info(f"     Colunas: {', '.join(tab['headers'])}")
            else:
                self.logger.info("⚠️  Nenhuma tabela encontrada")

            self.logger.info("")

            # 5. PROCURAR PALAVRAS-CHAVE RELACIONADAS A FGTS/GUIAS
            self.logger.info("🔍 Procurando seções relacionadas a FGTS...")
            palavras_chave = await self.page.evaluate("""
                () => {
                    const texto = document.body.innerText;
                    const keywords = {
                        'guias': (texto.match(/guias?/gi) || []).length,
                        'fgts': (texto.match(/fgts/gi) || []).length,
                        'competência': (texto.match(/competência/gi) || []).length,
                        'boleto': (texto.match(/boletos?/gi) || []).length,
                        'pagamento': (texto.match(/pagamentos?/gi) || []).length,
                        'empresa': (texto.match(/empresas?/gi) || []).length,
                        'cnpj': (texto.match(/cnpj/gi) || []).length
                    };
                    return keywords;
                }
            """)

            encontradas = [k for k, v in palavras_chave.items() if v > 0]
            if encontradas:
                self.logger.info("✓ Palavras-chave encontradas:")
                for palavra, count in palavras_chave.items():
                    if count > 0:
                        self.logger.info(f"  - '{palavra}': {count} ocorrências")
            else:
                self.logger.info("⚠️  Nenhuma palavra-chave específica encontrada")

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✓ Exploração concluída!")
            self.logger.info("=" * 70)

            return info

        except Exception as e:
            self.logger.error(f"Erro ao explorar página: {str(e)}")
            return {}

    async def _selecionar_empresa(self, cnpj: str) -> bool:
        """
        Seleciona uma empresa específica

        Args:
            cnpj: CNPJ da empresa

        Returns:
            bool: True se seleção bem-sucedida, False caso contrário
        """
        try:
            self.logger.info(f"Selecionando empresa: {cnpj}")

            # Aguardar dropdown de empresas
            seletor = await self._aguardar_elemento(
                config.SELECTORS["empresas"]["dropdown_empresa"],
                timeout=10000
            )

            if not seletor:
                self.logger.warning("Dropdown de empresas não encontrado, pode haver apenas uma empresa")
                return True

            # Selecionar empresa pelo CNPJ
            cnpj_formatado = cnpj.replace(".", "").replace("/", "").replace("-", "")
            await self.page.select_option(seletor, label=cnpj_formatado)
            await self._delay_aleatorio()

            # Clicar em selecionar se houver botão
            await self._clicar_com_retry(config.SELECTORS["empresas"]["btn_selecionar"])

            self.logger.info(f"Empresa {cnpj} selecionada")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao selecionar empresa {cnpj}: {str(e)}")
            await self._screenshot_erro(f"selecao_empresa_{cnpj}")
            return False

    async def _extrair_guias(self, cnpj: str) -> List[Dict[str, Any]]:
        """
        Extrai dados das guias FGTS de uma empresa

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Lista com dados das guias
        """
        guias = []

        try:
            self.logger.info(f"Acessando área de guias para {cnpj}...")

            # Clicar no link de guias
            if not await self._clicar_com_retry(config.SELECTORS["guias"]["link_guias"]):
                self.logger.error("Link de guias não encontrado")
                return guias

            # Aguardar tabela de guias
            seletor_tabela = await self._aguardar_elemento(
                config.SELECTORS["guias"]["tabela_guias"],
                timeout=15000
            )

            if not seletor_tabela:
                self.logger.warning(f"Tabela de guias não encontrada para {cnpj}")
                await self._screenshot_erro(f"guias_tabela_{cnpj}")
                return guias

            # Extrair dados de todas as páginas
            pagina = 1
            while True:
                self.logger.info(f"Extraindo página {pagina}...")

                # Aguardar carregamento da tabela
                await asyncio.sleep(1)

                # Extrair linhas da tabela
                linhas = await self.page.query_selector_all(config.SELECTORS["guias"]["linha_guia"][0])

                for linha in linhas:
                    try:
                        # Extrair células
                        celulas = await linha.query_selector_all("td")

                        if len(celulas) >= 4:
                            competencia = await celulas[0].inner_text()
                            status = await celulas[1].inner_text()
                            valor = await celulas[2].inner_text()
                            vencimento = await celulas[3].inner_text()
                            codigo_barras = await celulas[4].inner_text() if len(celulas) > 4 else ""

                            guia = {
                                "CNPJ": cnpj,
                                "Empresa": "",  # Será preenchido depois se possível
                                "Competência": competencia.strip(),
                                "Status": status.strip(),
                                "Valor": valor.strip(),
                                "Vencimento": vencimento.strip(),
                                "Código Barras": codigo_barras.strip(),
                                "Data Consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }

                            guias.append(guia)

                    except Exception as e:
                        self.logger.warning(f"Erro ao extrair linha: {str(e)}")
                        continue

                # Verificar se há próxima página
                try:
                    btn_proxima = await self._aguardar_elemento(
                        config.SELECTORS["guias"]["btn_proxima_pagina"],
                        timeout=2000
                    )

                    if btn_proxima:
                        is_disabled = await self.page.evaluate(
                            f"document.querySelector('{btn_proxima}').disabled"
                        )

                        if not is_disabled:
                            await self.page.click(btn_proxima)
                            await self._delay_aleatorio()
                            pagina += 1
                            continue

                except:
                    pass

                # Não há mais páginas
                break

            self.logger.info(f"Total de guias extraídas para {cnpj}: {len(guias)}")

        except Exception as e:
            self.logger.error(f"Erro ao extrair guias para {cnpj}: {str(e)}")
            await self._screenshot_erro(f"extracao_guias_{cnpj}")

        return guias

    async def _processar_empresa(self, cnpj: str) -> List[Dict[str, Any]]:
        """
        Processa uma empresa: seleciona e extrai guias

        Args:
            cnpj: CNPJ da empresa

        Returns:
            Lista com dados das guias
        """
        self.logger.info(f"Processando empresa: {cnpj}")

        if not await self._selecionar_empresa(cnpj):
            self.logger.error(f"Não foi possível selecionar empresa {cnpj}")
            return []

        guias = await self._extrair_guias(cnpj)
        return guias

    def _exportar_excel(self, dados: List[Dict[str, Any]], nome_arquivo: Optional[str] = None):
        """
        Exporta dados para Excel

        Args:
            dados: Lista de dicionários com dados
            nome_arquivo: Nome do arquivo (opcional, gera automaticamente se não fornecido)
        """
        try:
            if not dados:
                self.logger.warning("Nenhum dado para exportar")
                return

            # Gerar nome do arquivo se não fornecido
            if not nome_arquivo:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                nome_arquivo = f"fgts_consulta_{timestamp}.xlsx"

            arquivo_path = config.RESULTS_DIR / nome_arquivo

            # Criar DataFrame
            df = pd.DataFrame(dados)

            # Garantir que todas as colunas esperadas existam
            for col in config.EXCEL_COLUMNS:
                if col not in df.columns:
                    df[col] = ""

            # Reordenar colunas
            df = df[config.EXCEL_COLUMNS]

            # Agrupar por CNPJ para criar abas
            with pd.ExcelWriter(arquivo_path, engine=config.EXCEL_ENGINE) as writer:
                if "CNPJ" in df.columns and not df.empty:
                    cnpjs_unicos = df["CNPJ"].unique()

                    for cnpj in cnpjs_unicos:
                        df_empresa = df[df["CNPJ"] == cnpj]
                        # Nome da aba: primeiros 31 caracteres (limite do Excel)
                        nome_aba = cnpj[:31] if cnpj else "Empresa"
                        df_empresa.to_excel(writer, sheet_name=nome_aba, index=False)

                else:
                    df.to_excel(writer, sheet_name="Dados", index=False)

            self.logger.info(f"Dados exportados para: {arquivo_path}")
            print(f"\n✓ Arquivo gerado: {arquivo_path}")

        except Exception as e:
            self.logger.error(f"Erro ao exportar Excel: {str(e)}")
            raise

    async def processar_clientes_async(self, lista_cnpj: List[str]) -> bool:
        """
        Processa lista de clientes (versão async)

        Args:
            lista_cnpj: Lista de CNPJs para processar

        Returns:
            bool: True se processamento bem-sucedido
        """
        try:
            self.logger.info("="*60)
            self.logger.info("INICIANDO PROCESSAMENTO FGTS")
            self.logger.info("="*60)

            # Validar certificado
            self.logger.info("Etapa 1/4: Validando certificado digital...")
            self.logger.info(f"  Caminho do certificado: {self.cert_path}")

            try:
                if not self._validar_certificado():
                    self.logger.error("❌ Certificado inválido. Abortando execução.")
                    self.logger.error("Verifique:")
                    self.logger.error(f"  1. Se o arquivo existe: {self.cert_path}")
                    self.logger.error("  2. Se a senha está correta no .env")
                    self.logger.error("  3. Se é um certificado A1 válido (.pfx)")
                    return False
                self.logger.info("  ✓ Certificado validado com sucesso")
            except Exception as e:
                self.logger.error(f"❌ Erro ao validar certificado: {str(e)}")
                self.logger.exception("Traceback completo:")
                return False

            # Iniciar navegador
            self.logger.info("Etapa 2/4: Iniciando navegador...")
            self.logger.info(f"  Modo headless: {self.headless}")

            try:
                await self._iniciar_navegador()
                self.logger.info("  ✓ Navegador iniciado com sucesso")
            except Exception as e:
                self.logger.error(f"❌ Erro ao iniciar navegador: {str(e)}")
                self.logger.exception("Traceback completo:")
                self.logger.error("Possíveis causas:")
                self.logger.error("  1. Playwright não está instalado (execute: playwright install chromium)")
                self.logger.error("  2. Problemas com permissões do sistema")
                self.logger.error("  3. Falta de dependências do Chromium")
                return False

            # Fazer login
            self.logger.info("Etapa 3/4: Fazendo login no portal FGTS...")
            self.logger.info(f"  URL: {config.FGTS_URL_LOGIN}")

            try:
                if not await self._fazer_login():
                    self.logger.error("❌ Falha no login. Abortando execução.")
                    self.logger.error("Verifique:")
                    self.logger.error("  1. Se o portal está acessível (execute: python testar_conexao.py)")
                    self.logger.error("  2. Se o certificado está configurado corretamente")
                    self.logger.error("  3. Screenshots em: logs/screenshots/")
                    return False
                self.logger.info("  ✓ Login realizado com sucesso")
            except Exception as e:
                self.logger.error(f"❌ Erro durante login: {str(e)}")
                self.logger.exception("Traceback completo:")
                return False

            # ============================================================
            # EXPLORAÇÃO: Fechar pop-ups e mapear estrutura do site
            # ============================================================
            self.logger.info("")
            self.logger.info("Etapa 3.5/4: Explorando site após login...")

            # NOTA: Seleção de perfil "Sou Procurador" agora é feita durante o login (PASSO 3)

            # PRIMEIRO: Fechar outros pop-ups/modais que possam ter aparecido
            try:
                await self._fechar_popups()
            except Exception as e:
                self.logger.warning(f"Erro ao fechar pop-ups: {str(e)}")

            # Explorar estrutura da página
            try:
                info_site = await self._explorar_pagina_inicial()

                # Salvar informações de exploração em arquivo JSON
                if info_site:
                    import json
                    exploracao_path = config.LOGS_DIR / f"exploracao_site_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(exploracao_path, 'w', encoding='utf-8') as f:
                        json.dump(info_site, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"📄 Informações de exploração salvas em: {exploracao_path}")

            except Exception as e:
                self.logger.warning(f"Erro durante exploração: {str(e)}")
                self.logger.warning("Continuando com processamento...")

            self.logger.info("")

            # Processar cada empresa
            self.logger.info("Etapa 4/4: Processando empresas...")
            self.logger.info(f"  Total de CNPJs: {len(lista_cnpj)}")
            self.logger.info("")

            todos_dados = []
            for i, cnpj in enumerate(lista_cnpj, 1):
                self.logger.info(f"Processando {i}/{len(lista_cnpj)}: {cnpj}")

                try:
                    guias = await self._processar_empresa(cnpj)
                    todos_dados.extend(guias)

                    if guias:
                        self.logger.info(f"  ✓ {len(guias)} guias extraídas de {cnpj}")
                    else:
                        self.logger.warning(f"  ⚠ Nenhuma guia encontrada para {cnpj}")

                except Exception as e:
                    self.logger.error(f"  ❌ Erro ao processar {cnpj}: {str(e)}")
                    self.logger.exception("  Traceback completo:")
                    continue

            # Exportar resultados
            self.logger.info("")
            self.logger.info("="*60)
            if todos_dados:
                self.logger.info("Exportando resultados...")
                self._exportar_excel(todos_dados)
                self.logger.info(f"✅ Processamento concluído: {len(todos_dados)} guias extraídas")
            else:
                self.logger.warning("⚠ Nenhum dado foi extraído")

            self.logger.info("="*60)
            return True

        except Exception as e:
            self.logger.error("="*60)
            self.logger.error(f"❌ ERRO CRÍTICO DURANTE PROCESSAMENTO")
            self.logger.error(f"Tipo do erro: {type(e).__name__}")
            self.logger.error(f"Mensagem: {str(e)}")
            self.logger.error("="*60)
            self.logger.exception("Traceback completo do erro:")

            try:
                await self._screenshot_erro("erro_geral")
                self.logger.error(f"Screenshot salvo em: logs/screenshots/")
            except:
                pass

            return False

        finally:
            self.logger.info("Fechando navegador...")
            await self._fechar_navegador()

    def processar_clientes(self, lista_cnpj: List[str]) -> bool:
        """
        Processa lista de clientes (versão síncrona - wrapper)

        Args:
            lista_cnpj: Lista de CNPJs para processar

        Returns:
            bool: True se processamento bem-sucedido
        """
        # Fix para Windows com Python 3.8+
        # O Playwright precisa do ProactorEventLoop no Windows para suportar subprocessos
        if sys.platform == 'win32':
            # Python 3.8+ no Windows: usar ProactorEventLoop
            try:
                # Configurar event loop policy para Windows
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                self.logger.debug("ProactorEventLoop configurado para Windows")
            except AttributeError:
                # Python < 3.8 ou não Windows
                pass

        return asyncio.run(self.processar_clientes_async(lista_cnpj))
