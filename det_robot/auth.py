"""
Módulo de autenticação para o DET Robot
Suporta login via Gov.br
"""

import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .browser import BrowserManager


class DETAuthenticator:
    """Gerencia autenticação no DET via Gov.br"""

    # URLs importantes
    DET_URL = "https://det.sit.trabalho.gov.br/"
    GOVBR_LOGIN_URL = "https://sso.acesso.gov.br/login"

    # Seletores (podem precisar de ajustes conforme o site)
    SELETORES = {
        # Página inicial DET
        "btn_entrar": [
            "//a[contains(text(), 'Entrar')]",
            "//button[contains(text(), 'Entrar')]",
            "//a[contains(@class, 'login')]",
            "//button[contains(@class, 'login')]",
            "//*[@id='login-button']",
        ],

        # Gov.br
        "input_cpf": [
            "//input[@id='accountId']",
            "//input[@name='accountId']",
            "//input[contains(@placeholder, 'CPF')]",
            "//input[@type='text']",
        ],
        "btn_continuar_cpf": [
            "//button[contains(text(), 'Continuar')]",
            "//button[@type='submit']",
            "//button[contains(@class, 'primary')]",
        ],
        "input_senha": [
            "//input[@id='password']",
            "//input[@name='password']",
            "//input[@type='password']",
        ],
        "btn_entrar_govbr": [
            "//button[contains(text(), 'Entrar')]",
            "//button[@type='submit']",
            "//button[contains(text(), 'Acessar')]",
        ],

        # Verificação de login bem sucedido
        "usuario_logado": [
            "//*[contains(@class, 'user-name')]",
            "//*[contains(@class, 'logged-user')]",
            "//span[contains(@class, 'nome-usuario')]",
            "//*[@id='usuario-logado']",
        ],
        "menu_principal": [
            "//nav",
            "//*[contains(@class, 'menu')]",
            "//*[contains(@class, 'navbar')]",
        ],
        "caixa_postal": [
            "//a[contains(text(), 'Caixa Postal')]",
            "//a[contains(text(), 'Mensagens')]",
            "//*[contains(@href, 'mensagem')]",
        ],
    }

    def __init__(self, browser_manager: BrowserManager, log_callback=None):
        """
        Inicializa o autenticador

        Args:
            browser_manager: Instância do BrowserManager
            log_callback: Função para logging
        """
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait
        self.log = log_callback or print
        self.autenticado = False

    def _encontrar_elemento(self, seletores: list, timeout: int = 10):
        """
        Tenta encontrar elemento usando múltiplos seletores

        Args:
            seletores: Lista de seletores XPath para tentar
            timeout: Timeout em segundos

        Returns:
            Elemento encontrado ou None
        """
        wait = WebDriverWait(self.driver, timeout)

        for seletor in seletores:
            try:
                elemento = wait.until(
                    EC.presence_of_element_located((By.XPATH, seletor))
                )
                self.log(f"Elemento encontrado com seletor: {seletor}")
                return elemento
            except TimeoutException:
                continue
            except Exception as e:
                self.log(f"Erro com seletor {seletor}: {e}")
                continue

        return None

    def _clicar_elemento(self, seletores: list, timeout: int = 10) -> bool:
        """
        Tenta clicar em elemento usando múltiplos seletores

        Returns:
            True se clicou com sucesso
        """
        wait = WebDriverWait(self.driver, timeout)

        for seletor in seletores:
            try:
                elemento = wait.until(
                    EC.element_to_be_clickable((By.XPATH, seletor))
                )
                elemento.click()
                self.log(f"Clicou no elemento: {seletor}")
                return True
            except TimeoutException:
                continue
            except Exception as e:
                self.log(f"Erro ao clicar {seletor}: {e}")
                continue

        return False

    def acessar_pagina_login(self) -> bool:
        """
        Acessa a página de login do DET

        Returns:
            True se acessou com sucesso
        """
        try:
            self.log("Acessando página do DET...")
            self.driver.get(self.DET_URL)
            time.sleep(2)

            # Procurar botão de entrar/login
            self.log("Procurando botão de login...")
            if self._clicar_elemento(self.SELETORES["btn_entrar"]):
                self.log("Redirecionando para página de login...")
                time.sleep(3)
                return True
            else:
                self.log("Botão de login não encontrado. Verificando se já está na página de login...")
                # Pode já estar na página de login
                if "gov.br" in self.driver.current_url or "login" in self.driver.current_url:
                    return True
                return False

        except Exception as e:
            self.log(f"Erro ao acessar página de login: {e}")
            return False

    def login_govbr(self, cpf: str, senha: str) -> bool:
        """
        Realiza login via Gov.br

        Args:
            cpf: CPF do usuário (apenas números)
            senha: Senha do Gov.br

        Returns:
            True se login bem sucedido
        """
        try:
            # Limpar CPF (apenas números)
            cpf_limpo = "".join(filter(str.isdigit, cpf))

            if len(cpf_limpo) != 11:
                self.log("CPF inválido. Deve ter 11 dígitos.")
                return False

            self.log(f"Iniciando login Gov.br para CPF: {cpf_limpo[:3]}...{cpf_limpo[-2:]}")

            # Passo 1: Inserir CPF
            self.log("Inserindo CPF...")
            input_cpf = self._encontrar_elemento(self.SELETORES["input_cpf"])
            if not input_cpf:
                self.log("Campo de CPF não encontrado")
                self.browser.capturar_screenshot("erro_cpf_campo.png")
                return False

            input_cpf.clear()
            input_cpf.send_keys(cpf_limpo)
            time.sleep(1)

            # Passo 2: Clicar em continuar
            self.log("Clicando em continuar...")
            if not self._clicar_elemento(self.SELETORES["btn_continuar_cpf"]):
                self.log("Botão continuar não encontrado")
                self.browser.capturar_screenshot("erro_btn_continuar.png")
                return False

            time.sleep(3)

            # Passo 3: Inserir senha
            self.log("Inserindo senha...")
            input_senha = self._encontrar_elemento(self.SELETORES["input_senha"])
            if not input_senha:
                self.log("Campo de senha não encontrado")
                self.browser.capturar_screenshot("erro_senha_campo.png")
                return False

            input_senha.clear()
            input_senha.send_keys(senha)
            time.sleep(1)

            # Passo 4: Clicar em entrar
            self.log("Clicando em entrar...")
            if not self._clicar_elemento(self.SELETORES["btn_entrar_govbr"]):
                self.log("Botão entrar não encontrado")
                self.browser.capturar_screenshot("erro_btn_entrar.png")
                return False

            time.sleep(5)

            # Verificar se login foi bem sucedido
            return self.verificar_autenticacao()

        except Exception as e:
            self.log(f"Erro durante login Gov.br: {e}")
            self.browser.capturar_screenshot("erro_login_govbr.png")
            return False

    def verificar_autenticacao(self) -> bool:
        """
        Verifica se o usuário está autenticado

        Returns:
            True se autenticado
        """
        try:
            self.log("Verificando autenticação...")

            # Aguardar um pouco para página carregar
            time.sleep(3)

            # Verificar URL - se estiver no DET e não na página de login
            url_atual = self.driver.current_url
            self.log(f"URL atual: {url_atual}")

            if "det.sit.trabalho.gov.br" in url_atual and "login" not in url_atual.lower():
                # Provavelmente logado, verificar elementos da página

                # Tentar encontrar indicadores de usuário logado
                if self._encontrar_elemento(self.SELETORES["usuario_logado"], timeout=5):
                    self.log("Usuário logado identificado na página")
                    self.autenticado = True
                    return True

                # Tentar encontrar menu/caixa postal (indica que está logado)
                if self._encontrar_elemento(self.SELETORES["caixa_postal"], timeout=5):
                    self.log("Caixa postal encontrada - usuário autenticado")
                    self.autenticado = True
                    return True

                # Verificar se tem menu principal
                if self._encontrar_elemento(self.SELETORES["menu_principal"], timeout=5):
                    self.log("Menu principal encontrado - provavelmente autenticado")
                    self.autenticado = True
                    return True

            # Se ainda estiver em página de login
            if "gov.br" in url_atual or "login" in url_atual.lower():
                self.log("Ainda na página de login - autenticação falhou")

                # Verificar se há mensagem de erro
                try:
                    erro = self.driver.find_element(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'erro')]")
                    if erro:
                        self.log(f"Mensagem de erro: {erro.text}")
                except:
                    pass

                self.autenticado = False
                return False

            self.log("Status de autenticação incerto")
            self.browser.capturar_screenshot("verificacao_auth.png")
            return False

        except Exception as e:
            self.log(f"Erro ao verificar autenticação: {e}")
            return False

    def login_manual(self, timeout_minutos: int = 5) -> bool:
        """
        Permite login manual pelo usuário (útil para 2FA ou captcha)

        Args:
            timeout_minutos: Tempo máximo para aguardar login manual

        Returns:
            True se login detectado
        """
        try:
            self.log(f"Aguardando login manual... (timeout: {timeout_minutos} minutos)")
            self.log("Por favor, faça login no navegador que foi aberto.")

            # Acessar página de login se necessário
            if "det.sit.trabalho.gov.br" not in self.driver.current_url:
                self.driver.get(self.DET_URL)

            # Aguardar até timeout
            tempo_inicio = time.time()
            timeout_segundos = timeout_minutos * 60

            while (time.time() - tempo_inicio) < timeout_segundos:
                if self.verificar_autenticacao():
                    self.log("Login manual detectado com sucesso!")
                    return True

                time.sleep(5)  # Verificar a cada 5 segundos
                tempo_restante = int(timeout_segundos - (time.time() - tempo_inicio))
                self.log(f"Aguardando login... ({tempo_restante}s restantes)")

            self.log("Timeout - login manual não completado")
            return False

        except Exception as e:
            self.log(f"Erro durante aguardo de login manual: {e}")
            return False

    def logout(self) -> bool:
        """
        Realiza logout do sistema

        Returns:
            True se logout bem sucedido
        """
        try:
            self.log("Realizando logout...")

            # Procurar botão de logout
            seletores_logout = [
                "//a[contains(text(), 'Sair')]",
                "//button[contains(text(), 'Sair')]",
                "//a[contains(text(), 'Logout')]",
                "//*[@id='logout']",
                "//*[contains(@class, 'logout')]",
            ]

            if self._clicar_elemento(seletores_logout):
                time.sleep(2)
                self.autenticado = False
                self.log("Logout realizado com sucesso")
                return True
            else:
                self.log("Botão de logout não encontrado")
                return False

        except Exception as e:
            self.log(f"Erro ao realizar logout: {e}")
            return False

    def obter_dados_usuario(self) -> dict:
        """
        Obtém dados do usuário logado

        Returns:
            Dicionário com dados do usuário
        """
        dados = {
            "nome": None,
            "cpf_cnpj": None,
            "email": None,
        }

        try:
            # Tentar extrair nome do usuário
            elemento_nome = self._encontrar_elemento(self.SELETORES["usuario_logado"], timeout=5)
            if elemento_nome:
                dados["nome"] = elemento_nome.text.strip()

            self.log(f"Dados do usuário: {dados}")

        except Exception as e:
            self.log(f"Erro ao obter dados do usuário: {e}")

        return dados
