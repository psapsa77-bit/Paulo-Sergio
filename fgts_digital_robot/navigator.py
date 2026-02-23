"""
Navegação no portal FGTS Digital usando Playwright.
Responsável pelo login, troca de empresa e navegação entre seções.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional

from .authenticator import FGTSAuthenticator
from .models import EmpresaFGTS

logger = logging.getLogger(__name__)

PORTAL_URL = "https://fgtsdigital.caixa.gov.br"
LOGIN_URL = f"{PORTAL_URL}/acessar"
GUIAS_URL = f"{PORTAL_URL}/guias"
EMPRESAS_URL = f"{PORTAL_URL}/procuracoes"

# Timeouts (ms)
TIMEOUT_NAVEGACAO = 60_000
TIMEOUT_LOGIN = 90_000
TIMEOUT_ELEMENTO = 30_000


class NavegacaoError(Exception):
    """Erro de navegação no portal."""
    pass


class FGTSNavigator:
    """
    Controla a navegação no portal FGTS Digital via Playwright.

    Gerencia sessão, login com certificado digital e navegação
    entre empresas e seções de guias.
    """

    TIMEOUT_LOGIN = TIMEOUT_LOGIN

    def __init__(
        self,
        autenticador: FGTSAuthenticator,
        headless: bool = False,
        timeout_navegacao: int = TIMEOUT_NAVEGACAO,
    ):
        self.autenticador = autenticador
        self.headless = headless
        self.timeout_navegacao = timeout_navegacao

        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def iniciar(self) -> None:
        """Inicia Playwright e o browser."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise NavegacaoError(
                "Playwright não está instalado. Execute: pip install playwright && playwright install chromium"
            ) from exc

        logger.info("Iniciando Playwright (headless=%s)…", self.headless)
        self._playwright = sync_playwright().start()

        # Extrair PEM do certificado
        cert_pem, key_pem = self.autenticador.extrair_pem()

        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        # Contexto com certificado cliente
        self._context = self._browser.new_context(
            client_certificates=[
                {
                    "origin": PORTAL_URL,
                    "certPath": str(cert_pem),
                    "keyPath": str(key_pem),
                }
            ],
            ignore_https_errors=False,
            java_script_enabled=True,
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        self._page = self._context.new_page()
        self._page.set_default_timeout(self.timeout_navegacao)
        logger.info("Browser iniciado com sucesso.")

    def fechar(self) -> None:
        """Fecha browser e limpa recursos."""
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as exc:
            logger.debug("Erro ao fechar browser: %s", exc)
        finally:
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None
            self.autenticador.limpar_arquivos_temporarios()

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------

    def fazer_login(self) -> None:
        """
        Executa o fluxo de login no portal FGTS Digital.
        Usa o certificado digital já configurado no contexto.
        """
        if self._page is None:
            raise NavegacaoError("Navigator não iniciado. Chame iniciar() primeiro.")

        logger.info("Acessando portal FGTS Digital…")
        self._page.goto(PORTAL_URL, timeout=self.TIMEOUT_LOGIN, wait_until="networkidle")

        # O portal pode exibir tela de seleção de certificado ou ir direto ao login
        self._aguardar_redirecionamento_login()
        self._confirmar_login()
        logger.info("Login realizado com sucesso.")

    def _aguardar_redirecionamento_login(self) -> None:
        """Aguarda o portal redirecionar após apresentar o certificado."""
        max_tentativas = 3
        for tentativa in range(max_tentativas):
            try:
                # Aguarda URL mudar para página autenticada
                self._page.wait_for_url(
                    f"{PORTAL_URL}/**",
                    timeout=self.TIMEOUT_LOGIN,
                    wait_until="networkidle",
                )
                return
            except Exception:
                if tentativa < max_tentativas - 1:
                    logger.debug("Aguardando autenticação… tentativa %d", tentativa + 1)
                    time.sleep(2)
                else:
                    raise NavegacaoError(
                        "Timeout aguardando login. Verifique o certificado e a conexão."
                    )

    def _confirmar_login(self) -> None:
        """Verifica se o login foi bem-sucedido procurando elementos da área autenticada."""
        page = self._page
        url_atual = page.url
        logger.debug("URL após login: %s", url_atual)

        # Verificar se há mensagem de erro
        erro_seletores = [
            "text=Certificado inválido",
            "text=Acesso negado",
            "text=Erro de autenticação",
            ".error-message",
            "#error",
        ]
        for sel in erro_seletores:
            try:
                el = page.query_selector(sel)
                if el and el.is_visible():
                    texto = el.inner_text()
                    raise NavegacaoError(f"Erro de login reportado pelo portal: {texto}")
            except NavegacaoError:
                raise
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Empresas
    # ------------------------------------------------------------------

    def listar_empresas(self) -> List[EmpresaFGTS]:
        """Lista empresas com procuração disponíveis."""
        if self._page is None:
            raise NavegacaoError("Navigator não iniciado.")

        logger.info("Listando empresas com procuração…")
        empresas: List[EmpresaFGTS] = []

        try:
            self._page.goto(EMPRESAS_URL, timeout=self.timeout_navegacao, wait_until="networkidle")
            self._page.wait_for_load_state("networkidle")

            html = self._page.content()
            empresas = self._parsear_empresas_da_pagina(html)

            if not empresas:
                # Tenta alternativa: menu de troca de empresa
                empresas = self._listar_empresas_via_menu()

        except NavegacaoError:
            raise
        except Exception as exc:
            logger.warning("Erro ao listar empresas: %s", exc)

        logger.info("Encontradas %d empresas.", len(empresas))
        return empresas

    def _parsear_empresas_da_pagina(self, html: str) -> List[EmpresaFGTS]:
        """Extrai lista de empresas do HTML da página de procurações."""
        from .extractor import FGTSExtractor
        extractor = FGTSExtractor()
        return extractor.extrair_empresas(html)

    def _listar_empresas_via_menu(self) -> List[EmpresaFGTS]:
        """Tenta listar empresas clicando no menu de troca."""
        page = self._page
        empresas: List[EmpresaFGTS] = []

        # Seletores comuns do menu de troca de empresa
        seletores_menu = [
            "[data-testid='trocar-empresa']",
            "button:has-text('Trocar empresa')",
            "a:has-text('Trocar empresa')",
            ".empresa-selector",
            "#empresa-menu",
        ]

        for sel in seletores_menu:
            try:
                el = page.query_selector(sel)
                if el:
                    el.click()
                    page.wait_for_load_state("networkidle")
                    html = page.content()
                    from .extractor import FGTSExtractor
                    extractor = FGTSExtractor()
                    empresas = extractor.extrair_empresas(html)
                    if empresas:
                        break
            except Exception:
                continue

        return empresas

    def selecionar_empresa(self, cnpj: str) -> bool:
        """
        Seleciona uma empresa específica para consulta.

        Returns:
            True se selecionada com sucesso, False caso contrário.
        """
        if self._page is None:
            raise NavegacaoError("Navigator não iniciado.")

        logger.info("Selecionando empresa CNPJ: %s", cnpj)

        # Seletores que podem conter o CNPJ da empresa
        cnpj_limpo = cnpj.replace(".", "").replace("/", "").replace("-", "")

        seletores = [
            f"[data-cnpj='{cnpj}']",
            f"[data-cnpj='{cnpj_limpo}']",
            f"tr:has-text('{cnpj}')",
            f"tr:has-text('{cnpj_limpo}')",
            f"li:has-text('{cnpj}')",
            f"option[value='{cnpj}']",
            f"option[value='{cnpj_limpo}']",
        ]

        page = self._page
        for sel in seletores:
            try:
                el = page.query_selector(sel)
                if el:
                    el.click()
                    page.wait_for_load_state("networkidle")
                    logger.info("Empresa selecionada via seletor: %s", sel)
                    return True
            except Exception:
                continue

        # Tenta clicar em botão/link de selecionar dentro da linha que contém o CNPJ
        try:
            row = page.locator(f"tr:has-text('{cnpj}')").first
            btn = row.locator("button, a").first
            if btn:
                btn.click()
                page.wait_for_load_state("networkidle")
                return True
        except Exception:
            pass

        logger.warning("Não foi possível selecionar a empresa CNPJ %s.", cnpj)
        return False

    # ------------------------------------------------------------------
    # Guias
    # ------------------------------------------------------------------

    def navegar_para_guias(self) -> None:
        """Navega para a seção de guias da empresa atual."""
        if self._page is None:
            raise NavegacaoError("Navigator não iniciado.")

        logger.debug("Navegando para seção de guias…")
        self._page.goto(GUIAS_URL, timeout=self.timeout_navegacao, wait_until="networkidle")

        # Fallback: tenta link de navegação no menu
        seletores_guias = [
            "a:has-text('Guias')",
            "a:has-text('guias')",
            "[href*='guias']",
            "[href*='guia']",
            "nav a:has-text('FGTS')",
        ]
        for sel in seletores_guias:
            try:
                el = self._page.query_selector(sel)
                if el and el.is_visible():
                    el.click()
                    self._page.wait_for_load_state("networkidle")
                    break
            except Exception:
                continue

    def obter_html_guias(self) -> str:
        """
        Retorna o HTML da página de guias atual.
        Garante que todas as guias estão carregadas (paginação).
        """
        if self._page is None:
            raise NavegacaoError("Navigator não iniciado.")

        paginas_html = [self._page.content()]
        paginas_html.extend(self._coletar_paginas_seguintes())

        return "\n".join(paginas_html)

    def _coletar_paginas_seguintes(self) -> List[str]:
        """Clica em 'Próxima' e coleta HTML de todas as páginas de paginação."""
        htmls: List[str] = []
        page = self._page

        seletores_proxima = [
            "button:has-text('Próxima')",
            "button:has-text('>')",
            "a:has-text('Próxima')",
            "[aria-label='Next page']",
            ".pagination-next",
            "li.next a",
        ]

        max_paginas = 50
        for _ in range(max_paginas):
            proxima = None
            for sel in seletores_proxima:
                try:
                    el = page.query_selector(sel)
                    if el and el.is_enabled():
                        proxima = el
                        break
                except Exception:
                    continue

            if proxima is None:
                break

            try:
                proxima.click()
                page.wait_for_load_state("networkidle")
                htmls.append(page.content())
            except Exception as exc:
                logger.debug("Erro ao paginar: %s", exc)
                break

        return htmls

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def fazer_screenshot(self, caminho: str) -> None:
        """Salva um screenshot para debug."""
        if self._page:
            self._page.screenshot(path=caminho, full_page=True)
            logger.info("Screenshot salvo: %s", caminho)

    def url_atual(self) -> str:
        if self._page:
            return self._page.url
        return ""

    @property
    def page(self):
        return self._page
