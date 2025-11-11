"""
Módulo de extração de dados das guias FGTS
==========================================

Extrai informações de guias FGTS a partir do HTML do portal,
processando tabelas e estruturas de dados.
"""

import logging
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup

from .models import GuiaFGTS, StatusGuia, TipoGuia, EmpresaFGTS

logger = logging.getLogger(__name__)


class FGTSExtractor:
    """
    Extrai e processa dados de guias FGTS do HTML do portal.
    """

    # Mapeamento de textos para StatusGuia
    STATUS_MAP = {
        "pendente": StatusGuia.PENDENTE,
        "paga": StatusGuia.PAGA,
        "pago": StatusGuia.PAGA,
        "quitada": StatusGuia.PAGA,
        "vencida": StatusGuia.VENCIDA,
        "em atraso": StatusGuia.VENCIDA,
        "parcelada": StatusGuia.PARCELADA,
        "parcelamento": StatusGuia.PARCELADA,
        "em análise": StatusGuia.EM_ANALISE,
        "análise": StatusGuia.EM_ANALISE,
        "cancelada": StatusGuia.CANCELADA,
    }

    # Mapeamento de textos para TipoGuia
    TIPO_MAP = {
        "mensal": TipoGuia.MENSAL,
        "rescisória": TipoGuia.RESCISORIA,
        "rescisoria": TipoGuia.RESCISORIA,
        "rescisão": TipoGuia.RESCISORIA,
        "complementar": TipoGuia.COMPLEMENTAR,
        "diferença": TipoGuia.DIFERENCA,
        "diferenca": TipoGuia.DIFERENCA,
        "sefip": TipoGuia.SEFIP,
    }

    def __init__(self):
        """Inicializa o extrator."""
        self.guias_extraidas: List[GuiaFGTS] = []
        self.erros: List[str] = []

    def extrair_guias_do_html(
        self,
        html: str,
        empresa: EmpresaFGTS,
        filtrar_status: Optional[List[StatusGuia]] = None
    ) -> List[GuiaFGTS]:
        """
        Extrai guias FGTS do HTML da página.

        Args:
            html: HTML da página de guias
            empresa: Informações da empresa
            filtrar_status: Lista de status para filtrar (opcional)

        Returns:
            Lista de objetos GuiaFGTS extraídos
        """
        try:
            logger.info(f"Extraindo guias para empresa {empresa.cnpj_formatado()}")

            soup = BeautifulSoup(html, 'html.parser')
            guias: List[GuiaFGTS] = []

            # Buscar tabelas de guias
            tabelas = soup.find_all('table')

            if not tabelas:
                logger.warning("Nenhuma tabela encontrada no HTML")
                # Tentar buscar divs com role="grid" (tabela moderna)
                tabelas = soup.find_all('div', {'role': 'grid'})

            for tabela in tabelas:
                guias_tabela = self._extrair_guias_tabela(tabela, empresa)
                guias.extend(guias_tabela)

            # Filtrar por status se solicitado
            if filtrar_status:
                guias = [g for g in guias if g.status in filtrar_status]

            logger.info(f"Total de {len(guias)} guia(s) extraída(s)")
            self.guias_extraidas = guias
            return guias

        except Exception as e:
            logger.error(f"Erro ao extrair guias do HTML: {e}")
            self.erros.append(f"Erro extração HTML: {e}")
            return []

    def _extrair_guias_tabela(self, tabela, empresa: EmpresaFGTS) -> List[GuiaFGTS]:
        """
        Extrai guias de uma tabela HTML.

        Args:
            tabela: Elemento BeautifulSoup da tabela
            empresa: Informações da empresa

        Returns:
            Lista de GuiaFGTS
        """
        guias: List[GuiaFGTS] = []

        try:
            # Buscar linhas da tabela
            linhas = tabela.find_all('tr')

            if not linhas:
                # Tentar formato de grid moderno
                linhas = tabela.find_all('div', {'role': 'row'})

            # Primeira linha geralmente é cabeçalho
            cabecalho = self._extrair_cabecalho(linhas[0] if linhas else None)

            # Processar linhas de dados
            for linha in linhas[1:]:  # Pular cabeçalho
                try:
                    guia = self._extrair_guia_linha(linha, cabecalho, empresa)
                    if guia:
                        guias.append(guia)
                except Exception as e:
                    logger.warning(f"Erro ao processar linha: {e}")
                    continue

        except Exception as e:
            logger.error(f"Erro ao processar tabela: {e}")

        return guias

    def _extrair_cabecalho(self, linha_cabecalho) -> List[str]:
        """
        Extrai nomes das colunas do cabeçalho.

        Args:
            linha_cabecalho: Elemento da linha de cabeçalho

        Returns:
            Lista com nomes das colunas (lowercase)
        """
        if not linha_cabecalho:
            return []

        colunas = []
        celulas = linha_cabecalho.find_all(['th', 'td', 'div'])

        for celula in celulas:
            texto = celula.get_text(strip=True).lower()
            colunas.append(texto)

        return colunas

    def _extrair_guia_linha(
        self,
        linha,
        cabecalho: List[str],
        empresa: EmpresaFGTS
    ) -> Optional[GuiaFGTS]:
        """
        Extrai uma guia de uma linha da tabela.

        Args:
            linha: Elemento da linha
            cabecalho: Lista com nomes das colunas
            empresa: Informações da empresa

        Returns:
            GuiaFGTS ou None se não conseguir extrair
        """
        try:
            # Extrair células
            celulas = linha.find_all(['td', 'div'])

            if len(celulas) < 3:  # Mínimo de colunas
                return None

            # Criar dicionário coluna -> valor
            dados = {}
            for i, celula in enumerate(celulas):
                if i < len(cabecalho):
                    chave = cabecalho[i]
                    valor = celula.get_text(strip=True)
                    dados[chave] = valor

            # Extrair campos (nomes podem variar)
            numero_guia = self._buscar_campo(dados, ['número', 'numero', 'guia', 'código', 'codigo'])
            tipo_texto = self._buscar_campo(dados, ['tipo', 'espécie', 'especie', 'categoria'])
            status_texto = self._buscar_campo(dados, ['status', 'situação', 'situacao'])
            competencia = self._buscar_campo(dados, ['competência', 'competencia', 'período', 'periodo', 'mês', 'mes'])
            vencimento = self._buscar_campo(dados, ['vencimento', 'venc', 'data vencimento'])
            pagamento = self._buscar_campo(dados, ['pagamento', 'pag', 'data pagamento', 'quitação'])
            valor_principal = self._buscar_campo(dados, ['valor', 'principal', 'valor principal'])
            valor_total = self._buscar_campo(dados, ['total', 'valor total', 'a pagar'])

            # Validar campos obrigatórios
            if not numero_guia or not competencia or not vencimento:
                logger.debug("Linha sem dados essenciais, ignorando")
                return None

            # Converter tipo
            tipo = self._converter_tipo(tipo_texto) if tipo_texto else TipoGuia.MENSAL

            # Converter status
            status = self._converter_status(status_texto) if status_texto else StatusGuia.PENDENTE

            # Converter datas
            data_vencimento = self._converter_data(vencimento)
            data_pagamento = self._converter_data(pagamento) if pagamento else None

            if not data_vencimento:
                logger.warning(f"Data de vencimento inválida: {vencimento}")
                return None

            # Converter valores
            val_principal = self._converter_valor(valor_principal) if valor_principal else Decimal("0.00")
            val_total = self._converter_valor(valor_total) if valor_total else val_principal

            # Criar objeto GuiaFGTS
            guia = GuiaFGTS(
                numero_guia=numero_guia,
                tipo=tipo,
                status=status,
                cnpj_empresa=empresa.cnpj,
                razao_social_empresa=empresa.razao_social,
                competencia=self._normalizar_competencia(competencia),
                data_vencimento=data_vencimento,
                data_pagamento=data_pagamento,
                valor_principal=val_principal,
                valor_total=val_total,
            )

            logger.debug(f"Guia extraída: {guia.numero_guia} - {guia.competencia} - {guia.status.value}")
            return guia

        except Exception as e:
            logger.warning(f"Erro ao extrair guia da linha: {e}")
            return None

    def _buscar_campo(self, dados: Dict[str, str], nomes_possiveis: List[str]) -> Optional[str]:
        """
        Busca um campo no dicionário usando nomes possíveis.

        Args:
            dados: Dicionário coluna -> valor
            nomes_possiveis: Lista de nomes possíveis para a coluna

        Returns:
            Valor encontrado ou None
        """
        for chave, valor in dados.items():
            for nome in nomes_possiveis:
                if nome in chave:
                    return valor
        return None

    def _converter_tipo(self, texto: str) -> TipoGuia:
        """Converte texto para TipoGuia."""
        texto_lower = texto.lower().strip()
        for chave, tipo in self.TIPO_MAP.items():
            if chave in texto_lower:
                return tipo
        return TipoGuia.MENSAL  # Padrão

    def _converter_status(self, texto: str) -> StatusGuia:
        """Converte texto para StatusGuia."""
        texto_lower = texto.lower().strip()
        for chave, status in self.STATUS_MAP.items():
            if chave in texto_lower:
                return status
        return StatusGuia.PENDENTE  # Padrão

    def _converter_data(self, texto: str) -> Optional[date]:
        """
        Converte texto para objeto date.

        Formatos aceitos: DD/MM/YYYY, DD/MM/YY, YYYY-MM-DD

        Args:
            texto: Texto da data

        Returns:
            Objeto date ou None se inválido
        """
        if not texto:
            return None

        texto = texto.strip()

        # Tentar formato DD/MM/YYYY
        match = re.match(r'(\d{2})/(\d{2})/(\d{4})', texto)
        if match:
            dia, mes, ano = match.groups()
            try:
                return date(int(ano), int(mes), int(dia))
            except ValueError:
                pass

        # Tentar formato DD/MM/YY
        match = re.match(r'(\d{2})/(\d{2})/(\d{2})', texto)
        if match:
            dia, mes, ano = match.groups()
            try:
                ano_completo = 2000 + int(ano) if int(ano) < 50 else 1900 + int(ano)
                return date(ano_completo, int(mes), int(dia))
            except ValueError:
                pass

        # Tentar formato YYYY-MM-DD
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})', texto)
        if match:
            ano, mes, dia = match.groups()
            try:
                return date(int(ano), int(mes), int(dia))
            except ValueError:
                pass

        return None

    def _converter_valor(self, texto: str) -> Decimal:
        """
        Converte texto de valor monetário para Decimal.

        Formatos aceitos: R$ 1.234,56 | 1.234,56 | 1234.56

        Args:
            texto: Texto do valor

        Returns:
            Decimal ou 0.00 se inválido
        """
        if not texto:
            return Decimal("0.00")

        # Remover símbolos de moeda e espaços
        texto = texto.replace('R$', '').replace(' ', '').strip()

        # Detectar formato brasileiro (1.234,56)
        if ',' in texto and '.' in texto:
            # Formato: 1.234,56
            texto = texto.replace('.', '').replace(',', '.')
        elif ',' in texto:
            # Formato: 1234,56
            texto = texto.replace(',', '.')

        try:
            return Decimal(texto)
        except (InvalidOperation, ValueError):
            logger.warning(f"Valor inválido: {texto}")
            return Decimal("0.00")

    def _normalizar_competencia(self, texto: str) -> str:
        """
        Normaliza competência para formato MM/AAAA.

        Args:
            texto: Texto da competência

        Returns:
            Competência no formato MM/AAAA
        """
        # Remover espaços
        texto = texto.strip()

        # Se já está no formato MM/AAAA
        if re.match(r'\d{2}/\d{4}', texto):
            return texto

        # Tentar extrair mês e ano
        match = re.search(r'(\d{1,2})/(\d{4})', texto)
        if match:
            mes, ano = match.groups()
            return f"{int(mes):02d}/{ano}"

        # Formato AAAA-MM
        match = re.search(r'(\d{4})-(\d{2})', texto)
        if match:
            ano, mes = match.groups()
            return f"{mes}/{ano}"

        # Retornar original se não conseguir normalizar
        return texto

    def obter_erros(self) -> List[str]:
        """Retorna lista de erros encontrados durante extração."""
        return self.erros

    def limpar(self) -> None:
        """Limpa dados extraídos e erros."""
        self.guias_extraidas = []
        self.erros = []
