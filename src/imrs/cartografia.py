"""Validação da Tabela 11 e desenho dos mapas do IMRS."""

import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from src.imrs.preparar_imrs import N_MUNICIPIOS_IMRS
from src.preparar import codigo_texto
from src.preparar_mapas import carregar_malha_municipal, juntar_dados_territoriais


COR_FORA_DO_RECORTE = "#d3d3d3"
COR_DIVISAS = "#969696"


def ler_tabela_11(caminho):
    """Lê os totais municipais já calculados na planilha do IMRS."""
    # Lê somente a chave do município e as duas colunas que definem as cores.
    # O código IBGE permanece como texto para o cruzamento com a malha.
    colunas = ["codigo_ibge", "programado", "realizado"]
    tabela = pd.read_excel(caminho, sheet_name="Tabela 11", dtype={"codigo_ibge": "string"})
    if "Município" in tabela:
        # O layout do relatório traz cabeçalhos com o período, Total Geral e notas.
        total = tabela.index[tabela["Município"].eq("Total Geral")]
        if len(total) != 1:
            raise ValueError("A Tabela 11 formatada deve ter uma linha Total Geral.")
        tabela = tabela.iloc[:total[0], [0, 2, 3]].set_axis(colunas, axis=1)
    else:
        tabela = tabela[colunas]
    return tabela


def preparar_mapa(tabela, caminho_malha):
    """Valida os valores municipais em memória e os associa à malha."""
    tabela = tabela[["codigo_ibge", "programado", "realizado"]].copy()
    tabela["codigo_ibge"] = codigo_texto(tabela["codigo_ibge"])
    codigos = tabela["codigo_ibge"]
    if len(tabela) != N_MUNICIPIOS_IMRS or not codigos.str.fullmatch(r"31\d{5}", na=False).all():
        raise ValueError("A Tabela 11 deve conter 50 municípios de Minas Gerais com código IBGE válido.")
    if codigos.duplicated().any():
        raise ValueError("A Tabela 11 contém códigos IBGE repetidos.")

    # Um zero na Tabela 11 é um valor válido. Uma célula vazia impede o mapa.
    for coluna in ("programado", "realizado"):
        tabela[coluna] = pd.to_numeric(tabela[coluna], errors="raise")
        if not np.isfinite(tabela[coluna].to_numpy(dtype=float, na_value=np.nan)).all():
            raise ValueError(f"A coluna {coluna} contém valores ausentes ou inválidos.")
    malha = carregar_malha_municipal(caminho_malha)
    return juntar_dados_territoriais(malha, tabela, "codigo_ibge")


def desenhar_mapa(malha, coluna, cores, destino):
    """Desenha as divisas e exporta o PNG com a escala e a legenda do recorte."""
    figura = Figure(figsize=(5.1, 4.6), dpi=300)
    eixo = figura.add_axes((0.01, 0.18, 0.98, 0.81))

    # Converter antes do desenho faz a barra do GeoPandas sair em R$ milhões.
    # Cada indicador tem sua escala, com um intervalo que inclui zero.
    valores = malha[coluna] / 1_000_000
    minimo, maximo = min(0, valores.min()), max(0, valores.max())
    tem_escala = maximo > minimo
    paleta = LinearSegmentedColormap.from_list(coluna, cores)
    barra = figura.add_axes((0.24, 0.14, 0.52, 0.022)) if tem_escala else None

    # Municípios fora do recorte ficaram sem valor na junção e aparecem em cinza.
    # Zero é um valor válido do recorte e recebe a cor correspondente na escala.
    malha.plot(
        valores.to_numpy(), ax=eixo, cmap=paleta, vmin=minimo, vmax=maximo if tem_escala else 1,
        edgecolor=COR_DIVISAS, linewidth=0.18,
        missing_kwds={"color": COR_FORA_DO_RECORTE},
        legend=tem_escala, cax=barra,
        legend_kwds={"orientation": "horizontal", "label": "R$ milhões"},
    )
    eixo.set_axis_off()

    legenda = [Patch(facecolor=COR_FORA_DO_RECORTE, edgecolor=COR_DIVISAS, label="Fora do recorte do IMRS")]
    if barra is not None:
        barra.tick_params(labelsize=8, length=2, pad=2)
        barra.xaxis.label.set_size(8)
    else:
        # Se todos os valores forem zero, uma amostra de cor substitui a barra.
        legenda.insert(0, Patch(facecolor=cores[0], label="Recorte do IMRS (R$ 0,00)"))
    figura.legend(handles=legenda, loc="lower center", frameon=False, fontsize=8)
    figura.savefig(destino)
