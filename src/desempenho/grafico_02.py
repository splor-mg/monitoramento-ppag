"""Gráfico 2 — desempenho com programação, separado por IAG e dimensão."""

import pandas as pd

from src.desempenho.grafico_01 import desenhar_colunas
from src.desempenho.preparar_desempenho import INTERVALOS


def gerar_grafico_2(tabela_6, caminho):
    """Devolve os percentuais do gráfico e grava quatro grupos de colunas."""
    quantidades = tabela_6.set_index("intervalo_desempenho").loc[INTERVALOS[1:]]
    linhas = []
    nomes = []
    for grupo, rotulo in [("demais", "Demais Projetos\ne Atividades"), ("estrategicos", "Projetos\nEstratégicos")]:
        for dimensao, nome in [("fisico", "Físico"), ("orcamentario", "Orçamentário")]:
            # Cada combinação IAG/dimensão tem seu próprio denominador,
            # excluindo Sem meta estabelecida e a linha Total Geral.
            serie = quantidades[f"qtd_acoes_validas_{dimensao}_{grupo}"]
            linhas.append(serie / serie.sum() if serie.sum() else serie.astype(float) * float("nan"))
            nomes.append(f"{rotulo}\n{nome}")
    dados = pd.DataFrame(linhas, index=nomes)
    desenhar_colunas(dados, caminho)
    return dados
