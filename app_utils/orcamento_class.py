class Orcamento:
    """
    Classe para gerenciar o orçamento 50-30-20.
    Contém a lógica para calcular limites e a divisão quinzenal 60/40.
    """
    def __init__(self, salario_liquido, mes, despesas_fixas, gastos_lazer, poupanca_investimentos):
        self.salario_liquido = salario_liquido
        self.mes = mes
        self.despesas_fixas = despesas_fixas
        self.gastos_lazer = gastos_lazer
        self.poupanca_investimentos = poupanca_investimentos

    def calcular_total_categoria(self, categoria: str) -> float:
        """Calcula o total de gastos para uma categoria específica."""
        if categoria == 'fixas':
            return sum(self.despesas_fixas.values())
        elif categoria == 'lazer':
            return sum(self.gastos_lazer.values())
        elif categoria == 'poupanca':
            return self.poupanca_investimentos
        return 0.0

    def calcular_limites_50_30_20(self) -> dict:
        """Calcula os valores ideais (limites) com base na regra 50-30-20."""
        if self.salario_liquido <= 0:
            return {}
        limites = {
            'Necessidades (50%)': self.salario_liquido * 0.50,
            'Desejos/Lazer (30%)': self.salario_liquido * 0.30,
            'Poupança/Investimento (20%)': self.salario_liquido * 0.20
        }
        return limites

    def calcular_economizado(self, limites, totais_reais):
        """Calcula a diferença entre o limite ideal e o gasto real para cada categoria."""
        economia_fixas = limites.get('Necessidades (50%)', 0) - totais_reais['total_fixas']
        economia_lazer = limites.get('Desejos/Lazer (30%)', 0) - totais_reais['total_lazer']
        economia_poupanca = totais_reais['total_poupanca'] - limites.get('Poupança/Investimento (20%)', 0)
        
        return {
            'fixas': economia_fixas,
            'lazer': economia_lazer,
            'poupanca_extra': economia_poupanca
        }

    def calcular_divisao_quinzenal(self, limites_50_30_20: dict):
        """
        Calcula a divisão ideal para as categorias Necessidades (50%) e Lazer (30%) 
        usando a regra 60/40 para salários quinzenais.
        """
        limites_quinzenais = {}
        if not limites_50_30_20:
            return limites_quinzenais

        # 1. Divisão do limite de 50% (Necessidades)
        limite_fixas = limites_50_30_20.get('Necessidades (50%)', 0)
        limites_quinzenais['Fixas - Início (60%)'] = limite_fixas * 0.60
        limites_quinzenais['Fixas - Meio (40%)'] = limite_fixas * 0.40

        # 2. Divisão do limite de 30% (Desejos/Lazer)
        limite_lazer = limites_50_30_20.get('Desejos/Lazer (30%)', 0)
        limites_quinzenais['Lazer - Início (60%)'] = limite_lazer * 0.60
        limites_quinzenais['Lazer - Meio (40%)'] = limite_lazer * 0.40
        
        return limites_quinzenais