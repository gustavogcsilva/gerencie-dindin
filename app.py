import streamlit as st
import base64
# from seu_modulo import criar_pdf_relatorio # Importe a função corrigida

# ... (Definição dos seus orcamento_obj, limites, totais_reais, etc.) ...

def exibir_pdf_na_tela(pdf_bytes):
    """Codifica os bytes do PDF em base64 e exibe em um iframe."""
    
    # 1. Codifica os bytes do PDF em Base64
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # 2. Cria o código HTML do iframe para incorporar o PDF
    pdf_display = f"""
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="700" 
            height="800" 
            type="application/pdf"
        ></iframe>
    """
    
    # 3. Exibe o HTML no Streamlit
    st.markdown(pdf_display, unsafe_allow_html=True)
    
# --- Exemplo de Uso no Streamlit ---

# 1. Gere os bytes do PDF
pdf_data = criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento)

st.header("Relatório Financeiro Gerado (Visualização)")
st.caption("O PDF é exibido usando codificação Base64 no navegador.")

# 2. Exibe o PDF na tela
exibir_pdf_na_tela(pdf_data)