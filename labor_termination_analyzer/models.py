"""
Modelos de dados para rescisão trabalhista
"""

from datetime import date
from decimal import Decimal
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class Funcionario(BaseModel):
    """Dados do funcionário"""
    nome: str
    cpf: str
    cargo: str
    data_admissao: date
    data_demissao: date
    salario_bruto: Decimal


class Verbas(BaseModel):
    """Verbas rescisórias"""
    saldo_salario: Decimal = Decimal("0.00")
    aviso_previo_indenizado: Decimal = Decimal("0.00")
    ferias_vencidas: Decimal = Decimal("0.00")
    ferias_proporcionais: Decimal = Decimal("0.00")
    um_terco_ferias: Decimal = Decimal("0.00")
    decimo_terceiro_proporcional: Decimal = Decimal("0.00")
    multa_fgts_40: Decimal = Decimal("0.00")
    saldo_fgts: Decimal = Decimal("0.00")
    outras_verbas: Dict[str, Decimal] = Field(default_factory=dict)


class Descontos(BaseModel):
    """Descontos na rescisão"""
    inss: Decimal = Decimal("0.00")
    irrf: Decimal = Decimal("0.00")
    aviso_previo_indenizado: Decimal = Decimal("0.00")
    outros_descontos: Dict[str, Decimal] = Field(default_factory=dict)


class RescisaoTrabalhista(BaseModel):
    """Modelo completo de uma rescisão trabalhista"""
    funcionario: Funcionario
    tipo_rescisao: str  # "sem justa causa", "com justa causa", "pedido de demissao", "acordo"
    verbas: Verbas
    descontos: Descontos
    observacoes: Optional[str] = None

    @property
    def total_verbas(self) -> Decimal:
        """Calcula o total de verbas"""
        total = (
            self.verbas.saldo_salario +
            self.verbas.aviso_previo_indenizado +
            self.verbas.ferias_vencidas +
            self.verbas.ferias_proporcionais +
            self.verbas.um_terco_ferias +
            self.verbas.decimo_terceiro_proporcional +
            self.verbas.multa_fgts_40 +
            self.verbas.saldo_fgts +
            sum(self.verbas.outras_verbas.values())
        )
        return total

    @property
    def total_descontos(self) -> Decimal:
        """Calcula o total de descontos"""
        total = (
            self.descontos.inss +
            self.descontos.irrf +
            self.descontos.aviso_previo_indenizado +
            sum(self.descontos.outros_descontos.values())
        )
        return total

    @property
    def valor_liquido(self) -> Decimal:
        """Calcula o valor líquido a receber"""
        return self.total_verbas - self.total_descontos

    @property
    def tempo_servico_anos(self) -> float:
        """Calcula o tempo de serviço em anos"""
        dias = (self.funcionario.data_demissao - self.funcionario.data_admissao).days
        return round(dias / 365.25, 2)

    @property
    def tempo_servico_meses(self) -> int:
        """Calcula o tempo de serviço em meses completos"""
        dias = (self.funcionario.data_demissao - self.funcionario.data_admissao).days
        return int(dias / 30.44)
