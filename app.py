import streamlit as st
import pandas as pd
# Certifique-se de que 'pdf_generator' está acessível no PYTHONPATH
# e que a função criar_pdf_relatorio está dentro dele.
from utils.pdf_generator import criar_pdf_relatorio

# --- IMPORTANTE: Estrutura de Cache para garantir que o PDF seja gerado uma única vez ---
@st.cache_data(show_spinner=False) # Adicionado show_spinner=False para um UI mais limpa
def get_pdf_bytes_report(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento):
    """Gera o PDF e armazena o resultado em cache."""
    # A função criar_pdf_relatorio deve retornar os bytes puros do PDF (bytestring)
    return criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento)

# --- Exemplo de Definição de Dados (Substitua pelos seus dados reais) ---
class Orcamento: # Nome renomeado de MockOrcamento para Orcamento
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

# --- PARÂMETROS E DADOS DE TESTE ---
salario = 3500.00
orcamento_obj = Orcamento(
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
    'total_fixas': sum(orcamento_obj.despesas_fixas.values()), 
    'total_lazer': sum(orcamento_obj.gastos_lazer.values()), 
    'total_poupanca': orcamento_obj.poupanca, 
    'total_gasto_real': sum(orcamento_obj.despesas_fixas.values()) + sum(orcamento_obj.gastos_lazer.values()) + orcamento_obj.poupanca
}
saldo = salario - totais_reais['total_gasto_real'] 
user_name = "João da Silva"
frequencia_pagamento = "Mensal"

# --- CHAMADA PRINCIPAL NO STREAMLIT (FLUXO OTIMIZADO) ---

st.title("Gerador de Relatórios Financeiros 📊")

# 1. Geração Otimizada: Obtenha os bytes do PDF (usa cache e é executado na inicialização)
# O st.cache_data garante que esta função seja chamada apenas quando os parâmetros mudam.
try:
    with st.spinner('Gerando o relatório...'):
        pdf_bytes = get_pdf_bytes_report(
            orcamento_obj, 
            limites, 
            totais_reais, 
            saldo, 
            user_name, 
            frequencia_pagamento
        )

    # 2. Configuração do botão de download (IMEDIATA)
    # Este botão é renderizado diretamente e usa os bytes pré-calculados.
    # O st.download_button não precisa ser ativado por outro botão; ele é sempre "ativo".
    st.download_button(
        label="✅ Baixar Relatório PDF",
        data=pdf_bytes,
        file_name=f"Relatorio_Dindin_{orcamento_obj.mes}.pdf",
        mime="application/pdf"
    )

    st.success("Relatório gerado com sucesso! Clique no botão de download acima.")

    # --- Opcional: Mostrar Resumo dos Dados ---
    st.subheader("Resumo dos Dados de Entrada:")
    st.metric("Salário Líquido", f"R$ {salario:,.2f}")
    st.metric("Total Gasto / Alocado", f"R$ {totais_reais['total_gasto_real']:,.2f}")
    st.metric("Saldo Final", f"R$ {saldo:,.2f}")

except Exception as e:
    st.error(f"❌ Erro ao gerar o PDF: Verifique o código 'pdf_generator.py'. Detalhes: {e}")