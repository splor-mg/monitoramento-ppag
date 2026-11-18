"""Tabela 7 — Programado e Executado global por região intermediária."""

import pandas as pd

from .preparar_regionalizacao import CODIGO, NOME


def gerar_tabela_7(programado, executado):
    """Combina os dois valores apropriados e acrescenta o Total Geral."""
    # As entradas já contêm as parcelas municipal, regional e estadual.
    tabela = programado[[CODIGO, NOME, "programado"]].merge(
        executado[[CODIGO, "executado"]], on=CODIGO, validate="one_to_one",
    ).sort_values(NOME)
    if len(tabela) != 13:
        raise ValueError("A Tabela 7 precisa conter as 13 regiões.")
    total = tabela[["programado", "executado"]].sum().to_dict()
    total[NOME] = "Total Geral"
    tabela = pd.concat([tabela, pd.DataFrame([total])], ignore_index=True)
    # Os percentuais de total são calculados sobre os valores agregados.
    tabela["execucao"] = tabela["executado"] / tabela["programado"].where(tabela["programado"].ne(0))
    tabela["analise_vertical"] = tabela["executado"] / total["executado"] if total["executado"] else float("nan")
    return tabela
