"""
Modelos de dados para o FGTS Digital Robot.
Usa Pydantic para validação e serialização.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import List, Optional


class TipoGuia(str, Enum):
    MENSAL = "mensal"
    RESCISORIA = "rescisória"
    COMPLEMENTAR = "complementar"
    DECIMO_TERCEIRO = "décimo_terceiro"
    DESCONHECIDO = "desconhecido"


class StatusGuia(str, Enum):
    PENDENTE = "pendente"
    PAGA = "paga"
    VENCIDA = "vencida"
    PARCELADA = "parcelada"
    CANCELADA = "cancelada"
    DESCONHECIDO = "desconhecido"


@dataclass
class CertificadoDigital:
    caminho: Path
    senha: str
    valido_ate: Optional[date] = None
    cpf_cnpj: Optional[str] = None
    nome_titular: Optional[str] = None

    def __post_init__(self):
        self.caminho = Path(self.caminho)

    @property
    def esta_valido(self) -> bool:
        if self.valido_ate is None:
            return True
        return self.valido_ate >= date.today()

    @property
    def dias_para_vencer(self) -> Optional[int]:
        if self.valido_ate is None:
            return None
        return (self.valido_ate - date.today()).days


@dataclass
class EmpresaFGTS:
    cnpj: str
    razao_social: str
    nome_fantasia: str = ""
    tem_procuracao: bool = True
    data_procuracao: Optional[date] = None

    @property
    def cnpj_formatado(self) -> str:
        c = self.cnpj.replace(".", "").replace("/", "").replace("-", "")
        if len(c) == 14:
            return f"{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:14]}"
        return self.cnpj


@dataclass
class GuiaFGTS:
    numero_guia: str
    cnpj_empresa: str
    tipo: TipoGuia = TipoGuia.DESCONHECIDO
    status: StatusGuia = StatusGuia.DESCONHECIDO
    competencia: str = ""
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    valor_principal: Decimal = field(default_factory=lambda: Decimal("0"))
    valor_multa: Decimal = field(default_factory=lambda: Decimal("0"))
    valor_juros: Decimal = field(default_factory=lambda: Decimal("0"))
    valor_total: Decimal = field(default_factory=lambda: Decimal("0"))
    codigo_barras: Optional[str] = None
    observacao: Optional[str] = None

    @property
    def dias_atraso(self) -> Optional[int]:
        if self.status not in (StatusGuia.VENCIDA, StatusGuia.PENDENTE):
            return None
        if self.data_vencimento is None:
            return None
        hoje = date.today()
        if hoje > self.data_vencimento:
            return (hoje - self.data_vencimento).days
        return 0

    @property
    def esta_vencida(self) -> bool:
        if self.data_vencimento is None:
            return False
        return date.today() > self.data_vencimento and self.status != StatusGuia.PAGA


@dataclass
class RelatorioFGTS:
    empresas: List[EmpresaFGTS] = field(default_factory=list)
    guias: List[GuiaFGTS] = field(default_factory=list)
    gerado_em: datetime = field(default_factory=datetime.now)
    tempo_execucao_segundos: float = 0.0

    @property
    def total_guias(self) -> int:
        return len(self.guias)

    @property
    def total_pendentes(self) -> int:
        return sum(1 for g in self.guias if g.status == StatusGuia.PENDENTE)

    @property
    def total_pagas(self) -> int:
        return sum(1 for g in self.guias if g.status == StatusGuia.PAGA)

    @property
    def total_vencidas(self) -> int:
        return sum(1 for g in self.guias if g.status == StatusGuia.VENCIDA)

    @property
    def total_parceladas(self) -> int:
        return sum(1 for g in self.guias if g.status == StatusGuia.PARCELADA)

    @property
    def valor_total_pendente(self) -> Decimal:
        return sum(
            (g.valor_total for g in self.guias if g.status in (StatusGuia.PENDENTE, StatusGuia.VENCIDA)),
            Decimal("0"),
        )

    @property
    def valor_total_pago(self) -> Decimal:
        return sum(
            (g.valor_total for g in self.guias if g.status == StatusGuia.PAGA),
            Decimal("0"),
        )

    def guias_por_empresa(self, cnpj: str) -> List[GuiaFGTS]:
        return [g for g in self.guias if g.cnpj_empresa == cnpj]

    def guias_por_status(self, status: StatusGuia) -> List[GuiaFGTS]:
        return [g for g in self.guias if g.status == status]

    def to_dict(self) -> dict:
        return {
            "gerado_em": self.gerado_em.isoformat(),
            "tempo_execucao_segundos": self.tempo_execucao_segundos,
            "resumo": {
                "total_guias": self.total_guias,
                "total_pendentes": self.total_pendentes,
                "total_pagas": self.total_pagas,
                "total_vencidas": self.total_vencidas,
                "total_parceladas": self.total_parceladas,
                "valor_total_pendente": str(self.valor_total_pendente),
                "valor_total_pago": str(self.valor_total_pago),
            },
            "empresas": [
                {
                    "cnpj": e.cnpj,
                    "razao_social": e.razao_social,
                    "nome_fantasia": e.nome_fantasia,
                }
                for e in self.empresas
            ],
            "guias": [
                {
                    "numero_guia": g.numero_guia,
                    "cnpj_empresa": g.cnpj_empresa,
                    "tipo": g.tipo.value,
                    "status": g.status.value,
                    "competencia": g.competencia,
                    "data_vencimento": g.data_vencimento.isoformat() if g.data_vencimento else None,
                    "data_pagamento": g.data_pagamento.isoformat() if g.data_pagamento else None,
                    "valor_principal": str(g.valor_principal),
                    "valor_multa": str(g.valor_multa),
                    "valor_juros": str(g.valor_juros),
                    "valor_total": str(g.valor_total),
                    "codigo_barras": g.codigo_barras,
                    "observacao": g.observacao,
                    "dias_atraso": g.dias_atraso,
                }
                for g in self.guias
            ],
        }
