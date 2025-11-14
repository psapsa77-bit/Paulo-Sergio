"""
Classe principal do Robô de Automação FGTS Digital
"""
import asyncio
import json
import logging
import os
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
        # Definir diretório de logs como atributo da instância
        self.log_dir = config.LOGS_DIR

        log_file = self.log_dir / f"fgts_robot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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

    async def _trocar_perfil_procurador(self, cnpj: str) -> bool:
        """
        Clica em "Trocar Perfil", seleciona "procurador" e digita CNPJ

        Args:
            cnpj: CNPJ da empresa para acessar como procurador

        Returns:
            bool: True se conseguiu trocar o perfil, False caso contrário
        """
        try:
            self.logger.info("=" * 70)
            self.logger.info("🔄 TROCANDO PERFIL PARA PROCURADOR...")
            self.logger.info("=" * 70)

            # Passo 1: Clicar no botão "Trocar Perfil"
            self.logger.info("🔍 Procurando botão 'Trocar Perfil'...")

            seletores_trocar_perfil = [
                "button:has-text('Trocar Perfil')",
                "button:has-text('Trocar perfil')",
                "a:has-text('Trocar Perfil')",
                "[aria-label*='Trocar']",
                "#btn-trocar-perfil",
                ".btn-trocar-perfil"
            ]

            clicou_trocar = False
            for seletor in seletores_trocar_perfil:
                try:
                    elemento = await self.page.query_selector(seletor)
                    if elemento and await elemento.is_visible():
                        await elemento.click()
                        clicou_trocar = True
                        self.logger.info("✅ Clicado em 'Trocar Perfil'!")
                        break
                except:
                    continue

            if not clicou_trocar:
                # Tentar via JavaScript
                self.logger.info("Tentando clicar via JavaScript...")
                resultado = await self.page.evaluate("""
                    () => {
                        const elementos = document.querySelectorAll('button, a');
                        for (const el of elementos) {
                            const texto = (el.innerText || '').toLowerCase();
                            if (texto.includes('trocar perfil')) {
                                el.click();
                                return { success: true, texto: el.innerText };
                            }
                        }
                        return { success: false };
                    }
                """)

                if resultado.get('success'):
                    clicou_trocar = True
                    self.logger.info(f"✅ Clicado via JavaScript: {resultado.get('texto')}")

            if not clicou_trocar:
                self.logger.error("❌ Não foi possível encontrar botão 'Trocar Perfil'")
                await self._screenshot_erro("trocar_perfil_nao_encontrado")
                return False

            # Aguardar pop-up aparecer
            await asyncio.sleep(3)

            # Passo 2: PRIMEIRA LINHA - Selecionar "Procurador" em dropdown/select
            self.logger.info("")
            self.logger.info("🔍 PRIMEIRA LINHA: Procurando dropdown para selecionar 'Procurador'...")

            # Primeiro, tentar encontrar e clicar no select/dropdown
            seletores_dropdown = [
                "select",
                "select[name*='perfil']",
                "select[name*='tipo']",
                "select[id*='perfil']",
                "select[id*='tipo']",
                ".br-select select",
                "br-select select"
            ]

            selecionou_procurador = False

            # Tentar selecionar via select normal
            for seletor in seletores_dropdown:
                try:
                    select_element = await self.page.query_selector(seletor)
                    if select_element and await select_element.is_visible():
                        # Selecionar a opção "Procurador"
                        await select_element.select_option(label="Procurador")
                        selecionou_procurador = True
                        self.logger.info("✅ Selecionado 'Procurador' no dropdown (via label)")
                        break
                except:
                    # Tentar por value
                    try:
                        await select_element.select_option(value="procurador")
                        selecionou_procurador = True
                        self.logger.info("✅ Selecionado 'Procurador' no dropdown (via value)")
                        break
                    except:
                        continue

            # Se não conseguiu com select, tentar clicar no dropdown primeiro
            if not selecionou_procurador:
                self.logger.info("Tentando clicar no dropdown primeiro...")
                try:
                    # Procurar por elementos que parecem dropdowns
                    dropdown_clicaveis = [
                        ".br-select",
                        "br-select",
                        "[class*='select']",
                        "[class*='dropdown']"
                    ]

                    for seletor in dropdown_clicaveis:
                        try:
                            elemento = await self.page.query_selector(seletor)
                            if elemento and await elemento.is_visible():
                                await elemento.click()
                                await asyncio.sleep(1)

                                # Agora tentar selecionar "Procurador" na lista que abriu
                                opcoes = [
                                    "text='Procurador'",
                                    "text='procurador'",
                                    "[data-value*='procurador']",
                                    "li:has-text('Procurador')",
                                    ".option:has-text('Procurador')"
                                ]

                                for opcao in opcoes:
                                    try:
                                        opcao_elem = await self.page.query_selector(opcao)
                                        if opcao_elem and await opcao_elem.is_visible():
                                            await opcao_elem.click()
                                            selecionou_procurador = True
                                            self.logger.info("✅ Selecionado 'Procurador' após clicar no dropdown")
                                            break
                                    except:
                                        continue

                                if selecionou_procurador:
                                    break
                        except:
                            continue
                except Exception as e:
                    self.logger.debug(f"Erro ao tentar dropdown clicável: {str(e)}")

            # Fallback via JavaScript
            if not selecionou_procurador:
                self.logger.info("Tentando selecionar 'Procurador' via JavaScript...")
                resultado = await self.page.evaluate("""
                    () => {
                        // Tentar selects
                        const selects = document.querySelectorAll('select');
                        for (const select of selects) {
                            for (const option of select.options) {
                                if (option.text.toLowerCase().includes('procurador')) {
                                    select.value = option.value;
                                    select.dispatchEvent(new Event('change', { bubbles: true }));
                                    return { success: true, tipo: 'select', texto: option.text };
                                }
                            }
                        }

                        // Tentar clicar em opção visível
                        const opcoes = document.querySelectorAll('li, .option, [role="option"]');
                        for (const opcao of opcoes) {
                            if (opcao.innerText.toLowerCase().includes('procurador')) {
                                opcao.click();
                                return { success: true, tipo: 'option', texto: opcao.innerText };
                            }
                        }

                        return { success: false };
                    }
                """)

                if resultado.get('success'):
                    selecionou_procurador = True
                    self.logger.info(f"✅ Selecionado via JavaScript: {resultado.get('texto')}")

            if not selecionou_procurador:
                self.logger.error("❌ Não foi possível selecionar 'Procurador' na primeira linha")
                await self._screenshot_erro("procurador_dropdown_nao_encontrado")
                return False

            await asyncio.sleep(1)

            # Passo 3: SEGUNDA LINHA - Digitar CNPJ no campo
            self.logger.info("")
            self.logger.info(f"🔍 SEGUNDA LINHA: Procurando campo para digitar CNPJ: {cnpj}")

            seletores_cnpj = [
                "input[name*='cnpj']",
                "input[id*='cnpj']",
                "input[placeholder*='CNPJ']",
                "input[placeholder*='cnpj']",
                "input[type='text'][name*='empresa']",
                "input[type='text'][id*='empresa']",
                "input[type='text']",  # Segundo input text (após o select)
                "input[type='number']"
            ]

            digitou_cnpj = False

            for seletor in seletores_cnpj:
                try:
                    elementos = await self.page.query_selector_all(seletor)
                    for elemento in elementos:
                        if await elemento.is_visible():
                            # Limpar campo primeiro
                            await elemento.fill("")
                            # Digitar CNPJ
                            await elemento.fill(cnpj)
                            digitou_cnpj = True
                            self.logger.info(f"✅ CNPJ digitado na segunda linha: {cnpj}")
                            break
                    if digitou_cnpj:
                        break
                except Exception as e:
                    continue

            if not digitou_cnpj:
                self.logger.error("❌ Não foi possível encontrar campo para digitar CNPJ na segunda linha")
                await self._screenshot_erro("campo_cnpj_nao_encontrado")
                return False

            await asyncio.sleep(1)

            # Passo 4: Clicar em "Selecionar"
            self.logger.info("")
            self.logger.info("🔍 Procurando botão 'Selecionar'...")

            seletores_selecionar = [
                "button:has-text('Selecionar')",
                "button:has-text('selecionar')",
                "a:has-text('Selecionar')",
                "input[value='Selecionar']",
                "button:has-text('Definir')",  # Fallback
                "button:has-text('Confirmar')",  # Fallback
                "button[type='submit']"
            ]

            selecionado = False

            for seletor in seletores_selecionar:
                try:
                    elemento = await self.page.query_selector(seletor)
                    if elemento and await elemento.is_visible():
                        texto = await elemento.inner_text() if hasattr(elemento, 'inner_text') else await elemento.get_attribute('value')
                        await elemento.click()
                        selecionado = True
                        self.logger.info(f"✅ Clicado em '{texto}'!")
                        break
                except:
                    continue

            if not selecionado:
                # Tentar via JavaScript
                self.logger.info("Tentando clicar em 'Selecionar' via JavaScript...")
                resultado = await self.page.evaluate("""
                    () => {
                        const botoes = document.querySelectorAll('button, input[type="submit"], a');
                        for (const btn of botoes) {
                            const texto = (btn.innerText || btn.value || '').toLowerCase();
                            if (texto.includes('selecionar') || texto.includes('definir') ||
                                texto.includes('confirmar') || texto.includes('ok')) {
                                btn.click();
                                return { success: true, texto: btn.innerText || btn.value };
                            }
                        }
                        return { success: false };
                    }
                """)

                if resultado.get('success'):
                    selecionado = True
                    self.logger.info(f"✅ Clicado via JavaScript: {resultado.get('texto')}")

            if not selecionado:
                self.logger.error("❌ Não foi possível clicar em botão 'Selecionar'")
                await self._screenshot_erro("selecionar_nao_encontrado")

            # Aguardar carregamento
            await asyncio.sleep(3)

            url_final = self.page.url
            self.logger.info(f"📍 URL após trocar perfil: {url_final}")

            self.logger.info("=" * 70)
            self.logger.info("✅ Troca de perfil concluída!")
            self.logger.info("=" * 70)

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao trocar perfil: {str(e)}")
            self.logger.exception("Traceback:")
            await self._screenshot_erro("erro_trocar_perfil")
            return False

    async def _buscar_competencias_em_aberto(self) -> List[str]:
        """
        Navega até Gestão de Guias > Emissão de Guia Rápida
        e busca competências em aberto no dropdown de Competência de Apuração

        Returns:
            List[str]: Lista de competências em aberto encontradas
        """
        try:
            self.logger.info("=" * 70)
            self.logger.info("📋 BUSCANDO COMPETÊNCIAS EM ABERTO...")
            self.logger.info("=" * 70)

            competencias = []

            # Passo 1: Clicar em "Gestão de Guias"
            self.logger.info("")
            self.logger.info("🔍 Passo 1: Procurando 'Gestão de Guias'...")

            seletores_gestao_guias = [
                "text='Gestão de Guias'",
                "text='GESTÃO DE GUIAS'",
                "text='Gestão de guias'",
                "div:has-text('GESTÃO DE GUIAS')",
                "a:has-text('Gestão de Guias')",
                ".cardListItem:has-text('GESTÃO DE GUIAS')",
                ".amplo:has-text('GESTÃO DE GUIAS')"
            ]

            clicou_gestao = False
            for seletor in seletores_gestao_guias:
                try:
                    elemento = await self.page.query_selector(seletor)
                    if elemento and await elemento.is_visible():
                        await elemento.click()
                        clicou_gestao = True
                        self.logger.info("✅ Clicado em 'Gestão de Guias'!")
                        break
                except:
                    continue

            if not clicou_gestao:
                # Tentar via JavaScript
                self.logger.info("Tentando clicar via JavaScript...")
                resultado = await self.page.evaluate("""
                    () => {
                        const elementos = document.querySelectorAll('div, a, button, span');
                        for (const el of elementos) {
                            const texto = (el.innerText || '').toLowerCase();
                            if (texto.includes('gestão de guias')) {
                                el.click();
                                return { success: true, texto: el.innerText };
                            }
                        }
                        return { success: false };
                    }
                """)

                if resultado.get('success'):
                    clicou_gestao = True
                    self.logger.info(f"✅ Clicado via JavaScript: {resultado.get('texto')}")

            if not clicou_gestao:
                self.logger.error("❌ Não foi possível encontrar 'Gestão de Guias'")
                await self._screenshot_erro("gestao_guias_nao_encontrado")
                return []

            # Aguardar carregamento
            await asyncio.sleep(3)

            # Passo 2: Clicar em "Emissão de Guia Rápida"
            self.logger.info("")
            self.logger.info("🔍 Passo 2: Procurando 'Emissão de Guia Rápida'...")

            seletores_emissao = [
                "text='Emissão de Guia Rápida'",
                "text='EMISSÃO DE GUIA RÁPIDA'",
                "text='Emissão de guia rápida'",
                "a:has-text('Emissão de Guia Rápida')",
                "button:has-text('Emissão de Guia Rápida')",
                "div:has-text('Emissão de Guia Rápida')",
                "[href*='emissao']",
                "[href*='guia-rapida']"
            ]

            clicou_emissao = False
            for seletor in seletores_emissao:
                try:
                    elemento = await self.page.query_selector(seletor)
                    if elemento and await elemento.is_visible():
                        await elemento.click()
                        clicou_emissao = True
                        self.logger.info("✅ Clicado em 'Emissão de Guia Rápida'!")
                        break
                except:
                    continue

            if not clicou_emissao:
                # Tentar via JavaScript
                self.logger.info("Tentando clicar via JavaScript...")
                resultado = await self.page.evaluate("""
                    () => {
                        const elementos = document.querySelectorAll('a, button, div, span');
                        for (const el of elementos) {
                            const texto = (el.innerText || '').toLowerCase();
                            if (texto.includes('emissão de guia rápida') ||
                                texto.includes('emissao de guia rapida')) {
                                el.click();
                                return { success: true, texto: el.innerText };
                            }
                        }
                        return { success: false };
                    }
                """)

                if resultado.get('success'):
                    clicou_emissao = True
                    self.logger.info(f"✅ Clicado via JavaScript: {resultado.get('texto')}")

            if not clicou_emissao:
                self.logger.error("❌ Não foi possível encontrar 'Emissão de Guia Rápida'")
                await self._screenshot_erro("emissao_guia_rapida_nao_encontrado")
                return []

            # Aguardar carregamento da página de emissão (SPA precisa de mais tempo)
            self.logger.info("⏳ Aguardando carregamento completo da página...")
            self.logger.info(f"📍 URL atual: {self.page.url}")

            # Esperar tempo inicial (aumentado para SPAs lentas)
            self.logger.info("⏳ Aguardando 8 segundos iniciais...")
            await asyncio.sleep(8)

            # Tentar esperar por elementos específicos aparecerem
            self.logger.info("⏳ Aguardando elementos da página carregarem (timeout: 30s)...")
            tentativas = 0
            elementos_encontrados = False

            while tentativas < 3 and not elementos_encontrados:
                tentativas += 1
                try:
                    # Esperar por qualquer label, input ou select aparecer (timeout 30 segundos)
                    await self.page.wait_for_selector('label, input, select, button, div[class*="form"]', timeout=30000)
                    self.logger.info("✓ Elementos encontrados, página carregada!")
                    elementos_encontrados = True
                except Exception as e:
                    if tentativas < 3:
                        self.logger.warning(f"⚠️  Tentativa {tentativas} falhou, tentando novamente...")
                        await asyncio.sleep(3)
                    else:
                        self.logger.warning(f"⚠️  Timeout aguardando elementos após {tentativas} tentativas")
                        self.logger.warning("Tentando continuar mesmo assim...")

            # Esperar mais um pouco para garantir que tudo carregou
            self.logger.info("⏳ Aguardando mais 8 segundos para garantir carregamento completo...")
            await asyncio.sleep(8)

            # Verificar se há iframes
            self.logger.info("🔍 Verificando se há iframes na página...")
            try:
                frames_info = await self.page.evaluate("""
                    () => {
                        const iframes = document.querySelectorAll('iframe');
                        return {
                            total: iframes.length,
                            urls: Array.from(iframes).map(f => f.src || f.name || 'sem URL')
                        };
                    }
                """)
                if frames_info['total'] > 0:
                    self.logger.info(f"📦 Encontrados {frames_info['total']} iframes:")
                    for i, url in enumerate(frames_info['urls'], 1):
                        self.logger.info(f"   {i}. {url}")
                else:
                    self.logger.info("   Nenhum iframe encontrado")
            except Exception as e:
                self.logger.warning(f"Erro ao verificar iframes: {str(e)}")

            # Passo 3: ANÁLISE COMPLETA DA PÁGINA
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("🔍 ANALISANDO PÁGINA 'EMISSÃO DE GUIA RÁPIDA'...")
            self.logger.info("=" * 70)

            # ANÁLISE COMPLETA DA PÁGINA
            analise_pagina = {
                "url": self.page.url,
                "titulo": await self.page.title(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "formularios": [],
                "textos_visiveis": [],
                "labels": [],
                "botoes": []
            }

            try:
                # DEBUG: Verificar HTML da página
                self.logger.info("🔍 DEBUG: Verificando HTML da página...")
                try:
                    html_info = await self.page.evaluate("""
                        () => {
                            return {
                                bodyLength: document.body ? document.body.innerHTML.length : 0,
                                bodyText: document.body ? document.body.innerText.substring(0, 500) : '',
                                elementsCount: document.querySelectorAll('*').length,
                                hasAngular: !!window.angular || !!document.querySelector('[ng-app]'),
                                hasReact: !!document.querySelector('[data-reactroot]'),
                                hasVue: !!document.querySelector('[data-v-]')
                            };
                        }
                    """)
                    self.logger.info(f"   Tamanho do HTML body: {html_info['bodyLength']} caracteres")
                    self.logger.info(f"   Total de elementos na página: {html_info['elementsCount']}")
                    if html_info.get('hasAngular'):
                        self.logger.info("   📦 Detectado: Angular")
                    if html_info.get('hasReact'):
                        self.logger.info("   📦 Detectado: React")
                    if html_info.get('hasVue'):
                        self.logger.info("   📦 Detectado: Vue")

                    if html_info['bodyText']:
                        self.logger.info(f"   Primeiros 200 caracteres do texto: {html_info['bodyText'][:200]}")
                    else:
                        self.logger.warning("   ⚠️  BODY está vazio!")

                    # Salvar HTML completo para análise
                    try:
                        html_completo = await self.page.content()
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        html_path = os.path.join(self.log_dir, f"html_emissao_{timestamp}.html")
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(html_completo)
                        self.logger.info(f"   💾 HTML completo salvo em: {html_path}")
                    except Exception as e:
                        self.logger.warning(f"Erro ao salvar HTML: {str(e)}")

                except Exception as e:
                    self.logger.error(f"Erro no debug HTML: {str(e)}")

                # 1. COLETAR TODOS OS DADOS DA PÁGINA
                self.logger.info("")
                self.logger.info("📊 1. Coletando informações da página...")
                dados_pagina = await self.page.evaluate("""
                    () => {
                        const dados = {
                            campos: [],
                            textos: [],
                            labels: [],
                            botoes: []
                        };

                        // === CAMPOS DE FORMULÁRIO ===

                        // Selects
                        document.querySelectorAll('select').forEach((el, i) => {
                            const label = el.closest('label') ||
                                         document.querySelector(`label[for="${el.id}"]`);

                            const opcoes = [];
                            if (el.options) {
                                for (let j = 0; j < el.options.length; j++) {
                                    opcoes.push({
                                        texto: el.options[j].text.trim(),
                                        valor: el.options[j].value
                                    });
                                }
                            }

                            dados.campos.push({
                                tipo: 'select',
                                id: el.id || '',
                                name: el.name || '',
                                classe: el.className || '',
                                label: label ? label.innerText.trim() : '',
                                valor: el.value || '',
                                opcoes: opcoes,
                                visivel: !!(el.offsetWidth || el.offsetHeight)
                            });
                        });

                        // Inputs
                        document.querySelectorAll('input, textarea').forEach((el, i) => {
                            const label = el.closest('label') ||
                                         document.querySelector(`label[for="${el.id}"]`);
                            dados.campos.push({
                                tipo: el.type || el.tagName.toLowerCase(),
                                id: el.id || '',
                                name: el.name || '',
                                placeholder: el.placeholder || '',
                                valor: el.value || '',
                                label: label ? label.innerText.trim() : '',
                                visivel: !!(el.offsetWidth || el.offsetHeight)
                            });
                        });

                        // === TODOS OS LABELS ===
                        document.querySelectorAll('label').forEach(label => {
                            if (label.innerText.trim() && (label.offsetWidth || label.offsetHeight)) {
                                dados.labels.push({
                                    texto: label.innerText.trim(),
                                    for: label.getAttribute('for') || ''
                                });
                            }
                        });

                        // === BOTÕES ===
                        document.querySelectorAll('button, input[type="submit"], input[type="button"]').forEach(btn => {
                            if (btn.offsetWidth || btn.offsetHeight) {
                                dados.botoes.push({
                                    texto: btn.innerText || btn.value || '',
                                    id: btn.id || '',
                                    tipo: btn.type || 'button'
                                });
                            }
                        });

                        // === TEXTOS VISÍVEIS NA PÁGINA ===
                        const elementosComTexto = document.querySelectorAll('p, div, span, h1, h2, h3, h4, h5, h6, td, th, li');
                        elementosComTexto.forEach(el => {
                            const texto = el.innerText ? el.innerText.trim() : '';
                            // Pegar apenas textos curtos (provavelmente labels ou títulos)
                            if (texto && texto.length > 0 && texto.length < 200 && (el.offsetWidth || el.offsetHeight)) {
                                // Verificar se não é apenas texto de um filho
                                const textoPropio = Array.from(el.childNodes)
                                    .filter(node => node.nodeType === 3) // Text nodes
                                    .map(node => node.textContent.trim())
                                    .join(' ');

                                if (textoPropio && textoPropio.length > 2) {
                                    dados.textos.push(textoPropio);
                                }
                            }
                        });

                        return dados;
                    }
                """)

                analise_pagina["formularios"] = dados_pagina.get("campos", [])
                analise_pagina["labels"] = dados_pagina.get("labels", [])
                analise_pagina["botoes"] = dados_pagina.get("botoes", [])
                analise_pagina["textos_visiveis"] = list(set(dados_pagina.get("textos", [])))[:50]  # Primeiros 50 únicos

                # 2. LOGAR ANÁLISE
                self.logger.info("")
                self.logger.info(f"📄 URL: {analise_pagina['url']}")
                self.logger.info(f"📄 Título: {analise_pagina['titulo']}")
                self.logger.info("")

                # CAMPOS DE FORMULÁRIO
                self.logger.info(f"📋 CAMPOS DE FORMULÁRIO ({len(analise_pagina['formularios'])} encontrados):")
                self.logger.info("")
                for i, campo in enumerate(analise_pagina['formularios'], 1):
                    if not campo.get('visivel'):
                        continue

                    visivel = "✓"
                    label = campo.get('label', '')[:60]
                    valor = campo.get('valor', '')[:40] if campo.get('valor') else ''

                    self.logger.info(f"  [{i}] {campo['tipo'].upper()}")
                    if campo.get('id'):
                        self.logger.info(f"      ID: {campo['id']}")
                    if campo.get('name'):
                        self.logger.info(f"      Name: {campo['name']}")
                    if label:
                        self.logger.info(f"      Label: {label}")
                    if valor:
                        self.logger.info(f"      Valor: {valor}")
                    if campo.get('placeholder'):
                        self.logger.info(f"      Placeholder: {campo['placeholder']}")
                    if campo.get('opcoes') and len(campo['opcoes']) > 0:
                        self.logger.info(f"      Opções ({len(campo['opcoes'])}):")
                        for j, opcao in enumerate(campo['opcoes'][:10], 1):  # Mostrar primeiras 10
                            self.logger.info(f"         {j}. {opcao['texto']} = {opcao['valor']}")
                        if len(campo['opcoes']) > 10:
                            self.logger.info(f"         ... e mais {len(campo['opcoes']) - 10} opções")
                    self.logger.info("")

                # LABELS
                self.logger.info(f"🏷️  LABELS ({len(analise_pagina['labels'])} encontrados):")
                for i, label in enumerate(analise_pagina['labels'][:20], 1):
                    self.logger.info(f"  {i}. {label['texto'][:80]}")
                    if label.get('for'):
                        self.logger.info(f"      → Aponta para: {label['for']}")
                if len(analise_pagina['labels']) > 20:
                    self.logger.info(f"  ... e mais {len(analise_pagina['labels']) - 20} labels")
                self.logger.info("")

                # BOTÕES
                self.logger.info(f"🔘 BOTÕES ({len(analise_pagina['botoes'])} encontrados):")
                for i, botao in enumerate(analise_pagina['botoes'], 1):
                    texto = botao['texto'][:50] if botao['texto'] else '(sem texto)'
                    self.logger.info(f"  {i}. {texto} - ID: {botao.get('id', 'N/A')}")
                self.logger.info("")

                # TEXTOS VISÍVEIS
                self.logger.info(f"📝 TEXTOS VISÍVEIS NA PÁGINA (primeiros 30):")
                for i, texto in enumerate(analise_pagina['textos_visiveis'][:30], 1):
                    self.logger.info(f"  {i}. {texto[:100]}")
                self.logger.info("")

            except Exception as e:
                self.logger.error(f"Erro ao analisar página: {str(e)}")
                self.logger.exception("Traceback:")

            # 3. SALVAR ANÁLISE EM JSON
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                analise_path = os.path.join(self.log_dir, f"analise_pagina_emissao_{timestamp}.json")

                with open(analise_path, 'w', encoding='utf-8') as f:
                    json.dump(analise_pagina, f, ensure_ascii=False, indent=2)

                self.logger.info(f"💾 Análise completa salva em: {analise_path}")
            except Exception as e:
                self.logger.warning(f"Erro ao salvar análise: {str(e)}")

            # 4. TIRAR SCREENSHOT
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(self.log_dir, f"pagina_emissao_{timestamp}.png")
                await self.page.screenshot(path=screenshot_path, full_page=True)
                self.logger.info(f"📸 Screenshot salvo: {screenshot_path}")
            except Exception as e:
                self.logger.warning(f"Erro ao tirar screenshot: {str(e)}")

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✅ ANÁLISE DA PÁGINA CONCLUÍDA!")
            self.logger.info("=" * 70)

            # AGORA VAMOS EXTRAIR AS COMPETÊNCIAS
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📋 EXTRAINDO COMPETÊNCIAS EM ABERTO...")
            self.logger.info("=" * 70)

            competencias = []

            try:
                # Procurar campo de competência pelo ID
                self.logger.info("🔍 Procurando campo 'selectCompetencia'...")
                campo_competencia = await self.page.query_selector('#selectCompetencia')

                if not campo_competencia:
                    self.logger.error("❌ Campo 'selectCompetencia' não encontrado")
                    await self._screenshot_erro("campo_competencia_nao_encontrado")
                    return []

                self.logger.info("✅ Campo encontrado!")

                # Clicar no campo para abrir o dropdown
                self.logger.info("🖱️  Clicando no campo para abrir dropdown...")
                await campo_competencia.click()

                # Aguardar dropdown abrir
                self.logger.info("⏳ Aguardando dropdown abrir (5 segundos)...")
                await asyncio.sleep(5)

                # Procurar lista de opções que apareceu
                self.logger.info("🔍 Procurando lista de opções...")

                # Tentar vários seletores para encontrar o dropdown
                opcoes_encontradas = await self.page.evaluate("""
                    () => {
                        const opcoes = [];
                        const regexCompetencia = /^\d{2}\/\d{4}$/; // Formato MM/YYYY

                        // Procurar por listas visíveis (ul, ol, div com role listbox, etc)
                        const listas = document.querySelectorAll('ul, ol, [role="listbox"], [role="menu"], .dropdown-menu, .options, .select-options');

                        for (const lista of listas) {
                            // Verificar se está visível
                            if (!(lista.offsetWidth || lista.offsetHeight || lista.getClientRects().length)) {
                                continue;
                            }

                            // Pegar itens da lista
                            const itens = lista.querySelectorAll('li, [role="option"], .option, .item');

                            for (const item of itens) {
                                const texto = item.innerText ? item.innerText.trim() : '';
                                const valor = item.getAttribute('data-value') ||
                                             item.getAttribute('value') ||
                                             texto;

                                // FILTRAR: Só adicionar se for no formato MM/YYYY
                                if (texto && regexCompetencia.test(texto)) {
                                    opcoes.push({
                                        texto: texto,
                                        valor: valor
                                    });
                                }
                            }

                            // Se encontrou opções, sair
                            if (opcoes.length > 0) {
                                break;
                            }
                        }

                        return opcoes;
                    }
                """)

                if opcoes_encontradas and len(opcoes_encontradas) > 0:
                    self.logger.info(f"✅ Encontradas {len(opcoes_encontradas)} competências:")
                    for i, opcao in enumerate(opcoes_encontradas, 1):
                        competencias.append(opcao['texto'])
                        self.logger.info(f"  {i}. {opcao['texto']}")
                else:
                    # Tentar método alternativo: verificar se há um select oculto
                    self.logger.warning("⚠️  Dropdown não encontrado visualmente, tentando método alternativo...")

                    # Procurar por select associado ou datalist
                    opcoes_alternativas = await self.page.evaluate("""
                        () => {
                            const opcoes = [];
                            const regexCompetencia = /^\d{2}\/\d{4}$/; // Formato MM/YYYY

                            // Procurar datalist associado ao input
                            const input = document.getElementById('selectCompetencia');
                            if (input && input.getAttribute('list')) {
                                const datalistId = input.getAttribute('list');
                                const datalist = document.getElementById(datalistId);

                                if (datalist) {
                                    const options = datalist.querySelectorAll('option');
                                    for (const opt of options) {
                                        const texto = opt.innerText || opt.value;
                                        if (texto && regexCompetencia.test(texto.trim())) {
                                            opcoes.push({
                                                texto: texto.trim(),
                                                valor: opt.value || texto.trim()
                                            });
                                        }
                                    }
                                }
                            }

                            // Procurar por divs/spans que possam conter as opções no formato MM/YYYY
                            if (opcoes.length === 0) {
                                const allElements = document.querySelectorAll('div, span, li, td');
                                const competenciasUnicas = new Set();

                                for (const el of allElements) {
                                    const texto = el.innerText ? el.innerText.trim() : '';
                                    // Verificar se parece uma competência (MM/YYYY) e está visível
                                    if (regexCompetencia.test(texto) && (el.offsetWidth || el.offsetHeight)) {
                                        if (!competenciasUnicas.has(texto)) {
                                            competenciasUnicas.add(texto);
                                            opcoes.push({
                                                texto: texto,
                                                valor: texto
                                            });
                                        }
                                    }
                                }
                            }

                            return opcoes;
                        }
                    """)

                    if opcoes_alternativas and len(opcoes_alternativas) > 0:
                        self.logger.info(f"✅ Encontradas {len(opcoes_alternativas)} competências (método alternativo):")
                        for i, opcao in enumerate(opcoes_alternativas, 1):
                            competencias.append(opcao['texto'])
                            self.logger.info(f"  {i}. {opcao['texto']}")
                    else:
                        self.logger.warning("⚠️  Nenhuma opção encontrada")

            except Exception as e:
                self.logger.error(f"❌ Erro ao extrair competências: {str(e)}")
                self.logger.exception("Traceback:")
                await self._screenshot_erro("erro_extrair_competencias")

            # Salvar competências em arquivo
            if competencias:
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    competencias_path = os.path.join(self.log_dir, f"competencias_em_aberto_{timestamp}.json")

                    dados = {
                        "timestamp": timestamp,
                        "total": len(competencias),
                        "competencias": competencias
                    }

                    with open(competencias_path, 'w', encoding='utf-8') as f:
                        json.dump(dados, f, ensure_ascii=False, indent=2)

                    self.logger.info(f"💾 Competências salvas em: {competencias_path}")
                except Exception as e:
                    self.logger.warning(f"Erro ao salvar arquivo: {str(e)}")

                # Tirar screenshot final
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = os.path.join(self.log_dir, f"competencias_tela_{timestamp}.png")
                    await self.page.screenshot(path=screenshot_path, full_page=True)
                    self.logger.info(f"📸 Screenshot salvo: {screenshot_path}")
                except Exception as e:
                    self.logger.warning(f"Erro ao tirar screenshot: {str(e)}")

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info(f"✅ Total de competências encontradas: {len(competencias)}")
            self.logger.info("=" * 70)

            return competencias

        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar competências: {str(e)}")
            self.logger.exception("Traceback:")
            await self._screenshot_erro("erro_buscar_competencias")
            return []

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

            # 5. PROCURAR TODOS OS ELEMENTOS CLICÁVEIS (ABRANGENTE)
            self.logger.info("🔍 Procurando TODOS os elementos clicáveis...")
            todos_clicaveis = await self.page.evaluate("""
                () => {
                    const clicaveis = [];
                    // Procurar por: a, button, div/span com onclick, elementos com cursor pointer
                    const seletores = 'a, button, [onclick], [role="button"], [class*="btn"], [class*="card"], [class*="link"], [class*="item"], div[style*="cursor"], span[style*="cursor"]';

                    document.querySelectorAll(seletores).forEach((el) => {
                        // Verificar se elemento está visível
                        const rect = el.getBoundingClientRect();
                        const isVisible = rect.width > 0 && rect.height > 0 &&
                                         window.getComputedStyle(el).display !== 'none' &&
                                         window.getComputedStyle(el).visibility !== 'hidden';

                        if (isVisible) {
                            const texto = el.innerText || el.textContent || el.getAttribute('aria-label') || el.getAttribute('title') || '';
                            const textoLimpo = texto.trim();

                            if (textoLimpo) {
                                clicaveis.push({
                                    tipo: el.tagName.toLowerCase(),
                                    texto: textoLimpo.substring(0, 100),
                                    href: el.href || '',
                                    id: el.id || '',
                                    class: el.className || '',
                                    onclick: el.onclick ? 'sim' : 'não',
                                    ariaLabel: el.getAttribute('aria-label') || '',
                                    dataAttributes: Object.keys(el.dataset || {}).length > 0 ?
                                        JSON.stringify(el.dataset).substring(0, 100) : ''
                                });
                            }
                        }
                    });

                    return clicaveis;
                }
            """)

            info["todos_clicaveis"] = todos_clicaveis

            if todos_clicaveis:
                self.logger.info(f"✓ Encontrados {len(todos_clicaveis)} elementos clicáveis no total:")
                for i, elem in enumerate(todos_clicaveis[:20], 1):
                    self.logger.info(f"  {i}. [{elem['tipo'].upper()}] {elem['texto']}")
                    if elem['href']:
                        self.logger.info(f"      → {elem['href']}")
                    if elem['id']:
                        self.logger.info(f"      ID: {elem['id']}")
                if len(todos_clicaveis) > 20:
                    self.logger.info(f"  ... e mais {len(todos_clicaveis) - 20} elementos")
            else:
                self.logger.info("⚠️  Nenhum elemento clicável encontrado")

            self.logger.info("")

            # 6. PROCURAR ESPECIFICAMENTE POR ELEMENTOS COM "GUIAS"
            self.logger.info("🔍 Procurando elementos específicos com 'GUIAS'...")
            elementos_guias = await self.page.evaluate("""
                () => {
                    const guias = [];
                    const todosElementos = document.querySelectorAll('*');

                    todosElementos.forEach((el) => {
                        const texto = (el.innerText || el.textContent || '').toLowerCase();
                        const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                        const title = (el.getAttribute('title') || '').toLowerCase();
                        const id = (el.id || '').toLowerCase();
                        const className = (el.className || '').toLowerCase();

                        // Verificar se contém "guia" em qualquer lugar
                        if (texto.includes('guia') || ariaLabel.includes('guia') ||
                            title.includes('guia') || id.includes('guia') || className.includes('guia')) {

                            // Verificar se é clicável
                            const tagName = el.tagName.toLowerCase();
                            const isClickable = tagName === 'a' || tagName === 'button' ||
                                               el.onclick || el.getAttribute('role') === 'button' ||
                                               className.includes('btn') || className.includes('link') ||
                                               className.includes('card') || className.includes('item');

                            // Verificar se está visível
                            const rect = el.getBoundingClientRect();
                            const isVisible = rect.width > 0 && rect.height > 0;

                            if (isVisible) {
                                guias.push({
                                    tipo: tagName,
                                    texto: (el.innerText || el.textContent || '').trim().substring(0, 100),
                                    href: el.href || '',
                                    id: el.id || '',
                                    class: el.className || '',
                                    clicavel: isClickable ? 'SIM' : 'NÃO',
                                    ariaLabel: el.getAttribute('aria-label') || '',
                                    title: el.getAttribute('title') || '',
                                    onclick: el.onclick ? 'sim' : 'não'
                                });
                            }
                        }
                    });

                    return guias;
                }
            """)

            info["elementos_guias"] = elementos_guias

            if elementos_guias:
                self.logger.info(f"✓ Encontrados {len(elementos_guias)} elementos relacionados a 'guias':")
                for i, elem in enumerate(elementos_guias, 1):
                    clicavel_icon = "🔘" if elem['clicavel'] == 'SIM' else "⚪"
                    self.logger.info(f"  {i}. {clicavel_icon} [{elem['tipo'].upper()}] {elem['texto']}")
                    if elem['href']:
                        self.logger.info(f"      → URL: {elem['href']}")
                    if elem['id']:
                        self.logger.info(f"      → ID: {elem['id']}")
                    if elem['class']:
                        self.logger.info(f"      → Classes: {elem['class'][:100]}")
                    if elem['ariaLabel']:
                        self.logger.info(f"      → Aria-Label: {elem['ariaLabel']}")
                    self.logger.info(f"      → Clicável: {elem['clicavel']}")
            else:
                self.logger.info("⚠️  Nenhum elemento com 'guias' encontrado")

            self.logger.info("")

            # 7. PROCURAR PALAVRAS-CHAVE RELACIONADAS A FGTS/GUIAS
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

            # 8. TIRAR SCREENSHOT DA PÁGINA EXPLORADA
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(self.log_dir, f"pagina_inicial_{timestamp}.png")
                await self.page.screenshot(path=screenshot_path, full_page=True)
                self.logger.info(f"📸 Screenshot salvo: {screenshot_path}")
            except Exception as e:
                self.logger.warning(f"Erro ao tirar screenshot: {str(e)}")

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✓ Exploração concluída!")
            self.logger.info("=" * 70)

            return info

        except Exception as e:
            self.logger.error(f"Erro ao explorar página: {str(e)}")
            return {}

    async def _explorar_navegacao_completa(self) -> Dict[str, Any]:
        """
        Explora a navegação completa do site clicando em todos os elementos clicáveis

        Para cada elemento:
        1. Clica no elemento
        2. Aguarda carregamento
        3. Mapeia a nova página (URL, título, elementos)
        4. Tira screenshot
        5. Volta à página anterior
        6. Salva informações

        Returns:
            dict: Mapeamento completo da navegação do site
        """
        try:
            self.logger.info("=" * 70)
            self.logger.info("🧭 EXPLORANDO NAVEGAÇÃO COMPLETA DO SITE...")
            self.logger.info("=" * 70)

            navegacao_completa = {
                "url_inicial": self.page.url,
                "timestamp": datetime.now().isoformat(),
                "paginas_exploradas": []
            }

            # Pegar URL inicial para poder voltar
            url_inicial = self.page.url

            # Encontrar todos os elementos clicáveis da página inicial
            self.logger.info("")
            self.logger.info("🔍 Identificando elementos clicáveis na página inicial...")

            elementos_clicaveis = await self.page.evaluate("""
                () => {
                    const elementos = [];

                    // Seletores para elementos clicáveis
                    const seletores = [
                        'div.cardListItem',  // Cards de menu
                        'div[class*="card"]',
                        'a[href]',
                        'button:not([disabled])',
                        '[role="button"]'
                    ];

                    seletores.forEach(seletor => {
                        document.querySelectorAll(seletor).forEach((el, index) => {
                            // Verificar se visível
                            const rect = el.getBoundingClientRect();
                            const isVisible = rect.width > 0 && rect.height > 0 &&
                                             window.getComputedStyle(el).display !== 'none';

                            if (isVisible) {
                                const texto = (el.innerText || el.textContent || '').trim();

                                if (texto && texto.length > 0 && texto.length < 200) {
                                    elementos.push({
                                        seletor: seletor,
                                        texto: texto.substring(0, 100),
                                        id: el.id || '',
                                        class: el.className || '',
                                        href: el.href || '',
                                        tag: el.tagName.toLowerCase(),
                                        // Criar um seletor único para este elemento
                                        seletorUnico: el.id ? `#${el.id}` :
                                                     (el.className ? `.${el.className.split(' ')[0]}` : seletor)
                                    });
                                }
                            }
                        });
                    });

                    // Remover duplicatas baseado no texto
                    const unicos = [];
                    const textosVistos = new Set();

                    elementos.forEach(el => {
                        const chave = `${el.texto}_${el.tag}`;
                        if (!textosVistos.has(chave)) {
                            textosVistos.add(chave);
                            unicos.push(el);
                        }
                    });

                    return unicos;
                }
            """)

            self.logger.info(f"✓ Encontrados {len(elementos_clicaveis)} elementos únicos para explorar")

            # Filtrar elementos que queremos clicar (ignorar header, footer, etc)
            elementos_para_explorar = []
            textos_ignorar = ['trocar perfil', 'fgts digital', 'sair', 'logout', 'canais de atendimento']

            for elem in elementos_clicaveis:
                texto_lower = elem['texto'].lower()
                # Ignorar elementos genéricos
                if not any(ignorar in texto_lower for ignorar in textos_ignorar):
                    elementos_para_explorar.append(elem)

            self.logger.info(f"📋 Elementos a explorar (após filtros): {len(elementos_para_explorar)}")
            self.logger.info("")

            # Explorar cada elemento
            for i, elemento in enumerate(elementos_para_explorar, 1):
                try:
                    self.logger.info("-" * 70)
                    self.logger.info(f"🔍 Explorando {i}/{len(elementos_para_explorar)}: {elemento['texto'][:50]}")
                    self.logger.info("-" * 70)

                    # Voltar para página inicial antes de cada clique
                    if self.page.url != url_inicial:
                        await self.page.goto(url_inicial, wait_until="networkidle")
                        await asyncio.sleep(2)

                    # Tentar clicar no elemento
                    clicou = False

                    # Estratégia 1: Tentar pelo seletor único
                    try:
                        if elemento['id']:
                            await self.page.click(f"#{elemento['id']}", timeout=5000)
                            clicou = True
                        elif elemento['class']:
                            # Pegar primeira classe
                            primeira_classe = elemento['class'].split()[0]
                            # Clicar usando texto para garantir que é o elemento certo
                            await self.page.click(f".{primeira_classe}:has-text('{elemento['texto'][:30]}')", timeout=5000)
                            clicou = True
                    except Exception as e:
                        self.logger.debug(f"Tentativa 1 falhou: {str(e)[:50]}")

                    # Estratégia 2: Tentar via JavaScript
                    if not clicou:
                        try:
                            resultado = await self.page.evaluate(f"""
                                () => {{
                                    const texto = "{elemento['texto'][:30]}";
                                    const elementos = document.querySelectorAll('div, a, button');

                                    for (const el of elementos) {{
                                        if (el.innerText && el.innerText.includes(texto)) {{
                                            el.click();
                                            return {{ success: true, texto: el.innerText.substring(0, 50) }};
                                        }}
                                    }}

                                    return {{ success: false }};
                                }}
                            """)

                            if resultado.get('success'):
                                clicou = True
                                self.logger.info(f"✓ Clicado via JavaScript: {resultado.get('texto')}")
                        except Exception as e:
                            self.logger.debug(f"Tentativa 2 falhou: {str(e)[:50]}")

                    if not clicou:
                        self.logger.warning(f"⚠️  Não foi possível clicar em: {elemento['texto'][:50]}")
                        continue

                    # Aguardar navegação/carregamento
                    await asyncio.sleep(3)

                    # Capturar informações da nova página
                    url_apos_clique = self.page.url
                    titulo_apos_clique = await self.page.title()

                    self.logger.info(f"📍 Nova URL: {url_apos_clique}")
                    self.logger.info(f"📄 Título: {titulo_apos_clique}")

                    # Mapear elementos da nova página
                    elementos_nova_pagina = await self.page.evaluate("""
                        () => {
                            const info = {
                                links: [],
                                botoes: [],
                                tabelas: 0,
                                formularios: 0
                            };

                            // Links
                            document.querySelectorAll('a[href]').forEach(a => {
                                const texto = (a.innerText || '').trim();
                                if (texto && texto.length < 100) {
                                    info.links.push({
                                        texto: texto.substring(0, 50),
                                        href: a.href
                                    });
                                }
                            });

                            // Botões
                            document.querySelectorAll('button').forEach(btn => {
                                const texto = (btn.innerText || '').trim();
                                if (texto) {
                                    info.botoes.push(texto.substring(0, 50));
                                }
                            });

                            // Tabelas
                            info.tabelas = document.querySelectorAll('table').length;

                            // Formulários
                            info.formularios = document.querySelectorAll('form').length;

                            return info;
                        }
                    """)

                    self.logger.info(f"  → {len(elementos_nova_pagina['links'])} links")
                    self.logger.info(f"  → {len(elementos_nova_pagina['botoes'])} botões")
                    self.logger.info(f"  → {elementos_nova_pagina['tabelas']} tabelas")
                    self.logger.info(f"  → {elementos_nova_pagina['formularios']} formulários")

                    # Tirar screenshot
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nome_arquivo = elemento['texto'][:30].replace(' ', '_').replace('/', '_')
                        screenshot_path = os.path.join(self.log_dir, f"nav_{i:02d}_{nome_arquivo}_{timestamp}.png")
                        await self.page.screenshot(path=screenshot_path, full_page=True)
                        self.logger.info(f"📸 Screenshot: {os.path.basename(screenshot_path)}")
                    except Exception as e:
                        self.logger.warning(f"Erro ao tirar screenshot: {str(e)[:50]}")
                        screenshot_path = ""

                    # Salvar informações
                    navegacao_completa["paginas_exploradas"].append({
                        "indice": i,
                        "elemento_clicado": {
                            "texto": elemento['texto'],
                            "tag": elemento['tag'],
                            "id": elemento['id'],
                            "class": elemento['class']
                        },
                        "url": url_apos_clique,
                        "titulo": titulo_apos_clique,
                        "elementos": elementos_nova_pagina,
                        "screenshot": screenshot_path
                    })

                    self.logger.info(f"✅ Exploração {i} concluída")

                except Exception as e:
                    self.logger.error(f"❌ Erro ao explorar elemento {i}: {str(e)}")
                    continue

            # Voltar para página inicial
            self.logger.info("")
            self.logger.info("🏠 Retornando à página inicial...")
            await self.page.goto(url_inicial, wait_until="networkidle")
            await asyncio.sleep(2)

            # Salvar mapeamento completo em JSON
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_path = os.path.join(self.log_dir, f"navegacao_completa_{timestamp}.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(navegacao_completa, f, ensure_ascii=False, indent=2)
                self.logger.info(f"💾 Mapeamento completo salvo: {json_path}")
            except Exception as e:
                self.logger.warning(f"Erro ao salvar JSON: {str(e)}")

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info(f"✅ Exploração completa finalizada!")
            self.logger.info(f"   Total de páginas exploradas: {len(navegacao_completa['paginas_exploradas'])}")
            self.logger.info("=" * 70)

            return navegacao_completa

        except Exception as e:
            self.logger.error(f"Erro na exploração completa: {str(e)}")
            self.logger.exception("Traceback:")
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
                    exploracao_path = config.LOGS_DIR / f"exploracao_site_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(exploracao_path, 'w', encoding='utf-8') as f:
                        json.dump(info_site, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"📄 Informações de exploração salvas em: {exploracao_path}")

            except Exception as e:
                self.logger.warning(f"Erro durante exploração: {str(e)}")
                self.logger.warning("Continuando com processamento...")

            # Explorar navegação completa (clicar em todos os botões)
            # DESABILITADO TEMPORARIAMENTE - Focando em trocar perfil
            # try:
            #     self.logger.info("")
            #     navegacao = await self._explorar_navegacao_completa()
            #
            # except Exception as e:
            #     self.logger.warning(f"Erro durante exploração de navegação: {str(e)}")
            #     self.logger.warning("Continuando com processamento...")

            self.logger.info("")

            # Trocar perfil para procurador (para cada CNPJ)
            # Isso permite acessar dados das empresas via procuração eletrônica
            for cnpj in lista_cnpj:
                try:
                    self.logger.info("")
                    await self._trocar_perfil_procurador(cnpj)
                    break  # Só precisa trocar uma vez para a primeira empresa
                except Exception as e:
                    self.logger.warning(f"Erro ao trocar perfil para {cnpj}: {str(e)}")
                    self.logger.warning("Continuando com processamento...")

            self.logger.info("")

            # Buscar competências em aberto
            try:
                self.logger.info("")
                competencias_encontradas = await self._buscar_competencias_em_aberto()

                if competencias_encontradas:
                    self.logger.info(f"✅ Total de competências em aberto: {len(competencias_encontradas)}")
                else:
                    self.logger.warning("⚠️  Nenhuma competência em aberto encontrada")

            except Exception as e:
                self.logger.warning(f"Erro ao buscar competências: {str(e)}")
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
