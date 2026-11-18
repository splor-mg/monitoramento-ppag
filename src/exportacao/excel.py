"""Funções de exportação dos resultados do monitoramento."""

import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from src.exportacao.estilo import AZUL, AZUL_CLARO, ELABORACAO, FONTE, NOTA_PODERES


def exportar_excel(tabelas, caminho, formatos=None, *, quadros=None):
    """
    Exporta um conjunto de DataFrames para um arquivo Excel.

    tabelas deve ser um dicionário no formato:
    {"nome_da_aba": dataframe}
    formatos associa nomes de colunas a formatos numéricos do Excel.
    """

    # Cada chave do dicionário vira o nome de uma aba. A primeira linha recebe
    # os nomes das colunas. O índice do DataFrame fica fora do relatório.
    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        for nome, df in tabelas.items():
            if quadros and nome in quadros:
                formatar_aba_rim(writer.book.create_sheet(nome), quadros[nome])
                continue
            df.to_excel(
                writer,
                sheet_name=nome,
                index=False
            )
            if formatos:
                planilha = writer.sheets[nome]
                for indice, coluna in enumerate(df.columns, start=1):
                    if coluna in formatos:
                        # Formata a exibição das células abaixo do cabeçalho.
                        # Os valores mantêm a precisão e o tipo de origem.
                        for linha in range(2, len(df) + 2):
                            planilha.cell(linha, indice).number_format = formatos[coluna]


MOEDA = '#,##0.00;-#,##0.00;"–"'
PERCENTUAL = "0.00%"


def formatar_aba_rim(aba, quadro):
    cabecalho, larguras, linhas = quadro
    aba.append(cabecalho)
    aba.sheet_view.showGridLines = False
    aba.freeze_panes = "A2"
    aba.print_title_rows = "1:1"
    aba.sheet_properties.pageSetUpPr.fitToPage = True
    aba.page_setup.fitToWidth, aba.page_setup.fitToHeight = 1, 0
    aba.sheet_properties.tabColor = AZUL

    for i, largura in enumerate(larguras, start=1):
        aba.column_dimensions[get_column_letter(i)].width = largura * 1.23
    if aba.title == "Tabela 11":
        aba.column_dimensions["A"].hidden = True

    numericas = {9: (3, 4), 10: (2, 3, 4, 5, 6), 11: (3, 4)}[int(aba.title[-2:])]
    faixa = 0
    for n, (tipo, valores) in enumerate([("cabecalho", cabecalho), *linhas], start=1):
        if n > 1:
            aba.append(valores)
        escura = tipo in ("cabecalho", "grupo")
        cor = AZUL if escura else AZUL_CLARO if tipo == "total" or faixa % 2 == 0 else "FFFFFF"
        for celula in aba[n]:
            celula.fill = PatternFill("solid", fgColor=cor)
            celula.font = Font(name="Arial", size=10, color="FFFFFF" if escura else "000000",
                               bold=escura or tipo == "total")
            celula.alignment = Alignment(
                vertical="center", wrap_text=escura or celula.column not in numericas,
                horizontal="center" if escura else "right" if celula.column in numericas else "left",
            )
            if not escura and celula.column in numericas:
                celula.number_format = PERCENTUAL if aba.title == "Tabela 10" and celula.column >= 4 else MOEDA
            if tipo == "total":
                celula.border = Border(top=Side(style="thin", color=AZUL))
        if tipo == "grupo":
            aba.merge_cells(start_row=n, start_column=1, end_row=n, end_column=len(cabecalho))
        if tipo == "cabecalho":
            aba.row_dimensions[n].height = 34 if aba.title == "Tabela 10" else 29
        if tipo == "dado":
            maior = max(len(str(valores[i])) / (larguras[i] * 1.3)
                        for i in range(len(valores)) if i + 1 not in numericas)
            aba.row_dimensions[n].height = 29 if maior > 1 else 16
            faixa += 1

    for nota in (FONTE, ELABORACAO, *((NOTA_PODERES,) if aba.title == "Tabela 10" else ())):
        primeira = 2 if aba.title == "Tabela 11" else 1
        linha = aba.max_row + 1
        aba.cell(linha, primeira, nota).font = Font(name="Arial", size=9)
        aba.merge_cells(start_row=linha, start_column=primeira, end_row=linha, end_column=len(cabecalho))
