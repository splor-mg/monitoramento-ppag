"""Geometrias, cores e legendas comuns aos cinco mapas regionais do RIM."""

import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from src.preparar_mapas import carregar_malha_municipal, juntar_dados_territoriais, montar_malha_regional
from .preparar_regionalizacao import CODIGO, NOME


CORES_GLOBAIS = ("#f6b2b2", "#c36d6d", "#8b3030")
CORES_PER_CAPITA = ("#b6e5df", "#4b9f92", "#085b52")


def preparar_geometrias(populacao, caminho_malha):
    """Associa os 853 municípios às 13 regiões e une as áreas regionais."""
    municipios = carregar_malha_municipal(caminho_malha)
    regioes = montar_malha_regional(municipios, populacao)
    # Os números da legenda seguem a ordem alfabética dos nomes, como no RIM.
    regioes = regioes.sort_values(NOME).reset_index(drop=True)
    regioes["numero_regiao"] = np.arange(1, 14)
    return municipios, regioes


def desenhar_mapa(municipios, regioes, destino, *, coluna=None, cores=None, unidade=None):
    """Exporta a geometria com numeração regional, legenda e escala do indicador."""
    figura = Figure(figsize=(8.8, 6), dpi=220)
    eixo = figura.add_axes((0.01, 0.16, 0.64, 0.82))
    nomes = regioes[NOME].str.replace("Região Intermediária de ", "", regex=False)
    if coluna is None:
        # Cores categóricas próximas da referência do Mapa 1, em ordem alfabética.
        paleta = ["#4979bd", "#94403d", "#897014", "#343c3b", "#bc4949", "#ff5a60",
                  "#59354f", "#00968b", "#f6bf9d", "#f6df53", "#a4dce8", "#b07faa", "#d1d1d1"]
        regioes.plot(ax=eixo, color=paleta, edgecolor="#777777", linewidth=0.5)
        legenda = [Patch(facecolor=cor, label=f"{n}. {nome}") for n, nome, cor in zip(regioes["numero_regiao"], nomes, paleta)]
        figura.legend(handles=legenda, loc="center left", bbox_to_anchor=(0.66, 0.55), frameon=False, fontsize=8)
    else:
        valores = regioes[coluna]
        if not np.isfinite(valores.to_numpy(dtype=float)).all():
            raise ValueError(f"Há indicador ausente ou inválido no mapa: {coluna}.")
        media = valores.mean()
        minimo, maximo = valores.min(), valores.max()
        # A média das 13 regiões ocupa o meio da paleta. As duas metades
        # interpolam de mínimo a média e de média a máximo, sem cortes de classes.
        if minimo == maximo:
            minimo, maximo = media - 1, media + 1
        norma = TwoSlopeNorm(vmin=minimo, vcenter=media, vmax=maximo)
        paleta = LinearSegmentedColormap.from_list(coluna, cores)
        barra = figura.add_axes((0.09, 0.09, 0.47, 0.025))
        regioes.plot(ax=eixo, column=coluna, cmap=paleta, norm=norma,
                     edgecolor="#777777", linewidth=0.5, legend=True, cax=barra,
                     legend_kwds={"orientation": "horizontal", "label": unidade})
        barra.tick_params(labelsize=7)
        barra.xaxis.label.set_size(8)
        eixo.text(0.5, -0.04, f"Média regional: {media:,.2f}".translate(str.maketrans(",.", ".,")),
                  transform=eixo.transAxes, ha="center", fontsize=8)
        # A lista identifica os números do mapa sem ocupar suas áreas internas.
        for posicao, (numero, nome) in enumerate(zip(regioes["numero_regiao"], nomes)):
            figura.text(0.67, 0.87 - posicao * 0.045, f"{numero}. {nome}", fontsize=8)
    # As divisas municipais são mantidas finas como nas imagens de referência.
    municipios.boundary.plot(ax=eixo, color="#999999", linewidth=0.12)
    for _, regiao in regioes.iterrows():
        ponto = regiao.geometry.representative_point()
        eixo.text(ponto.x, ponto.y, str(regiao["numero_regiao"]), ha="center", va="center",
                  fontsize=9, fontweight="bold", color="#222222")
    eixo.set_axis_off()
    destino.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino)
    return destino


def desenhar_indicador(municipios, regioes, tabela, coluna, cores, unidade, divisor, destino):
    """Junta somente os detalhes da tabela à malha e converte a unidade da barra."""
    detalhes = tabela.loc[tabela[CODIGO].notna(), [CODIGO, coluna]].copy()
    detalhes[coluna] = detalhes[coluna] / divisor
    mapa = juntar_dados_territoriais(regioes, detalhes, CODIGO, cobertura_completa=True)
    return desenhar_mapa(municipios, mapa, destino, coluna=coluna, cores=cores, unidade=unidade)
