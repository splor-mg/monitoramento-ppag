"""Bases do IMRS, recorte dos 50 municípios e rateio territorial."""

import numpy as np
import pandas as pd

from src.config import N_MUNICIPIOS_MG, PASTA_DADOS
from src.preparar import (
    COLUNAS_PERIODO,
    carregar_excel,
    carregar_txt,
    codigo_texto,
    numero_decimal,
    validar_periodo_monitoramento,
)


N_MUNICIPIOS_IMRS = 50
COD_IBGE = "codigo_ibge"
COD_REGIAO = "codigo_regiao_intermediaria"
GRUPOS = (
    "Áreas Temáticas Finalísticas",
    "Áreas Temáticas de Apoio e Suporte",
    "Outros Poderes",
)
CHAVES_AREA = ["grupo_area_tematica", "area_tematica"]


# Colunas do SIGPlan consultadas nesta seção.
COLUNAS_SIGPLAN = {
    "Código do Programa": "codigo_programa",
    "Nome do Programa": "programa",
    "Código da Área Temática": "codigo_area",
    "Área Temática": "area_tematica",
    "Código do Município IBGE": "codigo_ibge",
    "Código da Região Geográfica Intermediária": "codigo_regiao_intermediaria",
}
EXCLUSAO_LOGICA_ACAO = "Exclusão Lógica da Ação"

# O recorte de 2024 usado no RIM de 2026 (1º e 2º bimestres) seleciona
# Presidente Olegário entre os três municípios com IMRS 0,225 no corte.
DESEMPATE_IMRS_RIM = {2024: "3153400"}

# Classificação do PPAG 2024–2027, conforme o parecer da ALMG sobre o PL 1496/2023.
# Os códigos são os da exportação do SIGPlan. A área 15 agrega Outros Poderes.
GRUPO_POR_AREA = {
    **dict.fromkeys(["02", "03", "04", "05", "06", "07", "09", "10", "11"], GRUPOS[0]),
    **dict.fromkeys(["01", "08", "12", "13", "14"], GRUPOS[1]),
    "15": GRUPOS[2],
}


def _ler_localizadores(caminho, coluna_origem, coluna_valor, periodo=None):
    """Lê os campos do SIGPlan e identifica o alcance de cada localizador."""
    # Lê as chaves e o valor do exercício. No monitoramento, inclui as colunas
    # de período para conferência. No planejamento, inclui a marca de exclusão.
    colunas = {**COLUNAS_SIGPLAN, coluna_origem: coluna_valor}
    campos_origem = COLUNAS_PERIODO if periodo else [EXCLUSAO_LOGICA_ACAO]
    dados = carregar_txt(caminho, usecols=[*colunas, *campos_origem], dtype="string")

    # Confere Ano Monitoramento, Mês Inicial = 1 e Mês Final = 2 × bimestre.
    # Assim, a Despesa Realizada Total cobre janeiro até o fim do bimestre.
    if periodo:
        validar_periodo_monitoramento(dados, caminho, *periodo)
    else:
        # Remove da base de planejamento os localizadores de ações excluídas
        # antes do rateio e das somas do programado nas três tabelas do IMRS.
        excluida = dados[EXCLUSAO_LOGICA_ACAO].str.strip().str.casefold().eq("true")
        dados = dados.loc[~excluida.fillna(False)]

    # Mantém os campos de cálculo, com códigos como texto e valores numéricos.
    dados = dados[list(colunas)].rename(columns=colunas)
    for campo in COLUNAS_SIGPLAN.values():
        dados[campo] = codigo_texto(dados[campo])
    dados[coluna_valor] = numero_decimal(dados[coluna_valor])

    # Planejamento usa códigos como 06AT06 e monitoramento usa 06. Normaliza
    # para 06 e usa o código para atribuir o grupo da Área Temática.
    dados["codigo_area"] = dados["codigo_area"].str.extract(r"^(\d{2})(?:AT\1)?$", expand=False)
    dados["grupo_area_tematica"] = dados["codigo_area"].map(GRUPO_POR_AREA)

    # Códigos 3199901–3199913 representam regiões intermediárias. O código
    # 3199999 representa o estado. Confere se o sufixo dos códigos regionais
    # coincide com a Região Geográfica Intermediária informada. Os demais
    # códigos seguem como municipais para conferência com a base populacional.
    ibge = dados["codigo_ibge"]
    regional = ibge.str.fullmatch(r"31999(?:0[1-9]|1[0-3])", na=False)
    estadual = ibge.eq("3199999").fillna(False)
    regiao_esperada = ibge.loc[regional].str[-2:].str.lstrip("0")
    regiao_informada = dados.loc[regional, "codigo_regiao_intermediaria"].str.lstrip("0")
    if not regiao_informada.eq(regiao_esperada).fillna(False).all():
        raise ValueError(f"{caminho.name} contém localizador regional com código de região divergente.")
    dados["codigo_regiao_intermediaria"] = dados["codigo_regiao_intermediaria"].str.lstrip("0")
    dados["tipo_localizador"] = "municipal"
    dados.loc[regional, "tipo_localizador"] = "regional"
    dados.loc[estadual, "tipo_localizador"] = "estadual"
    return dados


