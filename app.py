# app.py
import streamlit as st
import pandas as pd # Mantido para garantir que o Streamlit carregue o ambiente corretamente
# Importa o controlador de estado e as views
from app_utils.state_manager import inicializar_estado
from app_views.auth_views import tela_login, tela_cadastro
from app_views.main_app_view import MainAppView

def main_app_controller():
    """Controla qual tela (Login, Cadastro ou App Principal) deve ser exibida."""
    
    # 1. Configuração da Página (DEVE SER A PRIMEIRA COISA)
    st.set_page_config(page_title="Gerencie Dindin!", layout="wide")
    
    # 2. Inicialização do Estado
    inicializar_estado() 

    # 3. Roteamento (Rotas)
    if st.session_state.authenticated:
        MainAppView()
    elif st.session_state.app_mode == 'cadastro':
        tela_cadastro()
    else: 
        # Rota: Login (Default)
        tela_login()

if __name__ == '__main__':
    main_app_controller()