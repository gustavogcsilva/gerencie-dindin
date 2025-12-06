from fpdf import FPDF
import pandas as pd
import io
from .orcamento_class import Orcamento 


def criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento):
    """Gera o PDF do relatório 50-30-20, usando a codificação estável (latin-1)."""
    pdf = FPDF()
    pdf.add_page()
    
    # ⚠️ Ajuste a fonte de volta para Arial.
    pdf.set_font("Arial", "B", 16)
    
    # Título Principal
    # Usamos strings normais. A codificação é tratada no pdf.output().
    pdf.cell(0, 10, f"Gerencie Dindin: Relatório {orcamento_obj.mes}", 0, 1, "C")
    
    # Informações do Usuário
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 5, f"Gerado para: {user_name}", 0, 1, "C")
    pdf.cell(0, 5, f"Frequência de Pagamento: {frequencia_pagamento}", 0, 1, "C")
    pdf.ln(5)

    # Resumo Geral e Saldo
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 7, "Resumo Geral e Saldo", 1, 1, "L", 1)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 5, "Salário Líquido:", 1, 0)
    pdf.cell(30, 5, f"R$ {orcamento_obj.salario_liquido:,.2f}", 1, 1, "R")
    
    pdf.cell(60, 5, "Total Gasto/Alocado:", 1, 0)
    pdf.cell(30, 5, f"R$ {totais_reais['total_gasto_real']:,.2f}", 1, 1, "R")
    
    # Saldo Final (Destacado)
    if saldo < 0:
        pdf.set_text_color(255, 0, 0)
        pdf.set_font("Arial", "B", 10)
    else:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 10)
        
    pdf.cell(60, 6, "SALDO FINAL (Salário - Total Gasto)", 1, 0, "L", 0)
    pdf.cell(30, 6, f"R$ {saldo:,.2f}", 1, 1, "R", 0)
    
    pdf.set_text_color(0, 0, 0) 
    pdf.ln(5)

    # --- DIVISÃO QUINZENAL NO PDF (Apenas se Quinzenal) ---
    if frequencia_pagamento == 'Quinzenal':
        
        divisao_quinzenal = orcamento_obj.calcular_divisao_quinzenal(limites)
        
        salario_liquido_mensal = orcamento_obj.salario_liquido
        valor_recebido_quinzenal = salario_liquido_mensal / 2
        
        limite_gasto_primeira_quize = divisao_quinzenal['Fixas - Início (60%)'] + divisao_quinzenal['Lazer - Início (60%)']
        limite_gasto_segunda_quize = divisao_quinzenal['Fixas - Meio (40%)'] + divisao_quinzenal['Lazer - Meio (40%)']
        
        
        # RESUMO FINANCEIRO QUINZENAL
        pdf.set_font("Arial", "B", 13)
        pdf.set_fill_color(200, 220, 255) 
        pdf.cell(0, 8, "Resumo de Pagamento Quinzenal", 1, 1, "C", 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 6, "Salário Líquido Mensal:", 1, 0, "L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 6, f"R$ {salario_liquido_mensal:,.2f}", 1, 1, "R")
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 6, "Valor Recebido por Quinzena:", 1, 0, "L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 6, f"R$ {valor_recebido_quinzenal:,.2f}", 1, 1, "R")
        
        pdf.ln(2)
        
        # Tabela Limite de Gastos Sugerido
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(255, 230, 200) 
        pdf.cell(0, 6, "Limite TOTAL Sugerido para Gastos (Necessidades + Lazer)", 1, 1, "C", 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, "Quinzena", 1, 0, "L")
        pdf.cell(65, 6, "Base de Cálculo", 1, 0, "C")
        pdf.cell(65, 6, "Limite Máximo de Gasto", 1, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        
        pdf.cell(60, 6, "1ª Quinzena", 1, 0, "L")
        pdf.cell(65, 6, "60% dos Limites Mensais", 1, 0, "C")
        pdf.cell(65, 6, f"R$ {limite_gasto_primeira_quize:,.2f}", 1, 1, "R")
        
        pdf.cell(60, 6, "2ª Quinzena", 1, 0, "L")
        pdf.cell(65, 6, "40% dos Limites Mensais", 1, 0, "C")
        pdf.cell(65, 6, f"R$ {limite_gasto_segunda_quize:,.2f}", 1, 1, "R")

        pdf.ln(5)

        # DETALHE DA DIVISÃO POR CATEGORIA (50-30-20)
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(255, 230, 200) 
        pdf.cell(0, 7, "Detalhamento da Divisão por Categoria (60% / 40%)", 1, 1, "C", 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, "Categoria", 1, 0, "L")
        pdf.cell(40, 6, "1ª Parcela (60%)", 1, 0, "R")
        pdf.cell(40, 6, "2ª Parcela (40%)", 1, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        
        pdf.cell(60, 6, "Necessidades (50%)", 1, 0, "L")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Fixas - Início (60%)']:,.2f}", 1, 0, "R")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Fixas - Meio (40%)']:,.2f}", 1, 1, "R")
        
        pdf.cell(60, 6, "Desejos/Lazer (30%)", 1, 0, "L")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Lazer - Início (60%)']:,.2f}", 1, 0, "R")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Lazer - Meio (40%)']:,.2f}", 1, 1, "R")
        
        pdf.ln(7)
    # --- FIM DA DIVISÃO QUINZENAL NO PDF ---


    # Função auxiliar para formatar a seção
    def adicionar_secao(titulo, total_real, limite, despesas, cor_limite):
        pdf.set_fill_color(*cor_limite)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, f"{titulo} (Limite: R$ {limite:,.2f})", 1, 1, "L", 1)
        pdf.set_font("Arial", "", 10)
        
        # Tabela de Despesas
        pdf.cell(60, 6, "Item", 1, 0, "L", 0)
        pdf.cell(30, 6, "Valor", 1, 1, "R", 0)
        
        for item, valor in sorted(despesas.items()):
            try:
                item_safe = item.encode('latin-1', 'ignore').decode('latin-1')
            except Exception:
                item_safe = item
                
            pdf.cell(60, 6, item_safe, 1, 0, "L", 0) 
            pdf.cell(30, 6, f"R$ {valor:,.2f}", 1, 1, "R", 0)
        
        # Linha do Total
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, "TOTAL GASTO", 1, 0, "L", 0)
        pdf.cell(30, 6, f"R$ {total_real:,.2f}", 1, 1, "R", 0)
        pdf.ln(7)

        # AVISO DE LIMITE
        if total_real > limite:
            pdf.set_fill_color(255, 192, 203)
            pdf.set_text_color(255, 0, 0)
            ultrapassado = total_real - limite
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, f"ATENCAO: Voce ULTRAPASSOU o limite em R$ {ultrapassado:,.2f}!", 1, 1, "C", 1)
        elif total_real < limite:
            pdf.set_text_color(0, 128, 0)
            economizado = limite - total_real
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, f"Parabens! Voce economizou R$ {economizado:,.2f} nesta categoria.", 0, 1, "C", 0)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # Chamadas finais
    adicionar_secao("50% Necessidades Fixas (Despesas Fixas)", totais_reais['total_fixas'], limites.get('Necessidades (50%)', 0.0), orcamento_obj.despesas_fixas, (144, 238, 144))
    adicionar_secao("30% Desejos e Lazer (Despesas Variáveis)", totais_reais['total_lazer'], limites.get('Desejos/Lazer (30%)', 0.0), orcamento_obj.gastos_lazer, (173, 216, 230))
    
    # 20% Poupança
    pdf.set_fill_color(255, 255, 153)
    pdf.set_font("Arial", "B", 12)
    meta_poupanca = limites.get('Poupança/Investimento (20%)', 0.0)
    pdf.cell(0, 7, f"20% Poupança/Investimento (Meta: R$ {meta_poupanca:,.2f})", 1, 1, "L", 1)
    total_poupanca = totais_reais['total_poupanca']
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, "Valor Destinado", 1, 0, "L", 0)
    pdf.cell(30, 6, f"R$ {total_poupanca:,.2f}", 1, 1, "R", 0)

    if total_poupanca < meta_poupanca:
        pdf.set_text_color(255, 0, 0)
        falta = meta_poupanca - total_poupanca
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, f"Atencao: Voce esta R$ {falta:,.2f} abaixo da meta de 20%."), 1, 1, "C", 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    return bytes(pdf.output(dest='S').encode('latin-1'))


