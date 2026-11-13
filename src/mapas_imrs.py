"""Gera os mapas 6 e 7 do RIM a partir da aba Tabela 11 do IMRS."""

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from src.config import PASTA_DADOS, PASTA_SAIDAS
from src.imrs import N_MUNICIPIOS_IMRS, N_MUNICIPIOS_MG


MALHA_PADRAO = PASTA_DADOS / "auxiliares" / "MG_Municipios_2025.zip"
COR_FORA_DO_RECORTE = "#d3d3d3"
COR_DIVISAS = "#969696"


def _ler_tabela_11(caminho):
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
    tabela["codigo_ibge"] = tabela["codigo_ibge"].str.strip()
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
    return tabela


def _juntar_malha(tabela, caminho_malha):
    """Mantém os 853 municípios no mapa e vincula valores aos 50 do recorte."""
    if not caminho_malha.is_file():
        raise FileNotFoundError(f"Malha municipal ausente em {caminho_malha}. Consulte o README ou use --malha.")
    malha = gpd.read_file(caminho_malha, columns=["CD_MUN"])
    if "CD_MUN" not in malha or malha.crs is None:
        raise ValueError("A malha precisa conter o campo CD_MUN e um sistema de coordenadas.")
    malha["codigo_ibge"] = malha["CD_MUN"].astype("string").str.strip()
    # O prefixo 31 identifica Minas Gerais, inclusive em uma malha nacional.
    minas = malha["codigo_ibge"].str.fullmatch(r"31\d{5}", na=False)
    malha = malha.loc[minas, ["codigo_ibge", "geometry"]]
    if len(malha) != N_MUNICIPIOS_MG or malha["codigo_ibge"].duplicated().any():
        raise ValueError("A malha deve conter uma geometria para cada um dos 853 municípios de MG.")
    if malha.geometry.isna().any() or malha.geometry.is_empty.any():
        raise ValueError("A malha contém municípios com geometria ausente ou vazia.")
    ausentes = tabela.loc[~tabela["codigo_ibge"].isin(malha["codigo_ibge"]), "codigo_ibge"]
    if not ausentes.empty:
        raise ValueError(f"Municípios da Tabela 11 ausentes na malha: {', '.join(ausentes)}.")

    # Projeta as divisas em SIRGAS 2000 / Brasil Policônica. A junção à esquerda
    # preserva a malha inteira. Só os municípios do recorte recebem valores.
    return malha.to_crs(epsg=5880).merge(tabela, on="codigo_ibge", how="left", validate="one_to_one")


def _desenhar_mapa(malha, coluna, cores, destino):
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


def gerar_mapas(tabela, ano, bimestre, saida, malha=None):
    """Gera o Mapa 6 com o programado anual e o Mapa 7 com o realizado acumulado."""
    # A aba Tabela 11 já contém os totais municipais. Faz uma única junção
    # pelo código IBGE e reutiliza as mesmas divisas nos dois PNGs.
    mapa = _juntar_malha(_ler_tabela_11(tabela), malha or MALHA_PADRAO)
    saida.mkdir(parents=True, exist_ok=True)
    # Cada mapa escolhe uma coluna da tabela e uma paleta do menor ao maior valor.
    mapas = [
        (6, "programado", ("#f5d4d0", "#a44b44")),
        (7, "realizado", ("#b6e5e0", "#236a68")),
    ]
    caminhos = []
    for numero, coluna, cores in mapas:
        # Ano e bimestre identificam os arquivos para inserção no relatório.
        destino = saida / f"Mapa_{numero}_IMRS_{ano}_{bimestre}bim.png"
        _desenhar_mapa(mapa, coluna, cores, destino)
        caminhos.append(destino)
    return caminhos


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera os mapas 6 e 7 do IMRS a partir da Tabela 11.")
    parser.add_argument("--ano", type=int, required=True, help="Ano do RIM.")
    parser.add_argument("--bimestre", type=int, choices=range(1, 7), required=True)
    parser.add_argument("--tabela", type=Path, help="Excel gerado pelo main.py com a aba Tabela 11.")
    parser.add_argument("--malha", type=Path, help="Malha do IBGE em ZIP, SHP, GeoJSON ou GPKG.")
    parser.add_argument("--saida", type=Path, default=PASTA_SAIDAS, help="Pasta dos dois PNGs.")
    args = parser.parse_args()
    tabela = args.tabela or PASTA_SAIDAS / f"IMRS_{args.ano}_{args.bimestre}bim.xlsx"
    try:
        for caminho in gerar_mapas(tabela, args.ano, args.bimestre, args.saida, args.malha):
            print(f"Mapa gerado: {caminho}")
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
