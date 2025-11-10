"""
Testes para o parser de rescisões
"""

from decimal import Decimal
from datetime import date
import json
import tempfile

from labor_termination_analyzer.parser import RescisaoParser


def test_parse_from_dict():
    """Testa parsing de dicionário"""
    data = {
        "funcionario": {
            "nome": "Teste Silva",
            "cpf": "123.456.789-00",
            "cargo": "Analista",
            "data_admissao": "2020-01-01",
            "data_demissao": "2025-01-01",
            "salario_bruto": "5000.00"
        },
        "tipo_rescisao": "sem justa causa",
        "verbas": {
            "saldo_salario": "1000.00"
        },
        "descontos": {
            "inss": "100.00"
        }
    }

    rescisao = RescisaoParser.from_dict(data)

    assert rescisao.funcionario.nome == "Teste Silva"
    assert rescisao.funcionario.salario_bruto == Decimal("5000.00")
    assert rescisao.verbas.saldo_salario == Decimal("1000.00")
    assert rescisao.descontos.inss == Decimal("100.00")


def test_parse_date_formats():
    """Testa diferentes formatos de data"""
    parser = RescisaoParser()

    # Formato ISO
    assert parser._parse_date("2025-01-01") == date(2025, 1, 1)

    # Formato brasileiro
    assert parser._parse_date("01/01/2025") == date(2025, 1, 1)

    # Formato com traços
    assert parser._parse_date("01-01-2025") == date(2025, 1, 1)


def test_parse_decimal_formats():
    """Testa diferentes formatos de valores decimais"""
    parser = RescisaoParser()

    # String com vírgula
    assert parser._parse_decimal("1.234,56") == Decimal("1234.56")

    # String com R$
    assert parser._parse_decimal("R$ 1.234,56") == Decimal("1234.56")

    # Float
    assert parser._parse_decimal(1234.56) == Decimal("1234.56")

    # Int
    assert parser._parse_decimal(1234) == Decimal("1234")


def test_parse_from_json_file():
    """Testa parsing de arquivo JSON"""
    data = {
        "funcionario": {
            "nome": "Teste",
            "cpf": "123.456.789-00",
            "cargo": "Analista",
            "data_admissao": "2020-01-01",
            "data_demissao": "2025-01-01",
            "salario_bruto": "5000.00"
        },
        "tipo_rescisao": "sem justa causa",
        "verbas": {},
        "descontos": {}
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(data, f)
        temp_path = f.name

    rescisao = RescisaoParser.from_json_file(temp_path)
    assert rescisao.funcionario.nome == "Teste"


if __name__ == "__main__":
    test_parse_from_dict()
    test_parse_date_formats()
    test_parse_decimal_formats()
    test_parse_from_json_file()
    print("✓ Todos os testes passaram!")
