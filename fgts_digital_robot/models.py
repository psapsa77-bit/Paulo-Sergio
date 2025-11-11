"""
Modelos de dados para o FGTS Digital Robot
==========================================

Define as estruturas de dados usando Pydantic para validação
e serialização de informações do FGTS Digital.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, ConfigDict


class StatusGuia(str, Enum):
    """Status possíveis de uma guia FGTS"""
    PENDENTE = "pendente"
    PAGA = "paga"
    VENCIDA = "vencida"
    PARCELADA = "parcelada"
    EM_ANALISE = "em_analise"
    CANCELADA = "cancelada"


class TipoGuia(str, Enum):
    """Tipos de guias FGTS"""
    MENSAL = "mensal"
    RESCISORIA = "rescisoria"
    COMPLEMENTAR = "complementar"
    DIFERENCA = "diferenca"
    SEFIP = "sefip"


class CertificadoDigital(BaseModel):
    """Informações do certificado digital A1"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    caminho: Path = Field(..., description="Caminho do arquivo .pfx ou .p12")
    senha: str = Field(..., description="Senha do certificado")
    valido_ate: Optional[date] = Field(None, description="Data de validade do certificado")
    cpf_cnpj: Optional[str] = Field(None, description="CPF/CNPJ associado ao certificado")
    nome_titular: Optional[str] = Field(None, description="Nome do titular do certificado")

    @field_validator("caminho")
    @classmethod
    def validar_caminho(cls, v: Path) -> Path:
        """Valida se o arquivo do certificado existe"""
        if not v.exists():
            raise ValueError(f"Certificado não encontrado em: {v}")
        if v.suffix.lower() not in ['.pfx', '.p12']:
            raise ValueError("Certificado deve ser .pfx ou .p12")
        return v

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        """Valida se a senha não está vazia"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Senha do certificado não pode estar vazia")
        return v


class EmpresaFGTS(BaseModel):
    """Informações de uma empresa no FGTS Digital"""

    cnpj: str = Field(..., description="CNPJ da empresa")
    razao_social: str = Field(..., description="Razão social da empresa")
    nome_fantasia: Optional[str] = Field(None, description="Nome fantasia")
    inscricao_cei: Optional[str] = Field(None, description="Inscrição CEI")
    situacao: Optional[str] = Field(None, description="Situação cadastral")
    tem_procuracao: bool = Field(True, description="Possui procuração ativa")
    data_procuracao: Optional[date] = Field(None, description="Data da procuração")

    @field_validator("cnpj")
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        """Remove formatação do CNPJ"""
        return ''.join(filter(str.isdigit, v))

    def cnpj_formatado(self) -> str:
        """Retorna CNPJ formatado: XX.XXX.XXX/XXXX-XX"""
        cnpj = self.cnpj
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"


class GuiaFGTS(BaseModel):
    """Informações de uma guia FGTS"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Identificação
    numero_guia: str = Field(..., description="Número da guia")
    tipo: TipoGuia = Field(..., description="Tipo da guia")
    status: StatusGuia = Field(..., description="Status da guia")

    # Empresa
    cnpj_empresa: str = Field(..., description="CNPJ da empresa")
    razao_social_empresa: str = Field(..., description="Razão social da empresa")

    # Datas
    competencia: str = Field(..., description="Competência (MM/AAAA)")
    data_vencimento: date = Field(..., description="Data de vencimento")
    data_pagamento: Optional[date] = Field(None, description="Data de pagamento")
    data_emissao: Optional[date] = Field(None, description="Data de emissão")

    # Valores
    valor_principal: Decimal = Field(..., description="Valor principal da guia")
    valor_multa: Decimal = Field(Decimal("0.00"), description="Valor de multa")
    valor_juros: Decimal = Field(Decimal("0.00"), description="Valor de juros")
    valor_total: Decimal = Field(..., description="Valor total a pagar")

    # Informações adicionais
    quantidade_trabalhadores: Optional[int] = Field(None, description="Quantidade de trabalhadores")
    codigo_barras: Optional[str] = Field(None, description="Código de barras para pagamento")
    linha_digitavel: Optional[str] = Field(None, description="Linha digitável")
    observacoes: Optional[str] = Field(None, description="Observações")

    # Metadados
    extraido_em: datetime = Field(default_factory=datetime.now, description="Data/hora da extração")

    @field_validator("valor_principal", "valor_multa", "valor_juros", "valor_total")
    @classmethod
    def validar_valores(cls, v: Decimal) -> Decimal:
        """Valida que valores monetários não sejam negativos"""
        if v < 0:
            raise ValueError("Valores não podem ser negativos")
        return v

    @field_validator("competencia")
    @classmethod
    def validar_competencia(cls, v: str) -> str:
        """Valida formato da competência MM/AAAA"""
        if not v or len(v) != 7 or v[2] != '/':
            raise ValueError("Competência deve estar no formato MM/AAAA")
        mes, ano = v.split('/')
        if not (1 <= int(mes) <= 12):
            raise ValueError("Mês deve estar entre 01 e 12")
        return v

    def calcular_dias_atraso(self) -> int:
        """Calcula quantos dias de atraso a guia possui"""
        if self.status == StatusGuia.PAGA:
            return 0
        hoje = date.today()
        if hoje > self.data_vencimento:
            return (hoje - self.data_vencimento).days
        return 0

    def esta_vencida(self) -> bool:
        """Verifica se a guia está vencida"""
        return date.today() > self.data_vencimento and self.status != StatusGuia.PAGA

    def valor_pago(self) -> Decimal:
        """Retorna o valor pago (0 se não paga)"""
        return self.valor_total if self.status == StatusGuia.PAGA else Decimal("0.00")