def criar_pdf_relatorio_historico(df_resumo_historico):
    """Gera um PDF contendo o resumo da comparação histórica de meses."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    pdf.cell(0, 10, "Relatório de Comparação Histórica Mensal", 0, 1, "C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Resumo Comparativo de Gastos e Economia (50-30-20)", 0, 1, "L")
    pdf.ln(2)
    
    # ... (Restante do código da função de relatório histórico) ...
    # É recomendável aplicar o encoding latin-1 nas strings da tabela histórica também.
    
    col_widths = [25, 35, 30, 30, 30]
    
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(col_widths[0], 7, "Mes", 1, 0, "C", 1)
    pdf.cell(col_widths[1], 7, "Salario Liquido", 1, 0, "R", 1)
    pdf.cell(col_widths[2], 7, "Total Gasto", 1, 0, "R", 1)
    pdf.cell(col_widths[3], 7, "Folga Necessidades", 1, 0, "R", 1)
    pdf.cell(col_widths[4], 7, "Folga Lazer", 1, 1, "R", 1)
    
    pdf.set_font("Arial", "", 9)
    for index, row in df_resumo_historico.iterrows():
        mes = index
        # Assumindo que os nomes dos meses não têm acentos problemáticos, mas codificando os valores.
        salario = f"R$ {row['Salário Líquido']:,.2f}"
        gasto = f"R$ {row['Total Gasto']:,.2f}"
        folga_fixas = f"R$ {row['Folga/Déficit Necessidades']:,.2f}"
        folga_lazer = f"R$ {row['Folga/Déficit Lazer']:,.2f}"
        
        if row['Folga/Déficit Necessidades'] < 0: pdf.set_text_color(255, 0, 0)
        elif row['Folga/Déficit Necessidades'] > 0: pdf.set_text_color(0, 128, 0)
        else: pdf.set_text_color(0, 0, 0)
            
        pdf.cell(col_widths[0], 6, mes, 1, 0, "L", 0)
        pdf.cell(col_widths[1], 6, salario, 1, 0, "R", 0)
        pdf.cell(col_widths[2], 6, gasto, 1, 0, "R", 0)
        pdf.cell(col_widths[3], 6, folga_fixas, 1, 0, "R", 0)
        
        if row['Folga/Déficit Lazer'] < 0: pdf.set_text_color(255, 0, 0)
        elif row['Folga/Déficit Lazer'] > 0: pdf.set_text_color(0, 128, 0)
        else: pdf.set_text_color(0, 0, 0)
            
        pdf.cell(col_widths[4], 6, folga_lazer, 1, 1, "R", 0)
        
        pdf.set_text_color(0, 0, 0) 
        
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 4, "Nota: Valores positivos em 'Folga' indicam que voce gastou menos que o limite sugerido (economia). Valores negativos indicam deficit (ultrapassagem).", 0, "L")
    
    return bytes(pdf.output(dest='S').encode('latin-1')) # 🎯 CORREÇÃO APLICADA AQUI TAMBÉM