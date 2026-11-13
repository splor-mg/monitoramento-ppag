"""Preparação e rateio compartilhados pelas tabelas 9, 10 e 11.

As entradas são DataFrames padronizados. Planejamento traz a previsão anual em
previsao_orcamentaria com as ações marcadas como excluídas já filtradas.
Monitoramento traz a despesa acumulada até o bimestre em
despesa_realizada_total. Cada registro já tem tipo_localizador (municipal,
regional ou estadual) e o código IBGE ou de região correspondente ao tipo.
As duas fontes trazem codigo_programa, programa, area_tematica e
grupo_area_tematica. A população cobre Minas Gerais em um único ano, com
codigo_ibge, municipio, codigo_regiao_intermediaria e populacao. A base de IMRS
traz codigo_ibge e imrs de uma única edição. O módulo preparar_imrs lê os
arquivos brutos e prepara os vínculos conforme o exercício e o bimestre.

Com essas bases em memória, chame gerar_tabelas_imrs(planejamento, monitoramento,
populacao, imrs) para obter o dicionário de tabelas e a memória da Tabela 11.
Passe o dicionário a exportar_tabelas_imrs(tabelas, caminho) para gravar o Excel.
"""

from math import isclose

import numpy as np
import pandas as pd

from src.exportar import exportar_excel
from src.imrs_tabela_9 import gerar_tabela_9
from src.imrs_tabela_10 import PERCENTUAIS, classificar_areas, gerar_tabela_10
from src.imrs_tabela_11 import gerar_tabela_11


N_MUNICIPIOS_IMRS = 50
N_MUNICIPIOS_MG = 853
COD_IBGE = "codigo_ibge"
COD_REGIAO = "codigo_regiao_intermediaria"
COLUNAS_VALORES = ["programado", "realizado"]


def _codigo_texto(serie):
    """Uniformiza identificadores de junção e sinaliza códigos em branco."""
    return serie.astype("string").str.strip().replace("", pd.NA)


def selecionar_menores_imrs(df, coluna="imrs"):
    """Ordena uma edição do IMRS e retorna os 50 municípios do recorte."""
    # Converte o índice em número para que a ordenação use o valor do IMRS.
    dados = df.copy()
    dados[COD_IBGE] = _codigo_texto(dados[COD_IBGE])
    dados[coluna] = pd.to_numeric(dados[coluna], errors="raise")
    # Exige um índice finito por código IBGE e pelo menos 50 registros válidos.
    if dados[COD_IBGE].isna().any() or dados[COD_IBGE].duplicated().any():
        raise ValueError("A edição do IMRS contém código IBGE ausente ou duplicado.")
    indices = dados[coluna].to_numpy(dtype=float, na_value=np.nan)
    if len(dados) < N_MUNICIPIOS_IMRS or not np.isfinite(indices).all():
        raise ValueError("A edição do IMRS precisa ter índices válidos para o recorte.")

    # Ordena do menor IMRS para o maior. Em empate, usa primeiro a prioridade
    # da edição, quando definida, e depois o código IBGE crescente. A saída
    # corresponde à lista imrs_2024_50 da referência quando a edição é 2024.
    dados["prioridade_desempate"] = dados.get("prioridade_desempate", False)
    ordem = [coluna, "prioridade_desempate", COD_IBGE]
    return dados.sort_values(ordem).head(N_MUNICIPIOS_IMRS).drop(columns="prioridade_desempate")