class RelatorioFGTS(BaseModel):
    """Relatório consolidado de guias FGTS"""

    # Informações gerais
    data_geracao: datetime = Field(default_factory=datetime.now, description="Data de geração do relatório")
    periodo_inicio: Optional[date] = Field(None, description="Início do período consultado")
    periodo_fim: Optional[date] = Field(None, description="Fim do período consultado")

    # Empresas e guias
    empresas: List[EmpresaFGTS] = Field(default_factory=list, description="Lista de empresas consultadas")
    guias: List[GuiaFGTS] = Field(default_factory=list, description="Lista de guias extraídas")

    # Estatísticas
    total_empresas: int = Field(0, description="Total de empresas consultadas")
    total_guias: int = Field(0, description="Total de guias encontradas")
    total_pendentes: int = Field(0, description="Total de guias pendentes")
    total_pagas: int = Field(0, description="Total de guias pagas")
    total_vencidas: int = Field(0, description="Total de guias vencidas")

    # Valores
    valor_total_pendente: Decimal = Field(Decimal("0.00"), description="Valor total pendente")
    valor_total_pago: Decimal = Field(Decimal("0.00"), description="Valor total pago")
    valor_total_geral: Decimal = Field(Decimal("0.00"), description="Valor total geral")

    # Metadados
    certificado_usado: Optional[str] = Field(None, description="CPF/CNPJ do certificado usado")
    tempo_execucao_segundos: Optional[float] = Field(None, description="Tempo de execução em segundos")
    erros: List[str] = Field(default_factory=list, description="Lista de erros encontrados")

    def calcular_estatisticas(self) -> None:
        """Calcula estatísticas do relatório baseado nas guias"""
        self.total_empresas = len(self.empresas)
        self.total_guias = len(self.guias)

        self.total_pendentes = sum(1 for g in self.guias if g.status == StatusGuia.PENDENTE)
        self.total_pagas = sum(1 for g in self.guias if g.status == StatusGuia.PAGA)
        self.total_vencidas = sum(1 for g in self.guias if g.esta_vencida())

        self.valor_total_pendente = sum(
            (g.valor_total for g in self.guias if g.status != StatusGuia.PAGA),
            Decimal("0.00")
        )
        self.valor_total_pago = sum(
            (g.valor_total for g in self.guias if g.status == StatusGuia.PAGA),
            Decimal("0.00")
        )
        self.valor_total_geral = self.valor_total_pendente + self.valor_total_pago

    def agrupar_por_empresa(self) -> Dict[str, List[GuiaFGTS]]:
        """Agrupa guias por CNPJ da empresa"""
        resultado: Dict[str, List[GuiaFGTS]] = {}
        for guia in self.guias:
            if guia.cnpj_empresa not in resultado:
                resultado[guia.cnpj_empresa] = []
            resultado[guia.cnpj_empresa].append(guia)
        return resultado

    def agrupar_por_status(self) -> Dict[StatusGuia, List[GuiaFGTS]]:
        """Agrupa guias por status"""
        resultado: Dict[StatusGuia, List[GuiaFGTS]] = {}
        for guia in self.guias:
            if guia.status not in resultado:
                resultado[guia.status] = []
            resultado[guia.status].append(guia)
        return resultado

    def exportar_dict(self) -> Dict[str, Any]:
        """Exporta relatório como dicionário"""
        return {
            "data_geracao": self.data_geracao.isoformat(),
            "periodo": {
                "inicio": self.periodo_inicio.isoformat() if self.periodo_inicio else None,
                "fim": self.periodo_fim.isoformat() if self.periodo_fim else None,
            },
            "estatisticas": {
                "total_empresas": self.total_empresas,
                "total_guias": self.total_guias,
                "total_pendentes": self.total_pendentes,
                "total_pagas": self.total_pagas,
                "total_vencidas": self.total_vencidas,
            },
            "valores": {
                "total_pendente": float(self.valor_total_pendente),
                "total_pago": float(self.valor_total_pago),
                "total_geral": float(self.valor_total_geral),
            },
            "empresas": [
                {
                    "cnpj": e.cnpj_formatado(),
                    "razao_social": e.razao_social,
                    "nome_fantasia": e.nome_fantasia,
                }
                for e in self.empresas
            ],
            "guias": [
                {
                    "numero_guia": g.numero_guia,
                    "tipo": g.tipo.value,
                    "status": g.status.value,
                    "cnpj_empresa": g.cnpj_empresa,
                    "razao_social": g.razao_social_empresa,
                    "competencia": g.competencia,
                    "vencimento": g.data_vencimento.isoformat(),
                    "valor_total": float(g.valor_total),
                    "dias_atraso": g.calcular_dias_atraso(),
                }
                for g in self.guias
            ],
            "metadados": {
                "certificado_usado": self.certificado_usado,
                "tempo_execucao": self.tempo_execucao_segundos,
                "erros": self.erros,
            }
        }
