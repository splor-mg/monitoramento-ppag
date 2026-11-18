"""Gráfico 1 — percentuais das ações válidas com programação no período."""

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from src.desempenho.preparar_desempenho import INTERVALOS


def desenhar_colunas(dados, caminho):
    """Exporta colunas agrupadas, recebendo percentuais em frações."""
    figura = Figure(figsize=(10, 5), dpi=180, layout="constrained")
    eixo = figura.subplots()
    largura = 0.8 / len(dados.columns)
    posicoes = np.arange(len(dados))
    cores = ["#205580", "#8dbbd9", "#b4753d", "#5e9277"]
    for numero, coluna in enumerate(dados.columns):
        valores = dados[coluna].to_numpy(dtype=float, na_value=np.nan)
        barras = eixo.bar(posicoes + (numero - (len(dados.columns) - 1) / 2) * largura,
                          valores, largura, label=coluna, color=cores[numero])
        # Rótulos usam duas casas apenas na apresentação. Percentuais ausentes
        # aparecem sem barra e sem rótulo, preservando o denominador inexistente.
        eixo.bar_label(barras, labels=[f"{v:.2%}".replace(".", ",") if np.isfinite(v) else "" for v in valores],
                       fontsize=8, padding=3)
    eixo.set_xticks(posicoes, dados.index)
    eixo.yaxis.set_major_formatter(PercentFormatter(1))
    eixo.set_ylim(0, 1.12)
    eixo.spines[["top", "right"]].set_visible(False)
    eixo.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=len(dados.columns))
    caminho.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(caminho)
    return caminho


def gerar_grafico_1(tabela_5, caminho):
    """Devolve os dados do gráfico e grava seu PNG."""
    # Exclui Sem meta estabelecida e Total. Recalcula os percentuais usando
    # somente os quatro intervalos com programação, em cada dimensão.
    quantidades = tabela_5.set_index("intervalo_desempenho").loc[INTERVALOS[1:]]
    dados = pd.DataFrame(index=quantidades.index)
    for dimensao, rotulo in [("fisico", "Físico"), ("orcamentario", "Orçamentário")]:
        serie = quantidades[f"qtd_acoes_validas_{dimensao}"]
        dados[rotulo] = serie / serie.sum() if serie.sum() else float("nan")
    desenhar_colunas(dados, caminho)
    return dados