def calcular_pesos_populacionais(populacao, recorte):
    """Retorna a referência de MG e o recorte com os dois pesos municipais."""
    referencia = populacao[[COD_IBGE, "municipio", COD_REGIAO, "populacao"]].copy()
    for coluna in [COD_IBGE, "municipio", COD_REGIAO]:
        referencia[coluna] = _codigo_texto(referencia[coluna])
    referencia["populacao"] = pd.to_numeric(referencia["populacao"], errors="raise")

    # Os denominadores usam todos os municípios, inclusive os fora do recorte.
    codigos_mg = referencia[COD_IBGE].str.fullmatch(r"31\d{5}", na=False)
    codigos_duplicados = referencia[COD_IBGE].duplicated().any()
    if len(referencia) != N_MUNICIPIOS_MG or not codigos_mg.all() or codigos_duplicados:
        raise ValueError("A população deve conter uma linha por município dos 853 de Minas Gerais.")
    if referencia[["municipio", COD_REGIAO]].isna().any().any():
        raise ValueError("Há municípios sem nome ou sem região intermediária.")
    habitantes = referencia["populacao"].to_numpy(dtype=float, na_value=np.nan)
    if not (np.isfinite(habitantes) & (habitantes > 0)).all():
        raise ValueError("A população de cada município deve ser positiva e finita.")

    # Equivale a % pop. Reginte e % pop Estado da aba pop_2025_ibge.
    # O transform repete o total populacional da Região Intermediária em cada
    # município da região. A população municipal é dividida por esse total e
    # pela população total de MG para obter os dois pesos, respectivamente.
    populacao_regiao = referencia.groupby(COD_REGIAO)["populacao"].transform("sum")
    populacao_mg = referencia["populacao"].sum()
    referencia["peso_municipio_regiao"] = referencia["populacao"].div(populacao_regiao)
    referencia["peso_municipio_mg"] = referencia["populacao"].div(populacao_mg)

    # Busca os 50 municípios e seus pesos por código IBGE, preservando o recorte.
    if len(recorte) != N_MUNICIPIOS_IMRS or not recorte[COD_IBGE].isin(referencia[COD_IBGE]).all():
        raise ValueError("O recorte precisa conter 50 municípios presentes na referência populacional.")
    municipios = recorte[[COD_IBGE]].merge(referencia, on=COD_IBGE, validate="one_to_one")
    return referencia, municipios


def calcular_valores_imrs(df, coluna_valor, referencia, municipios):
    """Calcula a parcela do valor de cada localizador apropriada ao recorte."""
    # valor guarda a Previsão Orçamentária ou a Despesa Realizada Total antes
    # do rateio. Uma célula financeira vazia entra como zero. A Tabela 11
    # usa esse valor para aplicar os pesos individuais de cada município.
    dados = df.copy()
    for coluna in ["tipo_localizador", COD_IBGE, COD_REGIAO]:
        dados[coluna] = _codigo_texto(dados[coluna])
    dados["valor"] = pd.to_numeric(dados[coluna_valor], errors="raise").fillna(0).astype(float)
    if not np.isfinite(dados["valor"]).all():
        raise ValueError(f"A coluna {coluna_valor} contém valor financeiro infinito.")

    # Valida os localizadores antes do rateio. Um código válido fora do recorte
    # pode apropriar zero. Um código desconhecido indica falha na preparação.
    municipal = dados["tipo_localizador"].eq("municipal").fillna(False)
    regional = dados["tipo_localizador"].eq("regional").fillna(False)
    estadual = dados["tipo_localizador"].eq("estadual").fillna(False)
    if not (municipal | regional | estadual).all():
        raise ValueError("Há registros com tipo de localizador inválido ou ausente.")
    if not dados.loc[municipal, COD_IBGE].isin(referencia[COD_IBGE]).all():
        raise ValueError("Há localizador municipal sem código IBGE válido de Minas Gerais.")
    if not dados.loc[regional, COD_REGIAO].isin(referencia[COD_REGIAO]).all():
        raise ValueError("Há localizador regional sem código válido de região intermediária.")

    # Para localizador municipal, usa peso 1 se o código IBGE estiver na lista
    # dos 50 menores IMRS e peso 0 para os demais.
    peso = pd.Series(0.0, index=dados.index)
    peso.loc[municipal] = dados.loc[municipal, COD_IBGE].isin(municipios[COD_IBGE]).astype(float)

    # Para localizador regional, usa a participação dos municípios do recorte
    # na população da Região Intermediária. A soma dos pesos individuais dá
    # essa proporção. Regiões sem município no recorte recebem peso zero.
    pesos_regiao = municipios.groupby(COD_REGIAO)["peso_municipio_regiao"].sum()
    peso.loc[regional] = dados.loc[regional, COD_REGIAO].map(pesos_regiao).fillna(0)

    # Para localizador estadual, usa a população dos 50 municípios dividida
    # pela população de MG, equivalente à soma dos seus pesos estaduais.
    # valor_imrs é valor vezes o peso e corresponde a Proporcional Reginte IMRS
    # na referência. As Tabelas 9 e 10 somam essa coluna.
    peso.loc[estadual] = municipios["peso_municipio_mg"].sum()
    dados["valor_imrs"] = dados["valor"].mul(peso)
    return dados


