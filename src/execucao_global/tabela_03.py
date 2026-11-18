"""Tabela 3 — Programado e Realizado por Área Temática e grupo."""

import pandas as pd

from .calculos import acrescentar_total, agregar, calcular_indicadores
from .preparar_global import VALORES


def gerar_tabela_3(acoes):
    # Uma linha de detalhe por código e nome de área. O grupo organiza a
    # apresentação e define os subtotais de Finalísticas e Apoio e Suporte.
    detalhes = agregar(acoes, ["codigo_area_tematica", "area_tematica", "grupo_area_tematica"])
    blocos = []
    for grupo in ["Áreas Temáticas Finalísticas", "Áreas Temáticas de Apoio e Suporte", "Outros"]:
        bloco = detalhes.loc[detalhes["grupo_area_tematica"].eq(grupo)].sort_values("area_tematica")
        if grupo != "Outros" and not bloco.empty:
            bloco = acrescentar_total(bloco, "area_tematica", f"Subtotal — {grupo}")
            bloco["grupo_area_tematica"] = grupo
        blocos.append(bloco)
    # O Total Geral vem dos detalhes originais para que os subtotais não sejam
    # somados novamente. Todos os indicadores usam o realizado global.
    total = detalhes[VALORES].sum().to_dict()
    total["area_tematica"] = "Total Geral"
    tabela = pd.concat([*blocos, pd.DataFrame([total])], ignore_index=True)
    return calcular_indicadores(tabela, detalhes["realizado"].sum())
