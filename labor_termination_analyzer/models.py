"""
Modelos de dados para análise de rescisões trabalhistas.

Este módulo define as estruturas de dados usando Pydantic para
validação e serialização de informações de rescisões trabalhistas.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Funcionario(BaseModel):
    """
    Representa os dados de um funcionário.

    Attributes:
        nome: Nome completo do funcionário
        cpf: CPF no formato XXX.XXX.XXX-XX ou apenas números
        cargo: Cargo/função exercida
        data_admissao: Data de admissão na empresa
        data_demissao: Data de demissão/rescisão
        salario_bruto: Salário bruto mensal
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(..., min_length=3, description="Nome completo do funcionário")
    cpf: str = Field(..., pattern=r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$", description="CPF do funcionário")
    cargo: str = Field(..., min_length=2, description="Cargo/função")
    data_admissao: date = Field(..., description="Data de admissão")
    data_demissao: date = Field(..., description="Data de demissão")
    salario_bruto: Decimal = Field(..., gt=0, description="Salário bruto mensal")

    @field_validator('data_demissao')
    @classmethod
    def validar_datas(cls, v: date, info) -> date:
        """Valida que a data de demissão é posterior à admissão."""
        if 'data_admissao' in info.data and v < info.data['data_admissao']:
            raise ValueError('Data de demissão deve ser posterior à data de admissão')
        return v

    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        """Valida o formato e dígitos verificadores do CPF."""
        # Remove pontos e traços
        cpf_numeros = ''.join(c for c in v if c.isdigit())

        if len(cpf_numeros) != 11:
            raise ValueError('CPF deve ter 11 dígitos')

        # Verifica se todos os dígitos são iguais (CPF inválido)
        if cpf_numeros == cpf_numeros[0] * 11:
            raise ValueError('CPF inválido')

        # Validação dos dígitos verificadores
        def calcular_digito(cpf_parcial: str) -> str:
            soma = sum(int(cpf_parcial[i]) * (len(cpf_parcial) + 1 - i) for i in range(len(cpf_parcial)))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        digito1 = calcular_digito(cpf_numeros[:9])
        digito2 = calcular_digito(cpf_numeros[:9] + digito1)

        if cpf_numeros[-2:] != digito1 + digito2:
            raise ValueError('CPF com dígitos verificadores inválidos')

        return v

    def tempo_servico_anos(self) -> int:
        """Calcula o tempo de serviço em anos completos."""
        delta = self.data_demissao - self.data_admissao
        return delta.days // 365

    def tempo_servico_meses(self) -> int:
        """Calcula o tempo de serviço em meses completos."""
        anos = (self.data_demissao.year - self.data_admissao.year)
        meses = (self.data_demissao.month - self.data_admissao.month)
        return anos * 12 + meses


class Rescisao(BaseModel):
    """
    Representa uma rescisão trabalhista completa.

    Attributes:
        funcionario: Dados do funcionário
        tipo_rescisao: Tipo de rescisão contratual
        verbas: Dicionário com valores a receber (nome da verba: valor)
        descontos: Dicionário com valores a descontar (nome do desconto: valor)
        observacoes: Observações adicionais opcionais
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    funcionario: Funcionario
    tipo_rescisao: Literal[
        "sem justa causa",
        "com justa causa",
        "pedido de demissao",
        "acordo"
    ] = Field(..., description="Tipo de rescisão")
    verbas: dict[str, Decimal] = Field(default_factory=dict, description="Verbas a receber")
    descontos: dict[str, Decimal] = Field(default_factory=dict, description="Descontos")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")

    @field_validator('verbas', 'descontos')
    @classmethod
    def validar_valores_positivos(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        """Valida que todos os valores são não-negativos."""
        for chave, valor in v.items():
            if valor < 0:
                raise ValueError(f'Valor de "{chave}" não pode ser negativo: {valor}')
        return v

    def total_verbas(self) -> Decimal:
        """Calcula o total de verbas a receber."""
        return sum(self.verbas.values(), Decimal('0'))

    def total_descontos(self) -> Decimal:
        """Calcula o total de descontos."""
        return sum(self.descontos.values(), Decimal('0'))

    def valor_liquido(self) -> Decimal:
        """Calcula o valor líquido da rescisão."""
        return self.total_verbas() - self.total_descontos()

    def porcentagem_desconto(self) -> Decimal:
        """Calcula a porcentagem de desconto sobre o total de verbas."""
        total_v = self.total_verbas()
        if total_v == 0:
            return Decimal('0')
        return (self.total_descontos() / total_v) * Decimal('100')


class RescisaoTrabalhista(Rescisao):
    """Alias para compatibilidade - mesmo que Rescisao."""
    pass


class Verbas(BaseModel):
    """
    Representa o conjunto de verbas rescisórias.

    Usado para organizar e validar verbas de forma estruturada.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    saldo_salario: Optional[Decimal] = Field(None, ge=0, description="Saldo de salário")
    aviso_previo: Optional[Decimal] = Field(None, ge=0, description="Aviso prévio indenizado")
    ferias_vencidas: Optional[Decimal] = Field(None, ge=0, description="Férias vencidas")
    ferias_proporcionais: Optional[Decimal] = Field(None, ge=0, description="Férias proporcionais")
    decimo_terceiro: Optional[Decimal] = Field(None, ge=0, description="13º salário proporcional")
    multa_fgts: Optional[Decimal] = Field(None, ge=0, description="Multa 40% FGTS")
    outros: Optional[dict[str, Decimal]] = Field(default_factory=dict, description="Outras verbas")

    def total(self) -> Decimal:
        """Calcula o total de todas as verbas."""
        total = Decimal('0')
        for field_name in ['saldo_salario', 'aviso_previo', 'ferias_vencidas',
                          'ferias_proporcionais', 'decimo_terceiro', 'multa_fgts']:
            valor = getattr(self, field_name)
            if valor is not None:
                total += valor

        if self.outros:
            total += sum(self.outros.values(), Decimal('0'))

        return total


class Descontos(BaseModel):
    """
    Representa o conjunto de descontos rescisórios.

    Usado para organizar e validar descontos de forma estruturada.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    inss: Optional[Decimal] = Field(None, ge=0, description="INSS")
    irrf: Optional[Decimal] = Field(None, ge=0, description="IRRF")
    aviso_previo_descontado: Optional[Decimal] = Field(None, ge=0, description="Aviso prévio não cumprido")
    outros: Optional[dict[str, Decimal]] = Field(default_factory=dict, description="Outros descontos")

    def total(self) -> Decimal:
        """Calcula o total de todos os descontos."""
        total = Decimal('0')
        for field_name in ['inss', 'irrf', 'aviso_previo_descontado']:
            valor = getattr(self, field_name)
            if valor is not None:
                total += valor

        if self.outros:
            total += sum(self.outros.values(), Decimal('0'))

        return total
