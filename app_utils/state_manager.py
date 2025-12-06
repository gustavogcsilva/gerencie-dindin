# app_utils/state_manager.py
import streamlit as st
import sqlite3

def carregar_dados_mes_selecionado():
    mes_atual = st.session_state.mes_selecionado
    dados = st.session_state.historico_orcamentos.get(mes_atual, {})

    st.session_state.salario_liquido = dados.get('salario_liquido', 0.0) 
    st.session_state.mes_referencia = mes_atual
    st.session_state.despesas_fixas = dados.get('despesas_fixas', {})
    st.session_state.gastos_lazer = dados.get('gastos_lazer', {})
    st.session_state.poupanca_investimentos = dados.get('poupanca_investimentos', 0.0)


def salvar_orcamento_atual():
    mes_atual = st.session_state.mes_selecionado
    st.session_state.historico_orcamentos[mes_atual] = {
        'salario_liquido': st.session_state.salario_liquido,
        'despesas_fixas': st.session_state.despesas_fixas.copy(),
        'gastos_lazer': st.session_state.gastos_lazer.copy(),
        'poupanca_investimentos': st.session_state.poupanca_investimentos
    }


def adicionar_gasto(categoria, item, valor):
    if valor > 0 and item:
        if categoria == 'fixas':
            st.session_state.despesas_fixas[item] = valor
        elif categoria == 'lazer':
            st.session_state.gastos_lazer[item] = valor
        st.success(f'Item "{item}" (R$ {valor:,.2f}) adicionado em {categoria.upper()}.')
        salvar_orcamento_atual() 
        st.rerun()

def atualizar_orcamento_do_selectbox():
    if 'mes_anterior' in st.session_state and st.session_state.mes_anterior != st.session_state.mes_select:
        mes_a_salvar = st.session_state.mes_anterior
        
        st.session_state.historico_orcamentos[mes_a_salvar] = {
            'salario_liquido': st.session_state.salario_liquido,
            'despesas_fixas': st.session_state.despesas_fixas.copy(),
            'gastos_lazer': st.session_state.gastos_lazer.copy(),
            'poupanca_investimentos': st.session_state.poupanca_investimentos
        }
    
    st.session_state.mes_selecionado = st.session_state.mes_select
    st.session_state.mes_anterior = st.session_state.mes_selecionado
    
    carregar_dados_mes_selecionado()
    st.rerun()


def inicializar_estado():
    MES_INICIAL = "Dezembro"
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_name = None
        st.session_state.user_email = None
        st.session_state.app_mode = 'login' 
        
    if 'usuarios' not in st.session_state:
        st.session_state.usuarios = {
            'exemplo@teste.com': {'nome': 'Exemplo User', 'senha': '123'}
        }
        
    if 'frequencia_pagamento' not in st.session_state:
        st.session_state.frequencia_pagamento = 'Mensal'

    if 'historico_orcamentos' not in st.session_state:
        st.session_state.historico_orcamentos = {
            "Novembro": {
                'salario_liquido': 0.0, 
                'despesas_fixas': {'Aluguel/Moradia': 0.0, 'Supermercado': 0.0, 'Contas (Luz/Água/Internet)': 0.0},
                'gastos_lazer': {'Streaming/Assinatura': 0.0, 'Lanches/Restaurantes': 0.0, 'Academia': 0.0},
                'poupanca_investimentos': 0.0
            }
        }
    
    if 'mes_selecionado' not in st.session_state:
        st.session_state.mes_selecionado = MES_INICIAL
    
    if MES_INICIAL not in st.session_state.historico_orcamentos:
        st.session_state.historico_orcamentos[MES_INICIAL] = {
            'salario_liquido': 0.0, 
            'despesas_fixas': {},
            'gastos_lazer': {},
            'poupanca_investimentos': 0.0
        }
    
    if st.session_state.authenticated:
        carregar_dados_mes_selecionado()

def logout():
    st.session_state.authenticated = False
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.app_mode = 'login'
    st.success("Sessão encerrada com sucesso.")
    st.rerun()

DATABASE_NAME = 'orcamento_app.db'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Tabela de Usuários (para autenticação)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            email TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            senha TEXT NOT NULL 
        )
    """)
    
    # Tabela de Orçamentos (para persistir os dados mensais de cada usuário)
    # Recomendação: Salvar os dados complexos (despesas_fixas, gastos_lazer) como JSON
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY,
            user_email TEXT,
            mes TEXT NOT NULL,
            dados_json TEXT NOT NULL,
            UNIQUE(user_email, mes)
        )
    """)
    
    conn.commit()
    conn.close()

# Você chamaria init_db() no início do seu app.py ou main_app_controller()