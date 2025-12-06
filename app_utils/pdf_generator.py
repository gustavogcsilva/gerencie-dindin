from fpdf import FPDF
import pandas as pd
import io
# from .orcamento_class import Orcamento 


def safe_text(text):
    """
    Garante que o objeto seja uma string (str) e o prepara para o FPDF usando latin-1,
    ignorando erros e tratando objetos binários (bytes/bytearray) de forma robusta.
    """
    # 1. Converte qualquer objeto de entrada para string (str) de maneira segura
    if isinstance(text, (bytes, bytearray)):
        try:
            # Tenta decodificar o objeto binário para string usando latin-1 (se vier do FPDF)
            text = text.decode('latin-1', 'ignore')
        except:
            # Se a decodificação falhar (ex: objeto binário não tem encoding latin-1),
            # força a conversão para string.
            text = str(text)
    else:
        # Se não for binário, apenas garante que é uma string
        text = str(text)

    # 2. Agora que temos certeza de que é uma string (str), aplicamos a limpeza
    # codificando e decodificando de volta para 'str' (latin-1) para o FPDF.
    try:
        # Codifica para bytes (latin-1) e depois decodifica de volta para string (str)
        return text.encode('latin-1', 'ignore').decode('latin-1')
    except:
        return text # Em caso de falha, retorna a string já convertida.


def criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento) -> bytes:
    """
    Gera o PDF do relatório 50-30-20, usando codificação estável (latin-1).
    Retorna os bytes do PDF (bytestring).
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # --- Títulos e Informações do Usuário ---
    pdf.cell(0, 10, safe_text(f"Gerencie Dindin: Relatorio {orcamento_obj.mes}"), 0, 1, "C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 5, safe_text(f"Gerado para: {user_name}"), 0, 1, "C")
    pdf.cell(0, 5, safe_text(f"Frequencia de Pagamento: {frequencia_pagamento}"), 0, 1, "C")
    pdf.ln(5)

    # --- Resumo Geral e Saldo ---
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 7, safe_text("Resumo Geral e Saldo"), 1, 1, "L", 1)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 5, safe_text("Salario Liquido:"), 1, 0)
    pdf.cell(30, 5, f"R$ {orcamento_obj.salario_liquido:,.2f}", 1, 1, "R")
    
    pdf.cell(60, 5, safe_text("Total Gasto/Alocado:"), 1, 0)
    pdf.cell(30, 5, f"R$ {totais_reais['total_gasto_real']:,.2f}", 1, 1, "R")
    
    # Saldo Final (Destacado)
    if saldo < 0:
        pdf.set_text_color(255, 0, 0)
        pdf.set_font("Arial", "B", 10)
    else:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 10)
        
    pdf.cell(60, 6, safe_text("SALDO FINAL (Salario - Total Gasto)"), 1, 0, "L", 0)
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
        pdf.cell(0, 8, safe_text("Resumo de Pagamento Quinzenal"), 1, 1, "C", 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 6, safe_text("Salario Liquido Mensal:"), 1, 0, "L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 6, f"R$ {salario_liquido_mensal:,.2f}", 1, 1, "R")
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 6, safe_text("Valor Recebido por Quinzena:"), 1, 0, "L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 6, f"R$ {valor_recebido_quinzenal:,.2f}", 1, 1, "R")
        
        pdf.ln(2)
        
        # Tabela Limite de Gastos Sugerido
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(255, 230, 200) 
        pdf.cell(0, 6, safe_text("Limite TOTAL Sugerido para Gastos (Necessidades + Lazer)"), 1, 1, "C", 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, safe_text("Quinzena"), 1, 0, "L")
        pdf.cell(65, 6, safe_text("Base de Calculo"), 1, 0, "C")
        pdf.cell(65, 6, safe_text("Limite Maximo de Gasto"), 1, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        
        pdf.cell(60, 6, safe_text("1a Quinzena"), 1, 0, "L")
        pdf.cell(65, 6, safe_text("60% dos Limites Mensais"), 1, 0, "C")
        pdf.cell(65, 6, f"R$ {limite_gasto_primeira_quize:,.2f}", 1, 1, "R")
        
        pdf.cell(60, 6, safe_text("2a Quinzena"), 1, 0, "L")
        pdf.cell(65, 6, safe_text("40% dos Limites Mensais"), 1, 0, "C")
        pdf.cell(65, 6, f"R$ {limite_gasto_segunda_quize:,.2f}", 1, 1, "R")

        pdf.ln(5)

        # DETALHE DA DIVISÃO POR CATEGORIA (50-30-20)
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(255, 230, 200) 
        pdf.cell(0, 7, safe_text("Detalhamento da Divisao por Categoria (60% / 40%)"), 1, 1, "C", 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, safe_text("Categoria"), 1, 0, "L")
        pdf.cell(40, 6, safe_text("1a Parcela (60%)"), 1, 0, "R")
        pdf.cell(40, 6, safe_text("2a Parcela (40%)"), 1, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        
        pdf.cell(60, 6, safe_text("Necessidades (50%)"), 1, 0, "L")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Fixas - Início (60%)']:,.2f}", 1, 0, "R")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Fixas - Meio (40%)']:,.2f}", 1, 1, "R")
        
        pdf.cell(60, 6, safe_text("Desejos/Lazer (30%)"), 1, 0, "L")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Lazer - Início (60%)']:,.2f}", 1, 0, "R")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Lazer - Meio (40%)']:,.2f}", 1, 1, "R")
        
        pdf.ln(7)
    # --- FIM DA DIVISÃO QUINZENAL NO PDF ---


    # Função auxiliar para formatar a seção
    def adicionar_secao(titulo, total_real, limite, despesas, cor_limite):
        pdf.set_fill_color(*cor_limite)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 7, safe_text(f"{titulo} (Limite: R$ {limite:,.2f})"), 1, 1, "L", 1)
        pdf.set_font("Arial", "", 10)
        
        # Tabela de Despesas
        pdf.cell(60, 6, safe_text("Item"), 1, 0, "L", 0)
        pdf.cell(30, 6, safe_text("Valor"), 1, 1, "R", 0)
        
        for item, valor in sorted(despesas.items()):
            # A correção do erro está aqui: o tratamento de codificação é feito pela safe_text
            item_safe = safe_text(item)
            
            pdf.cell(60, 6, item_safe, 1, 0, "L", 0) 
            pdf.cell(30, 6, f"R$ {valor:,.2f}", 1, 1, "R", 0)
        
        # Linha do Total
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, safe_text("TOTAL GASTO"), 1, 0, "L", 0)
        pdf.cell(30, 6, f"R$ {total_real:,.2f}", 1, 1, "R", 0)
        pdf.ln(7)

        # AVISO DE LIMITE
        if total_real > limite:
            pdf.set_fill_color(255, 192, 203)
            pdf.set_text_color(255, 0, 0)
            ultrapassado = total_real - limite
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, safe_text(f"ATENCAO: Voce ULTRAPASSOU o limite em R$ {ultrapassado:,.2f}!"), 1, 1, "C", 1)
        elif total_real < limite:
            pdf.set_text_color(0, 128, 0)
            economizado = limite - total_real
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, safe_text(f"Parabens! Voce economizou R$ {economizado:,.2f} nesta categoria."), 0, 1, "C", 0)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # Chamadas finais
    adicionar_secao("50% Necessidades Fixas (Despesas Fixas)", totais_reais['total_fixas'], limites.get('Necessidades (50%)', 0.0), orcamento_obj.despesas_fixas, (144, 238, 144))
    adicionar_secao("30% Desejos e Lazer (Despesas Variaveis)", totais_reais['total_lazer'], limites.get('Desejos/Lazer (30%)', 0.0), orcamento_obj.gastos_lazer, (173, 216, 230))
    
    # 20% Poupança
    pdf.set_fill_color(255, 255, 153)
    pdf.set_font("Arial", "B", 12)
    meta_poupanca = limites.get('Poupança/Investimento (20%)', 0.0)
    pdf.cell(0, 7, safe_text(f"20% Poupanca/Investimento (Meta: R$ {meta_poupanca:,.2f})"), 1, 1, "L", 1)
    total_poupanca = totais_reais['total_poupanca']
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, safe_text("Valor Destinado"), 1, 0, "L", 0)
    pdf.cell(30, 6, f"R$ {total_poupanca:,.2f}", 1, 1, "R", 0)

    if total_poupanca < meta_poupanca:
        pdf.set_text_color(255, 0, 0)
        falta = meta_poupanca - total_poupanca
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, safe_text(f"Atencao: Voce esta R$ {falta:,.2f} abaixo da meta de 20%!"), 1, 1, "C", 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # SAÍDA FINAL SEGURA COM BYTES PURAS (latin-1)
    pdf_output = pdf.output(dest='S')
    return pdf_output.encode('latin-1')


def criar_pdf_relatorio_historico(df_resumo_historico) -> bytes:
    """
    Gera um PDF contendo o resumo da comparação histórica de meses.
    Retorna os bytes do PDF (bytestring) codificado em 'latin-1'.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Títulos e textos da função histórica
    pdf.cell(0, 10, safe_text("Relatorio de Comparacao Historica Mensal"), 0, 1, "C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, safe_text("Resumo Comparativo de Gastos e Economia (50-30-20)"), 0, 1, "L")
    pdf.ln(2)
    
    col_widths = [25, 35, 30, 30, 30]
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(col_widths[0], 7, safe_text("Mes"), 1, 0, "C", 1)
    pdf.cell(col_widths[1], 7, safe_text("Salario Liquido"), 1, 0, "R", 1)
    pdf.cell(col_widths[2], 7, safe_text("Total Gasto"), 1, 0, "R", 1)
    pdf.cell(col_widths[3], 7, safe_text("Folga Necessidades"), 1, 0, "R", 1)
    pdf.cell(col_widths[4], 7, safe_text("Folga Lazer"), 1, 1, "R", 1)
    
    pdf.set_font("Arial", "", 9)
    for index, row in df_resumo_historico.iterrows():
        # Usando safe_text para garantir que 'index' (nome do mês) seja string tratada
        mes = safe_text(index) 
        salario = f"R$ {row['Salário Líquido']:,.2f}"
        gasto = f"R$ {row['Total Gasto']:,.2f}"
        folga_fixas = f"R$ {row['Folga/Déficit Necessidades']:,.2f}"
        folga_lazer = f"R$ {row['Folga/Déficit Lazer']:,.2f}"
        
        # Lógica de cores para Folga Necessidades
        if row['Folga/Déficit Necessidades'] < 0: pdf.set_text_color(255, 0, 0)
        elif row['Folga/Déficit Necessidades'] > 0: pdf.set_text_color(0, 128, 0)
        else: pdf.set_text_color(0, 0, 0)
            
        pdf.cell(col_widths[0], 6, mes, 1, 0, "L", 0)
        pdf.cell(col_widths[1], 6, salario, 1, 0, "R", 0)
        pdf.cell(col_widths[2], 6, gasto, 1, 0, "R", 0)
        pdf.cell(col_widths[3], 6, folga_fixas, 1, 0, "R", 0)
        
        # Lógica de cores para Folga Lazer
        if row['Folga/Déficit Lazer'] < 0: pdf.set_text_color(255, 0, 0)
        elif row['Folga/Déficit Lazer'] > 0: pdf.set_text_color(0, 128, 0)
        else: pdf.set_text_color(0, 0, 0)
            
        pdf.cell(col_widths[4], 6, folga_lazer, 1, 1, "R", 0)
        
        pdf.set_text_color(0, 0, 0) 
        
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 4, safe_text("Nota: Valores positivos em 'Folga' indicam que voce gastou menos que o limite sugerido (economia). Valores negativos indicam deficit (ultrapassagem)."), 0, "L")

    # SAÍDA FINAL SEGURA COM BYTES PURAS (latin-1)
    pdf_output = pdf.output(dest='S')
    return pdf_output.encode('latin-1')