"""
Robô principal para automação do FGTS Digital
=============================================

Orquestra todos os componentes: autenticação, navegação e extração.
"""

import logging
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from .models import (
    CertificadoDigital,
    EmpresaFGTS,
    GuiaFGTS,
    StatusGuia,
    RelatorioFGTS
)
from .authenticator import FGTSAuthenticator
from .navigator import FGTSNavigator
from .extractor import FGTSExtractor

logger = logging.getLogger(__name__)


class FGTSRobot:
    """
    Robô principal para automação de consultas no FGTS Digital.

    Exemplo de uso:
        robot = FGTSRobot(
            certificado_path="certificado.pfx",
            senha_certificado="senha123"
        )

        with robot:
            robot.autenticar()
            empresas = robot.listar_empresas()
            relatorio = robot.processar_todas_empresas()
            robot.exportar_relatorio(relatorio, "relatorio_fgts.json")
    """

    def __init__(
        self,
        certificado_path: str | Path,
        senha_certificado: str,
        headless: bool = False,
        log_level: str = "INFO"
    ):
        """
        Inicializa o robô FGTS.

        Args:
            certificado_path: Caminho para arquivo .pfx do certificado digital
            senha_certificado: Senha do certificado
            headless: Se True, executa navegador sem interface gráfica
            log_level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        """
        # Configurar logging
        self._configurar_logging(log_level)

        # Criar certificado
        self.certificado = CertificadoDigital(
            caminho=Path(certificado_path),
            senha=senha_certificado
        )

        # Inicializar componentes
        self.authenticator = FGTSAuthenticator(self.certificado)
        self.navigator: Optional[FGTSNavigator] = None
        self.extractor = FGTSExtractor()

        # Configurações
        self.headless = headless

        # Estado
        self.empresas_disponiveis: List[EmpresaFGTS] = []
        self.relatorio: Optional[RelatorioFGTS] = None
        self._tempo_inicio: Optional[float] = None

        logger.info("FGTSRobot inicializado")

    def _configurar_logging(self, level: str) -> None:
        """Configura sistema de logging."""
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def validar_certificado(self) -> Dict[str, Any]:
        """
        Valida o certificado digital.

        Returns:
            Dicionário com informações do certificado

        Raises:
            ValueError: Se certificado for inválido
        """
        logger.info("Validando certificado digital...")
        info = self.authenticator.validar_certificado()
        logger.info(f"Certificado válido: {info['nome_titular']} - Expira em {info['dias_para_vencer']} dias")
        return info

    def autenticar(self) -> bool:
        """
        Autentica no portal FGTS Digital.

        Returns:
            True se autenticação foi bem-sucedida

        Raises:
            RuntimeError: Se falhar ao autenticar
        """
        logger.info("Iniciando processo de autenticação...")
        self._tempo_inicio = time.time()

        try:
            # Validar certificado
            self.validar_certificado()

            # Iniciar navegador
            self.navigator = FGTSNavigator(self.authenticator, headless=self.headless)
            self.navigator.iniciar_navegador()

            # Acessar portal
            sucesso = self.navigator.acessar_portal()

            if sucesso:
                logger.info("Autenticação realizada com sucesso!")
                return True
            else:
                raise RuntimeError("Falha na autenticação no portal FGTS Digital")

        except Exception as e:
            logger.error(f"Erro durante autenticação: {e}")
            self.fechar()
            raise

    def listar_empresas(self) -> List[EmpresaFGTS]:
        """
        Lista todas as empresas disponíveis (com procuração).

        Returns:
            Lista de objetos EmpresaFGTS

        Raises:
            RuntimeError: Se não estiver autenticado
        """
        if not self.navigator:
            raise RuntimeError("Navegador não inicializado. Chame autenticar() primeiro.")

        logger.info("Listando empresas disponíveis...")
        self.empresas_disponiveis = self.navigator.listar_empresas_disponiveis()

        logger.info(f"Encontradas {len(self.empresas_disponiveis)} empresa(s)")
        for empresa in self.empresas_disponiveis:
            logger.info(f"  - {empresa.razao_social} ({empresa.cnpj_formatado()})")

        return self.empresas_disponiveis

    def extrair_guias_empresa(
        self,
        cnpj: str,
        filtrar_status: Optional[List[StatusGuia]] = None
    ) -> List[GuiaFGTS]:
        """
        Extrai guias de uma empresa específica.

        Args:
            cnpj: CNPJ da empresa
            filtrar_status: Lista de status para filtrar (opcional)

        Returns:
            Lista de GuiaFGTS

        Raises:
            RuntimeError: Se não estiver autenticado ou empresa não encontrada
        """
        if not self.navigator:
            raise RuntimeError("Navegador não inicializado. Chame autenticar() primeiro.")

        # Buscar informações da empresa
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        empresa = None

        for emp in self.empresas_disponiveis:
            if emp.cnpj == cnpj_limpo:
                empresa = emp
                break

        if not empresa:
            raise RuntimeError(f"Empresa {cnpj} não encontrada na lista de empresas disponíveis")

        logger.info(f"Extraindo guias da empresa: {empresa.razao_social}")

        try:
            # Selecionar empresa
            if not self.navigator.selecionar_empresa(cnpj_limpo):
                raise RuntimeError(f"Falha ao selecionar empresa {cnpj_limpo}")

            # Navegar para seção de guias
            if not self.navigator.navegar_para_guias():
                logger.warning("Falha ao navegar para guias, tentando extrair da página atual")

            # Aguardar carregamento
            time.sleep(2)

            # Obter HTML da página
            html = self.navigator.obter_html_pagina()

            # Extrair guias
            guias = self.extractor.extrair_guias_do_html(html, empresa, filtrar_status)

            logger.info(f"Extraídas {len(guias)} guia(s) da empresa {empresa.razao_social}")
            return guias

        except Exception as e:
            logger.error(f"Erro ao extrair guias da empresa {cnpj}: {e}")
            raise

    def processar_todas_empresas(
        self,
        empresas_cnpj: Optional[List[str]] = None,
        filtrar_status: Optional[List[StatusGuia]] = None
    ) -> RelatorioFGTS:
        """
        Processa todas as empresas e gera relatório consolidado.

        Args:
            empresas_cnpj: Lista de CNPJs específicos (None = todas)
            filtrar_status: Lista de status para filtrar (opcional)

        Returns:
            RelatorioFGTS com dados consolidados

        Raises:
            RuntimeError: Se não estiver autenticado
        """
        if not self.navigator:
            raise RuntimeError("Navegador não inicializado. Chame autenticar() primeiro.")

        logger.info("Iniciando processamento de empresas...")

        # Listar empresas se ainda não listou
        if not self.empresas_disponiveis:
            self.listar_empresas()

        # Filtrar empresas se especificado
        if empresas_cnpj:
            empresas_cnpj_limpos = [''.join(filter(str.isdigit, c)) for c in empresas_cnpj]
            empresas_processar = [e for e in self.empresas_disponiveis if e.cnpj in empresas_cnpj_limpos]
        else:
            empresas_processar = self.empresas_disponiveis

        # Criar relatório
        relatorio = RelatorioFGTS(
            empresas=empresas_processar,
            certificado_usado=self.certificado.cpf_cnpj
        )

        # Processar cada empresa
        for i, empresa in enumerate(empresas_processar, 1):
            logger.info(f"[{i}/{len(empresas_processar)}] Processando: {empresa.razao_social}")

            try:
                guias = self.extrair_guias_empresa(empresa.cnpj, filtrar_status)
                relatorio.guias.extend(guias)

            except Exception as e:
                erro = f"Erro ao processar {empresa.cnpj_formatado()}: {e}"
                logger.error(erro)
                relatorio.erros.append(erro)
                continue

            # Aguardar entre empresas
            if i < len(empresas_processar):
                time.sleep(1)

        # Calcular estatísticas
        relatorio.calcular_estatisticas()

        # Tempo de execução
        if self._tempo_inicio:
            relatorio.tempo_execucao_segundos = time.time() - self._tempo_inicio

        self.relatorio = relatorio

        logger.info("Processamento concluído!")
        logger.info(f"  Total de guias: {relatorio.total_guias}")
        logger.info(f"  Pendentes: {relatorio.total_pendentes}")
        logger.info(f"  Pagas: {relatorio.total_pagas}")
        logger.info(f"  Vencidas: {relatorio.total_vencidas}")
        logger.info(f"  Valor total pendente: R$ {relatorio.valor_total_pendente:,.2f}")

        return relatorio

    def exportar_relatorio(
        self,
        relatorio: Optional[RelatorioFGTS] = None,
        caminho: str | Path = "relatorio_fgts.json",
        formato: str = "json"
    ) -> Path:
        """
        Exporta relatório para arquivo.

        Args:
            relatorio: Relatório a exportar (usa self.relatorio se None)
            caminho: Caminho do arquivo de saída
            formato: Formato de exportação ('json' ou 'excel')

        Returns:
            Path do arquivo gerado

        Raises:
            ValueError: Se formato for inválido
        """
        if relatorio is None:
            if self.relatorio is None:
                raise ValueError("Nenhum relatório disponível para exportar")
            relatorio = self.relatorio

        caminho_path = Path(caminho)

        if formato.lower() == "json":
            return self._exportar_json(relatorio, caminho_path)
        elif formato.lower() in ["excel", "xlsx"]:
            return self._exportar_excel(relatorio, caminho_path)
        else:
            raise ValueError(f"Formato '{formato}' não suportado. Use 'json' ou 'excel'")

    def _exportar_json(self, relatorio: RelatorioFGTS, caminho: Path) -> Path:
        """Exporta relatório em JSON."""
        logger.info(f"Exportando relatório JSON: {caminho}")

        # Converter para dicionário
        dados = relatorio.exportar_dict()

        # Salvar JSON
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"Relatório JSON salvo: {caminho.absolute()}")
        return caminho

    def _exportar_excel(self, relatorio: RelatorioFGTS, caminho: Path) -> Path:
        """Exporta relatório em Excel."""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            raise ImportError("openpyxl não instalado. Instale com: pip install openpyxl")

        logger.info(f"Exportando relatório Excel: {caminho}")

        # Criar workbook
        wb = openpyxl.Workbook()

        # Aba de resumo
        ws_resumo = wb.active
        ws_resumo.title = "Resumo"

        # Cabeçalho
        ws_resumo['A1'] = "RELATÓRIO FGTS DIGITAL"
        ws_resumo['A1'].font = Font(size=14, bold=True)

        ws_resumo['A3'] = "Data de Geração:"
        ws_resumo['B3'] = relatorio.data_geracao.strftime("%d/%m/%Y %H:%M:%S")

        ws_resumo['A5'] = "ESTATÍSTICAS"
        ws_resumo['A5'].font = Font(bold=True)

        estatisticas = [
            ("Total de Empresas:", relatorio.total_empresas),
            ("Total de Guias:", relatorio.total_guias),
            ("Guias Pendentes:", relatorio.total_pendentes),
            ("Guias Pagas:", relatorio.total_pagas),
            ("Guias Vencidas:", relatorio.total_vencidas),
            ("", ""),
            ("Valor Total Pendente:", f"R$ {float(relatorio.valor_total_pendente):,.2f}"),
            ("Valor Total Pago:", f"R$ {float(relatorio.valor_total_pago):,.2f}"),
            ("Valor Total Geral:", f"R$ {float(relatorio.valor_total_geral):,.2f}"),
        ]

        for i, (label, valor) in enumerate(estatisticas, start=6):
            ws_resumo[f'A{i}'] = label
            ws_resumo[f'B{i}'] = valor

        # Aba de guias
        ws_guias = wb.create_sheet("Guias")

        headers = [
            "Número", "Tipo", "Status", "CNPJ", "Empresa",
            "Competência", "Vencimento", "Pagamento",
            "Valor Principal", "Valor Total", "Dias Atraso"
        ]

        for col, header in enumerate(headers, start=1):
            cell = ws_guias.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")

        # Dados das guias
        for row_idx, guia in enumerate(relatorio.guias, start=2):
            ws_guias.cell(row=row_idx, column=1, value=guia.numero_guia)
            ws_guias.cell(row=row_idx, column=2, value=guia.tipo.value)
            ws_guias.cell(row=row_idx, column=3, value=guia.status.value)
            ws_guias.cell(row=row_idx, column=4, value=guia.cnpj_empresa)
            ws_guias.cell(row=row_idx, column=5, value=guia.razao_social_empresa)
            ws_guias.cell(row=row_idx, column=6, value=guia.competencia)
            ws_guias.cell(row=row_idx, column=7, value=guia.data_vencimento.strftime("%d/%m/%Y"))
            ws_guias.cell(row=row_idx, column=8, value=guia.data_pagamento.strftime("%d/%m/%Y") if guia.data_pagamento else "")
            ws_guias.cell(row=row_idx, column=9, value=float(guia.valor_principal))
            ws_guias.cell(row=row_idx, column=10, value=float(guia.valor_total))
            ws_guias.cell(row=row_idx, column=11, value=guia.calcular_dias_atraso())

        # Ajustar largura das colunas
        for col in ws_guias.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_guias.column_dimensions[column].width = adjusted_width

        # Salvar
        wb.save(caminho)

        logger.info(f"Relatório Excel salvo: {caminho.absolute()}")
        return caminho

    def fazer_screenshot(self, caminho: str = "fgts_screenshot.png") -> bool:
        """
        Captura screenshot da página atual.

        Args:
            caminho: Caminho onde salvar

        Returns:
            True se sucesso
        """
        if not self.navigator:
            return False
        return self.navigator.fazer_screenshot(caminho)

    def fechar(self) -> None:
        """Fecha navegador e libera recursos."""
        logger.info("Fechando robô...")
        if self.navigator:
            self.navigator.fechar_navegador()
        self.navigator = None
        logger.info("Robô fechado")

    def __enter__(self):
        """Context manager: entrada"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: saída"""
        self.fechar()
        return False

    def __repr__(self) -> str:
        """Representação string do robô"""
        return (
            f"FGTSRobot("
            f"certificado={self.certificado.caminho.name}, "
            f"empresas={len(self.empresas_disponiveis)}, "
            f"autenticado={self.authenticator.autenticado})"
        )