def _ler_populacao(caminho, planejamento, monitoramento):
    """Associa a população dos municípios de MG à região registrada no SIGPlan."""
    if caminho.suffix == ".xlsx":
        # A FJP publicou em 2025 a projeção municipal para 2026, baseada no
        # IBGE. Na aba 2026, A:C contêm código IBGE, município e população total;
        # as três primeiras linhas são cabeçalhos. Não usa os recortes por sexo.
        populacao = carregar_excel(
            caminho, sheet_name="2026", header=None, skiprows=3, usecols="A:C",
            names=["codigo_ibge", "municipio", "populacao"], dtype="string",
        )
        populacao["codigo_ibge"] = codigo_texto(populacao["codigo_ibge"])
        populacao = populacao.loc[populacao["codigo_ibge"].str.fullmatch(r"31\d{5}", na=False)].copy()
        populacao["municipio"] = codigo_texto(populacao["municipio"])
        populacao["populacao"] = numero_decimal(populacao["populacao"])
    else:
        # Mantém a leitura da estimativa IBGE de 2025 para reproduzir rodadas
        # anteriores quando --ano-populacao 2025 for solicitado explicitamente.
        colunas = ["UF", "COD. UF", "COD. MUNIC", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA"]
        dados = carregar_excel(caminho, sheet_name="Municípios", header=1, usecols=colunas, dtype="string")
        mg = dados.loc[dados["UF"].eq("MG")].copy()
        populacao = pd.DataFrame({
            "codigo_ibge": mg["COD. UF"].str.strip() + mg["COD. MUNIC"].str.strip().str.zfill(5),
            "municipio": mg["NOME DO MUNICÍPIO"].str.strip(),
            "populacao": numero_decimal(mg["POPULAÇÃO ESTIMADA"]),
        })

    # Os registros municipais dos dois arquivos já contêm a região. Remove
    # repetições e valida que cada município tem uma única região intermediária.
    # Mantém todos os municípios do IBGE para formar a referência populacional.
    chaves = ["codigo_ibge", "codigo_regiao_intermediaria"]
    vinculos = pd.concat([
        planejamento.loc[planejamento["tipo_localizador"].eq("municipal"), chaves],
        monitoramento.loc[monitoramento["tipo_localizador"].eq("municipal"), chaves],
    ]).drop_duplicates()
    return populacao.merge(vinculos, on="codigo_ibge", how="left", validate="one_to_one")


def carregar_populacao(ano_populacao, planejamento, monitoramento):
    """Escolhe a edição local, comum ao IMRS e à Regionalização."""
    externas = PASTA_DADOS / "raw" / "externas"
    arquivo = (
        "projecoes_populacionais_fjp_2025_2047.xlsx" if ano_populacao == 2026
        else f"estimativa_dou_{ano_populacao}.xls"
    )
    return _ler_populacao(externas / arquivo, planejamento, monitoramento)


def _ler_imrs(caminho, ano_imrs):
    """Lê o índice municipal da edição usada para definir o recorte."""
    # Filtra a aba Geral pelo ano da edição e conserva IBGE7 e o índice. A
    # seleção dos 50 menores valores é feita depois nesta preparação.
    coluna_indice = "Índice Mineiro de Responsabilidade Social (imrs)"
    dados = carregar_excel(caminho, sheet_name="Geral", usecols=["Ano", "IBGE7", coluna_indice], dtype="string")
    anos = pd.to_numeric(dados["Ano"], errors="raise")
    edicao = dados.loc[anos.eq(ano_imrs), ["IBGE7", coluna_indice]].rename(
        columns={"IBGE7": "codigo_ibge", coluna_indice: "imrs"}
    )
    if edicao.empty:
        raise ValueError(f"A edição {ano_imrs} do IMRS não consta em {caminho.name}.")
    edicao["imrs"] = numero_decimal(edicao["imrs"])
    if ano_imrs in DESEMPATE_IMRS_RIM:
        edicao["prioridade_desempate"] = edicao["codigo_ibge"].ne(DESEMPATE_IMRS_RIM[ano_imrs])
    return edicao


def _padronizar_areas(planejamento, monitoramento):
    """Usa uma denominação por código de área nas duas fontes do SIGPlan."""
    chaves = ["codigo_area", "area_tematica"]
    nomes_plan = planejamento[chaves].dropna().drop_duplicates()
    nomes_mon = monitoramento[chaves].dropna().drop_duplicates()
    if nomes_plan["codigo_area"].duplicated().any() or nomes_mon["codigo_area"].duplicated().any():
        raise ValueError("Há mais de uma denominação para o mesmo código de área em uma base.")

    # O nome do planejamento tem prioridade quando a diferença é de grafia.
    # Se só houver nome no monitoramento, usa esse nome nas duas bases.
    nomes = pd.concat([nomes_plan, nomes_mon]).drop_duplicates("codigo_area").set_index("codigo_area")
    for base in (planejamento, monitoramento):
        base["area_tematica"] = base["codigo_area"].map(nomes["area_tematica"])


def carregar_bases_imrs(ano, bimestre, ano_imrs, ano_populacao):
    """Retorna as quatro bases prontas para as tabelas 9, 10 e 11."""
    raw = PASTA_DADOS / "raw"
    externas = raw / "externas"
    planejamento = _ler_localizadores(
        raw / "planejamento" / "localizadores_todos_planejamento.txt",
        f"Previsão Orçamentária {ano}",
        "previsao_orcamentaria",
    )
    monitoramento = _ler_localizadores(
        raw / "monitoramento" / f"{bimestre}bim" / "localizadores_monitoramento.txt",
        f"Despesa Realizada Total {ano}",
        "despesa_realizada_total",
        periodo=(ano, bimestre),
    )
    _padronizar_areas(planejamento, monitoramento)
    populacao = carregar_populacao(ano_populacao, planejamento, monitoramento)
    imrs = _ler_imrs(externas / "IMRS-consulta-indicadores.xlsx", ano_imrs)
    return planejamento, monitoramento, populacao, imrs


def classificar_areas(base):
    """Confere o vínculo entre cada Área Temática e seu grupo antes do rateio."""
    # A preparação associa o código da Área Temática a um grupo do PPAG e
    # padroniza a denominação entre planejamento e monitoramento. Aqui, limpa
    # os espaços nas duas chaves e trata textos vazios como dados ausentes.
    dados = base.copy()
    for coluna in CHAVES_AREA:
        dados[coluna] = dados[coluna].astype("string").str.strip().replace("", pd.NA)

    # Quando o registro já pertence a Outros Poderes e a área está vazia,
    # preenche a área com Outros Poderes para incluí-la no agrupamento.
    outros_poderes = dados["grupo_area_tematica"].eq("Outros Poderes").fillna(False)
    sem_area = dados["area_tematica"].isna()
    dados.loc[outros_poderes & sem_area, "area_tematica"] = "Outros Poderes"
    # Interrompe se sobrar área em branco ou se o grupo estiver fora da lista.
    # Assim, nenhum valor fica fora dos subtotais por falta de classificação.
    if not dados["grupo_area_tematica"].isin(GRUPOS).all() or dados["area_tematica"].isna().any():
        raise ValueError("Há registros sem classificação válida de área temática e grupo.")
    return dados


def selecionar_menores_imrs(df, coluna="imrs"):
    """Ordena uma edição do IMRS e retorna os 50 municípios do recorte."""
    # Converte o índice em número para que a ordenação use o valor do IMRS.
    dados = df.copy()
    dados[COD_IBGE] = codigo_texto(dados[COD_IBGE])
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
        referencia[coluna] = codigo_texto(referencia[coluna])
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
        dados[coluna] = codigo_texto(dados[coluna])
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
