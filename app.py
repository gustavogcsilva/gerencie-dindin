import streamlit as st
import pandas as pd
from utils.pdf_generator import criar_pdf_relatorio # Assumindo a correção do path

# --- Classes (Mantidas) ---

class Orcamento:
    """Classe para estruturar os dados do orçamento."""
    # ... (definição da classe Orcamento) ...
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

# --- Funções de Cache (CORRIGIDA) ---

@st.cache_data(show_spinner=False)
# AQUI: Mudança de 'orcamento_obj' para '_orcamento_obj'
def get_pdf_bytes_report(_orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento):
    """
    Gera o PDF e armazena o resultado em cache. O '_' evita o erro de hashing
    na classe customizada Orcamento.
    """
    # Usamos o nome com underscore na chamada para a função externa.
    return criar_pdf_relatorio(_orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento)

# --- FUNÇÕES AUXILIARES DE ENTRADA ---

def input_despesas(titulo, default_data={'Item 1': 0.0}):
    """Cria campos de entrada para despesas (nome e valor) de forma dinâmica."""
    st.subheader(titulo)
    despesas = {}
    
    # Criar DataFrame para capturar os dados
    if 'df_despesas' not in st.session_state or titulo not in st.session_state:
        df_initial = pd.DataFrame(default_data.items(), columns=['Item', 'Valor'])
        # Usar uma chave específica no session_state para garantir que o DataFrame seja inicializado apenas uma vez por widget
        st.session_state[f'df_initial_{titulo.replace(" ", "_")}'] = df_initial
    
    # Usar a chave de sessão correta para o st.data_editor
    edited_df = st.data_editor(
        st.session_state.get(f'df_initial_{titulo.replace(" ", "_")}', pd.DataFrame(default_data.items(), columns=['Item', 'Valor'])),
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Item": st.column_config.TextColumn("Descrição", required=True),
            "Valor": st.column_config.NumberColumn("Valor (R$)", format="%.2f", min_value=0.0, required=True),
        },
        key=titulo.replace(" ", "_") # Chave única para o widget
    )
    
    # Processar o DataFrame editado para o dicionário final
    for index, row in edited_df.iterrows():
        # Apenas inclui linhas com item e valor > 0
        if row['Item'] and row['Valor'] is not None and row['Valor'] > 0:
            despesas[row['Item']] = row['Valor']

    # Não precisamos salvar no session_state aqui se retornamos, mas mantemos a variável local.
    return despesas

# --- LAYOUT PRINCIPAL E ENTRADA DE DADOS ---

st.title("Gerenciamento de Dividas: 💰")
st.subheader("Finalidade em ajudar com despesas e prever o que pode ser gasto.", divider="gray")

# --- BARRA LATERAL PARA ENTRADA DE DADOS ---
with st.sidebar:
    st.header("⚙️ Configurações do Orçamento")
    
    # Dados básicos
    user_name = st.text_input("Seu Nome:", "Digite o nome")
    mes = st.text_input("Mês/Ano do Relatório:", "Dezembro 2025")
    salario = st.number_input("Salário Líquido Total (R$):", min_value=0.0, value=00.00, step=100.00)
    frequencia_pagamento = st.selectbox("Frequência de Pagamento:", ["Mensal", "Quinzenal"])
    
    # 20% Poupança/Investimento
    poupanca_alocada = st.number_input("Valor Alocado em Poupança/Investimento (R$):", min_value=0.0, value=00.00, step=50.00)

    st.subheader("Entrada de Despesas (50% e 30%)")
    st.markdown("Digite os valores nas tabelas.")

# --- ENTRADA DE DESPESAS USANDO st.data_editor ---
st.subheader("Dados de Entrada ✏️")

col1, col2 = st.columns(2)

with col1:
    # 50% NECESSIDADES FIXAS
    # Correção: O valor padrão deve ser um dicionário único para cada chamada
    despesas_fixas = input_despesas(
        "50% Necessidades Fixas", 
        default_data={'Aluguel': 0.00, 'Conta de Luz': 0.00, 'Telefone/Internet': 0.00, 'Cartões de Crédito': 0.00, 'Dividas (Terceiros)': 0.00, 'Seguro': 0.00}
    )

with col2:
    # 30% DESEJOS E LAZER
    despesas_lazer = input_despesas(
        "30% Desejos e Lazer", 
        default_data={'Cinema/Teatro': 0.00, 'Fast/Food-Restaurantes': 0.00}
    )
# Nota: Renomeei a variável de 'gastos_lazer' para 'despesas_lazer' na chamada para refletir o nome da função.

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
    total_lazer = sum(despesas_lazer.values()) # Usando 'despesas_lazer'
    
    totais_reais = {
        'total_fixas': total_fixas,
        'total_lazer': total_lazer,
        'total_poupanca': poupanca_alocada,
        'total_gasto_real': total_fixas + total_lazer + poupanca_alocada
    }
    
    saldo = salario - totais_reais['total_gasto_real']
    
    # 2. Criar Objeto do Orçamento 
    orcamento_obj = Orcamento(
        mes=mes, 
        salario=salario,
        fixas=despesas_fixas,
        lazer=despesas_lazer, # Usando 'despesas_lazer'
        poupanca=poupanca_alocada
    )

    # 3. Geração Otimizada (Chamada ao cache)
    try:
        with st.spinner('Gerando o relatório PDF...'):
            # Passamos o objeto 'orcamento_obj' que será mapeado para o parâmetro '_orcamento_obj'
            pdf_bytes = get_pdf_bytes_report(
                orcamento_obj, 
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
        # A mensagem de erro agora será mais limpa, mas ainda aponta para o gerador de PDF
        st.error(f" Erro ao gerar o PDF: Verifique o código do gerador de PDF. Detalhes: {e}")