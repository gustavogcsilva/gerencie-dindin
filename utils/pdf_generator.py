from fpdf import FPDF # Mantido apenas para contexto, mas não é usado na saída
import pandas as pd
import io

def safe_text(text):
    """Placeholder para a função safe_text que transforma objetos em strings seguras."""
    # Como não temos o módulo safe_text aqui, esta é uma implementação básica.
    return str(text) 


def formatar_secao_markdown(titulo, total_real, limite, despesas):
    """Formata uma seção do orçamento (50/30) em string Markdown."""
    
    # Dicionário de despesas para DataFrame
    df_despesas = pd.DataFrame(
        list(despesas.items()), 
        columns=['Item', 'Valor']
    )
    df_despesas['Valor'] = df_despesas['Valor'].apply(lambda x: f"R$ {x:,.2f}")
    
    # Construção da string Markdown
    markdown_output = f"### {safe_text(titulo)} (Limite: R$ {limite:,.2f})"
    
    # Tabela de Despesas (Streamlit renderizará isso como uma tabela limpa)
    markdown_output += "\n\n| Item | Valor |\n| :--- | ---: |\n"
    for item, valor_original in despesas.items():
        valor_formatado = f"R$ {valor_original:,.2f}"
        markdown_output += f"| {safe_text(item)} | {valor_formatado} |\n"
    
    # Linha do Total
    markdown_output += f"| **TOTAL GASTO** | **R$ {total_real:,.2f}** |\n"
    
    # Aviso de Limite
    if total_real > limite:
        ultrapassado = total_real - limite
        markdown_output += f"\n**⚠️ ATENÇÃO:** Você **ULTRAPASSOU** o limite em **R$ {ultrapassado:,.2f}**!"
    elif total_real < limite:
        economizado = limite - total_real
        markdown_output += f"\n**✅ Parabéns!** Você economizou **R$ {economizado:,.2f}** nesta categoria."
    
    markdown_output += "\n\n---\n"
    return markdown_output

# --- Funções Principais Refatoradas ---

def criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento) -> str:
    """
    Gera o conteúdo do relatório 50-30-20 em string Markdown para visualização no Streamlit.
    """
    
    output_md = []

    # 1. Títulos e Resumo Geral
    output_md.append(f"# Gerencie Dindin: Relatório {safe_text(orcamento_obj.mes)}")
    output_md.append(f"Gerado para: **{safe_text(user_name)}** | Frequência: **{safe_text(frequencia_pagamento)}**")
    output_md.append("---")
    
    output_md.append("## Resumo Geral e Saldo")
    output_md.append(f"| Indicador | Valor |\n| :--- | ---: |\n")
    output_md.append(f"| Salário Líquido | R$ {orcamento_obj.salario_liquido:,.2f} |\n")
    output_md.append(f"| Total Gasto/Alocado | R$ {totais_reais['total_gasto_real']:,.2f} |\n")
    
    if saldo < 0:
        saldo_cor = f"🔴 **R$ {saldo:,.2f}**"
    else:
        saldo_cor = f"🟢 **R$ {saldo:,.2f}**"
        
    output_md.append(f"| **SALDO FINAL** | {saldo_cor} |\n")
    output_md.append("\n---\n")

    # 2. Divisão Quinzenal (Se aplicável)
    if frequencia_pagamento == 'Quinzenal':
        divisao_quinzenal = orcamento_obj.calcular_divisao_quinzenal(limites)
        
        limite_gasto_primeira_quize = divisao_quinzenal['Fixas - Início (60%)'] + divisao_quinzenal['Lazer - Início (60%)']
        limite_gasto_segunda_quize = divisao_quinzenal['Fixas - Meio (40%)'] + divisao_quinzenal['Lazer - Meio (40%)']
        
        output_md.append("## Divisão de Pagamento Quinzenal (60% / 40%)")
        output_md.append(f"Valor Recebido por Quinzena: **R$ {orcamento_obj.salario_liquido / 2:,.2f}**")
        
        output_md.append("\n**Limites Sugeridos de Gasto (Necessidades + Lazer):**")
        output_md.append("| Quinzena | Base de Cálculo | Limite Máximo |\n| :--- | :--- | ---: |\n")
        output_md.append(f"| 1ª Quinzena | 60% dos Limites Mensais | R$ {limite_gasto_primeira_quize:,.2f} |\n")
        output_md.append(f"| 2ª Quinzena | 40% dos Limites Mensais | R$ {limite_gasto_segunda_quize:,.2f} |\n")
        output_md.append("\n---\n")


    # 3. Seção 50% Necessidades
    output_md.append(formatar_secao_markdown(
        "50% Necessidades Fixas (Despesas Fixas)",
        totais_reais['total_fixas'], 
        limites.get('Necessidades (50%)', 0.0), 
        orcamento_obj.despesas_fixas
    ))

    # 4. Seção 30% Desejos/Lazer
    output_md.append(formatar_secao_markdown(
        "30% Desejos e Lazer (Despesas Variáveis)",
        totais_reais['total_lazer'], 
        limites.get('Desejos/Lazer (30%)', 0.0), 
        orcamento_obj.gastos_lazer
    ))

    # 5. Seção 20% Poupança
    meta_poupanca = limites.get('Poupança/Investimento (20%)', 0.0)
    total_poupanca = totais_reais['total_poupanca']
    
    output_md.append("## 20% Poupança/Investimento")
    output_md.append(f"Meta: **R$ {meta_poupanca:,.2f}**")
    output_md.append(f"Valor Destinado: **R$ {total_poupanca:,.2f}**")

    if total_poupanca < meta_poupanca:
        falta = meta_poupanca - total_poupanca
        output_md.append(f"\n**⚠️ Atenção:** Você está **R$ {falta:,.2f}** abaixo da meta de 20%!")
    else:
        output_md.append("\n**👍 Meta de 20% atingida ou superada!**")
        
    output_md.append("\n---\n")

    return "\n".join(output_md)


def criar_pdf_relatorio_historico(df_resumo_historico) -> str:
    """
    Gera o resumo da comparação histórica em string Markdown para visualização no Streamlit.
    """
    output_md = []
    
    output_md.append("# Relatório de Comparação Histórica Mensal")
    output_md.append("## Resumo Comparativo de Gastos e Economia (50-30-20)")
    output_md.append("---")
    
    # Criar DataFrame com formatação de moeda para Streamlit
    df = df_resumo_historico.copy()
    colunas_moeda = ['Salário Líquido', 'Total Gasto', 'Folga/Déficit Necessidades', 'Folga/Déficit Lazer']
    
    for col in colunas_moeda:
        df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}")
        
    # Adicionar o DataFrame na saída (o Streamlit fará o resto)
    output_md.append("O DataFrame a seguir será exibido pelo Streamlit usando `st.dataframe`:")
    
    # Retornamos o DataFrame em vez da string Markdown da tabela,
    # pois o st.dataframe é melhor para exibir tabelas complexas no Streamlit.
    return df, safe_text("\nNota: Valores positivos em 'Folga' indicam que você economizou. Valores negativos indicam déficit (ultrapassagem).")