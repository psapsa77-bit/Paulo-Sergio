"""
Analisador de rescisões trabalhistas.

Este módulo fornece análises detalhadas e explicações sobre
verbas, descontos e direitos trabalhistas.
"""

from decimal import Decimal
from typing import Any
from .models import Rescisao


class RescisaoAnalyzer:
    """
    Analisador de rescisões trabalhistas.

    Fornece explicações detalhadas, cálculos e verificações de conformidade.
    """

    # Explicações detalhadas para verbas rescisórias
    EXPLICACOES_VERBAS = {
        'Saldo de Salário': {
            'titulo': '💰 SALDO DE SALÁRIO',
            'o_que_e': (
                'Pagamento dos dias trabalhados no mês da rescisão, '
                'proporcional ao período entre o primeiro dia do mês até o último dia trabalhado.'
            ),
            'base_legal': 'Art. 462 da CLT',
            'calculo': (
                'Salário Mensal ÷ 30 dias × Número de Dias Trabalhados no Mês\n'
                'Exemplo: R$ 3.000,00 ÷ 30 × 10 dias = R$ 1.000,00'
            ),
            'quando_aplica': 'Em todas as rescisões contratuais, independentemente do tipo.'
        },
        'Aviso Prévio Indenizado': {
            'titulo': '⏰ AVISO PRÉVIO INDENIZADO',
            'o_que_e': (
                'Pagamento correspondente a 30 dias de trabalho quando a empresa dispensa '
                'o empregado sem justa causa sem conceder o aviso prévio trabalhado. '
                'Acrescenta-se 3 dias por ano trabalhado (máximo 90 dias).'
            ),
            'base_legal': 'Art. 487 da CLT + Lei 12.506/2011',
            'calculo': (
                'Salário + (3 dias × anos trabalhados) [máximo 90 dias]\n'
                'Exemplo com 5 anos: R$ 5.000,00 + (5 anos × 3 dias × R$ 166,67) = R$ 7.500,00'
            ),
            'quando_aplica': 'Demissão sem justa causa por iniciativa do empregador.'
        },
        'Aviso Prévio Trabalhado': {
            'titulo': '⏰ AVISO PRÉVIO TRABALHADO',
            'o_que_e': (
                'Período de 30 dias trabalhados após a comunicação da rescisão, '
                'com redução de 2 horas diárias ou 7 dias corridos no final.'
            ),
            'base_legal': 'Art. 488 da CLT',
            'calculo': 'Salário mensal normal (já incluído no salário do mês)',
            'quando_aplica': 'Quando o empregado cumpre o aviso prévio trabalhando.'
        },
        'Férias Vencidas': {
            'titulo': '🏖️ FÉRIAS VENCIDAS + 1/3',
            'o_que_e': (
                'Pagamento de período de férias já adquirido (após 12 meses de trabalho) '
                'mas não gozado, acrescido do terço constitucional (1/3 do valor).'
            ),
            'base_legal': 'Arts. 129, 130 e 142 da CLT + Art. 7º, XVII da CF/88',
            'calculo': (
                'Salário + 1/3\n'
                'Exemplo: R$ 5.000,00 + R$ 1.666,67 (1/3) = R$ 6.666,67'
            ),
            'quando_aplica': 'Quando há período aquisitivo completo (12 meses) não gozado.'
        },
        'Férias Proporcionais': {
            'titulo': '🏖️ FÉRIAS PROPORCIONAIS + 1/3',
            'o_que_e': (
                'Pagamento proporcional de férias referente ao período aquisitivo incompleto, '
                'calculado com base nos meses trabalhados, acrescido de 1/3.'
            ),
            'base_legal': 'Art. 147 da CLT + Súmula 261 do TST',
            'calculo': (
                '(Salário ÷ 12 × meses trabalhados) + 1/3\n'
                'Exemplo com 10 meses: (R$ 5.000,00 ÷ 12 × 10) + 1/3 = R$ 5.555,56'
            ),
            'quando_aplica': (
                'Em todas as rescisões sem justa causa e pedido de demissão '
                'com mais de 1 ano de empresa.'
            )
        },
        '1/3 de Férias': {
            'titulo': '➕ ADICIONAL DE 1/3 DE FÉRIAS',
            'o_que_e': (
                'Acréscimo de um terço (33,33%) sobre o valor das férias, '
                'garantido constitucionalmente.'
            ),
            'base_legal': 'Art. 7º, XVII da Constituição Federal/88',
            'calculo': 'Valor das férias × 1/3',
            'quando_aplica': 'Sempre que há pagamento de férias (vencidas ou proporcionais).'
        },
        '13º Salário Proporcional': {
            'titulo': '🎄 13º SALÁRIO PROPORCIONAL',
            'o_que_e': (
                'Gratificação natalina proporcional aos meses trabalhados no ano da rescisão. '
                'Conta-se 1/12 por mês trabalhado (15 dias ou mais = mês completo).'
            ),
            'base_legal': 'Lei 4.090/62 e Lei 4.749/65',
            'calculo': (
                'Salário ÷ 12 × número de meses trabalhados no ano\n'
                'Exemplo com 11 meses: R$ 5.000,00 ÷ 12 × 11 = R$ 4.583,33'
            ),
            'quando_aplica': (
                'Em todas as rescisões, exceto dispensa por justa causa '
                '(neste caso, perde o direito).'
            )
        },
        'Multa 40% FGTS': {
            'titulo': '🏦 MULTA DE 40% DO FGTS',
            'o_que_e': (
                'Indenização de 40% sobre o saldo total do FGTS depositado durante '
                'todo o contrato de trabalho. Paga pelo empregador ao empregado.'
            ),
            'base_legal': 'Art. 18, §1º da Lei 8.036/90',
            'calculo': (
                'Saldo total do FGTS × 40%\n'
                'Exemplo: R$ 8.000,00 de FGTS × 40% = R$ 3.200,00'
            ),
            'quando_aplica': 'Exclusivamente em demissão sem justa causa pelo empregador.'
        },
        'Multa 20% FGTS': {
            'titulo': '🏦 MULTA DE 20% DO FGTS',
            'o_que_e': (
                'Indenização de 20% sobre o saldo do FGTS no caso de rescisão por acordo '
                'entre empregado e empregador (demissão consensual).'
            ),
            'base_legal': 'Art. 484-A da CLT (Reforma Trabalhista - Lei 13.467/17)',
            'calculo': (
                'Saldo total do FGTS × 20%\n'
                'Exemplo: R$ 8.000,00 de FGTS × 20% = R$ 1.600,00'
            ),
            'quando_aplica': 'Apenas em rescisão por acordo (comum acordo).'
        },
        'Saque FGTS': {
            'titulo': '🏦 SAQUE DO FGTS',
            'o_que_e': (
                'Direito de sacar o saldo total depositado na conta do FGTS. '
                'O valor não é pago na rescisão, mas pode ser sacado na Caixa Econômica.'
            ),
            'base_legal': 'Art. 20 da Lei 8.036/90',
            'calculo': 'Valor total depositado + rendimentos',
            'quando_aplica': (
                'Demissão sem justa causa (100% do saldo) ou '
                'Acordo (80% do saldo - Reforma Trabalhista).'
            )
        },
        'Indenização Adicional': {
            'titulo': '💵 INDENIZAÇÃO ADICIONAL',
            'o_que_e': (
                'Indenização de 1 salário mensal quando a rescisão sem justa causa ocorre '
                'nos 30 dias que antecedem a data-base da categoria.'
            ),
            'base_legal': 'Art. 9º da Lei 7.238/84 + Lei 6.708/79',
            'calculo': 'Valor de 1 salário mensal',
            'quando_aplica': 'Demissão sem justa causa dentro dos 30 dias anteriores à data-base.'
        },
        'Horas Extras': {
            'titulo': '⏱️ HORAS EXTRAS',
            'o_que_e': (
                'Pagamento de horas trabalhadas além da jornada normal, '
                'com adicional mínimo de 50% (dias normais) ou 100% (domingos e feriados).'
            ),
            'base_legal': 'Art. 59 da CLT + Art. 7º, XVI da CF/88',
            'calculo': (
                'Valor hora normal × 1,5 × quantidade de horas\n'
                'Exemplo: R$ 25,00/hora × 1,5 × 20 horas = R$ 750,00'
            ),
            'quando_aplica': 'Quando há horas extras não pagas acumuladas.'
        },
        'Adicional Noturno': {
            'titulo': '🌙 ADICIONAL NOTURNO',
            'o_que_e': (
                'Acréscimo de 20% sobre o valor da hora normal para trabalho realizado '
                'entre 22h e 5h (urbano) ou 21h e 5h (rural).'
            ),
            'base_legal': 'Art. 73 da CLT',
            'calculo': 'Valor da hora × 20% × horas noturnas trabalhadas',
            'quando_aplica': 'Trabalho habitual no período noturno.'
        },
        'Insalubridade': {
            'titulo': '☣️ ADICIONAL DE INSALUBRIDADE',
            'o_que_e': (
                'Adicional pago quando o trabalho expõe o empregado a agentes nocivos à saúde. '
                'Percentuais: 10% (grau mínimo), 20% (médio) ou 40% (máximo) do salário mínimo.'
            ),
            'base_legal': 'Art. 192 da CLT + NR-15',
            'calculo': 'Salário mínimo × percentual do grau × meses trabalhados',
            'quando_aplica': 'Trabalho em condições insalubres com laudo pericial.'
        },
        'Periculosidade': {
            'titulo': '⚠️ ADICIONAL DE PERICULOSIDADE',
            'o_que_e': (
                'Adicional de 30% sobre o salário base para trabalho com exposição '
                'a riscos de vida (explosivos, inflamáveis, energia elétrica, etc).'
            ),
            'base_legal': 'Art. 193 da CLT + NR-16',
            'calculo': 'Salário base × 30%',
            'quando_aplica': 'Trabalho em condições perigosas com laudo pericial.'
        },
        'Comissões': {
            'titulo': '💼 COMISSÕES',
            'o_que_e': (
                'Valores devidos referentes a comissões sobre vendas ou serviços '
                'realizados mas ainda não pagos.'
            ),
            'base_legal': 'Arts. 457 e 466 da CLT',
            'calculo': 'Conforme regra contratual ou acordo coletivo',
            'quando_aplica': 'Quando há comissões pendentes de pagamento.'
        },
    }

    # Explicações detalhadas para descontos
    EXPLICACOES_DESCONTOS = {
        'INSS': {
            'titulo': '🏥 INSS - PREVIDÊNCIA SOCIAL',
            'o_que_e': (
                'Contribuição obrigatória para a Previdência Social, '
                'descontada do empregado conforme faixas salariais progressivas.'
            ),
            'base_legal': 'Art. 20 da Lei 8.212/91',
            'calculo': (
                'Faixas 2024:\n'
                '• Até R$ 1.302,00: 7,5%\n'
                '• R$ 1.302,01 a R$ 2.571,29: 9%\n'
                '• R$ 2.571,30 a R$ 3.856,94: 12%\n'
                '• R$ 3.856,95 a R$ 7.507,49: 14%\n'
                'Cálculo progressivo por faixa.'
            ),
            'quando_aplica': 'Em todas as rescisões sobre verbas de natureza salarial.'
        },
        'IRRF': {
            'titulo': '💰 IRRF - IMPOSTO DE RENDA',
            'o_que_e': (
                'Imposto de Renda Retido na Fonte sobre verbas rescisórias tributáveis, '
                'conforme tabela progressiva da Receita Federal.'
            ),
            'base_legal': 'Lei 7.713/88 e atualizações anuais',
            'calculo': (
                'Tabela 2024 (mensal):\n'
                '• Até R$ 2.112,00: Isento\n'
                '• R$ 2.112,01 a R$ 2.826,65: 7,5%\n'
                '• R$ 2.826,66 a R$ 3.751,05: 15%\n'
                '• R$ 3.751,06 a R$ 4.664,68: 22,5%\n'
                '• Acima de R$ 4.664,68: 27,5%\n'
                'Desconta-se a parcela dedutível por faixa.'
            ),
            'quando_aplica': (
                'Sobre saldo de salário, férias, 13º e outras verbas tributáveis. '
                'Aviso prévio indenizado e multa FGTS são isentos.'
            )
        },
        'Aviso Prévio Descontado': {
            'titulo': '⏰ DESCONTO DE AVISO PRÉVIO',
            'o_que_e': (
                'Desconto equivalente a 30 dias de salário quando o empregado pede demissão '
                'e não cumpre o aviso prévio (não trabalha os 30 dias).'
            ),
            'base_legal': 'Art. 487, §2º da CLT',
            'calculo': 'Valor de 1 salário mensal (30 dias)',
            'quando_aplica': (
                'Pedido de demissão pelo empregado sem cumprimento do aviso prévio, '
                'desde que o empregador tenha direito ao aviso.'
            )
        },
        'Vale Transporte': {
            'titulo': '🚌 VALE TRANSPORTE',
            'o_que_e': (
                'Desconto de até 6% do salário básico referente ao vale-transporte utilizado. '
                'Eventual saldo devedor de VT adiantado pode ser descontado.'
            ),
            'base_legal': 'Lei 7.418/85 e Decreto 95.247/87',
            'calculo': 'Máximo de 6% do salário básico ou saldo devedor',
            'quando_aplica': 'Quando o empregado optou pelo vale-transporte.'
        },
        'Vale Refeição/Alimentação': {
            'titulo': '🍽️ VALE REFEIÇÃO/ALIMENTAÇÃO',
            'o_que_e': (
                'Desconto de até 20% do valor do benefício (PAT - Programa de Alimentação do Trabalhador) '
                'ou saldo devedor de vale-refeição/alimentação adiantado.'
            ),
            'base_legal': 'Lei 6.321/76 (PAT)',
            'calculo': 'Até 20% do valor do benefício ou saldo devedor',
            'quando_aplica': 'Quando há participação do empregado no PAT ou saldo devedor.'
        },
        'Plano de Saúde': {
            'titulo': '🏥 PLANO DE SAÚDE',
            'o_que_e': (
                'Desconto referente à co-participação do empregado no plano de saúde '
                'ou saldo devedor do último mês.'
            ),
            'base_legal': 'Lei 9.656/98 (conforme acordo coletivo ou contrato)',
            'calculo': 'Conforme regra contratual',
            'quando_aplica': 'Quando há plano de saúde com co-participação do empregado.'
        },
        'Adiantamento Salarial': {
            'titulo': '💵 ADIANTAMENTO SALARIAL',
            'o_que_e': (
                'Desconto de valores que foram adiantados ao empregado durante o mês '
                '(adiantamento quinzenal, por exemplo).'
            ),
            'base_legal': 'Art. 462, §1º da CLT',
            'calculo': 'Valor total adiantado e não compensado',
            'quando_aplica': 'Quando há adiantamentos pendentes de compensação.'
        },
        'Pensão Alimentícia': {
            'titulo': '👨‍👩‍👧 PENSÃO ALIMENTÍCIA',
            'o_que_e': (
                'Desconto obrigatório determinado judicialmente para pagamento de pensão alimentícia, '
                'geralmente percentual sobre os rendimentos.'
            ),
            'base_legal': 'Lei 5.478/68 (Lei de Alimentos) + decisão judicial',
            'calculo': 'Conforme determinação judicial (geralmente % sobre rendimentos)',
            'quando_aplica': 'Quando há ordem judicial de desconto de pensão alimentícia.'
        },
        'Empréstimo Consignado': {
            'titulo': '🏦 EMPRÉSTIMO CONSIGNADO',
            'o_que_e': (
                'Desconto de parcelas de empréstimo consignado (descontado em folha) '
                'que ainda estão em aberto.'
            ),
            'base_legal': 'Lei 10.820/03',
            'calculo': 'Valor das parcelas em aberto (limitado a 30% da rescisão)',
            'quando_aplica': 'Quando há saldo devedor de empréstimo consignado.'
        },
    }

    # Direitos por tipo de rescisão
    TIPOS_RESCISAO = {
        'sem justa causa': {
            'nome': 'Dispensa Sem Justa Causa',
            'descricao': 'Demissão por iniciativa do empregador sem motivo grave.',
            'direitos': [
                'Saldo de salário',
                'Aviso prévio indenizado (+ 3 dias/ano)',
                'Férias vencidas + 1/3',
                'Férias proporcionais + 1/3',
                '13º salário proporcional',
                'Multa de 40% do FGTS',
                'Saque do FGTS (100%)',
                'Seguro-desemprego (se preencher requisitos)',
            ],
        },
        'com justa causa': {
            'nome': 'Dispensa Com Justa Causa',
            'descricao': 'Demissão por falta grave cometida pelo empregado.',
            'direitos': [
                'Apenas saldo de salário',
                'Férias vencidas + 1/3 (se houver)',
            ],
            'perdas': [
                'Não tem aviso prévio',
                'Não tem férias proporcionais',
                'Não tem 13º proporcional',
                'Não tem multa do FGTS',
                'Não pode sacar FGTS',
                'Não tem seguro-desemprego',
            ],
        },
        'pedido de demissao': {
            'nome': 'Pedido de Demissão',
            'descricao': 'Rescisão por iniciativa do empregado.',
            'direitos': [
                'Saldo de salário',
                'Férias vencidas + 1/3',
                'Férias proporcionais + 1/3 (se mais de 1 ano)',
                '13º salário proporcional',
            ],
            'perdas': [
                'Não tem aviso prévio indenizado',
                'Não tem multa do FGTS',
                'Não pode sacar FGTS',
                'Não tem seguro-desemprego',
            ],
            'observacoes': [
                'Deve cumprir aviso prévio de 30 dias ou será descontado',
            ],
        },
        'acordo': {
            'nome': 'Rescisão por Acordo (Comum Acordo)',
            'descricao': 'Rescisão consensual entre empregado e empregador (Reforma Trabalhista).',
            'direitos': [
                'Saldo de salário',
                'Metade (50%) do aviso prévio indenizado',
                'Férias vencidas + 1/3',
                'Férias proporcionais + 1/3',
                '13º salário proporcional',
                'Multa de 20% do FGTS (ao invés de 40%)',
                'Saque de 80% do FGTS',
            ],
            'perdas': [
                'Não tem seguro-desemprego',
                'Aviso prévio reduzido (50%)',
                'Multa FGTS reduzida (20% ao invés de 40%)',
                'Saque FGTS parcial (80% ao invés de 100%)',
            ],
            'observacoes': [
                'Modalidade criada pela Reforma Trabalhista (Lei 13.467/2017)',
            ],
        },
    }

    def __init__(self, rescisao: Rescisao):
        """
        Inicializa o analisador.

        Args:
            rescisao: Objeto Rescisao para análise
        """
        self.rescisao = rescisao

    def explicar_verba(self, nome_verba: str) -> dict[str, str]:
        """
        Retorna explicação detalhada sobre uma verba.

        Args:
            nome_verba: Nome da verba

        Returns:
            Dicionário com explicação completa
        """
        # Busca correspondência aproximada
        for chave, explicacao in self.EXPLICACOES_VERBAS.items():
            if chave.lower() in nome_verba.lower() or nome_verba.lower() in chave.lower():
                return explicacao

        # Explicação genérica se não encontrar
        return {
            'titulo': f'💰 {nome_verba.upper()}',
            'o_que_e': 'Verba rescisória (consulte legislação específica)',
            'base_legal': 'CLT',
            'calculo': 'Conforme acordo coletivo ou legislação aplicável',
            'quando_aplica': 'Conforme condições contratuais',
        }

    def explicar_desconto(self, nome_desconto: str) -> dict[str, str]:
        """
        Retorna explicação detalhada sobre um desconto.

        Args:
            nome_desconto: Nome do desconto

        Returns:
            Dicionário com explicação completa
        """
        # Busca correspondência aproximada
        for chave, explicacao in self.EXPLICACOES_DESCONTOS.items():
            if chave.lower() in nome_desconto.lower() or nome_desconto.lower() in chave.lower():
                return explicacao

        # Explicação genérica se não encontrar
        return {
            'titulo': f'➖ {nome_desconto.upper()}',
            'o_que_e': 'Desconto rescisório (consulte legislação específica)',
            'base_legal': 'CLT',
            'calculo': 'Conforme regra aplicável',
            'quando_aplica': 'Conforme condições contratuais',
        }

    def obter_direitos_tipo_rescisao(self) -> dict[str, Any]:
        """
        Retorna informações sobre direitos do tipo de rescisão.

        Returns:
            Dicionário com direitos, perdas e observações
        """
        tipo = self.rescisao.tipo_rescisao
        return self.TIPOS_RESCISAO.get(tipo, {
            'nome': tipo.title(),
            'descricao': 'Tipo de rescisão',
            'direitos': [],
        })

    def verificar_conformidade(self) -> list[dict[str, str]]:
        """
        Verifica possíveis inconsistências nos cálculos.

        Returns:
            Lista de alertas/avisos encontrados
        """
        alertas = []

        # Verifica INSS (7,5% a 14% do salário)
        if 'INSS' in self.rescisao.descontos or 'inss' in str(self.rescisao.descontos).lower():
            inss = self.rescisao.descontos.get('INSS', Decimal('0'))
            salario = self.rescisao.funcionario.salario_bruto

            # INSS não deve ser maior que 14% do salário
            max_inss = salario * Decimal('0.14')
            if inss > max_inss:
                alertas.append({
                    'tipo': 'warning',
                    'campo': 'INSS',
                    'mensagem': f'INSS parece alto: R$ {inss}. Máximo esperado ~R$ {max_inss:.2f} (14% do salário)',
                })

        # Verifica multa FGTS em rescisão sem justa causa
        if self.rescisao.tipo_rescisao == 'sem justa causa':
            tem_multa = any('fgts' in k.lower() and 'multa' in k.lower() for k in self.rescisao.verbas.keys())
            if not tem_multa:
                alertas.append({
                    'tipo': 'info',
                    'campo': 'Multa FGTS',
                    'mensagem': 'Em rescisão sem justa causa, há direito a multa de 40% do FGTS',
                })

        # Verifica aviso prévio em rescisão sem justa causa
        if self.rescisao.tipo_rescisao == 'sem justa causa':
            tem_aviso = any('aviso' in k.lower() and 'prévio' in k.lower() for k in self.rescisao.verbas.keys())
            if not tem_aviso:
                alertas.append({
                    'tipo': 'warning',
                    'campo': 'Aviso Prévio',
                    'mensagem': 'Falta aviso prévio indenizado (obrigatório em rescisão sem justa causa)',
                })

        # Verifica 13º proporcional em rescisão com justa causa
        if self.rescisao.tipo_rescisao == 'com justa causa':
            tem_13 = any('13' in k or 'décimo' in k.lower() for k in self.rescisao.verbas.keys())
            if tem_13:
                alertas.append({
                    'tipo': 'error',
                    'campo': '13º Salário',
                    'mensagem': 'Em rescisão COM justa causa, NÃO há direito a 13º proporcional',
                })

        return alertas

    def gerar_resumo_completo(self) -> dict[str, Any]:
        """
        Gera resumo completo da análise.

        Returns:
            Dicionário com todas as informações da análise
        """
        # Informações do funcionário
        func = self.rescisao.funcionario

        # Análise de verbas
        verbas_detalhadas = []
        for nome, valor in self.rescisao.verbas.items():
            explicacao = self.explicar_verba(nome)
            verbas_detalhadas.append({
                'nome': nome,
                'valor': valor,
                'explicacao': explicacao,
            })

        # Análise de descontos
        descontos_detalhados = []
        for nome, valor in self.rescisao.descontos.items():
            explicacao = self.explicar_desconto(nome)
            descontos_detalhados.append({
                'nome': nome,
                'valor': valor,
                'explicacao': explicacao,
            })

        # Totais
        total_verbas = self.rescisao.total_verbas()
        total_descontos = self.rescisao.total_descontos()
        valor_liquido = self.rescisao.valor_liquido()

        # Direitos do tipo de rescisão
        direitos = self.obter_direitos_tipo_rescisao()

        # Verificações
        alertas = self.verificar_conformidade()

        return {
            'funcionario': {
                'nome': func.nome,
                'cpf': func.cpf,
                'cargo': func.cargo,
                'data_admissao': func.data_admissao,
                'data_demissao': func.data_demissao,
                'salario_bruto': func.salario_bruto,
                'tempo_servico_anos': func.tempo_servico_anos(),
                'tempo_servico_meses': func.tempo_servico_meses(),
            },
            'tipo_rescisao': self.rescisao.tipo_rescisao,
            'direitos_tipo_rescisao': direitos,
            'verbas': verbas_detalhadas,
            'descontos': descontos_detalhados,
            'totais': {
                'verbas': total_verbas,
                'descontos': total_descontos,
                'liquido': valor_liquido,
                'porcentagem_desconto': self.rescisao.porcentagem_desconto(),
            },
            'alertas': alertas,
            'observacoes': self.rescisao.observacoes,
        }
