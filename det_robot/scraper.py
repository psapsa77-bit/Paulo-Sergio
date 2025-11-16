"""
Extrator de mensagens do DET
Extrai informações das mensagens sem abrir/ler cada uma
"""

import time
import re
from datetime import datetime, timedelta
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .browser import BrowserManager
from .auth import DETAuthenticator
from .models import (
    MensagemDET,
    EmpregadorDET,
    ResultadoExtracao,
    StatusMensagem,
    TipoMensagem,
)


class DETScraper:
    """Extrai informações de mensagens do DET"""

    # Seletores para navegação e extração
    SELETORES = {
        # Navegação
        "menu_caixa_postal": [
            "//a[contains(text(), 'Caixa Postal')]",
            "//a[contains(text(), 'Mensagens')]",
            "//a[contains(@href, 'caixa')]",
            "//a[contains(@href, 'mensagem')]",
            "//*[@id='menu-caixa-postal']",
        ],
        "filtro_nao_lidas": [
            "//select[contains(@id, 'status')]//option[contains(text(), 'não lida')]",
            "//input[contains(@id, 'nao-lida')]",
            "//button[contains(text(), 'Não lidas')]",
            "//a[contains(text(), 'Não lidas')]",
        ],

        # Tabela de mensagens
        "tabela_mensagens": [
            "//table[contains(@class, 'mensagens')]",
            "//table[contains(@id, 'mensagens')]",
            "//div[contains(@class, 'lista-mensagens')]",
            "//table",
        ],
        "linha_mensagem": [
            "//table//tr[contains(@class, 'mensagem')]",
            "//table//tbody//tr",
            "//div[contains(@class, 'mensagem-item')]",
        ],

        # Dados do empregador
        "info_empregador": [
            "//*[contains(@class, 'empregador')]",
            "//*[contains(@class, 'empresa')]",
            "//*[@id='dados-empregador']",
        ],

        # Paginação
        "proxima_pagina": [
            "//a[contains(text(), 'Próxima')]",
            "//button[contains(text(), 'Próxima')]",
            "//a[contains(@class, 'next')]",
            "//*[@id='proxima-pagina']",
        ],
        "total_paginas": [
            "//*[contains(@class, 'paginacao')]",
            "//*[contains(@class, 'pagination')]",
        ],
    }

    def __init__(
        self,
        browser_manager: BrowserManager,
        authenticator: DETAuthenticator,
        log_callback=None
    ):
        """
        Inicializa o scraper

        Args:
            browser_manager: Instância do BrowserManager
            authenticator: Instância do DETAuthenticator
            log_callback: Função para logging
        """
        self.browser = browser_manager
        self.auth = authenticator
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait
        self.log = log_callback or print

    def _encontrar_elemento(self, seletores: list, timeout: int = 10):
        """Tenta encontrar elemento usando múltiplos seletores"""
        wait = WebDriverWait(self.driver, timeout)

        for seletor in seletores:
            try:
                elemento = wait.until(
                    EC.presence_of_element_located((By.XPATH, seletor))
                )
                return elemento
            except TimeoutException:
                continue
            except Exception:
                continue

        return None

    def _clicar_elemento(self, seletores: list, timeout: int = 10) -> bool:
        """Tenta clicar em elemento"""
        wait = WebDriverWait(self.driver, timeout)

        for seletor in seletores:
            try:
                elemento = wait.until(
                    EC.element_to_be_clickable((By.XPATH, seletor))
                )
                elemento.click()
                return True
            except TimeoutException:
                continue
            except Exception:
                continue

        return False

    def acessar_caixa_postal(self) -> bool:
        """
        Navega até a caixa postal de mensagens

        Returns:
            True se acessou com sucesso
        """
        try:
            self.log("Acessando caixa postal...")

            if not self.auth.autenticado:
                self.log("Usuário não autenticado")
                return False

            # Clicar no menu da caixa postal
            if self._clicar_elemento(self.SELETORES["menu_caixa_postal"]):
                time.sleep(3)
                self.log("Caixa postal acessada")
                return True
            else:
                self.log("Menu da caixa postal não encontrado")
                self.browser.capturar_screenshot("erro_caixa_postal.png")
                return False

        except Exception as e:
            self.log(f"Erro ao acessar caixa postal: {e}")
            return False

    def filtrar_nao_lidas(self) -> bool:
        """
        Aplica filtro para mostrar apenas mensagens não lidas

        Returns:
            True se filtro aplicado
        """
        try:
            self.log("Aplicando filtro para mensagens não lidas...")

            # Tentar diferentes formas de filtrar
            if self._clicar_elemento(self.SELETORES["filtro_nao_lidas"]):
                time.sleep(2)
                self.log("Filtro aplicado com sucesso")
                return True
            else:
                self.log("Filtro de não lidas não encontrado - mostrando todas as mensagens")
                return False

        except Exception as e:
            self.log(f"Erro ao aplicar filtro: {e}")
            return False

    def _extrair_data(self, texto: str) -> Optional[datetime]:
        """
        Extrai data de uma string de texto

        Args:
            texto: Texto contendo data

        Returns:
            datetime ou None
        """
        # Padrões comuns de data
        padroes = [
            r"(\d{2}/\d{2}/\d{4})",  # DD/MM/YYYY
            r"(\d{2}-\d{2}-\d{4})",  # DD-MM-YYYY
            r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
            r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})",  # DD/MM/YYYY HH:MM
        ]

        for padrao in padroes:
            match = re.search(padrao, texto)
            if match:
                data_str = match.group(1)
                try:
                    # Tentar diferentes formatos
                    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y %H:%M"]:
                        try:
                            return datetime.strptime(data_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    pass

        return None

    def _identificar_tipo_mensagem(self, texto: str) -> TipoMensagem:
        """
        Identifica o tipo da mensagem baseado no texto

        Args:
            texto: Texto da mensagem (assunto/conteúdo)

        Returns:
            TipoMensagem
        """
        texto_lower = texto.lower()

        if "notificação" in texto_lower or "notificacao" in texto_lower:
            return TipoMensagem.NOTIFICACAO
        elif "intimação" in texto_lower or "intimacao" in texto_lower:
            return TipoMensagem.INTIMACAO
        elif "auto" in texto_lower and "infração" in texto_lower:
            return TipoMensagem.AUTO_INFRACAO
        elif "comunicado" in texto_lower:
            return TipoMensagem.COMUNICADO
        else:
            return TipoMensagem.OUTRO

    def _calcular_dias_restantes(self, prazo: datetime) -> int:
        """Calcula dias restantes para um prazo"""
        hoje = datetime.now()
        delta = prazo - hoje
        return max(0, delta.days)

    def extrair_mensagens_tabela(self) -> List[MensagemDET]:
        """
        Extrai informações das mensagens da tabela/lista

        Returns:
            Lista de MensagemDET
        """
        mensagens = []

        try:
            self.log("Extraindo mensagens da página...")

            # Encontrar tabela ou lista de mensagens
            tabela = self._encontrar_elemento(self.SELETORES["tabela_mensagens"])
            if not tabela:
                self.log("Tabela de mensagens não encontrada")
                self.browser.capturar_screenshot("tabela_nao_encontrada.png")
                return mensagens

            # Encontrar todas as linhas de mensagens
            linhas = self.driver.find_elements(By.XPATH, "//table//tbody//tr")

            if not linhas:
                # Tentar outros seletores
                linhas = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'mensagem')]")

            self.log(f"Encontradas {len(linhas)} linhas/mensagens")

            for idx, linha in enumerate(linhas):
                try:
                    mensagem = self._extrair_dados_linha(linha, idx)
                    if mensagem:
                        mensagens.append(mensagem)
                        self.log(f"  Mensagem {idx+1}: {mensagem.assunto[:50]}...")
                except Exception as e:
                    self.log(f"Erro ao extrair linha {idx}: {e}")
                    continue

        except Exception as e:
            self.log(f"Erro ao extrair mensagens: {e}")
            self.browser.capturar_screenshot("erro_extracao.png")

        return mensagens

    def _extrair_dados_linha(self, linha, indice: int) -> Optional[MensagemDET]:
        """
        Extrai dados de uma linha da tabela

        Args:
            linha: Elemento da linha
            indice: Índice da mensagem

        Returns:
            MensagemDET ou None
        """
        try:
            # Extrair células da linha
            celulas = linha.find_elements(By.TAG_NAME, "td")

            if not celulas or len(celulas) < 2:
                # Pode ser uma div, não tabela
                texto_completo = linha.text.strip()
                if not texto_completo:
                    return None

                # Tentar extrair informações do texto completo
                return MensagemDET(
                    id_mensagem=f"msg_{indice}_{int(time.time())}",
                    assunto=texto_completo[:100],
                    data_envio=self._extrair_data(texto_completo) or datetime.now(),
                    remetente="DET",
                    status=StatusMensagem.NAO_LIDA,
                    tipo=self._identificar_tipo_mensagem(texto_completo),
                )

            # Extrair dados das células (ajustar conforme estrutura real)
            dados = {
                "id_mensagem": f"msg_{indice}_{int(time.time())}",
                "numero": None,
                "assunto": "",
                "data_envio": datetime.now(),
                "remetente": "DET - Auditoria Fiscal do Trabalho",
                "status": StatusMensagem.NAO_LIDA,
                "prazo_resposta": None,
                "resumo": None,
                "url_mensagem": None,
                "anexos": [],
            }

            # Mapear células para campos (estrutura típica)
            # Célula 0: Número/ID
            # Célula 1: Assunto
            # Célula 2: Data
            # Célula 3: Status/Prazo

            for i, celula in enumerate(celulas):
                texto = celula.text.strip()

                if i == 0:
                    # Número ou checkbox
                    if texto.isdigit():
                        dados["numero"] = texto
                elif i == 1 or (i == 0 and not texto.isdigit()):
                    # Assunto
                    dados["assunto"] = texto
                    dados["tipo"] = self._identificar_tipo_mensagem(texto)

                    # Verificar se tem link
                    try:
                        link = celula.find_element(By.TAG_NAME, "a")
                        dados["url_mensagem"] = link.get_attribute("href")
                    except:
                        pass

                elif i == 2 or (i == 1 and self._extrair_data(texto)):
                    # Data
                    data = self._extrair_data(texto)
                    if data:
                        dados["data_envio"] = data

                elif i >= 3:
                    # Prazo ou status
                    if "dia" in texto.lower() or self._extrair_data(texto):
                        data_prazo = self._extrair_data(texto)
                        if data_prazo:
                            dados["prazo_resposta"] = data_prazo
                            dados["dias_restantes"] = self._calcular_dias_restantes(data_prazo)

                    # Verificar status
                    if "lida" in texto.lower() and "não" not in texto.lower():
                        dados["status"] = StatusMensagem.LIDA
                    elif "arquivada" in texto.lower():
                        dados["status"] = StatusMensagem.ARQUIVADA

            # Verificar se linha tem indicador visual de não lida
            classe_linha = linha.get_attribute("class") or ""
            if "nao-lida" in classe_linha or "unread" in classe_linha or "nova" in classe_linha:
                dados["status"] = StatusMensagem.NAO_LIDA

            # Só retornar se tiver assunto
            if dados["assunto"]:
                return MensagemDET(**dados)
            else:
                return None

        except Exception as e:
            self.log(f"Erro ao extrair dados da linha: {e}")
            return None

    def extrair_dados_empregador(self) -> Optional[EmpregadorDET]:
        """
        Extrai dados do empregador logado

        Returns:
            EmpregadorDET ou None
        """
        try:
            self.log("Extraindo dados do empregador...")

            dados = {
                "cnpj_cpf": "",
                "razao_social": None,
                "nome_fantasia": None,
                "email_cadastrado": None,
                "telefone": None,
                "endereco": None,
                "ultimo_acesso": datetime.now(),
                "total_mensagens": 0,
                "mensagens_nao_lidas": 0,
            }

            # Tentar encontrar informações na página
            elemento_info = self._encontrar_elemento(self.SELETORES["info_empregador"], timeout=5)
            if elemento_info:
                texto = elemento_info.text

                # Extrair CNPJ/CPF
                cnpj_match = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto)
                cpf_match = re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto)

                if cnpj_match:
                    dados["cnpj_cpf"] = cnpj_match.group()
                elif cpf_match:
                    dados["cnpj_cpf"] = cpf_match.group()

            # Contar mensagens na página
            try:
                linhas = self.driver.find_elements(By.XPATH, "//table//tbody//tr")
                dados["total_mensagens"] = len(linhas)

                # Contar não lidas
                nao_lidas = self.driver.find_elements(
                    By.XPATH, "//tr[contains(@class, 'nao-lida') or contains(@class, 'unread')]"
                )
                dados["mensagens_nao_lidas"] = len(nao_lidas) if nao_lidas else len(linhas)

            except:
                pass

            if dados["cnpj_cpf"]:
                return EmpregadorDET(**dados)
            else:
                self.log("Não foi possível identificar CNPJ/CPF do empregador")
                return None

        except Exception as e:
            self.log(f"Erro ao extrair dados do empregador: {e}")
            return None

    def extrair_todas_paginas(self, limite: int = 100) -> List[MensagemDET]:
        """
        Extrai mensagens de todas as páginas disponíveis

        Args:
            limite: Número máximo de mensagens

        Returns:
            Lista de todas as mensagens
        """
        todas_mensagens = []
        pagina_atual = 1

        try:
            while len(todas_mensagens) < limite:
                self.log(f"Extraindo página {pagina_atual}...")

                # Extrair mensagens da página atual
                mensagens = self.extrair_mensagens_tabela()

                if not mensagens:
                    self.log("Nenhuma mensagem na página atual")
                    break

                todas_mensagens.extend(mensagens)
                self.log(f"Total acumulado: {len(todas_mensagens)} mensagens")

                # Verificar se atingiu limite
                if len(todas_mensagens) >= limite:
                    self.log(f"Limite de {limite} mensagens atingido")
                    break

                # Tentar ir para próxima página
                if self._clicar_elemento(self.SELETORES["proxima_pagina"]):
                    pagina_atual += 1
                    time.sleep(2)
                else:
                    self.log("Não há mais páginas")
                    break

        except Exception as e:
            self.log(f"Erro ao extrair múltiplas páginas: {e}")

        return todas_mensagens[:limite]

    def executar_extracao_completa(
        self,
        apenas_nao_lidas: bool = True,
        limite: int = 100
    ) -> ResultadoExtracao:
        """
        Executa extração completa do DET

        Args:
            apenas_nao_lidas: Se True, extrai apenas não lidas
            limite: Limite de mensagens

        Returns:
            ResultadoExtracao com todos os dados
        """
        inicio = time.time()
        resultado = ResultadoExtracao(
            apenas_nao_lidas=apenas_nao_lidas,
            sucesso=False
        )

        try:
            self.log("Iniciando extração completa do DET...")

            # Verificar autenticação
            if not self.auth.autenticado:
                resultado.erros.append("Usuário não autenticado")
                return resultado

            # Acessar caixa postal
            if not self.acessar_caixa_postal():
                resultado.erros.append("Falha ao acessar caixa postal")
                return resultado

            # Aplicar filtro se necessário
            if apenas_nao_lidas:
                self.filtrar_nao_lidas()

            # Extrair dados do empregador
            resultado.empregador = self.extrair_dados_empregador()

            # Extrair mensagens
            resultado.mensagens = self.extrair_todas_paginas(limite)
            resultado.total_extraido = len(resultado.mensagens)

            # Finalizar
            resultado.sucesso = True
            resultado.tempo_execucao = time.time() - inicio

            self.log(f"Extração concluída: {resultado.total_extraido} mensagens em {resultado.tempo_execucao:.2f}s")

        except Exception as e:
            resultado.erros.append(str(e))
            resultado.tempo_execucao = time.time() - inicio
            self.log(f"Erro na extração: {e}")
            self.browser.capturar_screenshot("erro_extracao_completa.png")

        return resultado
