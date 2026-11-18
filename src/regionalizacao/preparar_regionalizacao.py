"""Lê localizadores, população e vínculos para consolidar as 13 regiões."""

import numpy as np
import pandas as pd

from src.config import N_MUNICIPIOS_MG, PASTA_DADOS
from src.imrs.preparar_imrs import _ler_localizadores, _ler_populacao
from src.preparar import carregar_txt, codigo_texto


CODIGO = "codigo_regiao_intermediaria"
NOME = "regiao_intermediaria"


def carregar_bases_regionalizacao(ano, bimestre, ano_populacao=2025):
    """Retorna planejamento elegível, monitoramento e população municipal."""
    if bimestre not in range(1, 7):
        raise ValueError("O bimestre deve estar entre 1 e 6.")
    raw = PASTA_DADOS / "raw"
    caminho = raw / "planejamento" / "localizadores_todos_planejamento.txt"
    # Reutiliza a leitura territorial do IMRS. No programado, desconsidera
    # Exclusão Lógica da Ação = True antes de somar qualquer localizador.
    planejamento = _ler_localizadores(caminho, f"Previsão Orçamentária {ano}", "programado")
    monitoramento = _ler_localizadores(
        raw / "monitoramento" / f"{bimestre}bim" / "localizadores_monitoramento.txt",
        f"Despesa Realizada Total {ano}", "executado", periodo=(ano, bimestre),
    )
    populacao = _ler_populacao(raw / "externas" / f"estimativa_dou_{ano_populacao}.xls", planejamento, monitoramento)
    # Os nomes ficam associados ao código do SIGPlan. Esse vínculo permite
    # formar a malha regional a partir da malha municipal, sem trocar códigos.
    nomes = carregar_txt(caminho, usecols=["Código da Região Geográfica Intermediária", "Região Geográfica Intermediária"], dtype="string")
    nomes.columns = [CODIGO, NOME]
    nomes[CODIGO] = codigo_texto(nomes[CODIGO]).str.lstrip("0")
    nomes[NOME] = codigo_texto(nomes[NOME])
    nomes = nomes.loc[nomes[CODIGO].isin([str(n) for n in range(1, 14)])].drop_duplicates()
    if nomes[CODIGO].duplicated().any() or len(nomes) != 13 or nomes.isna().any().any():
        raise ValueError("A referência precisa identificar as 13 regiões com um nome por código.")
    populacao = populacao.merge(nomes, on=CODIGO, how="left", validate="many_to_one")
    if len(populacao) != N_MUNICIPIOS_MG or populacao["codigo_ibge"].duplicated().any():
        raise ValueError("A população deve identificar os 853 municípios de MG uma vez.")
    if populacao.isna().any().any() or not np.isfinite(populacao["populacao"].to_numpy(dtype=float)).all():
        raise ValueError("Há município sem população ou vínculo regional válido.")
    if not populacao["populacao"].gt(0).all():
        raise ValueError("A população municipal precisa ser positiva para os rateios.")
    return planejamento, monitoramento, populacao


def agregar_populacao(populacao):
    """Soma os habitantes da região e calcula a participação no total de MG."""
    regioes = populacao.groupby([CODIGO, NOME], as_index=False)["populacao"].sum()
    regioes = regioes.rename(columns={"populacao": "populacao_regiao"}).sort_values(NOME).reset_index(drop=True)
    regioes["populacao_mg"] = regioes["populacao_regiao"].sum()
    regioes["peso_regiao"] = regioes["populacao_regiao"] / regioes["populacao_mg"]
    return regioes


def apropriar_regioes(base, coluna_valor, populacao, regioes):
    """Apura parcelas municipal, regional e estadual para cada região."""
    # Municipal e regional pertencem integralmente à região de origem.
    # O estadual é repartido pelo peso populacional das 13 regiões.
    municipal = base["tipo_localizador"].eq("municipal")
    regional = base["tipo_localizador"].eq("regional")
    estadual = base["tipo_localizador"].eq("estadual")
    if not (municipal | regional | estadual).all():
        raise ValueError("Há tipo de localizador desconhecido.")
    vinculo = populacao.set_index("codigo_ibge")[CODIGO]
    correspondencia = base.loc[municipal, "codigo_ibge"].map(vinculo)
    if not correspondencia.eq(base.loc[municipal, CODIGO]).fillna(False).all():
        raise ValueError("Há localizador municipal sem correspondência na referência regional.")
    if not base.loc[regional, CODIGO].isin(regioes[CODIGO]).all():
        raise ValueError("Há localizador regional fora das 13 regiões.")
    valores = base[coluna_valor].fillna(0)
    if not np.isfinite(valores.to_numpy(dtype=float)).all():
        raise ValueError(f"Há valor inválido em {coluna_valor}.")
    dados = base.assign(valor=valores)
    resultado = regioes.copy()
    for tipo, filtro in [("municipal", municipal), ("regional", regional)]:
        soma = dados.loc[filtro].groupby(CODIGO)["valor"].sum()
        resultado[f"{coluna_valor}_{tipo}"] = resultado[CODIGO].map(soma).fillna(0)
    resultado[f"{coluna_valor}_estadual"] = valores.loc[estadual].sum() * resultado["peso_regiao"]
    parcelas = [f"{coluna_valor}_{tipo}" for tipo in ["municipal", "regional", "estadual"]]
    resultado[coluna_valor] = resultado[parcelas].sum(axis=1)
    # A apropriação deve preservar todo o valor elegível da base original.
    if not np.isclose(resultado[coluna_valor].sum(), valores.sum(), rtol=0, atol=0.005):
        raise ValueError(f"O rateio regional de {coluna_valor} não fecha com a origem.")
    return resultado
