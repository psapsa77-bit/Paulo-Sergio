"""
Robô DET - Verificador de Mensagens do Portal DET
Autor: Paulo Sergio
Versão: 1.0.0

Descrição:
    Robô automatizado para acessar o portal do DET (https://det.sit.trabalho.gov.br/)
    e verificar se existem mensagens não lidas para empresas cadastradas.
"""

import asyncio
import sys
import platform
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from . import config

# Fix para Python 3.13+ no Windows
if sys.platform == 'win32' and sys.version_info >= (3, 8):
    try:
        # Para Python 3.13+, usar WindowsSelectorEventLoopPolicy
        if sys.version_info >= (3, 13):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        # Para Python 3.8-3.12, usar WindowsProactorEventLoopPolicy se disponível
        elif hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass  # Ignorar erros de configuração do event loop


class RobotDET:
    """
    Robô para verificar mensagens não lidas no Portal DET
    """

    def __init__(self, headless: bool = False):
        """
        Inicializa o robô

        Args:
            headless: Se True, executa o navegador em modo headless (sem interface)
        """
        self.headless = headless
        self.logger = self._configurar_logger()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        # Dados de resultado
        self.mensagens_encontradas: List[Dict[str, Any]] = []
        self.resultados_por_empresa: List[Dict[str, Any]] = []
        self.dados_resultado: Dict[str, Any] = {}

        self.logger.info("="*70)
        self.logger.info("🤖 ROBÔ DET - VERIFICADOR DE MENSAGENS")
        self.logger.info("="*70)

    def _configurar_logger(self) -> logging.Logger:
        """Configura o sistema de logging"""
        logger = logging.getLogger("RobotDET")
        logger.setLevel(config.LOG_LEVEL)

        # Handler para arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = config.LOGS_DIR / f"det_robot_{timestamp}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formato
        formatter = logging.Formatter(config.LOG_FORMAT, config.LOG_DATE_FORMAT)
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    async def inicializar_browser(self) -> bool:
        """
        Inicializa o navegador Playwright

        Returns:
            bool: True se inicializado com sucesso
        """
        try:
            self.logger.info("🌐 Iniciando navegador...")
            self.playwright = await async_playwright().start()

            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=config.SLOW_MO,
                args=[
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                locale='pt-BR',
                timezone_id='America/Sao_Paulo'
            )

            self.page = await self.context.new_page()
            self.page.set_default_timeout(config.TIMEOUT_PADRAO * 1000)

            self.logger.info("✅ Navegador iniciado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar navegador: {str(e)}")
            self.logger.exception("Traceback:")
            return False

    async def fechar_browser(self):
        """Fecha o navegador e libera recursos"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("🔒 Navegador fechado")
        except Exception as e:
            self.logger.warning(f"⚠️  Erro ao fechar navegador: {str(e)}")

    async def acessar_portal(self) -> bool:
        """
        Acessa o portal do DET

        Returns:
            bool: True se acessou com sucesso
        """
        try:
            self.logger.info(f"🌐 Acessando portal: {config.DET_URL}")
            await self.page.goto(config.DET_URL, wait_until="domcontentloaded")
            await asyncio.sleep(2)

            self.logger.info("✅ Portal acessado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao acessar portal: {str(e)}")
            self.logger.exception("Traceback:")
            return False

    async def fazer_login_certificado(self) -> bool:
        """
        Realiza login com certificado digital

        Returns:
            bool: True se login bem-sucedido
        """
        try:
            self.logger.info("🔐 Iniciando login com certificado digital...")

            # Aguardar e clicar no botão de certificado digital
            try:
                btn_certificado = await self.page.wait_for_selector(
                    config.SELETORES["btn_certificado"],
                    timeout=config.TIMEOUT_LOGIN * 1000
                )
                await btn_certificado.click()
                self.logger.info("🖱️  Clicado no botão de certificado digital")
                await asyncio.sleep(3)
            except Exception:
                self.logger.info("⚠️  Botão de certificado não encontrado, continuando...")

            # Aguardar seleção manual do certificado pelo usuário
            self.logger.info("⏳ Aguardando seleção do certificado digital...")
            self.logger.info("👉 Por favor, selecione o certificado digital na janela que apareceu")

            # Aguardar até que o login seja concluído (ajustar seletor conforme o portal)
            await self.page.wait_for_load_state("networkidle", timeout=config.TIMEOUT_LOGIN * 1000)
            await asyncio.sleep(5)

            # Verificar se o login foi bem-sucedido
            url_atual = self.page.url
            if "login" not in url_atual.lower() or "autenticacao" not in url_atual.lower():
                self.logger.info("✅ Login realizado com sucesso")
                return True
            else:
                self.logger.warning("⚠️  Ainda na página de login, verificando...")
                return False

        except Exception as e:
            self.logger.error(f"❌ Erro ao fazer login: {str(e)}")
            self.logger.exception("Traceback:")
            return False

    async def selecionar_empresa(self, cnpj: str, nome: str = "") -> bool:
        """
        Seleciona uma empresa específica no portal

        Args:
            cnpj: CNPJ da empresa
            nome: Nome da empresa (opcional)

        Returns:
            bool: True se selecionou com sucesso
        """
        try:
            self.logger.info(f"🏢 Selecionando empresa: {nome} ({cnpj})")

            # Aguardar carregamento da página
            await asyncio.sleep(2)

            # Procurar por seletor de empresa (ajustar conforme o portal)
            try:
                # Tentar encontrar um select ou input de CNPJ
                await self.page.fill("input[name*='cnpj']", cnpj)
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(3)
                self.logger.info("✅ Empresa selecionada")
                return True
            except Exception:
                self.logger.warning("⚠️  Seletor de empresa não encontrado")
                # Pode já estar na empresa correta ou não ter seletor
                return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao selecionar empresa: {str(e)}")
            self.logger.exception("Traceback:")
            return False

    async def acessar_mensagens(self) -> bool:
        """
        Navega até a seção de mensagens

        Returns:
            bool: True se acessou com sucesso
        """
        try:
            self.logger.info("📧 Acessando seção de mensagens...")

            # Procurar por link/menu de mensagens
            try:
                # Tentar XPath primeiro
                link_mensagens = await self.page.wait_for_selector(
                    config.SELETORES["menu_mensagens"],
                    timeout=10000
                )
                await link_mensagens.click()
            except Exception:
                # Tentar CSS selector
                try:
                    link_mensagens = await self.page.wait_for_selector(
                        config.SELETORES["link_mensagens"],
                        timeout=10000
                    )
                    await link_mensagens.click()
                except Exception:
                    self.logger.warning("⚠️  Link de mensagens não encontrado via seletor")
                    # Tentar navegar diretamente pela URL
                    await self.page.goto(config.DET_MENSAGENS_URL)

            await asyncio.sleep(3)
            await self.page.wait_for_load_state("networkidle")

            self.logger.info("✅ Seção de mensagens acessada")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao acessar mensagens: {str(e)}")
            self.logger.exception("Traceback:")
            return False

    async def verificar_mensagens_nao_lidas(self) -> List[Dict[str, Any]]:
        """
        Verifica se existem mensagens não lidas

        Returns:
            List[Dict]: Lista de mensagens não lidas com seus dados
        """
        try:
            self.logger.info("🔍 Verificando mensagens não lidas...")

            mensagens = []

            # Método 1: Verificar contador de mensagens
            try:
                contador = await self.page.query_selector(config.SELETORES["contador_mensagens"])
                if contador:
                    texto_contador = await contador.text_content()
                    num_mensagens = int(texto_contador.strip())
                    if num_mensagens > 0:
                        self.logger.info(f"📬 Encontradas {num_mensagens} mensagens não lidas (via contador)")
            except Exception:
                self.logger.debug("Contador de mensagens não encontrado")

            # Método 2: Buscar mensagens não lidas na lista
            try:
                elementos_mensagens = await self.page.query_selector_all(
                    config.SELETORES["mensagens_nao_lidas"]
                )

                for elemento in elementos_mensagens:
                    try:
                        mensagem = await self._extrair_dados_mensagem(elemento)
                        if mensagem:
                            mensagens.append(mensagem)
                    except Exception as e:
                        self.logger.warning(f"⚠️  Erro ao extrair dados da mensagem: {str(e)}")
                        continue

            except Exception as e:
                self.logger.debug(f"Erro ao buscar mensagens via seletor: {str(e)}")

            # Método 3: Verificar todos os itens de mensagem
            try:
                todos_itens = await self.page.query_selector_all(
                    config.SELETORES["mensagem_item"]
                )

                for item in todos_itens:
                    try:
                        # Verificar se tem indicador de não lida
                        indicador = await item.query_selector(config.SELETORES["indicador_nao_lida"])
                        if indicador:
                            mensagem = await self._extrair_dados_mensagem(item)
                            if mensagem and mensagem not in mensagens:
                                mensagens.append(mensagem)
                    except Exception:
                        continue

            except Exception as e:
                self.logger.debug(f"Erro ao verificar itens de mensagem: {str(e)}")

            if mensagens:
                self.logger.info(f"📬 Total de {len(mensagens)} mensagens não lidas encontradas")
            else:
                self.logger.info("📭 Nenhuma mensagem não lida encontrada")

            return mensagens

        except Exception as e:
            self.logger.error(f"❌ Erro ao verificar mensagens: {str(e)}")
            self.logger.exception("Traceback:")
            return []

    async def _extrair_dados_mensagem(self, elemento) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de uma mensagem

        Args:
            elemento: Elemento da página contendo a mensagem

        Returns:
            Dict com dados da mensagem ou None
        """
        try:
            mensagem = {
                "assunto": "",
                "data": "",
                "remetente": "",
                "tem_anexo": False,
                "conteudo_preview": ""
            }

            # Extrair assunto
            try:
                assunto_elem = await elemento.query_selector(config.SELETORES["mensagem_assunto"])
                if assunto_elem:
                    mensagem["assunto"] = (await assunto_elem.text_content()).strip()
            except Exception:
                pass

            # Extrair data
            try:
                data_elem = await elemento.query_selector(config.SELETORES["mensagem_data"])
                if data_elem:
                    mensagem["data"] = (await data_elem.text_content()).strip()
            except Exception:
                pass

            # Extrair remetente
            try:
                remetente_elem = await elemento.query_selector(config.SELETORES["mensagem_remetente"])
                if remetente_elem:
                    mensagem["remetente"] = (await remetente_elem.text_content()).strip()
            except Exception:
                pass

            # Verificar se tem anexo
            try:
                anexo_elem = await elemento.query_selector(config.SELETORES["icone_anexo"])
                if anexo_elem:
                    mensagem["tem_anexo"] = True
            except Exception:
                pass

            return mensagem if mensagem["assunto"] or mensagem["data"] else None

        except Exception as e:
            self.logger.debug(f"Erro ao extrair dados da mensagem: {str(e)}")
            return None

    async def processar_empresa(self, cnpj: str, nome: str = "") -> Dict[str, Any]:
        """
        Processa uma empresa: seleciona e verifica mensagens

        Args:
            cnpj: CNPJ da empresa
            nome: Nome da empresa

        Returns:
            Dict com resultado do processamento
        """
        resultado = {
            "cnpj": cnpj,
            "nome": nome,
            "sucesso": False,
            "total_mensagens": 0,
            "mensagens": [],
            "status": "",
            "erro": None
        }

        try:
            self.logger.info("")
            self.logger.info("="*70)
            self.logger.info(f"🏢 Processando: {nome} ({cnpj})")
            self.logger.info("="*70)

            # Selecionar empresa
            if not await self.selecionar_empresa(cnpj, nome):
                resultado["status"] = "Erro ao selecionar empresa"
                resultado["erro"] = "Falha na seleção da empresa"
                return resultado

            # Acessar mensagens
            if not await self.acessar_mensagens():
                resultado["status"] = "Erro ao acessar mensagens"
                resultado["erro"] = "Falha ao acessar seção de mensagens"
                return resultado

            # Verificar mensagens não lidas
            mensagens = await self.verificar_mensagens_nao_lidas()

            resultado["mensagens"] = mensagens
            resultado["total_mensagens"] = len(mensagens)
            resultado["sucesso"] = True

            if len(mensagens) > 0:
                resultado["status"] = f"{len(mensagens)} mensagem(ns) não lida(s)"
                self.logger.info(f"✅ {len(mensagens)} mensagem(ns) não lida(s) encontrada(s)")
            else:
                resultado["status"] = "Nenhuma mensagem não lida"
                self.logger.info("✅ Nenhuma mensagem não lida")

            return resultado

        except Exception as e:
            self.logger.error(f"❌ Erro ao processar empresa: {str(e)}")
            self.logger.exception("Traceback:")
            resultado["status"] = f"Erro: {str(e)}"
            resultado["erro"] = str(e)
            return resultado

    async def processar_empresas(self, lista_cnpj: List[Dict[str, str]]) -> bool:
        """
        Processa múltiplas empresas

        Args:
            lista_cnpj: Lista de dicionários com 'cnpj' e 'nome'

        Returns:
            bool: True se processamento concluído
        """
        try:
            self.logger.info("")
            self.logger.info("="*70)
            self.logger.info(f"🏢 PROCESSANDO {len(lista_cnpj)} EMPRESA(S)")
            self.logger.info("="*70)

            # Inicializar browser
            if not await self.inicializar_browser():
                return False

            # Acessar portal
            if not await self.acessar_portal():
                await self.fechar_browser()
                return False

            # Fazer login
            if not await self.fazer_login_certificado():
                self.logger.error("❌ Falha no login")
                await self.fechar_browser()
                return False

            # Processar cada empresa
            self.resultados_por_empresa = []
            self.mensagens_encontradas = []

            for idx, empresa in enumerate(lista_cnpj, 1):
                cnpj = empresa.get('cnpj', '')
                nome = empresa.get('nome', f'Empresa {idx}')

                resultado = await self.processar_empresa(cnpj, nome)
                self.resultados_por_empresa.append(resultado)

                # Adicionar mensagens encontradas
                for mensagem in resultado.get('mensagens', []):
                    mensagem['empresa_cnpj'] = cnpj
                    mensagem['empresa_nome'] = nome
                    self.mensagens_encontradas.append(mensagem)

                # Delay entre empresas
                if idx < len(lista_cnpj):
                    await asyncio.sleep(2)

            # Gerar resumo
            await self._gerar_resumo()

            # Fechar browser
            await self.fechar_browser()

            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao processar empresas: {str(e)}")
            self.logger.exception("Traceback:")
            await self.fechar_browser()
            return False

    async def _gerar_resumo(self):
        """Gera resumo do processamento e salva resultados"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_empresas = len(self.resultados_por_empresa)
            empresas_com_msg = sum(1 for r in self.resultados_por_empresa if r['total_mensagens'] > 0)
            empresas_sem_msg = sum(1 for r in self.resultados_por_empresa if r['total_mensagens'] == 0 and r['sucesso'])
            empresas_erro = sum(1 for r in self.resultados_por_empresa if not r['sucesso'])
            total_mensagens = len(self.mensagens_encontradas)

            self.dados_resultado = {
                "timestamp": timestamp,
                "total_empresas_processadas": total_empresas,
                "empresas_com_mensagens": empresas_com_msg,
                "empresas_sem_mensagens": empresas_sem_msg,
                "empresas_com_erro": empresas_erro,
                "total_mensagens_nao_lidas": total_mensagens,
                "mensagens": self.mensagens_encontradas,
                "resultados_por_empresa": self.resultados_por_empresa
            }

            self.logger.info("")
            self.logger.info("="*70)
            self.logger.info("📊 RESUMO DO PROCESSAMENTO")
            self.logger.info("="*70)
            self.logger.info(f"Total de empresas: {total_empresas}")
            self.logger.info(f"Com mensagens não lidas: {empresas_com_msg}")
            self.logger.info(f"Sem mensagens: {empresas_sem_msg}")
            self.logger.info(f"Com erro: {empresas_erro}")
            self.logger.info(f"Total de mensagens não lidas: {total_mensagens}")
            self.logger.info("="*70)

            # Salvar em JSON
            try:
                timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
                json_path = config.RESULTS_DIR / f"mensagens_det_{timestamp_file}.json"
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.dados_resultado, f, ensure_ascii=False, indent=2)
                self.logger.info(f"💾 Resultado salvo em JSON: {json_path}")
            except Exception as e:
                self.logger.warning(f"Erro ao salvar JSON: {str(e)}")

            # Salvar em HTML
            try:
                html_content = self._gerar_relatorio_html(self.dados_resultado)
                html_path = config.RESULTS_DIR / f"mensagens_det_{timestamp_file}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.logger.info(f"📊 Resultado salvo em HTML: {html_path}")
            except Exception as e:
                self.logger.warning(f"Erro ao salvar HTML: {str(e)}")

        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo: {str(e)}")
            self.logger.exception("Traceback:")

    def _gerar_relatorio_html(self, dados: Dict[str, Any]) -> str:
        """
        Gera relatório HTML visual com os resultados

        Args:
            dados: Dicionário com os dados do resultado

        Returns:
            str: Conteúdo HTML formatado
        """
        timestamp = dados.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        total_empresas = dados.get('total_empresas_processadas', 0)
        empresas_com_msg = dados.get('empresas_com_mensagens', 0)
        empresas_sem_msg = dados.get('empresas_sem_mensagens', 0)
        total_mensagens = dados.get('total_mensagens_nao_lidas', 0)
        resultados_empresas = dados.get('resultados_por_empresa', [])

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Mensagens DET - {timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1f4788 0%, #4a90e2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .metric-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.2);
        }}
        .metric-card .icon {{
            font-size: 3rem;
            margin-bottom: 15px;
        }}
        .metric-card .number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f4788;
            margin: 10px 0;
        }}
        .metric-card .label {{
            color: #666;
            font-size: 1rem;
        }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 1.8rem;
            color: #1f4788;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #4a90e2;
        }}
        .empresa-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }}
        .empresa-card:hover {{
            border-color: #4a90e2;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .empresa-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        .empresa-nome {{
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
            flex: 1;
        }}
        .empresa-cnpj {{
            background: #f0f0f0;
            padding: 8px 15px;
            border-radius: 20px;
            font-family: 'Courier New', monospace;
            color: #555;
            margin-left: 10px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            margin-top: 10px;
        }}
        .status-sucesso {{
            background: #d4edda;
            color: #155724;
        }}
        .status-sem-mensagens {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        .status-erro {{
            background: #f8d7da;
            color: #721c24;
        }}
        .status-alerta {{
            background: #fff3cd;
            color: #856404;
        }}
        .mensagens-list {{
            margin-top: 15px;
            padding-left: 20px;
        }}
        .mensagem-item {{
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #4a90e2;
            margin-bottom: 10px;
            border-radius: 5px;
        }}
        .mensagem-assunto {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .mensagem-info {{
            font-size: 0.9rem;
            color: #666;
        }}
        .info-message {{
            background: #d1ecf1;
            border-left: 4px solid #0c5460;
            padding: 20px;
            border-radius: 5px;
            color: #0c5460;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Relatório de Mensagens DET</h1>
            <p>Gerado em: {timestamp}</p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="icon">🏢</div>
                <div class="number">{total_empresas}</div>
                <div class="label">Total de Empresas</div>
            </div>
            <div class="metric-card">
                <div class="icon">📬</div>
                <div class="number">{empresas_com_msg}</div>
                <div class="label">Com Mensagens</div>
            </div>
            <div class="metric-card">
                <div class="icon">📭</div>
                <div class="number">{empresas_sem_msg}</div>
                <div class="label">Sem Mensagens</div>
            </div>
            <div class="metric-card">
                <div class="icon">📧</div>
                <div class="number">{total_mensagens}</div>
                <div class="label">Total de Mensagens</div>
            </div>
        </div>

        <div class="content">
"""

        # Seção de Empresas
        html += """
            <div class="section">
                <h2 class="section-title">🏢 Detalhes por Empresa</h2>
"""

        if resultados_empresas:
            for resultado in resultados_empresas:
                nome = resultado.get('nome', '')
                cnpj = resultado.get('cnpj', '')
                status = resultado.get('status', '')
                sucesso = resultado.get('sucesso', False)
                total_msg = resultado.get('total_mensagens', 0)
                mensagens = resultado.get('mensagens', [])

                # Formatar CNPJ
                cnpj_formatado = cnpj
                if len(cnpj) == 14:
                    cnpj_formatado = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

                # Definir classe do status
                if not sucesso:
                    status_class = "status-erro"
                elif total_msg > 0:
                    status_class = "status-alerta"
                else:
                    status_class = "status-sucesso"

                html += f"""
                <div class="empresa-card">
                    <div class="empresa-header">
                        <div class="empresa-nome">📋 {nome}</div>
                        <div class="empresa-cnpj">{cnpj_formatado}</div>
                    </div>
                    <div class="status-badge {status_class}">{status}</div>
"""

                if total_msg > 0:
                    html += """
                    <div class="mensagens-list">
"""
                    for msg in mensagens:
                        assunto = msg.get('assunto', 'Sem assunto')
                        data = msg.get('data', '')
                        remetente = msg.get('remetente', '')
                        tem_anexo = msg.get('tem_anexo', False)

                        html += f"""
                        <div class="mensagem-item">
                            <div class="mensagem-assunto">📧 {assunto}</div>
                            <div class="mensagem-info">
                                {f'📅 {data}' if data else ''}
                                {f'| 👤 {remetente}' if remetente else ''}
                                {' | 📎 Anexo' if tem_anexo else ''}
                            </div>
                        </div>
"""
                    html += """
                    </div>
"""
                elif sucesso:
                    html += """
                    <div class="info-message" style="margin-top: 15px;">
                        ✅ Nenhuma mensagem não lida para esta empresa
                    </div>
"""

                html += """
                </div>
"""
        else:
            html += """
                <div class="info-message">
                    ℹ️ Nenhuma empresa foi processada
                </div>
"""

        html += """
            </div>
        </div>

        <div class="footer">
            <p><strong>Robô DET - Verificador de Mensagens</strong></p>
            <p>Automação de verificação de mensagens do Portal DET</p>
        </div>
    </div>
</body>
</html>"""

        return html


async def main():
    """Função principal para testes"""
    robot = RobotDET(headless=False)

    # Lista de empresas para teste
    empresas = [
        {"cnpj": "12345678000199", "nome": "Empresa Teste 1"},
        {"cnpj": "98765432000188", "nome": "Empresa Teste 2"},
    ]

    await robot.processar_empresas(empresas)


if __name__ == "__main__":
    asyncio.run(main())
