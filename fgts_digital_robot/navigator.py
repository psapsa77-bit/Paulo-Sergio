"""
Módulo de navegação no portal FGTS Digital
==========================================

Gerencia a navegação automatizada no portal usando Playwright,
incluindo login, alternância entre empresas e navegação por menus.
"""

import logging
import time
from typing import List, Optional, Dict, Any
from playwright.sync_api import (
    sync_playwright,
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PlaywrightTimeoutError
)

from .models import EmpresaFGTS
from .authenticator import FGTSAuthenticator

logger = logging.getLogger(__name__)


class FGTSNavigator:
    """
    Gerencia navegação automatizada no portal FGTS Digital.
    """

    # Timeouts em milissegundos
    TIMEOUT_NAVEGACAO = 30000  # 30 segundos
    TIMEOUT_ELEMENTO = 10000   # 10 segundos
    TIMEOUT_LOGIN = 60000      # 60 segundos (certificado pode demorar)

    # Seletores CSS (podem precisar ajustes conforme portal)
    SELETORES = {
        "menu_empresas": "a[href*='empresa'], button[aria-label*='empresa' i]",
        "lista_empresas": "select#empresa, div[role='listbox'], ul[role='listbox']",
        "item_empresa": "option, li[role='option'], div[data-cnpj]",
        "botao_confirmar": "button[type='submit'], button:has-text('Confirmar'), button:has-text('Acessar')",
        "menu_guias": "a[href*='guia'], a:has-text('Guias')",
        "tabela_guias": "table, div[role='grid']",
        "logout": "a[href*='logout'], button:has-text('Sair')",
    }

    def __init__(self, authenticator: FGTSAuthenticator, headless: bool = False):
        """
        Inicializa o navegador.

        Args:
            authenticator: Instância do FGTSAuthenticator configurado
            headless: Se True, executa navegador em modo headless (sem interface gráfica)
        """
        self.authenticator = authenticator
        self.headless = headless

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self._empresa_atual: Optional[EmpresaFGTS] = None

    def iniciar_navegador(self) -> None:
        """
        Inicia o navegador Playwright com configuração de certificado.

        Raises:
            Exception: Se falhar ao iniciar o navegador
        """
        try:
            logger.info("Iniciando navegador Playwright...")

            self.playwright = sync_playwright().start()

            # Iniciar navegador Chromium
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )

            # Criar contexto com certificado digital
            cert_config = self.authenticator.obter_configuracao_playwright()

            self.context = self.browser.new_context(
                client_certificates=[cert_config],
                extra_http_headers=self.authenticator.get_headers_autenticacao(),
                viewport={'width': 1920, 'height': 1080},
                locale='pt-BR',
                timezone_id='America/Sao_Paulo',
                ignore_https_errors=False,  # Validar certificados SSL
            )

            # Criar nova página
            self.page = self.context.new_page()

            # Configurar timeouts padrão
            self.page.set_default_timeout(self.TIMEOUT_NAVEGACAO)

            logger.info("Navegador iniciado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao iniciar navegador: {e}")
            self.fechar_navegador()
            raise

    def acessar_portal(self) -> bool:
        """
        Acessa o portal FGTS Digital e realiza login com certificado.

        Returns:
            True se login foi bem-sucedido, False caso contrário

        Raises:
            Exception: Se falhar ao acessar o portal
        """
        if not self.page:
            raise RuntimeError("Navegador não foi iniciado. Chame iniciar_navegador() primeiro.")

        try:
            logger.info(f"Acessando portal FGTS Digital: {self.authenticator.URL_LOGIN}")

            # Navegar para página de login
            self.page.goto(self.authenticator.URL_LOGIN, wait_until='networkidle', timeout=self.TIMEOUT_LOGIN)

            # Aguardar redirecionamento após seleção de certificado
            # O navegador deve mostrar popup de seleção de certificado automaticamente
            time.sleep(3)

            # Verificar se está na página do portal (após login)
            url_atual = self.page.url
            if self.authenticator.verificar_autenticacao(url_atual):
                logger.info("Login realizado com sucesso!")
                return True

            # Tentar aguardar elemento do portal
            try:
                self.page.wait_for_selector(
                    self.SELETORES["menu_empresas"],
                    timeout=self.TIMEOUT_LOGIN
                )
                logger.info("Portal carregado com sucesso")
                return True
            except PlaywrightTimeoutError:
                logger.warning("Timeout aguardando carregamento do portal")
                # Pode estar autenticado mesmo assim
                return "fgtsdigital" in self.page.url.lower()

        except Exception as e:
            logger.error(f"Erro ao acessar portal: {e}")
            # Salvar screenshot para debug
            try:
                screenshot_path = f"/tmp/fgts_erro_login_{int(time.time())}.png"
                self.page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot salvo em: {screenshot_path}")
            except:
                pass
            return False

    def listar_empresas_disponiveis(self) -> List[EmpresaFGTS]:
        """
        Lista todas as empresas disponíveis (com procuração).

        Returns:
            Lista de objetos EmpresaFGTS

        Raises:
            RuntimeError: Se não estiver autenticado
        """
        if not self.page:
            raise RuntimeError("Navegador não foi iniciado")

        if not self.authenticator.autenticado:
            raise RuntimeError("Não está autenticado no portal")

        empresas: List[EmpresaFGTS] = []

        try:
            logger.info("Listando empresas disponíveis...")

            # Tentar encontrar seletor de empresas
            try:
                self.page.click(self.SELETORES["menu_empresas"], timeout=self.TIMEOUT_ELEMENTO)
                time.sleep(1)
            except PlaywrightTimeoutError:
                logger.warning("Menu de empresas não encontrado, tentando alternativa...")

            # Buscar lista de empresas
            lista_selector = self.SELETORES["lista_empresas"]

            try:
                self.page.wait_for_selector(lista_selector, timeout=self.TIMEOUT_ELEMENTO)
            except PlaywrightTimeoutError:
                logger.warning("Lista de empresas não encontrada com timeout padrão")
                return empresas

            # Extrair empresas
            elementos = self.page.query_selector_all(self.SELETORES["item_empresa"])

            for elemento in elementos:
                try:
                    # Extrair texto do elemento
                    texto = elemento.inner_text().strip()

                    # Extrair CNPJ (formato: XX.XXX.XXX/XXXX-XX)
                    cnpj = self._extrair_cnpj(texto)
                    if not cnpj:
                        # Tentar atributo data-cnpj
                        cnpj = elemento.get_attribute("data-cnpj")
                        if cnpj:
                            cnpj = ''.join(filter(str.isdigit, cnpj))

                    if not cnpj or len(cnpj) != 14:
                        continue

                    # Extrair razão social (resto do texto após remover CNPJ)
                    razao_social = texto.replace(cnpj, '').strip()
                    # Remover formatação de CNPJ do texto
                    for char in ['.', '/', '-']:
                        razao_social = razao_social.replace(char, ' ')
                    razao_social = ' '.join(razao_social.split()).strip()

                    empresa = EmpresaFGTS(
                        cnpj=cnpj,
                        razao_social=razao_social or f"Empresa {cnpj}",
                        tem_procuracao=True
                    )

                    empresas.append(empresa)
                    logger.debug(f"Empresa encontrada: {empresa.razao_social} - {empresa.cnpj_formatado()}")

                except Exception as e:
                    logger.warning(f"Erro ao extrair empresa: {e}")
                    continue

            logger.info(f"Total de {len(empresas)} empresa(s) encontrada(s)")
            return empresas

        except Exception as e:
            logger.error(f"Erro ao listar empresas: {e}")
            return empresas

    def selecionar_empresa(self, cnpj: str) -> bool:
        """
        Seleciona uma empresa específica para consulta.

        Args:
            cnpj: CNPJ da empresa (com ou sem formatação)

        Returns:
            True se seleção foi bem-sucedida, False caso contrário
        """
        if not self.page:
            raise RuntimeError("Navegador não foi iniciado")

        try:
            # Limpar formatação do CNPJ
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))

            logger.info(f"Selecionando empresa CNPJ: {cnpj_limpo}")

            # Buscar elemento da empresa
            elementos = self.page.query_selector_all(self.SELETORES["item_empresa"])

            for elemento in elementos:
                texto = elemento.inner_text()
                cnpj_elemento = self._extrair_cnpj(texto)

                if cnpj_elemento == cnpj_limpo:
                    # Clicar no elemento
                    elemento.click()
                    time.sleep(1)

                    # Confirmar seleção se houver botão
                    try:
                        self.page.click(self.SELETORES["botao_confirmar"], timeout=3000)
                        time.sleep(2)
                    except:
                        pass  # Pode não ter botão de confirmação

                    logger.info(f"Empresa {cnpj_limpo} selecionada com sucesso")
                    return True

            logger.warning(f"Empresa {cnpj_limpo} não encontrada na lista")
            return False

        except Exception as e:
            logger.error(f"Erro ao selecionar empresa: {e}")
            return False

    def navegar_para_guias(self) -> bool:
        """
        Navega para a seção de guias FGTS.

        Returns:
            True se navegação foi bem-sucedida, False caso contrário
        """
        if not self.page:
            raise RuntimeError("Navegador não foi iniciado")

        try:
            logger.info("Navegando para seção de guias...")

            # Clicar no menu de guias
            self.page.click(self.SELETORES["menu_guias"], timeout=self.TIMEOUT_ELEMENTO)
            time.sleep(2)

            # Aguardar tabela de guias carregar
            self.page.wait_for_selector(self.SELETORES["tabela_guias"], timeout=self.TIMEOUT_ELEMENTO)

            logger.info("Seção de guias carregada")
            return True

        except PlaywrightTimeoutError:
            logger.error("Timeout ao navegar para guias")
            return False
        except Exception as e:
            logger.error(f"Erro ao navegar para guias: {e}")
            return False

    def obter_html_pagina(self) -> str:
        """
        Retorna o HTML completo da página atual.

        Returns:
            String com HTML da página
        """
        if not self.page:
            return ""
        return self.page.content()

    def fazer_screenshot(self, caminho: str) -> bool:
        """
        Captura screenshot da página atual.

        Args:
            caminho: Caminho onde salvar a imagem

        Returns:
            True se screenshot foi salvo, False caso contrário
        """
        if not self.page:
            return False

        try:
            self.page.screenshot(path=caminho, full_page=True)
            logger.info(f"Screenshot salvo em: {caminho}")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer screenshot: {e}")
            return False

    def fazer_logout(self) -> bool:
        """
        Faz logout do portal.

        Returns:
            True se logout foi bem-sucedido, False caso contrário
        """
        if not self.page:
            return False

        try:
            logger.info("Fazendo logout...")
            self.page.click(self.SELETORES["logout"], timeout=self.TIMEOUT_ELEMENTO)
            time.sleep(2)
            self.authenticator.limpar_sessao()
            logger.info("Logout realizado")
            return True
        except Exception as e:
            logger.warning(f"Erro ao fazer logout: {e}")
            return False

    def fechar_navegador(self) -> None:
        """Fecha o navegador e libera recursos."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

            logger.info("Navegador fechado")
        except Exception as e:
            logger.warning(f"Erro ao fechar navegador: {e}")
        finally:
            self.page = None
            self.context = None
            self.browser = None
            self.playwright = None

    def _extrair_cnpj(self, texto: str) -> Optional[str]:
        """
        Extrai CNPJ de um texto (formato XX.XXX.XXX/XXXX-XX ou apenas números).

        Args:
            texto: Texto contendo CNPJ

        Returns:
            CNPJ sem formatação (14 dígitos) ou None se não encontrado
        """
        # Extrair apenas números
        numeros = ''.join(filter(str.isdigit, texto))

        # Procurar sequência de 14 dígitos
        for i in range(len(numeros) - 13):
            possivel_cnpj = numeros[i:i+14]
            if len(possivel_cnpj) == 14:
                return possivel_cnpj

        return None

    def __enter__(self):
        """Context manager: entrada"""
        self.iniciar_navegador()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: saída"""
        self.fechar_navegador()
        return False
