"""Somas e indicadores usados nas quatro tabelas da Execução Global."""

import pandas as pd

from .preparar_global import VALORES


def agregar(acoes, chaves):
    """Soma A, B e C por chave, antes de calcular qualquer percentual."""
    return acoes.groupby(chaves, as_index=False, sort=True)[VALORES].sum()


def calcular_indicadores(tabela, realizado_global):
    """Calcula D, C/A e C/B sobre cada linha já agregada."""
    tabela = tabela.copy()
    tabela["analise_vertical"] = tabela["realizado"] / realizado_global if realizado_global else float("nan")
    tabela["execucao_anual"] = tabela["realizado"] / tabela["programado_anual"].where(tabela["programado_anual"].ne(0))
    tabela["execucao_periodo"] = tabela["realizado"] / tabela["programado_periodo"].where(tabela["programado_periodo"].ne(0))
    return tabela


def acrescentar_total(detalhes, coluna_nome, nome="Total Geral"):
    """Acrescenta a soma de A, B e C. As taxas serão recalculadas depois."""
    total = detalhes[VALORES].sum().to_dict()
    total[coluna_nome] = nome
    return pd.concat([detalhes, pd.DataFrame([total])], ignore_index=True)
