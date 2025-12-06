# app_views/auth_views.py
import streamlit as st
# Importa o logout do state_manager (importação absoluta)
from app_utils.state_manager import logout

def tela_cadastro():
    st.sidebar.title("🔒 Acesso")
    # Alterna o modo da aplicação para 'login' para forçar o roteamento
    st.sidebar.button("Voltar para Login", on_click=lambda: st.session_state.update(app_mode='login'))
    
    st.title("🚀 Crie sua Conta")
    
    with st.form("cadastro_form"):
        st.markdown("#### Preencha os detalhes da sua nova conta")
        new_name = st.text_input("Nome", key="cadastro_name_input")
        new_email = st.text_input("Email", key="cadastro_email_input").lower()
        new_password = st.text_input("Senha", type="password", key="cadastro_password_input")
        
        cadastrar_button = st.form_submit_button("Cadastrar e Entrar")
        
        if cadastrar_button:
            if not new_name.strip() or "@" not in new_email or len(new_password) < 3:
                st.error("Por favor, preencha todos os campos corretamente (a senha deve ter no mínimo 3 caracteres).")
                return
            
            if new_email in st.session_state.usuarios:
                st.error("Este email já está cadastrado. Tente fazer Login.")
                return
            
            st.session_state.usuarios[new_email] = {'nome': new_name.strip().title(), 'senha': new_password}
            
            # Autentica e muda o modo
            st.session_state.authenticated = True
            st.session_state.user_name = new_name.strip().title()
            st.session_state.user_email = new_email
            st.session_state.app_mode = 'main_app'
            st.success(f"Cadastro efetuado! Bem-vindo(a), {st.session_state.user_name}!")
            st.rerun()

def tela_login():
    st.sidebar.title("🔒 Acesso")
    # Alterna o modo da aplicação para 'cadastro' para forçar o roteamento
    st.sidebar.button("Ir para Cadastro", on_click=lambda: st.session_state.update(app_mode='cadastro'))

    st.title("Acesse sua Conta")
    
    with st.form("login_form"):
        st.markdown("#### Insira suas credenciais")
        email = st.text_input("Email", key="login_email_input").lower()
        password = st.text_input("Senha", type="password", key="login_password_input")
        login_button = st.form_submit_button("Entrar no Sistema 🚀")
        
        if login_button:
            if email in st.session_state.usuarios:
                user_data = st.session_state.usuarios[email]
                if user_data['senha'] == password:
                    # Autentica e muda o modo
                    st.session_state.authenticated = True
                    st.session_state.user_name = user_data['nome']
                    st.session_state.user_email = email
                    st.session_state.app_mode = 'main_app'
                    st.success(f"Bem-vindo(a), {st.session_state.user_name}!")
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            else:
                st.error("Email não encontrado. Tente Cadastrar-se.")