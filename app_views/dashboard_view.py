# app_views/dashboard_view.py
import streamlit as st
import pandas as pd
import plotly.express as px
from app_utils.orcamento_class import Orcamento 

def criar_dashboard_historico():
    st.header("Análise de Desempenho Histórico Mensal")

    if len(st.session_state.historico_orcamentos) <= 1:
        st.info("Adicione e salve orçamentos de meses anteriores para ver a comparação histórica aqui.")
        return pd.DataFrame() 

    # --- Filtro de Meses ---
    meses_disponiveis = sorted(list(st.session_state.historico_orcamentos.keys()))
    meses_selecionados = st.multiselect(
        'Selecione os meses para incluir na análise (deixe vazio para todos):',
        options=meses_disponiveis,
        default=meses_disponiveis,
        key='historico_meses_select'
    )
    
    if not meses_selecionados:
        st.warning("Selecione pelo menos um mês para visualizar o histórico.")
        return pd.DataFrame()

    dados_historicos = []
    
    for mes in meses_selecionados:
        dados = st.session_state.historico_orcamentos.get(mes, None)
        if dados and dados.get('salario_liquido', 0.0) > 0: 
            orc = Orcamento(
                dados['salario_liquido'], mes, dados['despesas_fixas'], 
                dados['gastos_lazer'], dados['poupanca_investimentos']
            )
            limites = orc.calcular_limites_50_30_20()
            totais_reais = {
                'total_fixas': orc.calcular_total_categoria('fixas'),
                'total_lazer': orc.calcular_total_categoria('lazer'),
                'total_poupanca': orc.calcular_total_categoria('poupanca'),
                'total_gasto_real': orc.calcular_total_categoria('fixas') + orc.calcular_total_categoria('lazer') + orc.calcular_total_categoria('poupanca')
            }
            
            economia = orc.calcular_economizado(limites, totais_reais)

            dados_historicos.append({
                'Mês': mes,
                'Salário Líquido': dados['salario_liquido'],
                'Total Gasto': totais_reais['total_gasto_real'],
                'Despesas Fixas Real': totais_reais['total_fixas'],
                'Lazer Real': totais_reais['total_lazer'],
                'Folga/Déficit Necessidades': economia['fixas'], 
                'Folga/Déficit Lazer': economia['lazer'],
                'Economia Total Potencial (Folga)': max(0, economia['fixas'] + economia['lazer'])
            })

    if not dados_historicos:
        st.info("Nenhum mês selecionado possui salário líquido > R$ 0,00 para comparação.")
        return pd.DataFrame()

    df_historico_geral = pd.DataFrame(dados_historicos)
    df_historico_geral.set_index('Mês', inplace=True)
    
    st.subheader("1. Resumo Histórico Mensal (50-30-20)")
    st.dataframe(df_historico_geral[['Salário Líquido', 'Total Gasto', 'Folga/Déficit Necessidades', 'Folga/Déficit Lazer']].style.format("R$ {:,.2f}"), use_container_width=True)

    # --- (Resto do código para gráficos detalhados mantido) ---
    st.markdown("---")
    # ... (código para gráficos de barras) ...
    
    # Criação do DataFrame detalhado para o segundo gráfico
    itens_detalhados = []
    for mes in meses_selecionados:
        dados = st.session_state.historico_orcamentos.get(mes, None)
        if dados and dados.get('salario_liquido', 0.0) > 0:
            despesas_combinadas = {k: {'Valor': v, 'Categoria': 'Fixa'} for k, v in dados['despesas_fixas'].items()}
            despesas_combinadas.update({k: {'Valor': v, 'Categoria': 'Lazer'} for k, v in dados['gastos_lazer'].items()})
            
            for item, info in despesas_combinadas.items():
                itens_detalhados.append({'Mês': mes, 'Item': item, 'Categoria': info['Categoria'], 'Valor': info['Valor']})
    
    df_itens_detalhado = pd.DataFrame(itens_detalhados)
    
    st.subheader("2. Comparação Detalhada de Itens de Despesa")
    st.info("Aqui você pode ver como o custo de itens específicos (Aluguel, Supermercado, Lazer, etc.) variou entre os meses selecionados.")

    if not df_itens_detalhado.empty:
        opcoes_itens = sorted(df_itens_detalhado['Item'].unique())
        if opcoes_itens:
            item_selecionado = st.selectbox('Selecione o Item para Comparação Histórica', options=opcoes_itens, key='item_historico_select')

            df_filtrado = df_itens_detalhado[df_itens_detalhado['Item'] == item_selecionado]
            
            if not df_filtrado.empty:
                st.dataframe(df_filtrado[['Mês', 'Categoria', 'Valor']].sort_values(by='Mês', ascending=False).style.format({'Valor': "R$ {:,.2f}"}), hide_index=True, use_container_width=True)

                fig_detalhe = px.bar(
                    df_filtrado, x='Mês', y='Valor', color='Mês', text='Valor', title=f"Variação de Custo do Item: **{item_selecionado}**",
                )
                fig_detalhe.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
                st.plotly_chart(fig_detalhe, use_container_width=True)
            
    # --- Gráfico de Economia Potencial ---
    st.markdown("---")
    st.subheader("3. Folga/Déficit em Necessidades (50%)")
    
    fig_economia = px.bar(
        df_historico_geral, y='Folga/Déficit Necessidades', text='Folga/Déficit Necessidades',
        color='Folga/Déficit Necessidades', color_continuous_scale=px.colors.diverging.RdYlGn,
        title="Folga/Déficit em Necessidades (50%) por Mês"
    )
    fig_economia.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
    st.plotly_chart(fig_economia, use_container_width=True)
    
    return df_historico_geral