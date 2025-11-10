"""
Analisador de rescisões trabalhistas com explicações detalhadas
"""

from typing import Dict, List
from decimal import Decimal

from .models import RescisaoTrabalhista


class RescisaoAnalyzer:
    """Analisa e explica os componentes de uma rescisão trabalhista"""

    # Explicações das verbas rescisórias
    EXPLICACOES_VERBAS = {
        "saldo_salario": {
            "titulo": "Saldo de Salário",
            "descricao": "Corresponde aos dias trabalhados no mês da rescisão até a data do desligamento. "
                        "É calculado proporcionalmente ao salário mensal dividido por 30 dias.",
            "calculo": "Salário mensal ÷ 30 × dias trabalhados no mês"
        },
        "aviso_previo_indenizado": {
            "titulo": "Aviso Prévio Indenizado",
            "descricao": "Quando o empregador dispensa o empregado sem justa causa sem cumprir o aviso prévio "
                        "de 30 dias, deve pagar esse período. Adiciona-se 3 dias por ano trabalhado (até no máximo 90 dias).",
            "calculo": "30 dias + (3 dias × anos trabalhados) = período total do aviso prévio"
        },
        "ferias_vencidas": {
            "titulo": "Férias Vencidas",
            "descricao": "Férias que já foram adquiridas (completou 12 meses de trabalho) mas não foram gozadas. "
                        "O trabalhador tem direito a receber o valor integral dessas férias acrescido de 1/3.",
            "calculo": "Salário mensal + 1/3 do salário"
        },
        "ferias_proporcionais": {
            "titulo": "Férias Proporcionais",
            "descricao": "Corresponde às férias do período incompleto (menos de 12 meses desde as últimas férias ou admissão). "
                        "É pago proporcionalmente aos meses trabalhados.",
            "calculo": "(Salário mensal ÷ 12) × meses trabalhados no período atual"
        },
        "um_terco_ferias": {
            "titulo": "1/3 Constitucional sobre Férias",
            "descricao": "A Constituição Federal garante o adicional de 1/3 sobre o valor das férias. "
                        "Esse valor é somado tanto às férias vencidas quanto às proporcionais.",
            "calculo": "1/3 do valor total de férias (vencidas + proporcionais)"
        },
        "decimo_terceiro_proporcional": {
            "titulo": "13º Salário Proporcional",
            "descricao": "O 13º salário é pago proporcionalmente aos meses trabalhados no ano da rescisão. "
                        "Cada mês trabalhado (15 dias ou mais) conta como 1/12 avos do 13º.",
            "calculo": "(Salário mensal ÷ 12) × meses trabalhados no ano"
        },
        "multa_fgts_40": {
            "titulo": "Multa de 40% do FGTS",
            "descricao": "Em caso de demissão sem justa causa, o empregador deve pagar multa de 40% "
                        "sobre o total depositado no FGTS durante todo o contrato de trabalho.",
            "calculo": "40% do saldo total do FGTS"
        },
        "saldo_fgts": {
            "titulo": "Saldo do FGTS",
            "descricao": "Valor total depositado na conta do FGTS durante o contrato de trabalho. "
                        "Em demissão sem justa causa, o trabalhador pode sacar todo o saldo.",
            "calculo": "Soma de todos os depósitos mensais de FGTS (8% do salário)"
        }
    }

    # Explicações dos descontos
    EXPLICACOES_DESCONTOS = {
        "inss": {
            "titulo": "INSS (Contribuição Previdenciária)",
            "descricao": "Desconto obrigatório para a Previdência Social. A alíquota varia conforme o salário, "
                        "seguindo a tabela progressiva do INSS (de 7,5% a 14%).",
            "calculo": "Aplicado sobre verbas de natureza salarial (saldo de salário, 13º, etc.)"
        },
        "irrf": {
            "titulo": "IRRF (Imposto de Renda Retido na Fonte)",
            "descricao": "Imposto de renda cobrado sobre os valores recebidos. Incide sobre verbas de natureza salarial, "
                        "com alíquotas progressivas conforme a tabela do IR.",
            "calculo": "Aplicado sobre a base de cálculo (verbas tributáveis - INSS - dependentes)"
        },
        "aviso_previo_indenizado": {
            "titulo": "Desconto de Aviso Prévio",
            "descricao": "Quando o empregado pede demissão e não cumpre o aviso prévio de 30 dias, "
                        "o empregador pode descontar esse valor da rescisão.",
            "calculo": "Salário mensal correspondente ao período não trabalhado do aviso"
        }
    }

    # Tipos de rescisão e suas características
    TIPOS_RESCISAO = {
        "sem justa causa": {
            "nome": "Demissão sem Justa Causa",
            "descricao": "O empregador dispensa o empregado por iniciativa própria, sem que haja falta grave. "
                        "É o tipo mais favorável ao trabalhador.",
            "direitos": [
                "Saldo de salário",
                "Aviso prévio indenizado ou trabalhado",
                "Férias vencidas e proporcionais + 1/3",
                "13º salário proporcional",
                "Multa de 40% do FGTS",
                "Saque do FGTS",
                "Seguro-desemprego (se cumprir requisitos)"
            ]
        },
        "com justa causa": {
            "nome": "Demissão com Justa Causa",
            "descricao": "O empregador dispensa o empregado por falta grave prevista em lei "
                        "(roubo, embriaguez, insubordinação, etc.). É a mais prejudicial ao trabalhador.",
            "direitos": [
                "Saldo de salário",
                "Férias vencidas + 1/3 (se houver)"
            ]
        },
        "pedido de demissao": {
            "nome": "Pedido de Demissão",
            "descricao": "O empregado solicita o desligamento por vontade própria. "
                        "Perde alguns direitos, especialmente relacionados ao FGTS.",
            "direitos": [
                "Saldo de salário",
                "Férias vencidas e proporcionais + 1/3",
                "13º salário proporcional",
                "Saldo do FGTS (sem poder sacar, exceto em casos específicos)"
            ]
        },
        "acordo": {
            "nome": "Demissão por Acordo (Comum Acordo)",
            "descricao": "Empregador e empregado entram em acordo para encerrar o contrato. "
                        "Modalidade criada pela Reforma Trabalhista de 2017.",
            "direitos": [
                "Saldo de salário",
                "Metade do aviso prévio indenizado",
                "Férias vencidas e proporcionais + 1/3",
                "13º salário proporcional",
                "Multa de 20% do FGTS (metade dos 40%)",
                "Saque de até 80% do FGTS",
                "NÃO tem direito ao seguro-desemprego"
            ]
        }
    }

    def __init__(self, rescisao: RescisaoTrabalhista):
        """
        Inicializa o analisador

        Args:
            rescisao: Objeto RescisaoTrabalhista a ser analisado
        """
        self.rescisao = rescisao

    def analisar_tipo_rescisao(self) -> Dict[str, str]:
        """Retorna informações sobre o tipo de rescisão"""
        tipo = self.rescisao.tipo_rescisao.lower()
        info = self.TIPOS_RESCISAO.get(tipo, {
            "nome": tipo.title(),
            "descricao": "Tipo de rescisão não especificado",
            "direitos": []
        })
        return info

    def explicar_verba(self, nome_verba: str, valor: Decimal) -> Dict[str, any]:
        """
        Retorna explicação detalhada de uma verba

        Args:
            nome_verba: Nome da verba
            valor: Valor da verba

        Returns:
            Dicionário com explicação completa
        """
        explicacao = self.EXPLICACOES_VERBAS.get(nome_verba, {
            "titulo": nome_verba.replace("_", " ").title(),
            "descricao": "Verba não catalogada",
            "calculo": "N/A"
        })

        return {
            **explicacao,
            "valor": valor,
            "valor_formatado": f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }

    def explicar_desconto(self, nome_desconto: str, valor: Decimal) -> Dict[str, any]:
        """
        Retorna explicação detalhada de um desconto

        Args:
            nome_desconto: Nome do desconto
            valor: Valor do desconto

        Returns:
            Dicionário com explicação completa
        """
        explicacao = self.EXPLICACOES_DESCONTOS.get(nome_desconto, {
            "titulo": nome_desconto.replace("_", " ").title(),
            "descricao": "Desconto não catalogado",
            "calculo": "N/A"
        })

        return {
            **explicacao,
            "valor": valor,
            "valor_formatado": f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }

    def gerar_resumo_completo(self) -> Dict:
        """Gera um resumo completo da rescisão com todas as explicações"""
        verbas_detalhadas = []
        descontos_detalhados = []

        # Análise das verbas
        verbas_dict = self.rescisao.verbas.model_dump()
        for nome, valor in verbas_dict.items():
            if nome == "outras_verbas":
                for outra_nome, outra_valor in valor.items():
                    if outra_valor > 0:
                        verbas_detalhadas.append({
                            "nome": outra_nome,
                            "valor": outra_valor,
                            "valor_formatado": f"R$ {outra_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                            "titulo": outra_nome.title(),
                            "descricao": "Verba adicional",
                            "calculo": "Conforme especificado no contrato"
                        })
            elif isinstance(valor, Decimal) and valor > 0:
                verbas_detalhadas.append(self.explicar_verba(nome, valor))

        # Análise dos descontos
        descontos_dict = self.rescisao.descontos.model_dump()
        for nome, valor in descontos_dict.items():
            if nome == "outros_descontos":
                for outro_nome, outro_valor in valor.items():
                    if outro_valor > 0:
                        descontos_detalhados.append({
                            "nome": outro_nome,
                            "valor": outro_valor,
                            "valor_formatado": f"R$ {outro_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                            "titulo": outro_nome.title(),
                            "descricao": "Desconto adicional",
                            "calculo": "Conforme especificado"
                        })
            elif isinstance(valor, Decimal) and valor > 0:
                descontos_detalhados.append(self.explicar_desconto(nome, valor))

        return {
            "funcionario": {
                "nome": self.rescisao.funcionario.nome,
                "cpf": self.rescisao.funcionario.cpf,
                "cargo": self.rescisao.funcionario.cargo,
                "data_admissao": self.rescisao.funcionario.data_admissao.strftime("%d/%m/%Y"),
                "data_demissao": self.rescisao.funcionario.data_demissao.strftime("%d/%m/%Y"),
                "salario_bruto": f"R$ {self.rescisao.funcionario.salario_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "tempo_servico": f"{self.rescisao.tempo_servico_anos} anos ({self.rescisao.tempo_servico_meses} meses)"
            },
            "tipo_rescisao": self.analisar_tipo_rescisao(),
            "verbas": verbas_detalhadas,
            "descontos": descontos_detalhados,
            "totais": {
                "total_verbas": self.rescisao.total_verbas,
                "total_verbas_formatado": f"R$ {self.rescisao.total_verbas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "total_descontos": self.rescisao.total_descontos,
                "total_descontos_formatado": f"R$ {self.rescisao.total_descontos:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "valor_liquido": self.rescisao.valor_liquido,
                "valor_liquido_formatado": f"R$ {self.rescisao.valor_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            },
            "observacoes": self.rescisao.observacoes
        }
