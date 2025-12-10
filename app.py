import streamlit as st
# from docx_generator import criar_docx_relatorio # Importe a nova função DOCX
# from pdf_generator import criar_pdf_relatorio  # Mantenha sua função de PDF

# [Definições de MockOrcamento, limites, totais_reais, etc. - como no exemplo anterior]

# --- Funções de Cache (CRUCIAIS para Streamlit) ---

@st.cache_data
def get_docx_bytes_report(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento):
    """Gera o DOCX e armazena o resultado em cache."""
    # Substitua esta chamada pela sua função DOCX
    return criar_docx_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento)

# Se você quiser o PDF, use esta função:
@st.cache_data
def get_pdf_bytes_report(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento):
    """Gera o PDF e armazena o resultado em cache."""
    return criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento)


# --- CHAMADA PRINCIPAL NO STREAMLIT ---
st.title("Gerador de Relatórios Financeiros")

# --- Opção 1: Download DOCX (Word) ---
docx_bytes = get_docx_bytes_report(
    orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento
)

st.download_button(
    label="⬇️ Baixar Relatório DOCX (Word)",
    data=docx_bytes,
    file_name=f"Relatorio_Dindin_{orcamento_obj.mes}.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

st.warning("⚠️ **ATENÇÃO:** A conversão de DOCX para PDF precisa de software externo. Baixe o DOCX e use o Word/LibreOffice para salvar como PDF manualmente.")

# --- Opção 2: Download PDF (Usando seu código original, que é mais fácil) ---
pdf_bytes = get_pdf_bytes_report(
    orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento
)

st.download_button(
    label="✅ Baixar Relatório PDF (Recomendado)",
    data=pdf_bytes,
    file_name=f"Relatorio_Dindin_{orcamento_obj.mes}.pdf",
    mime="application/pdf"
)