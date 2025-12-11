from fpdf import FPDF

import pandas as pd
import io


try:
    import safe_text
except ImportError:

    def safe_text(text):
        return text 
    print("Aviso: Módulo safe_text não encontrado. Usando função dummy.")


def _configurar_pdf(pdf: FPDF, title: str, user_name: str, frequencia_pagamento: str):
    """Configura o cabeçalho inicial do PDF."""
    pdf.add_page()
    
    # Define a fonte para uma que suporte português (Se FPDF2 estiver em uso, Arial pode funcionar)
    pdf.set_font("Arial", "B", 16)
    
    pdf.cell(0, 10, safe_text(title), 0, 1, "C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 5, safe_text(f"Gerado para: {user_name}"), 0, 1, "C")
    pdf.cell(0, 5, safe_text(f"Frequencia de Pagamento: {frequencia_pagamento}"), 0, 1, "C")
    pdf.ln(5)


def _adicionar_secao_pdf(pdf: FPDF, titulo: str, total_real: float, limite: float, despesas: dict, cor_limite: tuple):
    """Função auxiliar para adicionar uma seção de categoria ao PDF."""
    pdf.set_fill_color(*cor_limite)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, safe_text(f"{titulo} (Limite: R$ {limite:,.2f})"), 1, 1, "L", 1)
    pdf.set_font("Arial", "", 10)
    
    # Tabela de Despesas
    pdf.cell(60, 6, safe_text("Item"), 1, 0, "L", 0)
    pdf.cell(30, 6, safe_text("Valor"), 1, 1, "R", 0)
    
    for item, valor in sorted(despesas.items()):
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
        pdf.cell(0, 6, safe_text(f"ATENÇÃO: Você ULTRAPASSOU o limite em R$ {ultrapassado:,.2f}!"), 1, 1, "C", 1)
    elif total_real < limite:
        pdf.set_text_color(0, 128, 0)
        economizado = limite - total_real
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, safe_text(f"Parabéns! Você economizou R$ {economizado:,.2f} nesta categoria."), 0, 1, "C", 0)
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)


def _saida_pdf_segura(pdf: FPDF) -> bytes:
    """Garante que a saída do PDF seja sempre em bytestring."""
    pdf_output = pdf.output(dest='S')
    
    if isinstance(pdf_output, str):
        # FPDF/fpdf2 em modo 'S' pode retornar str (latin-1), precisa de encode
        return pdf_output.encode('latin-1') 
    
    # Garante que seja bytes, caso o fpdf retorne diretamente bytes
    return bytes(pdf_output) if isinstance(pdf_output, (bytes, bytearray)) else b''


def criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento) -> bytes:
    """Gera o PDF do relatório 50-30-20."""
    pdf = FPDF()
    _configurar_pdf(pdf, f"Gerencie Dindin: Relatório {orcamento_obj.mes}", user_name, frequencia_pagamento)

    # --- Resumo Geral e Saldo ---
    # ... (Bloco de Resumo Geral e Saldo idêntico ao original, apenas com safe_text mantido/ajustado) ...
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 7, safe_text("Resumo Geral e Saldo"), 1, 1, "L", 1)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 5, safe_text("Salário Líquido:"), 1, 0)
    pdf.cell(30, 5, f"R$ {orcamento_obj.salario_liquido:,.2f}", 1, 1, "R")
    
    pdf.cell(60, 5, safe_text("Total Gasto/Alocado:"), 1, 0)
    pdf.cell(30, 5, f"R$ {totais_reais['total_gasto_real']:,.2f}", 1, 1, "R")
    
    if saldo < 0:
        pdf.set_text_color(255, 0, 0)
        pdf.set_font("Arial", "B", 10)
    else:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 10)
        
    pdf.cell(60, 6, safe_text("SALDO FINAL (Salário - Total Gasto)"), 1, 0, "L", 0)
    pdf.cell(30, 6, f"R$ {saldo:,.2f}", 1, 1, "R", 0)
    pdf.set_text_color(0, 0, 0) 
    pdf.ln(5)
    # ... (Fim do Bloco de Resumo Geral e Saldo) ...

    # --- DIVISÃO QUINZENAL NO PDF ---
    # ... (Bloco Quinzenal idêntico ao original, apenas com safe_text mantido/ajustado) ...
    if frequencia_pagamento == 'Quinzenal':
        
        divisao_quinzenal = orcamento_obj.calcular_divisao_quinzenal(limites) 
        salario_liquido_mensal = orcamento_obj.salario_liquido
        
        limite_gasto_primeira_quize = divisao_quinzenal['Fixas - Início (60%)'] + divisao_quinzenal['Lazer - Início (60%)']
        limite_gasto_segunda_quize = divisao_quinzenal['Fixas - Meio (40%)'] + divisao_quinzenal['Lazer - Meio (40%)']
        
        
        # RESUMO FINANCEIRO QUINZENAL
        pdf.set_font("Arial", "B", 13)
        pdf.set_fill_color(200, 220, 255) 
        pdf.cell(0, 8, safe_text("Resumo de Pagamento Quinzenal"), 1, 1, "C", 1)
        
        # ... (Tabelas Quinzenais) ...
        pdf.set_font("Arial", "B", 10)
        pdf.cell(95, 6, safe_text("Salário Líquido Mensal:"), 1, 0, "L")
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 6, f"R$ {salario_liquido_mensal:,.2f}", 1, 1, "R")
        
        pdf.ln(2)
        
        # Tabela Limite de Gastos Sugerido
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(255, 230, 200) 
        pdf.cell(0, 6, safe_text("Limite TOTAL Sugerido para Gastos (Necessidades + Lazer)"), 1, 1, "C", 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, safe_text("Quinzena"), 1, 0, "L")
        pdf.cell(65, 6, safe_text("Base de Cálculo"), 1, 0, "C")
        pdf.cell(65, 6, safe_text("Limite Máximo de Gasto"), 1, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        
        pdf.cell(60, 6, safe_text("1ª Quinzena"), 1, 0, "L")
        pdf.cell(65, 6, safe_text("60% dos Limites Mensais"), 1, 0, "C")
        pdf.cell(65, 6, f"R$ {limite_gasto_primeira_quize:,.2f}", 1, 1, "R")
        
        pdf.cell(60, 6, safe_text("2ª Quinzena"), 1, 0, "L")
        pdf.cell(65, 6, safe_text("40% dos Limites Mensais"), 1, 0, "C")
        pdf.cell(65, 6, f"R$ {limite_gasto_segunda_quize:,.2f}", 1, 1, "R")

        pdf.ln(5)

        # DETALHE DA DIVISÃO POR CATEGORIA (50-30-20)
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(255, 230, 200) 
        pdf.cell(0, 7, safe_text("Detalhamento da Divisão por Categoria (60% / 40%)"), 1, 1, "C", 1)
        
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, safe_text("Categoria"), 1, 0, "L")
        pdf.cell(40, 6, safe_text("1ª Parcela (60%)"), 1, 0, "R")
        pdf.cell(40, 6, safe_text("2ª Parcela (40%)"), 1, 1, "R")
        
        pdf.set_font("Arial", "", 10)
        
        pdf.cell(60, 6, safe_text("Necessidades (50%)"), 1, 0, "L")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Fixas - Início (60%)']:,.2f}", 1, 0, "R")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Fixas - Meio (40%)']:,.2f}", 1, 1, "R")
        
        pdf.cell(60, 6, safe_text("Desejos/Lazer (30%)"), 1, 0, "L")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Lazer - Início (60%)']:,.2f}", 1, 0, "R")
        pdf.cell(40, 6, f"R$ {divisao_quinzenal['Lazer - Meio (40%)']:,.2f}", 1, 1, "R")
        
        pdf.ln(7)
    # --- FIM DA DIVISÃO QUINZENAL NO PDF ---
    
    # Chamadas para Funções Auxiliares
    _adicionar_secao_pdf(pdf, "50% Necessidades Fixas (Despesas Fixas)", totais_reais['total_fixas'], limites.get('Necessidades (50%)', 0.0), orcamento_obj.despesas_fixas, (144, 238, 144))
    _adicionar_secao_pdf(pdf, "30% Desejos e Lazer (Despesas Variáveis)", totais_reais['total_lazer'], limites.get('Desejos/Lazer (30%)', 0.0), orcamento_obj.gastos_lazer, (173, 216, 230))
    
    # 20% Poupança
    pdf.set_fill_color(255, 255, 153)
    pdf.set_font("Arial", "B", 12)
    meta_poupanca = limites.get('Poupança/Investimento (20%)', 0.0)
    pdf.cell(0, 7, safe_text(f"20% Poupança/Investimento (Meta: R$ {meta_poupanca:,.2f})"), 1, 1, "L", 1)
    total_poupanca = totais_reais['total_poupanca']
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 6, safe_text("Valor Destinado"), 1, 0, "L", 0)
    pdf.cell(30, 6, f"R$ {total_poupanca:,.2f}", 1, 1, "R", 0)

    if total_poupanca < meta_poupanca:
        pdf.set_text_color(255, 0, 0)
        falta = meta_poupanca - total_poupanca
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, safe_text(f"Atenção: Você está R$ {falta:,.2f} abaixo da meta de 20%!"), 1, 1, "C", 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    return _saida_pdf_segura(pdf) 


def criar_pdf_relatorio_historico(df_resumo_historico) -> bytes:
    """Gera o resumo da comparação histórica em PDF."""
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, safe_text("Relatório de Comparação Histórica Mensal"), 0, 1, "C")
    pdf.ln(5)
    
    # ... (O restante do código de histórico pode ser mantido, apenas corrigindo a acentuação se necessário) ...
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, safe_text("Resumo Comparativo de Gastos e Economia (50-30-20)"), 0, 1, "L")
    pdf.ln(2)
    
    col_widths = [25, 35, 30, 30, 30]
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(col_widths[0], 7, safe_text("Mês"), 1, 0, "C", 1)
    pdf.cell(col_widths[1], 7, safe_text("Salário Líquido"), 1, 0, "R", 1)
    pdf.cell(col_widths[2], 7, safe_text("Total Gasto"), 1, 0, "R", 1)
    pdf.cell(col_widths[3], 7, safe_text("Folga Necessidades"), 1, 0, "R", 1)
    pdf.cell(col_widths[4], 7, safe_text("Folga Lazer"), 1, 1, "R", 1)
    
    pdf.set_font("Arial", "", 9)
    for index, row in df_resumo_historico.iterrows():
        mes = safe_text(index) 
        salario = f"R$ {row['Salário Líquido']:,.2f}"
        gasto = f"R$ {row['Total Gasto']:,.2f}"
        folga_fixas = f"R$ {row['Folga/Déficit Necessidades']:,.2f}"
        folga_lazer = f"R$ {row['Folga/Déficit Lazer']:,.2f}"
        
        # Lógica de cores para Folga Necessidades
        # ... (Mantém a lógica de cores) ...
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
    pdf.multi_cell(0, 4, safe_text("Nota: Valores positivos em 'Folga' indicam que você gastou menos que o limite sugerido (economia). Valores negativos indicam déficit (ultrapassagem)."), 0, "L")

    return _saida_pdf_segura(pdf)