def gerar_tabelas_imrs(planejamento, monitoramento, populacao, imrs, *, bases_processadas=None):
    """Devolve as tabelas e a memória municipal. Pode registrar as etapas em um dicionário."""
    recorte = selecionar_menores_imrs(imrs)
    referencia, municipios = calcular_pesos_populacionais(populacao, recorte)

    # Classifica as áreas antes do cálculo. Apropria o programado anual e o
    # realizado acumulado separadamente, usando os mesmos pesos territoriais.
    planejado = calcular_valores_imrs(
        classificar_areas(planejamento), "previsao_orcamentaria", referencia, municipios,
    )
    monitorado = calcular_valores_imrs(
        classificar_areas(monitoramento), "despesa_realizada_total", referencia, municipios,
    )

    # As Tabelas 9 e 10 agregam por programa e área. A Tabela 11 recebe também
    # os pesos dos 50 municípios para separar as três parcelas territoriais.
    tabela_9 = gerar_tabela_9(planejado, monitorado)
    tabela_10 = gerar_tabela_10(planejado, monitorado)
    tabela_11, memoria = gerar_tabela_11(planejado, monitorado, municipios)

    # Confere cada tabela com a apropriação original, separadamente para as duas
    # fontes. A tolerância absoluta absorve diferenças abaixo de um centavo.
    totais = {
        "programado": planejado["valor_imrs"].sum(),
        "realizado": monitorado["valor_imrs"].sum(),
    }
    tabelas = {"Tabela 9": tabela_9, "Tabela 10": tabela_10, "Tabela 11": tabela_11}
    for nome, tabela in tabelas.items():
        for coluna, esperado in totais.items():
            total = tabela[coluna].sum()
            if not isclose(total, esperado, rel_tol=0, abs_tol=0.005):
                raise ValueError(f"{nome}: total {coluna} de {total} diverge de {esperado}.")

    if bases_processadas is not None:
        # Reúne as entradas padronizadas, os resultados do recorte e do rateio
        # e as saídas já conferidas. O chamador pode gravá-los em disco.
        bases_processadas.update(
            planejamento=planejamento,
            monitoramento=monitoramento,
            populacao=populacao,
            imrs=imrs,
            recorte=recorte,
            referencia=referencia,
            municipios=municipios,
            planejado=planejado,
            monitorado=monitorado,
            tabela_9=tabela_9,
            tabela_10=tabela_10,
            tabela_11=tabela_11,
            memoria_tabela_11=memoria,
        )
    return tabelas, memoria


def exportar_tabelas_imrs(tabelas, caminho, *, quadros=None):
    """Escreve uma aba por tabela, com formatação numérica aplicada no Excel."""
    # Duas casas para os valores monetários e para os percentuais. O Excel
    # mantém códigos como texto, frações como números e percentuais nulos vazios.
    formatos = dict.fromkeys(COLUNAS_VALORES, "#,##0.00")
    for valor in COLUNAS_VALORES:
        for tipo in ("municipal", "regional", "estadual"):
            formatos[f"{valor}_{tipo}"] = "#,##0.00"
    formatos.update(dict.fromkeys(PERCENTUAIS, "0.00%"))
    exportar_excel(tabelas, caminho, formatos=formatos, quadros=quadros)
