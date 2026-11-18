"""Prepara as geometrias e os cruzamentos territoriais dos mapas do RIM."""

import geopandas as gpd

from src.config import N_MUNICIPIOS_MG, PASTA_DADOS
from src.preparar import codigo_texto


MALHA_PADRAO = PASTA_DADOS / "auxiliares" / "MG_Municipios_2025.zip"
N_REGIOES_MG = 13
COD_IBGE = "codigo_ibge"
COD_REGIAO = "codigo_regiao_intermediaria"
NOME_REGIAO = "regiao_intermediaria"


def carregar_malha_municipal(caminho=MALHA_PADRAO):
    """Carrega os limites projetados dos 853 municípios de Minas Gerais."""
    if not caminho.is_file():
        raise FileNotFoundError(f"Malha municipal ausente em {caminho}. Consulte o README ou use --malha.")
    malha = gpd.read_file(caminho, columns=["CD_MUN"])
    if "CD_MUN" not in malha or malha.crs is None:
        raise ValueError("A malha precisa conter o campo CD_MUN e um sistema de coordenadas.")

    # CD_MUN traz o código IBGE de sete dígitos. O prefixo 31 identifica MG,
    # inclusive quando o arquivo de origem contém municípios de outros estados.
    malha[COD_IBGE] = codigo_texto(malha["CD_MUN"])
    minas = malha[COD_IBGE].str.fullmatch(r"31\d{5}", na=False)
    malha = malha.loc[minas, [COD_IBGE, "geometry"]]
    if len(malha) != N_MUNICIPIOS_MG or malha[COD_IBGE].duplicated().any():
        raise ValueError("A malha deve conter uma geometria para cada um dos 853 municípios de MG.")
    if malha.geometry.isna().any() or malha.geometry.is_empty.any():
        raise ValueError("A malha contém municípios com geometria ausente ou vazia.")

    return malha.to_crs(epsg=5880)  # SIRGAS 2000 / Brasil Policônica


def juntar_dados_territoriais(malha, dados, chave, *, cobertura_completa=False):
    """Associa dados pela chave territorial e preserva todos os limites da malha."""
    codigos = dados[chave]
    if codigos.isna().any() or codigos.duplicated().any():
        raise ValueError(f"Os dados devem conter um registro por código válido de {chave}.")

    ausentes_na_malha = codigos.loc[~codigos.isin(malha[chave])]
    if not ausentes_na_malha.empty:
        raise ValueError(f"Códigos de {chave} ausentes na malha: {', '.join(ausentes_na_malha.astype(str))}.")
    if cobertura_completa:
        ausentes_nos_dados = malha.loc[~malha[chave].isin(codigos), chave]
        if not ausentes_nos_dados.empty:
            raise ValueError(f"Códigos de {chave} ausentes nos dados: {', '.join(ausentes_nos_dados.astype(str))}.")

    # O IMRS fornece valores só para o recorte. Os outros municípios
    # continuam na malha com valores ausentes e aparecem em cinza.
    return malha.merge(dados, on=chave, how="left", validate="one_to_one")


def montar_malha_regional(malha_municipal, vinculos):
    """Agrupa os municípios nas 13 Regiões Geográficas Intermediárias de MG."""
    colunas = [COD_IBGE, COD_REGIAO]
    if NOME_REGIAO in vinculos:
        colunas.append(NOME_REGIAO)
    regioes = vinculos[colunas].copy()
    regioes[COD_IBGE] = codigo_texto(regioes[COD_IBGE])
    regioes[COD_REGIAO] = codigo_texto(regioes[COD_REGIAO]).str.lstrip("0").replace("", None)
    if regioes[COD_REGIAO].isna().any() or regioes[COD_REGIAO].nunique() != N_REGIOES_MG:
        raise ValueError("Os vínculos devem identificar as 13 regiões intermediárias de Minas Gerais.")
    if NOME_REGIAO in regioes:
        regioes[NOME_REGIAO] = codigo_texto(regioes[NOME_REGIAO])
        nomes_por_regiao = regioes.groupby(COD_REGIAO)[NOME_REGIAO].nunique()
        if regioes[NOME_REGIAO].isna().any() or not nomes_por_regiao.eq(1).all():
            raise ValueError("Cada região intermediária deve ter um único nome.")

    municipios = juntar_dados_territoriais(
        malha_municipal, regioes.drop_duplicates(), COD_IBGE, cobertura_completa=True,
    )
    # Une as geometrias de cada região e elimina as divisas internas entre
    # seus municípios. A malha resultante serve aos cinco mapas regionais.
    return municipios.drop(columns=COD_IBGE).dissolve(by=COD_REGIAO, as_index=False)
