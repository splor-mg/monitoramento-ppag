"""Funções de exportação dos resultados do monitoramento."""

import pandas as pd


def exportar_excel(tabelas, caminho):
    """
    Exporta um conjunto de DataFrames para um arquivo Excel.

    tabelas deve ser um dicionário no formato:
    {"nome_da_aba": dataframe}
    """

    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        for nome, df in tabelas.items():
            df.to_excel(
                writer,
                sheet_name=nome,
                index=False
            )