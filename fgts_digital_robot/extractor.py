"""
Extração de dados HTML do portal FGTS Digital.
Usa BeautifulSoup para parsear listas de empresas e guias.

Os seletores CSS/XPath são baseados na estrutura do portal observada até 2024.
Se o portal mudar, ajuste os seletores neste arquivo.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List, Optional

from .models import EmpresaFGTS, GuiaFGTS, StatusGuia, TipoGuia

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapeamentos
# ---------------------------------------------------------------------------

_STATUS_MAP = {
    "pendente": StatusGuia.PENDENTE,
    "a vencer": StatusGuia.PENDENTE,
    "em aberto": StatusGuia.PENDENTE,
    "paga": StatusGuia.PAGA,
    "pago": StatusGuia.PAGA,
    "quitada": StatusGuia.PAGA,
    "quitado": StatusGuia.PAGA,
    "vencida": StatusGuia.VENCIDA,
    "vencido": StatusGuia.VENCIDA,
    "em atraso": StatusGuia.VENCIDA,
    "parcelada": StatusGuia.PARCELADA,
    "parcelado": StatusGuia.PARCELADA,
    "cancelada": StatusGuia.CANCELADA,
    "cancelado": StatusGuia.CANCELADA,
}

_TIPO_MAP = {
    "mensal": TipoGuia.MENSAL,
    "rescisória": TipoGuia.RESCISORIA,
    "rescisoria": TipoGuia.RESCISORIA,
    "rescisório": TipoGuia.RESCISORIA,
    "rescisorio": TipoGuia.RESCISORIA,
    "complementar": TipoGuia.COMPLEMENTAR,
    "décimo terceiro": TipoGuia.DECIMO_TERCEIRO,
    "decimo terceiro": TipoGuia.DECIMO_TERCEIRO,
    "13º salário": TipoGuia.DECIMO_TERCEIRO,
    "13 salario": TipoGuia.DECIMO_TERCEIRO,
}


# ---------------------------------------------------------------------------
# Helpers de parsing
# ---------------------------------------------------------------------------

def _limpar_valor(texto: Optional[str]) -> Decimal:
    """Converte string de valor monetário em Decimal. Ex: 'R$ 1.234,56' -> Decimal('1234.56')"""
    if not texto:
        return Decimal("0")
    texto = texto.strip()
    texto = re.sub(r"[R$\s]", "", texto)
    texto = texto.replace(".", "").replace(",", ".")
    try:
        return Decimal(texto)
    except InvalidOperation:
        return Decimal("0")


def _parsear_data(texto: Optional[str]) -> Optional[date]:
    """Tenta converter string de data em objeto date. Suporta dd/mm/yyyy e yyyy-mm-dd."""
    if not texto:
        return None
    texto = texto.strip()
    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"]
    for fmt in formatos:
        try:
            return date(*[int(p) for p in __import__("datetime").datetime.strptime(texto, fmt).timetuple()[:3]])
        except (ValueError, TypeError):
            continue
    return None


def _normalizar(texto: Optional[str]) -> str:
    if not texto:
        return ""
    return texto.strip().lower()


def _mapear_status(texto: str) -> StatusGuia:
    n = _normalizar(texto)
    for chave, status in _STATUS_MAP.items():
        if chave in n:
            return status
    return StatusGuia.DESCONHECIDO


def _mapear_tipo(texto: str) -> TipoGuia:
    n = _normalizar(texto)
    for chave, tipo in _TIPO_MAP.items():
        if chave in n:
            return tipo
    return TipoGuia.DESCONHECIDO


def _extrair_cnpj(texto: str) -> str:
    """Extrai CNPJ de um texto, retornando apenas os dígitos."""
    match = re.search(r"\d{2}[\.\s]?\d{3}[\.\s]?\d{3}[/\s]?\d{4}[-\s]?\d{2}", texto)
    if match:
        return re.sub(r"\D", "", match.group())
    return re.sub(r"\D", "", texto)[:14]


# ---------------------------------------------------------------------------
# Extractor principal
# ---------------------------------------------------------------------------

class FGTSExtractor:
    """
    Extrai dados estruturados do HTML do portal FGTS Digital.

    Os seletores foram construídos com base na estrutura do portal.
    Caso o portal mude, atualize os seletores abaixo.
    """

    def __init__(self):
        try:
            from bs4 import BeautifulSoup  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "BeautifulSoup4 não está instalado. Execute: pip install beautifulsoup4"
            ) from exc

    def _soup(self, html: str):
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, "html.parser")

    # ------------------------------------------------------------------
    # Empresas
    # ------------------------------------------------------------------

    def extrair_empresas(self, html: str) -> List[EmpresaFGTS]:
        """Extrai lista de empresas do HTML da página de procurações."""
        soup = self._soup(html)
        empresas: List[EmpresaFGTS] = []

        # Estratégia 1: tabela com classe relacionada a empresas/procurações
        empresas = self._extrair_empresas_tabela(soup)
        if empresas:
            return empresas

        # Estratégia 2: lista/cards
        empresas = self._extrair_empresas_lista(soup)
        if empresas:
            return empresas

        # Estratégia 3: select/dropdown
        empresas = self._extrair_empresas_select(soup)

        return empresas

    def _extrair_empresas_tabela(self, soup) -> List[EmpresaFGTS]:
        """Extrai empresas de uma tabela HTML."""
        empresas: List[EmpresaFGTS] = []

        # Candidatos a tabelas de empresa
        seletores = [
            "table.procuracoes",
            "table.empresas",
            "table#tabelaEmpresas",
            "table#tabelaProcuracoes",
            "table",
        ]

        tabela = None
        for sel in seletores:
            tabela = soup.select_one(sel)
            if tabela:
                break

        if tabela is None:
            return empresas

        linhas = tabela.select("tbody tr")
        if not linhas:
            linhas = tabela.select("tr")[1:]  # Pula cabeçalho

        for linha in linhas:
            cols = linha.select("td")
            if len(cols) < 2:
                continue

            textos = [c.get_text(strip=True) for c in cols]
            cnpj = _extrair_cnpj(textos[0])
            razao = textos[1] if len(textos) > 1 else ""
            fantasia = textos[2] if len(textos) > 2 else ""

            if not cnpj:
                # Tenta encontrar CNPJ em qualquer célula
                for t in textos:
                    cnpj = _extrair_cnpj(t)
                    if cnpj:
                        break

            if cnpj:
                empresas.append(
                    EmpresaFGTS(
                        cnpj=cnpj,
                        razao_social=razao,
                        nome_fantasia=fantasia,
                        tem_procuracao=True,
                    )
                )

        return empresas

    def _extrair_empresas_lista(self, soup) -> List[EmpresaFGTS]:
        """Extrai empresas de uma lista ou cards."""
        empresas: List[EmpresaFGTS] = []

        seletores = [
            ".empresa-item",
            ".card-empresa",
            "li.empresa",
            "[data-empresa]",
        ]

        for sel in seletores:
            items = soup.select(sel)
            if not items:
                continue
            for item in items:
                texto = item.get_text(" ", strip=True)
                cnpj = _extrair_cnpj(texto)
                if cnpj:
                    # Razão social: texto após o CNPJ
                    razao = re.sub(r"[\d./-]+", "", texto).strip()
                    empresas.append(
                        EmpresaFGTS(cnpj=cnpj, razao_social=razao, tem_procuracao=True)
                    )
            if empresas:
                break

        return empresas

    def _extrair_empresas_select(self, soup) -> List[EmpresaFGTS]:
        """Extrai empresas de um elemento <select>."""
        empresas: List[EmpresaFGTS] = []

        seletores = [
            "select#empresa",
            "select#cnpj",
            "select.empresa-select",
            "select",
        ]

        for sel in seletores:
            select = soup.select_one(sel)
            if select is None:
                continue
            for option in select.select("option"):
                val = option.get("value", "")
                texto = option.get_text(strip=True)
                cnpj = _extrair_cnpj(val) or _extrair_cnpj(texto)
                if cnpj:
                    razao = re.sub(r"[\d./-]+", "", texto).strip()
                    empresas.append(
                        EmpresaFGTS(cnpj=cnpj, razao_social=razao, tem_procuracao=True)
                    )
            if empresas:
                break

        return empresas

    # ------------------------------------------------------------------
    # Guias
    # ------------------------------------------------------------------

    def extrair_guias(self, html: str, cnpj_empresa: str) -> List[GuiaFGTS]:
        """Extrai lista de guias do HTML da página de guias."""
        soup = self._soup(html)
        guias: List[GuiaFGTS] = []

        # Estratégia 1: tabela
        guias = self._extrair_guias_tabela(soup, cnpj_empresa)
        if guias:
            return guias

        # Estratégia 2: cards/divs
        guias = self._extrair_guias_cards(soup, cnpj_empresa)

        return guias

    def _extrair_guias_tabela(self, soup, cnpj_empresa: str) -> List[GuiaFGTS]:
        """Extrai guias de uma tabela HTML."""
        guias: List[GuiaFGTS] = []

        seletores = [
            "table.guias",
            "table#tabelaGuias",
            "table.table-guias",
            "table",
        ]

        tabela = None
        for sel in seletores:
            tabela = soup.select_one(sel)
            if tabela:
                break

        if tabela is None:
            return guias

        # Tentar inferir índices das colunas pelo cabeçalho
        cabecalho = tabela.select("thead th")
        if not cabecalho:
            cabecalho = tabela.select("tr th")

        indices = self._inferir_indices_colunas(cabecalho)

        linhas = tabela.select("tbody tr")
        if not linhas:
            todas = tabela.select("tr")
            linhas = todas[1:] if todas else []

        for linha in linhas:
            guia = self._parsear_linha_guia(linha, cnpj_empresa, indices)
            if guia:
                guias.append(guia)

        return guias

    def _inferir_indices_colunas(self, cabecalhos) -> dict:
        """
        Tenta mapear colunas por texto do cabeçalho.
        Retorna dicionário com índices: numero, tipo, status, competencia,
        vencimento, pagamento, valor_principal, valor_total.
        """
        indices = {
            "numero": 0,
            "tipo": 1,
            "status": 2,
            "competencia": 3,
            "vencimento": 4,
            "pagamento": 5,
            "valor_principal": 6,
            "valor_total": 7,
        }

        if not cabecalhos:
            return indices

        mapa = {
            "número": "numero",
            "numero": "numero",
            "guia": "numero",
            "tipo": "tipo",
            "status": "status",
            "situação": "status",
            "situacao": "status",
            "competência": "competencia",
            "competencia": "competencia",
            "vencimento": "vencimento",
            "pagamento": "pagamento",
            "principal": "valor_principal",
            "valor principal": "valor_principal",
            "total": "valor_total",
            "valor total": "valor_total",
        }

        for i, th in enumerate(cabecalhos):
            texto = _normalizar(th.get_text())
            for chave, campo in mapa.items():
                if chave in texto:
                    indices[campo] = i
                    break

        return indices

    def _parsear_linha_guia(self, linha, cnpj_empresa: str, indices: dict) -> Optional[GuiaFGTS]:
        """Extrai uma GuiaFGTS de uma linha de tabela."""
        cols = linha.select("td")
        if not cols:
            return None

        def _texto(campo: str) -> str:
            idx = indices.get(campo, -1)
            if 0 <= idx < len(cols):
                return cols[idx].get_text(strip=True)
            return ""

        numero = _texto("numero")
        if not numero:
            # Se não tem número de guia, pula a linha
            return None

        return GuiaFGTS(
            numero_guia=numero,
            cnpj_empresa=cnpj_empresa,
            tipo=_mapear_tipo(_texto("tipo")),
            status=_mapear_status(_texto("status")),
            competencia=_texto("competencia"),
            data_vencimento=_parsear_data(_texto("vencimento")),
            data_pagamento=_parsear_data(_texto("pagamento")),
            valor_principal=_limpar_valor(_texto("valor_principal")),
            valor_total=_limpar_valor(_texto("valor_total")),
        )

    def _extrair_guias_cards(self, soup, cnpj_empresa: str) -> List[GuiaFGTS]:
        """Extrai guias de cards/divs."""
        guias: List[GuiaFGTS] = []

        seletores = [
            ".card-guia",
            ".guia-item",
            "[data-guia]",
            ".detalhe-guia",
        ]

        for sel in seletores:
            cards = soup.select(sel)
            if not cards:
                continue
            for card in cards:
                texto = card.get_text(" ", strip=True)

                # Número de guia
                match_numero = re.search(r"(?:guia|n[°º\.])[\s:]*([A-Z0-9/-]+)", texto, re.IGNORECASE)
                numero = match_numero.group(1).strip() if match_numero else texto[:20]

                # Valor total
                match_valor = re.search(r"R\$[\s]*([\d.,]+)", texto)
                valor_total = _limpar_valor(match_valor.group(1) if match_valor else "0")

                # Status
                status = StatusGuia.DESCONHECIDO
                for chave, s in _STATUS_MAP.items():
                    if chave in texto.lower():
                        status = s
                        break

                guias.append(
                    GuiaFGTS(
                        numero_guia=numero,
                        cnpj_empresa=cnpj_empresa,
                        status=status,
                        valor_total=valor_total,
                    )
                )
            if guias:
                break

        return guias
