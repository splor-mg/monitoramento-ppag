"""Tabela 8 — Programado e Executado por habitante de cada região."""

import pandas as pd

from .preparar_regionalizacao import CODIGO, NOME


def gerar_tabela_8(tabela_7, regioes):
    """Calcula os per capita e usa o per capita estadual como referência de C."""
    # Retira o Total Geral antes de juntar os dados à população das regiões.
    detalhes = tabela_7.loc[tabela_7[CODIGO].notna(), [CODIGO, NOME, "programado", "executado"]]
    dados = detalhes.merge(regioes[[CODIGO, "populacao_regiao"]], on=CODIGO, how="left", validate="one_to_one")
    populacao = dados["populacao_regiao"].where(dados["populacao_regiao"].gt(0))
    tabela = dados[[CODIGO, NOME]].copy()
    tabela["programado_per_capita"] = dados["programado"] / populacao
    tabela["executado_per_capita"] = dados["executado"] / populacao
    # O total estadual divide os valores globais pela população de MG.
    # Somar os per capita regionais produziria um total sem essa interpretação.
    habitantes = regioes["populacao_regiao"].sum()
    total = {NOME: "Total Estadual",
             "programado_per_capita": dados["programado"].sum() / habitantes,
             "executado_per_capita": dados["executado"].sum() / habitantes}
    tabela = pd.concat([tabela, pd.DataFrame([total])], ignore_index=True)
    tabela["execucao"] = tabela["executado_per_capita"] / tabela["programado_per_capita"].where(tabela["programado_per_capita"].ne(0))
    referencia = total["executado_per_capita"]
    tabela["analise_vertical"] = tabela["executado_per_capita"] / referencia if referencia else float("nan")
    return tabela
