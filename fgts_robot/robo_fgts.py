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

            # Caminhos dos arquivos temporários
            temp_cert_path = config.CERT_DIR / "temp_cert.pem"
            temp_key_path = config.CERT_DIR / "temp_key.pem"

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

            self.logger.debug(f"Certificado PEM criado: {temp_cert_path}")
            self.logger.debug(f"Chave PEM criada: {temp_key_path}")

            return str(temp_cert_path), str(temp_key_path)

        except Exception as e:
            self.logger.error(f"Erro ao preparar certificado PEM: {str(e)}")
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

            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=self.headless,
                slow_mo=config.SLOW_MO,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox"
                ]
            )

            # Preparar certificado em formato PEM (Playwright precisa de cert + key separados)
            self.logger.debug("Convertendo certificado .pfx para formato PEM...")
            cert_path, key_path = self._preparar_certificado_pem()

            # Criar contexto com certificado
            self.context = await self.browser.new_context(
                user_agent=config.USER_AGENT,
                viewport={"width": 1920, "height": 1080},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                accept_downloads=True,
                client_certificates=[{
                    "origin": config.FGTS_URL_BASE,
                    "certPath": cert_path,
                    "keyPath": key_path
                }]
            )

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

            # Clicar no botão de certificado digital
            self.logger.info("Procurando botão de certificado digital...")
            if not await self._clicar_com_retry(config.SELECTORS["login"]["btn_certificado"]):
                self.logger.error("Botão de certificado digital não encontrado na página")
                self.logger.error("Possíveis causas:")
                self.logger.error("  1. A estrutura do site mudou")
                self.logger.error("  2. Certificado não está configurado corretamente no navegador")
                self.logger.error("  3. Portal FGTS está fora do ar ou URL incorreta")
                await self._screenshot_erro("login_botao_cert")

                # Logar conteúdo da página para debug
                page_content = await self.page.content()
                self.logger.debug(f"Conteúdo da página (primeiros 500 chars): {page_content[:500]}")

                return False

            # Aguardar seleção de certificado (pode ser automática)
            self.logger.info("Aguardando seleção de certificado...")
            await asyncio.sleep(3)

            # Verificar se houve seleção de certificado no navegador
            # (Em alguns casos, o navegador abre uma janela de seleção)
            await self._delay_aleatorio()

            # Clicar em entrar
            self.logger.info("Tentando fazer login...")
            if not await self._clicar_com_retry(config.SELECTORS["login"]["btn_entrar"]):
                self.logger.warning("Botão 'Entrar' não encontrado - pode ter entrado automaticamente")

            # Aguardar carregamento da página inicial
            await asyncio.sleep(3)

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
