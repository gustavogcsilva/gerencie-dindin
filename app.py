import streamlit as st
import pandas as pd
# Importe as funções corrigidas do seu módulo
from pdf_generator import criar_pdf_relatorio 

# --- IMPORTANTE: Estrutura de Cache para garantir que o PDF seja gerado uma única vez ---
@st.cache_data
def get_pdf_bytes_report(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento):
    """Gera o PDF e armazena o resultado em cache."""
    return criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento)

# --- Exemplo de Definição de Dados (Substitua pelos seus dados reais) ---
class MockOrcamento: # Classe fictícia para simulação
    def __init__(self, mes, salario, fixas, lazer, poupanca):
        self.mes = mes
        self.salario_liquido = salario
        self.despesas_fixas = fixas
        self.gastos_lazer = lazer
        self.poupanca = poupanca

    def calcular_divisao_quinzenal(self, limites):
        # Simulação para o exemplo
        return {
            'Fixas - Início (60%)': limites.get('Necessidades (50%)', 0) * 0.6,
            'Fixas - Meio (40%)': limites.get('Necessidades (50%)', 0) * 0.4,
            'Lazer - Início (60%)': limites.get('Desejos/Lazer (30%)', 0) * 0.6,
            'Lazer - Meio (40%)': limites.get('Desejos/Lazer (30%)', 0) * 0.4,
        }

# Parâmetros de exemplo
salario = 3500.00
orcamento_obj = MockOrcamento(
    mes="Dezembro 2025", 
    salario=salario,
    fixas={'Aluguel': 1000, 'Conta de Luz': 150},
    lazer={'Cinema': 80, 'Restaurante': 200},
    poupanca=700
)

limites = {
    'Necessidades (50%)': salario * 0.5, # 1750
    'Desejos/Lazer (30%)': salario * 0.3, # 1050
    'Poupança/Investimento (20%)': salario * 0.2 # 700
}

totais_reais = {
    'total_fixas': sum(orcamento_obj.despesas_fixas.values()), # 1150
    'total_lazer': sum(orcamento_obj.gastos_lazer.values()), # 280
    'total_poupanca': orcamento_obj.poupanca, # 700
    'total_gasto_real': 1150 + 280 + 700 # 2130
}
saldo = salario - totais_reais['total_gasto_real'] # 3500 - 2130 = 1370
user_name = "João da Silva"
frequencia_pagamento = "Mensal"

# --- CHAMADA PRINCIPAL NO STREAMLIT ---
st.title("Gerador de Relatórios Financeiros")

if st.button("Gerar e Baixar Relatório"):
    # 1. Obtenha os bytes do PDF (usa cache se os parâmetros forem os mesmos)
    pdf_bytes = get_pdf_bytes_report(
        orcamento_obj, 
        limites, 
        totais_reais, 
        saldo, 
        user_name, 
        frequencia_pagamento
    )

    # 2. Configure o botão de download
    st.download_button(
        label="✅ Clique aqui para Baixar Relatório PDF",
        data=pdf_bytes,
        file_name=f"Relatorio_Dindin_{orcamento_obj.mes}.pdf",
        mime="application/pdf"
    )