"""
Parser para processar dados de rescisões trabalhistas.

Este módulo converte dados de diferentes formatos (JSON, dict)
para objetos Pydantic validados.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Union
from pathlib import Path

from .models import Rescisao, Funcionario


class RescisaoParser:
    """
    Parser para converter dados de rescisões trabalhistas.

    Converte dados de JSON ou dicionários Python para objetos
    Rescisao validados.
    """

    @staticmethod
    def converter_data(valor: Union[str, date]) -> date:
        """
        Converte string para objeto date.

        Args:
            valor: String no formato 'YYYY-MM-DD' ou 'DD/MM/YYYY' ou objeto date

        Returns:
            Objeto date

        Raises:
            ValueError: Se o formato da data for inválido
        """
        if isinstance(valor, date):
            return valor

        # Tenta formato ISO (YYYY-MM-DD)
        try:
            return datetime.strptime(valor, '%Y-%m-%d').date()
        except ValueError:
            pass

        # Tenta formato brasileiro (DD/MM/YYYY)
        try:
            return datetime.strptime(valor, '%d/%m/%Y').date()
        except ValueError:
            pass

        raise ValueError(f'Formato de data inválido: {valor}. Use YYYY-MM-DD ou DD/MM/YYYY')

    @staticmethod
    def converter_decimal(valor: Union[str, int, float, Decimal]) -> Decimal:
        """
        Converte diversos formatos numéricos para Decimal.

        Args:
            valor: Número em formato string, int, float ou Decimal

        Returns:
            Objeto Decimal

        Examples:
            >>> RescisaoParser.converter_decimal("1.234,56")
            Decimal('1234.56')
            >>> RescisaoParser.converter_decimal("1,234.56")
            Decimal('1234.56')
            >>> RescisaoParser.converter_decimal(1234.56)
            Decimal('1234.56')
        """
        if isinstance(valor, Decimal):
            return valor

        if isinstance(valor, (int, float)):
            return Decimal(str(valor))

        # Remove espaços
        valor_str = str(valor).strip().replace(' ', '')

        # Formato brasileiro: 1.234,56
        if ',' in valor_str and '.' in valor_str:
            if valor_str.rindex(',') > valor_str.rindex('.'):
                # É formato brasileiro
                valor_str = valor_str.replace('.', '').replace(',', '.')
            else:
                # É formato americano
                valor_str = valor_str.replace(',', '')
        elif ',' in valor_str:
            # Apenas vírgula - formato brasileiro
            valor_str = valor_str.replace(',', '.')

        return Decimal(valor_str)

    @classmethod
    def processar_verbas(cls, verbas_raw: dict[str, Any]) -> dict[str, Decimal]:
        """
        Processa dicionário de verbas convertendo valores para Decimal.

        Args:
            verbas_raw: Dicionário com nomes e valores de verbas

        Returns:
            Dicionário com valores convertidos para Decimal
        """
        verbas_processadas = {}
        for chave, valor in verbas_raw.items():
            try:
                verbas_processadas[chave] = cls.converter_decimal(valor)
            except (ValueError, TypeError) as e:
                raise ValueError(f'Erro ao processar verba "{chave}": {e}')
        return verbas_processadas

    @classmethod
    def processar_descontos(cls, descontos_raw: dict[str, Any]) -> dict[str, Decimal]:
        """
        Processa dicionário de descontos convertendo valores para Decimal.

        Args:
            descontos_raw: Dicionário com nomes e valores de descontos

        Returns:
            Dicionário com valores convertidos para Decimal
        """
        descontos_processados = {}
        for chave, valor in descontos_raw.items():
            try:
                descontos_processados[chave] = cls.converter_decimal(valor)
            except (ValueError, TypeError) as e:
                raise ValueError(f'Erro ao processar desconto "{chave}": {e}')
        return descontos_processados

    @classmethod
    def processar_funcionario(cls, func_data: dict[str, Any]) -> Funcionario:
        """
        Processa dados do funcionário.

        Args:
            func_data: Dicionário com dados do funcionário

        Returns:
            Objeto Funcionario validado
        """
        # Converte datas
        if 'data_admissao' in func_data:
            func_data['data_admissao'] = cls.converter_data(func_data['data_admissao'])
        if 'data_demissao' in func_data:
            func_data['data_demissao'] = cls.converter_data(func_data['data_demissao'])

        # Converte salário
        if 'salario_bruto' in func_data:
            func_data['salario_bruto'] = cls.converter_decimal(func_data['salario_bruto'])

        return Funcionario(**func_data)

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> Rescisao:
        """
        Converte dicionário para objeto Rescisao.

        Args:
            dados: Dicionário com dados da rescisão

        Returns:
            Objeto Rescisao validado

        Raises:
            ValueError: Se os dados forem inválidos
        """
        try:
            # Processa funcionário
            if 'funcionario' not in dados:
                raise ValueError('Campo "funcionario" é obrigatório')

            funcionario = cls.processar_funcionario(dados['funcionario'])

            # Processa verbas
            verbas = {}
            if 'verbas' in dados and dados['verbas']:
                verbas = cls.processar_verbas(dados['verbas'])

            # Processa descontos
            descontos = {}
            if 'descontos' in dados and dados['descontos']:
                descontos = cls.processar_descontos(dados['descontos'])

            # Cria objeto Rescisao
            return Rescisao(
                funcionario=funcionario,
                tipo_rescisao=dados.get('tipo_rescisao', 'sem justa causa'),
                verbas=verbas,
                descontos=descontos,
                observacoes=dados.get('observacoes')
            )

        except Exception as e:
            raise ValueError(f'Erro ao processar dados da rescisão: {e}')

    @classmethod
    def de_json(cls, json_str: str) -> Rescisao:
        """
        Converte string JSON para objeto Rescisao.

        Args:
            json_str: String JSON com dados da rescisão

        Returns:
            Objeto Rescisao validado

        Raises:
            ValueError: Se o JSON for inválido
        """
        try:
            dados = json.loads(json_str)
            return cls.de_dict(dados)
        except json.JSONDecodeError as e:
            raise ValueError(f'JSON inválido: {e}')

    @classmethod
    def de_arquivo(cls, caminho: Union[str, Path]) -> Rescisao:
        """
        Lê arquivo JSON e converte para objeto Rescisao.

        Args:
            caminho: Caminho para o arquivo JSON

        Returns:
            Objeto Rescisao validado

        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se o JSON for inválido
        """
        caminho_path = Path(caminho)

        if not caminho_path.exists():
            raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')

        with open(caminho_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        return cls.de_json(conteudo)

    @staticmethod
    def para_dict(rescisao: Rescisao) -> dict[str, Any]:
        """
        Converte objeto Rescisao para dicionário.

        Args:
            rescisao: Objeto Rescisao

        Returns:
            Dicionário com dados serializáveis
        """
        return rescisao.model_dump(mode='json')

    @staticmethod
    def para_json(rescisao: Rescisao, indent: int = 2) -> str:
        """
        Converte objeto Rescisao para string JSON.

        Args:
            rescisao: Objeto Rescisao
            indent: Número de espaços para indentação

        Returns:
            String JSON formatada
        """
        return rescisao.model_dump_json(indent=indent)

    @staticmethod
    def para_arquivo(rescisao: Rescisao, caminho: Union[str, Path], indent: int = 2) -> None:
        """
        Salva objeto Rescisao em arquivo JSON.

        Args:
            rescisao: Objeto Rescisao
            caminho: Caminho para salvar o arquivo
            indent: Número de espaços para indentação
        """
        caminho_path = Path(caminho)

        # Cria diretórios se necessário
        caminho_path.parent.mkdir(parents=True, exist_ok=True)

        with open(caminho_path, 'w', encoding='utf-8') as f:
            f.write(RescisaoParser.para_json(rescisao, indent=indent))

    @staticmethod
    def gerar_exemplo() -> Rescisao:
        """
        Gera um exemplo de rescisão para testes.

        Returns:
            Objeto Rescisao de exemplo
        """
        return Rescisao(
            funcionario=Funcionario(
                nome="João da Silva Santos",
                cpf="123.456.789-09",
                cargo="Analista de Sistemas",
                data_admissao=date(2020, 1, 15),
                data_demissao=date(2024, 11, 10),
                salario_bruto=Decimal("5000.00")
            ),
            tipo_rescisao="sem justa causa",
            verbas={
                "Saldo de Salário": Decimal("1666.67"),
                "Aviso Prévio Indenizado": Decimal("6500.00"),
                "Férias Vencidas + 1/3": Decimal("6666.67"),
                "Férias Proporcionais + 1/3": Decimal("5555.56"),
                "13º Salário Proporcional": Decimal("4583.33"),
                "Multa 40% FGTS": Decimal("3200.00")
            },
            descontos={
                "INSS": Decimal("828.38"),
                "IRRF": Decimal("505.64")
            },
            observacoes="Rescisão sem justa causa por iniciativa do empregador."
        )
