"""Funções de exportação dos resultados do monitoramento."""

import pandas as pd


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
                from src.exportar_excel_rim import formatar_aba_rim

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
