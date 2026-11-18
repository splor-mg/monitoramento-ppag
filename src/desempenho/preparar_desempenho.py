"""Prepara as ações do SIGPlan para as Tabelas 5 e 6 do RIM."""

import numpy as np
import pandas as pd

from src.config import PASTA_DADOS
from src.preparar import COLUNAS_PERIODO, carregar_txt, codigo_texto, numero_decimal, validar_periodo_monitoramento


MESES = ("Fev", "Abr", "Jun", "Ago", "Out", "Dez")
CHAVES = ["codigo_uo", "codigo_acao"]
INTERVALOS = ["Sem meta estabelecida", "Sem execução", "Crítico", "Satisfatório", "Subestimado"]
GRUPOS_IAG = {"0": "demais", "1": "estrategicos"}


def classificar_desempenho(programado, realizado):
    """Devolve a taxa como fração e o intervalo, antes do arredondamento."""
    # Programação zero recebe Sem meta estabelecida, inclusive quando existe
    # realização. A divisão fica ausente nesses registros.
    taxa = realizado.div(programado.where(programado.ne(0)))
    intervalo = pd.Series(pd.NA, index=programado.index, dtype="string")
    intervalo.loc[programado.eq(0)] = INTERVALOS[0]
    intervalo.loc[taxa.eq(0)] = INTERVALOS[1]
    intervalo.loc[taxa.gt(0) & taxa.lt(0.7)] = INTERVALOS[2]
    intervalo.loc[taxa.ge(0.7) & taxa.le(1.3)] = INTERVALOS[3]
    intervalo.loc[taxa.gt(1.3)] = INTERVALOS[4]
    return taxa, intervalo


def carregar_acoes_desempenho(ano, bimestre):
    """Lê ações e localizadores do período e devolve uma linha por UO e ação."""
    if bimestre not in range(1, 7):
        raise ValueError("O bimestre deve estar entre 1 e 6.")
    pasta = PASTA_DADOS / "raw" / "monitoramento" / f"{bimestre}bim"
    campos_chave = {
        "Código da Unidade Orçamentária Responsável pela Ação": "codigo_uo",
        "Código da Ação": "codigo_acao",
    }
    campos = {
        **campos_chave,
        "Título da Ação": "acao",
        "Código do Tipo de Ação": "codigo_tipo_acao",
        "Código do Identificador de Ação Governamental (IAG)": "iag",
        f"Previsão Orçamentária {ano} (LOA)": "previsao_orcamentaria_loa",
        f"Fis Programado Inicial de Jan  a {MESES[bimestre - 1]}": "meta_fisica_periodo",
        f"Realização Física {ano}": "realizado_fisico",
        "Total Prog. Inicial Outras Desp.": "programado_orcamentario_periodo",
    }
    caminho = pasta / "acoes_monitoramento.txt"
    acoes = carregar_txt(caminho, usecols=[*campos, *COLUNAS_PERIODO], dtype="string")
    validar_periodo_monitoramento(acoes, caminho, ano, bimestre)
    acoes = acoes.rename(columns=campos)[list(campos.values())]

    # Conserva as chaves em colunas separadas, retirando zeros de preenchimento
    # de modo igual nas duas bases. Uma ação deve aparecer uma vez no período.
    for coluna in [*CHAVES, "codigo_tipo_acao", "iag"]:
        acoes[coluna] = codigo_texto(acoes[coluna]).str.replace(r"^0+(?=\d)", "", regex=True)
    if acoes[CHAVES].isna().any().any() or acoes.duplicated(CHAVES).any():
        raise ValueError("Há UO/ação ausente ou repetida na base de ações.")
    if not acoes["iag"].isin(GRUPOS_IAG).all() or acoes["codigo_tipo_acao"].isna().any():
        raise ValueError("Há IAG desconhecido ou Tipo de Ação ausente.")
    numericas = ["previsao_orcamentaria_loa", "meta_fisica_periodo", "realizado_fisico",
                 "programado_orcamentario_periodo"]
    for coluna in numericas:
        acoes[coluna] = numero_decimal(acoes[coluna])
    if not np.isfinite(acoes["previsao_orcamentaria_loa"].to_numpy(dtype=float, na_value=np.nan)).all():
        raise ValueError("Há previsão orçamentária da LOA ausente ou inválida.")

    # Cada localizador contribui com Investimento + Outros. A parcela de
    # Pessoal e Auxílios fica fora desta soma, como na planilha de desempenho.
    valores = [f"Despesa Realizada Investimento {ano}", f"Despesa Realizada Outros {ano}"]
    caminho = pasta / "localizadores_monitoramento.txt"
    localizadores = carregar_txt(caminho, usecols=[*campos_chave, *valores, *COLUNAS_PERIODO], dtype="string")
    validar_periodo_monitoramento(localizadores, caminho, ano, bimestre)
    localizadores = localizadores.rename(columns=campos_chave)
    for coluna in CHAVES:
        localizadores[coluna] = codigo_texto(localizadores[coluna]).str.replace(r"^0+(?=\d)", "", regex=True)
    for coluna in valores:
        localizadores[coluna] = numero_decimal(localizadores[coluna])
    if localizadores[CHAVES + valores].isna().any().any():
        raise ValueError("Há chave ou parcela de despesa ausente nos localizadores.")
    localizadores["realizado_orcamentario"] = localizadores[valores].sum(axis=1)
    despesas = localizadores.groupby(CHAVES, as_index=False)["realizado_orcamentario"].sum()
    # Agrega antes de juntar para evitar multiplicar as ações e suas despesas.
    vinculos = despesas.merge(acoes[CHAVES], on=CHAVES, how="left", indicator=True, validate="one_to_one")
    if vinculos["_merge"].ne("both").any():
        raise ValueError("Há localizadores sem correspondência na base de ações.")
    acoes = acoes.merge(despesas, on=CHAVES, how="left", validate="one_to_one")
    acoes["realizado_orcamentario"] = acoes["realizado_orcamentario"].fillna(0)

    # A validade depende somente da LOA e do Tipo de Ação. As metas físicas
    # serão usadas na classificação, preservando as ações válidas sem meta.
    acoes["valida_orcamentaria"] = acoes["previsao_orcamentaria_loa"].ne(0)
    acoes["valida_fisica"] = acoes["valida_orcamentaria"] | acoes["codigo_tipo_acao"].eq("5")
    for dimensao, programado, realizado in [
        ("fisico", "meta_fisica_periodo", "realizado_fisico"),
        ("orcamentario", "programado_orcamentario_periodo", "realizado_orcamentario"),
    ]:
        validade = "valida_fisica" if dimensao == "fisico" else "valida_orcamentaria"
        usados = acoes.loc[acoes[validade], [programado, realizado]]
        if not np.isfinite(usados.to_numpy(dtype=float, na_value=np.nan)).all():
            raise ValueError(f"Há valores ausentes ou inválidos nas ações válidas do {dimensao}.")
        taxa, intervalo = classificar_desempenho(acoes[programado], acoes[realizado])
        if intervalo.loc[acoes[validade]].isna().any():
            raise ValueError(f"Há taxa fora das faixas documentadas no {dimensao}. Conferir valores negativos.")
        acoes[f"taxa_{dimensao}"] = taxa
        acoes[f"intervalo_{dimensao}"] = intervalo
    return acoes
