"""Regras de negócio dos demonstrativos relacionados ao IMRS."""

import pandas as pd

from src.config import N_MUNICIPIOS_IMRS


def selecionar_menores_imrs(df, coluna="imrs"):
    """Seleciona os municípios com menores valores de IMRS."""
    return (
        df
        .sort_values(coluna)
        .head(N_MUNICIPIOS_IMRS)
        .copy()
    )


def calcular_pesos_populacionais(df):
    """Calcula os pesos populacionais usados nos rateios do IMRS."""
    # Regra será implementada após validação da metodologia.
    return df.copy()


def calcular_valores_imrs(df):
    """Aplica as regras de apropriação municipal, regional e estadual."""
    # Regra será implementada após validação da metodologia.
    return df.copy()


def gerar_tabelas_imrs(df):
    """Gera os demonstrativos do IMRS por programa, área e município."""
    # Tabelas 9, 10 e 11 do RIM.
    pass