"""
Parser para processar dados de rescisão trabalhista
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, Union
from pathlib import Path

from .models import RescisaoTrabalhista, Funcionario, Verbas, Descontos


class RescisaoParser:
    """Parser para criar objetos RescisaoTrabalhista a partir de diferentes fontes"""

    @staticmethod
    def _parse_date(date_value: Union[str, date]) -> date:
        """Converte string para date"""
        if isinstance(date_value, date):
            return date_value

        # Tenta diferentes formatos de data
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_value, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Formato de data inválido: {date_value}")

    @staticmethod
    def _parse_decimal(value: Union[str, int, float, Decimal]) -> Decimal:
        """Converte valor para Decimal"""
        if isinstance(value, Decimal):
            return value

        if isinstance(value, str):
            # Remove formatação brasileira
            value = value.replace("R$", "").replace(".", "").replace(",", ".").strip()

        return Decimal(str(value))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RescisaoTrabalhista:
        """
        Cria uma RescisaoTrabalhista a partir de um dicionário

        Args:
            data: Dicionário com os dados da rescisão

        Returns:
            RescisaoTrabalhista: Objeto com os dados parseados
        """
        # Parse funcionário
        func_data = data["funcionario"]
        funcionario = Funcionario(
            nome=func_data["nome"],
            cpf=func_data["cpf"],
            cargo=func_data["cargo"],
            data_admissao=cls._parse_date(func_data["data_admissao"]),
            data_demissao=cls._parse_date(func_data["data_demissao"]),
            salario_bruto=cls._parse_decimal(func_data["salario_bruto"])
        )

        # Parse verbas
        verbas_data = data.get("verbas", {})
        verbas = Verbas(
            saldo_salario=cls._parse_decimal(verbas_data.get("saldo_salario", 0)),
            aviso_previo_indenizado=cls._parse_decimal(verbas_data.get("aviso_previo_indenizado", 0)),
            ferias_vencidas=cls._parse_decimal(verbas_data.get("ferias_vencidas", 0)),
            ferias_proporcionais=cls._parse_decimal(verbas_data.get("ferias_proporcionais", 0)),
            um_terco_ferias=cls._parse_decimal(verbas_data.get("um_terco_ferias", 0)),
            decimo_terceiro_proporcional=cls._parse_decimal(verbas_data.get("decimo_terceiro_proporcional", 0)),
            multa_fgts_40=cls._parse_decimal(verbas_data.get("multa_fgts_40", 0)),
            saldo_fgts=cls._parse_decimal(verbas_data.get("saldo_fgts", 0)),
            outras_verbas={
                k: cls._parse_decimal(v)
                for k, v in verbas_data.get("outras_verbas", {}).items()
            }
        )

        # Parse descontos
        descontos_data = data.get("descontos", {})
        descontos = Descontos(
            inss=cls._parse_decimal(descontos_data.get("inss", 0)),
            irrf=cls._parse_decimal(descontos_data.get("irrf", 0)),
            aviso_previo_indenizado=cls._parse_decimal(descontos_data.get("aviso_previo_indenizado", 0)),
            outros_descontos={
                k: cls._parse_decimal(v)
                for k, v in descontos_data.get("outros_descontos", {}).items()
            }
        )

        return RescisaoTrabalhista(
            funcionario=funcionario,
            tipo_rescisao=data["tipo_rescisao"],
            verbas=verbas,
            descontos=descontos,
            observacoes=data.get("observacoes")
        )

    @classmethod
    def from_json_file(cls, filepath: Union[str, Path]) -> RescisaoTrabalhista:
        """
        Cria uma RescisaoTrabalhista a partir de arquivo JSON

        Args:
            filepath: Caminho para o arquivo JSON

        Returns:
            RescisaoTrabalhista: Objeto com os dados parseados
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_json_string(cls, json_str: str) -> RescisaoTrabalhista:
        """
        Cria uma RescisaoTrabalhista a partir de string JSON

        Args:
            json_str: String JSON com os dados

        Returns:
            RescisaoTrabalhista: Objeto com os dados parseados
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
