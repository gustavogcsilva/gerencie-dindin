import streamlit as st
import pandas as pd
from utils.pdf_generator import criar_pdf_relatorio # Assumindo a correção do path

# --- Classes (Mantidas) ---

class Orcamento:
    """Classe para estruturar os dados do orçamento."""
    def __init__(self, mes, salario, fixas, lazer, poupanca):
        self.mes = mes
        self.salario_liquido = salario
        self.despesas_fixas = fixas
        self.gastos_lazer = lazer
        self.poupanca = poupanca

    def calcular_divisao_quinzenal(self, limites):
        # Lógica de simulação de divisão quinzenal
        return {
            'Fixas - Início (60%)': limites.get('Necessidades (50%)', 0) * 0.6,
            'Fixas - Meio (40%)': limites.get('Necessidades (50%)', 0) * 0.4,
            'Lazer - Início (60%)': limites.get('Desejos/Lazer (30%)', 0) * 0.6,
            'Lazer - Meio (40%)': limites.get('Desejos/Lazer (30%)', 0) * 0.4,
        }

# --- Funções de Cache (Corrigida) ---

@st.cache_data(show_spinner=False) 
def get_pdf_bytes_report(_orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento):
    """Gera o PDF e armazena o resultado em cache. '_' para evitar erro de hash."""
    return criar_pdf_relatorio(_orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento)

# --- FUNÇÕES AUXILIARES DE ENTRADA ---

def input_despesas(titulo, default_data={'Item 1': 0.0}):
    """Cria campos de entrada para despesas (nome e valor) de forma dinâmica."""
    st.subheader(titulo)
    despesas = {}
    
    # Criar DataFrame para capturar os dados
    if 'df_despesas' not in st.session_state or st.session_state.df_despesas.empty:
        df_initial = pd.DataFrame(default_data.items(), columns=['Item', 'Valor'])
        st.session_state.df_despesas = df_initial
        
    edited_df = st.data_editor(
        st.session_state.df_despesas,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Item": st.column_config.TextColumn("Descrição", required=True),
            "Valor": st.column_config.NumberColumn("Valor (R$)", format="%.2f", min_value=0.0, required=True),
        },
        key=titulo.replace(" ", "_") # Chave única
    )
    
    # Processar o DataFrame editado para o dicionário final
    for index, row in edited_df.iterrows():
        # Apenas inclui linhas com item e valor > 0
        if row['Item'] and row['Valor'] is not None and row['Valor'] > 0:
             despesas[row['Item']] = row['Valor']
             
    st.session_state[f'final_{titulo}'] = despesas
    return despesas

# --- LAYOUT PRINCIPAL E ENTRADA DE DADOS ---

st.title("Gerencie Dindin: Orçamento 50-30-20 Dinâmico 💰")

# --- BARRA LATERAL PARA ENTRADA DE DADOS ---
with st.sidebar:
    st.header("⚙️ Configurações do Orçamento")
    
    # Dados básicos
    user_name = st.text_input("Seu Nome:", "Usuário Teste")
    mes = st.text_input("Mês/Ano do Relatório:", "Dezembro 2025")
    salario = st.number_input("Salário Líquido Total (R$):", min_value=0.0, value=3500.00, step=100.00)
    frequencia_pagamento = st.selectbox("Frequência de Pagamento:", ["Mensal", "Quinzenal"])
    
    # 20% Poupança/Investimento
    poupanca_alocada = st.number_input("Valor Alocado em Poupança/Investimento (R$):", min_value=0.0, value=700.00, step=50.00)

    st.subheader("Entrada de Despesas (50% e 30%)")
    st.markdown("Use as tabelas para adicionar ou remover itens.")

# --- ENTRADA DE DESPESAS USANDO st.data_editor ---
st.subheader("Dados de Entrada ✏️")

col1, col2 = st.columns(2)

with col1:
    # 50% NECESSIDADES FIXAS
    despesas_fixas = input_despesas(
        "50% Necessidades Fixas", 
        default_data={'Aluguel': 1000.00, 'Conta de Luz': 150.00, 'Telefone/Internet': 50.00}
    )

with col2:
    # 30% DESEJOS E LAZER
    gastos_lazer = input_despesas(
        "30% Desejos e Lazer", 
        default_data={'Cinema': 80.00, 'Restaurante': 200.00}
    )

st.divider()

# --- CÁLCULOS E GERAÇÃO DE RELATÓRIO ---

if st.button("💰 Gerar Relatório e Download"):
    
    # 1. Definir Limites e Totais
    limites = {
        'Necessidades (50%)': salario * 0.5,
        'Desejos/Lazer (30%)': salario * 0.3,
        'Poupança/Investimento (20%)': salario * 0.2
    }
    
    total_fixas = sum(despesas_fixas.values())
    total_lazer = sum(gastos_lazer.values())
    
    totais_reais = {
        'total_fixas': total_fixas,
        'total_lazer': total_lazer,
        'total_poupanca': poupanca_alocada,
        'total_gasto_real': total_fixas + total_lazer + poupanca_alocada
    }
    
    saldo = salario - totais_reais['total_gasto_real']
    
    # 2. Criar Objeto do Orçamento (necessário para a função PDF)
    orcamento_obj = Orcamento(
        mes=mes, 
        salario=salario,
        fixas=despesas_fixas,
        lazer=gastos_lazer,
        poupanca=poupanca_alocada
    )

    # 3. Geração Otimizada (Chamada ao cache)
    try:
        with st.spinner('Gerando o relatório PDF...'):
            pdf_bytes = get_pdf_bytes_report(
                orcamento_obj, # Passamos o objeto (Streamlit ignora o hash devido ao '_')
                limites, 
                totais_reais, 
                saldo, 
                user_name, 
                frequencia_pagamento
            )

        # 4. Configuração e Exibição do Download
        st.success("Relatório gerado com sucesso!")
        
        st.download_button(
            label="✅ Clique para Baixar Relatório PDF",
            data=pdf_bytes,
            file_name=f"Relatorio_Dindin_{mes.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
        
        # --- Demonstração dos Resultados na Tela ---
        st.subheader("Resumo Final do Orçamento")
        
        st.metric("Salário Líquido", f"R$ {salario:,.2f}")
        st.metric("Total Gasto/Alocado", f"R$ {totais_reais['total_gasto_real']:,.2f}")
        
        if saldo < 0:
            st.metric("SALDO FINAL (DÉFICIT)", f"R$ {saldo:,.2f}", delta=f"R$ {abs(saldo):,.2f}", delta_color="inverse")
            st.warning("Atenção: O saldo está negativo. Você gastou/alocou mais do que recebeu!")
        else:
            st.metric("SALDO FINAL (SOBRA)", f"R$ {saldo:,.2f}", delta=f"R$ {saldo:,.2f}", delta_color="normal")
            st.info("Parabéns! Você tem um saldo positivo.")
            
        st.divider()

    except Exception as e:
        st.error(f"❌ Erro ao gerar o PDF: Verifique o código do gerador de PDF. Detalhes: {e}")