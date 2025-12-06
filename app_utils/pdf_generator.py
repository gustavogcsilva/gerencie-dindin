
from fpdf import FPDF
import pandas as pd
import io
import unicodedata 


def remove_accents(input_str):
    """Remove acentos e caracteres especiais para compatibilidade com FPDF."""
    if not isinstance(input_str, str):
        return str(input_str)
    return input_str.encode('latin-1', 'ignore').decode('latin-1') 
    # Usamos latin-1 apenas para limpar, e a fonte cuida do resto


def criar_pdf_relatorio(orcamento_obj, limites, totais_reais, saldo, user_name, frequencia_pagamento):
    """Gera o PDF do relatório 50-30-20, usando uma fonte compatível com UTF-8."""
    pdf = FPDF()
    pdf.add_page()
    
    pdf.add_font("DejaVuSansMono", "", "DejaVuSansMono.ttf", uni=True) 
    pdf.set_font("DejaVuSansMono", "", 16)
    
    # Título Principal
    pdf.cell(0, 10, f"Gerencie Dindin: Relatório {orcamento_obj.mes}", 0, 1, "C") 
    
    # Informações do Usuário
    pdf.set_font("DejaVuSansMono", "", 12)
    pdf.cell(0, 5, f"Gerado para: {user_name}", 0, 1, "C")
    pdf.cell(0, 5, f"Frequência de Pagamento: {frequencia_pagamento}", 0, 1, "C")
    pdf.ln(5)

    # Resumo Geral e Saldo
    pdf.set_font("DejaVuSansMono", "B", 12)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(0, 7, "Resumo Geral e Saldo", 1, 1, "L", 1)
    
    pdf.set_font("DejaVuSansMono", "", 10)
    pdf.cell(60, 5, "Salário Líquido:", 1, 0)
    pdf.cell(30, 5, f"R$ {orcamento_obj.salario_liquido:,.2f}", 1, 1, "R")
    
    pdf.cell(60, 5, "Total Gasto/Alocado:", 1, 0)
    pdf.cell(30, 5, f"R$ {totais_reais['total_gasto_real']:,.2f}", 1, 1, "R")
    
    # Saldo Final (Destacado)
    if saldo < 0:
        pdf.set_text_color(255, 0, 0)
        pdf.set_font("DejaVuSansMono", "B", 10)
    else:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVuSansMono", "B", 10)
        
    pdf.cell(60, 6, "SALDO FINAL (Salário - Total Gasto)", 1, 0, "L", 0)
    pdf.cell(30, 6, f"R$ {saldo:,.2f}", 1, 1, "R", 0)
    
    pdf.set_text_color(0, 0, 0) 
    pdf.ln(5)

    # --- DIVISÃO QUINZENAL NO PDF (Apenas se Quinzenal) ---
    if frequencia_pagamento == 'Quinzenal':
        
        # O objeto Orcamento precisa ser importado e ter o método calcular_divisao_quinzenal
        from .orcamento_class import Orcamento 
        
        divisao_quinzenal = Orcamento.calcular_divisao_quinzenal(orcamento_obj, limites)
        
        salario_liquido_mensal = orcamento_obj.salario_liquido
        valor_recebido_quinzenal = salario_liquido_mensal / 2
        
        limite_gasto_primeira_quize = divisao_quinzenal['Fixas - Início (60%)'] + divisao_quinzenal['Lazer - Início (60%)']
        limite_gasto_segunda_quize = divisao_quinzenal['Fixas - Meio (40%)'] + divisao_quinzenal['Lazer - Meio (40%)']
        
        
        # RESUMO FINANCEIRO QUINZENAL
        pdf.set_font("DejaVuSansMono", "B", 13)
        pdf.set_fill_color(200, 220, 255) 
        pdf.cell(0, 8, "Resumo de Pagamento Quinzenal", 1, 1, "C", 1)
        
        pdf.set_font("DejaVuSansMono", "B", 10)
        pdf.cell(95, 6, "Salário Líquido Mensal:", 1, 0, "L")
        pdf.set_font("DejaVuSansMono", "", 10)
        pdf.cell(95, 6, f"R$ {salario_liquido_mensal:,.2f}", 1, 1, "R")
        
        pdf.set_font("DejaVuSansMono", "B", 10)
        pdf.cell(95, 6, "Valor Recebido por Quinzena:", 1, 0, "L")
        pdf.set_font("DejaVuSansMono", "", 10)
        pdf.cell(95, 6, f"R$ {valor_recebido_quinzenal:,.2f}", 1, 1, "R")
        
        pdf.ln(2)
        
        # Tabela Limite de Gastos Sugerido
        pdf.set_font("DejaVuSansMono", "B", 11)
        pdf.set_fill_color(255, 230, 200) 
        pdf.cell(0, 6, "Limite TOTAL Sugerido para Gastos (Necessidades + Lazer)", 1, 1, "C", 1)
        
        pdf.set_font("DejaVuSansMono", "B", 10)
        pdf.cell(60, 6, "Quinzena", 1, 0, "L")
        pdf.cell(65, 6, "Base de Cálculo", 1, 0, "C")
        pdf.cell(65, 6, "Limite Máximo de Gasto", 1, 1, "R")
        
        pdf.set_font("DejaVuSansMono", "", 10)
        
        pdf.cell(60, 6, "1ª Quinzena", 1, 0, "L")
        pdf.cell(65, 6, "60% dos Limites Mensais", 1, 0, "C")
        pdf.cell(65, 6, f"R$ {limite_gasto_primeira_quize:,.2f}", 1, 1, "R")
        
        pdf.cell(60, 6, "2ª Quinzena", 1, 0, "L")
        pdf.cell(65, 6, "40% dos Limites Mensais", 1, 0, "C")
        pdf.cell(65, 6, f"R$ {limite_gasto_segunda_quize:,.2f}", 1, 1, "R")

        pdf.ln(5)

        # DETALHE DA DIVISÃO POR CATEGORIA (50-30-20)
        pdf.set_font("DejaVuSansMono", "B", 12)
        pdf.set_fill_color(255, 230, 200) 
        pdf.cell(0, 7, "Detalhamento da Divisão por Categoria (60% / 40%)", 1, 1, "C", 1)
        
        pdf.set_font("DejaVuSansMono", "B", 10)
        pdf.cell(60, 6, "Categoria", 1, 0, "L")
        pdf.cell(40, 6, "1ª Parcela (60%)", 1, 0, "R")
        pdf.cell(40, 6, "2ª Parcela (40%)", 1, 1, "R")
        
        pdf.set_font("DejaVuSansMono", "", 10)
        
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
        safe_titulo = remove_accents(titulo)
        pdf.set_fill_color(*cor_limite)
        pdf.set_font("DejaVuSansMono", "B", 12)
        pdf.cell(0, 7, f"{safe_titulo} (Limite: R$ {limite:,.2f})", 1, 1, "L", 1)
        pdf.set_font("DejaVuSansMono", "", 10)
        
        # Tabela de Despesas
        pdf.cell(60, 6, "Item", 1, 0, "L", 0)
        pdf.cell(30, 6, "Valor", 1, 1, "R", 0)
        
        for item, valor in sorted(despesas.items()):
            pdf.cell(60, 6, remove_accents(item), 1, 0, "L", 0) 
            pdf.cell(30, 6, f"R$ {valor:,.2f}", 1, 1, "R", 0)
        
        # Linha do Total
        pdf.set_font("DejaVuSansMono", "B", 10)
        pdf.cell(60, 6, "TOTAL GASTO", 1, 0, "L", 0)
        pdf.cell(30, 6, f"R$ {total_real:,.2f}", 1, 1, "R", 0)
        pdf.ln(7)

        # AVISO DE LIMITE
        if total_real > limite:
            pdf.set_fill_color(255, 192, 203)
            pdf.set_text_color(255, 0, 0)
            ultrapassado = total_real - limite
            pdf.set_font("DejaVuSansMono", "B", 10)
            pdf.cell(0, 6, f"ATENCAO: Voce ULTRAPASSOU o limite em R$ {ultrapassado:,.2f}!", 1, 1, "C", 1)
        elif total_real < limite:
            pdf.set_text_color(0, 128, 0)
            economizado = limite - total_real
            pdf.set_font("DejaVuSansMono", "", 10)
            pdf.cell(0, 6, f"Parabens! Voce economizou R$ {economizado:,.2f} nesta categoria.", 0, 1, "C", 0)
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

    # Chamadas finais
    adicionar_secao("50% Necessidades Fixas (Despesas Fixas)", totais_reais['total_fixas'], limites.get('Necessidades (50%)', 0.0), orcamento_obj.despesas_fixas, (144, 238, 144))
    adicionar_secao("30% Desejos e Lazer (Despesas Variaveis)", totais_reais['total_lazer'], limites.get('Desejos/Lazer (30%)', 0.0), orcamento_obj.gastos_lazer, (173, 216, 230))
    
    # 20% Poupança
    pdf.set_fill_color(255, 255, 153)
    pdf.set_font("DejaVuSansMono", "B", 12)
    meta_poupanca = limites.get('Poupança/Investimento (20%)', 0.0)
    pdf.cell(0, 7, f"20% Poupanca/Investimento (Meta: R$ {meta_poupanca:,.2f})", 1, 1, "L", 1)
    total_poupanca = totais_reais['total_poupanca']
    pdf.set_font("DejaVuSansMono", "", 10)
    pdf.cell(60, 6, "Valor Destinado", 1, 0, "L", 0)
    pdf.cell(30, 6, f"R$ {total_poupanca:,.2f}", 1, 1, "R", 0)

    if total_poupanca < meta_poupanca:
        pdf.set_text_color(255, 0, 0)
        falta = meta_poupanca - total_poupanca
        pdf.set_font("DejaVuSansMono", "B", 10)
        pdf.cell(0, 6, f"Atencao: Voce esta R$ {falta:,.2f} abaixo da meta de 20%."), 1, 1, "C", 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    return bytes(pdf.output(dest='S')) 


def criar_pdf_relatorio_historico(df_resumo_historico):
    """Gera um PDF contendo o resumo da comparação histórica de meses."""
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVuSansMono", "", "DejaVuSansMono.ttf", uni=True) 
    pdf.set_font("DejaVuSansMono", "B", 16)
    
    pdf.cell(0, 10, "Relatório de Comparação Histórica Mensal", 0, 1, "C")
    
    return bytes(pdf.output(dest='S'))