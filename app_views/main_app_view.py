import streamlit as st
import pandas as pd
import plotly.express as px
from app_utils.state_manager import logout, salvar_orcamento_atual, atualizar_orcamento_do_selectbox, adicionar_gasto
from app_utils.orcamento_class import Orcamento
from app_utils.pdf_generator import criar_pdf_relatorio, criar_pdf_relatorio_historico
from .dashboard_view import criar_dashboard_historico

def MainAppView():


    st.title("💰 Gerenciador de Orçamento 50-30-20 Histórico")
    
    st.sidebar.success(f"Logado como: **{st.session_state.user_name}**")
    st.sidebar.button("Sair", on_click=logout)
    
    # Inicializa variáveis para evitar NameError se o salário for <= 0
    meu_orcamento = None
    limites = {}
    total_fixas = 0.0
    total_lazer = 0.0
    total_poupanca = st.session_state.get('poupanca_investimentos', 0.0)
    total_gasto_real = 0.0
    saldo = st.session_state.salario_liquido
    df_historico_geral = pd.DataFrame() 
    


    # --- 1. Entrada de Dados Principais e Seleção de Mês ---
    st.header("1. 📝 Configuração Inicial e Seleção")
    col_mes_select, col_salario, col_frequencia, col_novo_mes = st.columns([1.5, 1.5, 1.5, 1]) 

    with col_mes_select:
        meses_disponiveis = list(st.session_state.historico_orcamentos.keys())
        if st.session_state.mes_selecionado not in meses_disponiveis:
            meses_disponiveis.append(st.session_state.mes_selecionado)
            
        st.selectbox(
            'Selecione o **mês** de referência',
            options=meses_disponiveis,
            index=meses_disponiveis.index(st.session_state.mes_selecionado),
            key="mes_select",
            on_change=atualizar_orcamento_do_selectbox 
        )
        st.session_state.mes_anterior = st.session_state.mes_selecionado 
    
    with col_salario:
        salario_input_value = st.session_state.get('salario_liquido', 0.0)
        st.session_state.salario_liquido = st.number_input(
            '**Salário Líquido** (R$)',
            min_value=0.0,
            value=salario_input_value, 
            step=100.0,
            format="%.2f",
            key="salario_input",
            on_change=salvar_orcamento_atual 
        )
    
    with col_frequencia:
        st.session_state.frequencia_pagamento = st.selectbox(
            '**Frequência de Pagamento**',
            options=['Mensal', 'Quinzenal'],
            index=['Mensal', 'Quinzenal'].index(st.session_state.frequencia_pagamento),
            key="frequencia_input",
            on_change=salvar_orcamento_atual 
        )
        
    with col_novo_mes:
        novo_mes_nome = st.text_input('Novo Mês (ex: Janeiro)', value="")
        if st.button('➕ Criar Novo Mês'):
            if novo_mes_nome and novo_mes_nome not in st.session_state.historico_orcamentos:
                salvar_orcamento_atual() 
                st.session_state.historico_orcamentos[novo_mes_nome] = {
                    'salario_liquido': 0.0, 
                    'despesas_fixas': {},
                    'gastos_lazer': {},
                    'poupanca_investimentos': 0.0
                }
                st.session_state.mes_selecionado = novo_mes_nome
                st.success(f"Mês **{novo_mes_nome}** criado. Insira o Salário Líquido!")
                st.rerun()
            elif novo_mes_nome in st.session_state.historico_orcamentos:
                st.error("Este mês já existe.")

    if st.session_state.salario_liquido <= 0:
        st.warning(f"Por favor, insira um **Salário Líquido** para o mês de **{st.session_state.mes_selecionado}** para ver os limites e gráficos.")
    else: 
        meu_orcamento = Orcamento(
            st.session_state.salario_liquido, st.session_state.mes_selecionado,
            st.session_state.despesas_fixas, st.session_state.gastos_lazer,
            st.session_state.poupanca_investimentos
        )
        limites = meu_orcamento.calcular_limites_50_30_20()
        
        st.markdown("---")
        
        # --- 2. Abas para Inserção/Edição de Gastos ---
        tab_fixas, tab_lazer, tab_poupanca, tab_historico = st.tabs([
            f"🏠 50% Necessidades ({st.session_state.mes_selecionado})", 
            f"✨ 30% Desejos e Lazer ({st.session_state.mes_selecionado})", 
            f"🎯 20% Poupança/Investimento ({st.session_state.mes_selecionado})",
            "📊 Dashboard Histórico e Economia"
        ])

        # Recalcula totais reais para uso na tela e PDF
        total_fixas = meu_orcamento.calcular_total_categoria('fixas')
        total_lazer = meu_orcamento.calcular_total_categoria('lazer')
        total_poupanca = meu_orcamento.calcular_total_categoria('poupanca')
        total_gasto_real = total_fixas + total_lazer + total_poupanca
        saldo = st.session_state.salario_liquido - total_gasto_real

        # 50% - Despesas Fixas (Mantido)
        with tab_fixas:
            limite_fixas = limites.get('Necessidades (50%)', 0.0)
            st.subheader(f"Limite Ideal (50%): R$ {limite_fixas:,.2f}")
            st.info(f"Total Gasto Atual: R$ {total_fixas:,.2f} | Restante: R$ {limite_fixas - total_fixas:,.2f}")

            with st.form("form_adicionar_fixa"):
                col_item, col_valor = st.columns([3, 2])
                with col_item: item_fixa = st.text_input('Nome da Nova Despesa Fixa', key="fixa_item")
                with col_valor: valor_fixa = st.number_input('Valor (R$)', min_value=0.0, step=1.0, key="fixa_valor")
                if st.form_submit_button('➕ Adicionar Fixa'): adicionar_gasto('fixas', item_fixa, valor_fixa)
                    
            if st.session_state.despesas_fixas:
                st.markdown("---")
                st.subheader("Itens Lançados: Edite o valor ou Exclua a linha (🗑️)")
                df_fixas = pd.DataFrame(st.session_state.despesas_fixas.items(), columns=['Item', 'Valor']).set_index('Item') 
                edited_df_fixas = st.data_editor(df_fixas, use_container_width=True, num_rows="dynamic", key="editor_fixas", column_config={"Valor": st.column_config.NumberColumn("Valor (R$)", min_value=0.0, format="R$ %.2f")})
                
                if len(edited_df_fixas) != len(df_fixas) or not edited_df_fixas['Valor'].equals(df_fixas['Valor']):
                    st.warning("Existem alterações pendentes (edição ou exclusão). Clique em Salvar para aplicar.")
                    if st.button('Salvar Alterações de Despesas Fixas', key="salvar_fixas"):
                        novo_estado_fixas = {k: v for k, v in edited_df_fixas['Valor'].to_dict().items() if v is not None and v > 0}
                        st.session_state.despesas_fixas = novo_estado_fixas
                        salvar_orcamento_atual()
                        st.success("Despesas Fixas atualizadas com sucesso!")
                        st.rerun()

        # 30% - Desejos e Lazer (Mantido)
        with tab_lazer:
            limite_lazer = limites.get('Desejos/Lazer (30%)', 0.0)
            st.subheader(f"Limite Ideal (30%): R$ {limite_lazer:,.2f}")
            st.info(f"Total Gasto Atual: R$ {total_lazer:,.2f} | Restante: R$ {limite_lazer - total_lazer:,.2f}")

            with st.form("form_adicionar_lazer"):
                col_item, col_valor = st.columns([3, 2])
                with col_item: item_lazer = st.text_input('Nome do Novo Gasto de Lazer/Desejo', key="lazer_item")
                with col_valor: valor_lazer = st.number_input('Valor (R$)', min_value=0.0, step=1.0, key="lazer_valor")
                if st.form_submit_button('➕ Adicionar Lazer'): adicionar_gasto('lazer', item_lazer, valor_lazer)

            if st.session_state.gastos_lazer:
                st.markdown("---")
                st.subheader("Itens Lançados: Edite o valor ou Exclua a linha (🗑️)")
                df_lazer = pd.DataFrame(st.session_state.gastos_lazer.items(), columns=['Item', 'Valor']).set_index('Item')
                edited_df_lazer = st.data_editor(df_lazer, use_container_width=True, num_rows="dynamic", key="editor_lazer", column_config={"Valor": st.column_config.NumberColumn("Valor (R$)", min_value=0.0, format="R$ %.2f")})
                
                if len(edited_df_lazer) != len(df_lazer) or not edited_df_lazer['Valor'].equals(df_lazer['Valor']):
                    st.warning("Existem alterações pendentes (edição ou exclusão). Clique em Salvar para aplicar.")
                    if st.button('Salvar Alterações de Desejos/Lazer', key="salvar_lazer"):
                        novo_estado_lazer = {k: v for k, v in edited_df_lazer['Valor'].to_dict().items() if v is not None and v > 0}
                        st.session_state.gastos_lazer = novo_estado_lazer
                        salvar_orcamento_atual()
                        st.success("Despesas de Lazer atualizadas com sucesso!")
                        st.rerun()
                
        # 20% - Poupança e Investimento (Mantido)
        with tab_poupanca:
            meta_poupanca = limites.get('Poupança/Investimento (20%)', 0.0)
            st.subheader(f"Meta Ideal (20%): R$ {meta_poupanca:,.2f}")
            
            st.session_state.poupanca_investimentos = st.number_input(
                'Digite o valor que você irá **poupar/investir** (R$)', min_value=0.0, value=st.session_state.poupanca_investimentos,
                step=10.0, format="%.2f", key="poupanca_input", on_change=salvar_orcamento_atual 
            )
            if total_poupanca >= meta_poupanca: st.success(f"Excelente! Você atingiu ou superou a meta de poupança (R$ {total_poupanca:,.2f}).")
            else: st.warning(f"Atenção: Você está R$ {meta_poupanca - total_poupanca:,.2f} abaixo da meta ideal de 20%.")
        

        with tab_historico:
            df_historico_geral = criar_dashboard_historico() 

        st.markdown("---")

        st.header("3. 📈 Relatório Final do Mês")
        
        col_resumo_salario, col_resumo_alocado, col_resumo_saldo = st.columns(3)
        with col_resumo_salario: st.metric("Salário Líquido", f"R$ {st.session_state.salario_liquido:,.2f}")
        with col_resumo_alocado: st.metric("Total Alocado/Gasto", f"R$ {total_gasto_real:,.2f}")
        with col_resumo_saldo: st.metric("Saldo Restante", f"R$ {saldo:,.2f}", delta_color=("inverse" if saldo < 0 else "normal"))

        df_grafico = pd.DataFrame({
            'Categoria': ['Necessidades (50%)', 'Desejos/Lazer (30%)', 'Poupança/Investimento (20%)'],
            'Ideal': [limites.get('Necessidades (50%)'), limites.get('Desejos/Lazer (30%)'), limites.get('Poupança/Investimento (20%)')],
            'Real': [total_fixas, total_lazer, total_poupanca]
        })
        df_grafico_melted = df_grafico.melt(id_vars='Categoria', var_name='Tipo', value_name='Valor')
        fig = px.bar(df_grafico_melted, x='Categoria', y='Valor', color='Tipo', barmode='group', text='Valor', title=f"Comparação de Orçamento Ideal vs. Real - {st.session_state.mes_selecionado}", color_discrete_map={'Ideal': '#1f77b4', 'Real': '#ff7f0e'})
        fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    user_name = st.session_state.get('user_name', 'Usuário Desconhecido') 
    frequencia_pagamento = st.session_state.get('frequencia_pagamento', 'N/A')

    if meu_orcamento and meu_orcamento.salario_liquido > 0:
        totais_reais = {'total_fixas': total_fixas, 'total_lazer': total_lazer, 'total_poupanca': total_poupanca, 'total_gasto_real': total_gasto_real}

        pdf_data = criar_pdf_relatorio(
            meu_orcamento, limites, totais_reais, saldo, user_name, frequencia_pagamento
        )

        st.download_button(
            label="⬇️ Baixar Relatório Mensal em PDF", data=pdf_data,
            file_name=f"Relatorio_Orcamento_{st.session_state.mes_selecionado}.pdf",
            mime="application/pdf"
        )

    # GERAÇÃO DO PDF E BOTÃO DE DOWNLOAD (Relatório Histórico)
    if not df_historico_geral.empty:
        pdf_data_historico = criar_pdf_relatorio_historico(df_historico_geral)
        st.download_button(
            label="⬇️ Baixar Relatório de Comparação Histórica em PDF",
            data=pdf_data_historico, file_name="Relatorio_Comparacao_Historica.pdf",
            mime="application/pdf"
        )