"""Leitura das bases brutas e preparação dos vínculos usados no IMRS."""

import pandas as pd

from src.config import PASTA_DADOS
from src.imrs_tabela_10 import GRUPOS
from src.preparar_dados import carregar_excel, carregar_txt


# Traduz os cabeçalhos do SIGPlan para os nomes usados nos DataFrames.
COLUNAS_SIGPLAN = {
    "Código do Programa": "codigo_programa",
    "Nome do Programa": "programa",
    "Código da Área Temática": "codigo_area",
    "Área Temática": "area_tematica",
    "Código do Município IBGE": "codigo_ibge",
    "Código da Região Geográfica Intermediária": "codigo_regiao_intermediaria",
}
PERIODO_MONITORAMENTO = ["Ano Monitoramento", "Mês Inicial", "Mês Final"]
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


def _numero_decimal(serie):
    """Converte valores numéricos e textos decimais no formato brasileiro."""
    # Em valores como 1.234,56, o ponto separa milhares e a vírgula é decimal.
    # Células vazias ficam ausentes. Um texto financeiro inválido gera erro.
    texto = serie.astype("string").str.strip().replace("", pd.NA)
    com_virgula = texto.str.contains(",", na=False)
    texto.loc[com_virgula] = (
        texto.loc[com_virgula].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(texto, errors="raise")


def _ler_localizadores(caminho, coluna_origem, coluna_valor, periodo=None):
    """Lê os campos do SIGPlan e identifica o alcance de cada localizador."""
    # Lê as chaves e o valor do exercício. No monitoramento, inclui as colunas
    # de período para conferência. No planejamento, inclui a marca de exclusão.
    colunas = {**COLUNAS_SIGPLAN, coluna_origem: coluna_valor}
    campos_origem = PERIODO_MONITORAMENTO if periodo else [EXCLUSAO_LOGICA_ACAO]
    dados = carregar_txt(caminho, usecols=[*colunas, *campos_origem], dtype="string")

    # Confere Ano Monitoramento, Mês Inicial = 1 e Mês Final = 2 × bimestre.
    # Assim, a Despesa Realizada Total cobre janeiro até o fim do bimestre.
    if periodo:
        ano, bimestre = periodo
        esperado = dict(zip(PERIODO_MONITORAMENTO, [ano, 1, 2 * bimestre]))
        for campo, valor in esperado.items():
            iguais = pd.to_numeric(dados[campo], errors="raise").eq(valor).fillna(False)
            if dados.empty or not iguais.all():
                raise ValueError(f"{caminho.name} não corresponde a {ano}, {bimestre}º bimestre ({campo}).")
    else:
        # Remove da base de planejamento os localizadores de ações excluídas
        # antes do rateio e das somas do programado nas três tabelas do IMRS.
        excluida = dados[EXCLUSAO_LOGICA_ACAO].str.strip().str.casefold().eq("true")
        dados = dados.loc[~excluida.fillna(False)]

    # Mantém os campos de cálculo, com códigos como texto e valores numéricos.
    dados = dados[list(colunas)].rename(columns=colunas)
    for campo in COLUNAS_SIGPLAN.values():
        dados[campo] = dados[campo].str.strip().replace("", pd.NA)
    dados[coluna_valor] = _numero_decimal(dados[coluna_valor])

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
    colunas = ["UF", "COD. UF", "COD. MUNIC", "NOME DO MUNICÍPIO", "POPULAÇÃO ESTIMADA"]
    dados = carregar_excel(caminho, sheet_name="Municípios", header=1, usecols=colunas, dtype="string")
    mg = dados.loc[dados["UF"].eq("MG")].copy()

    # O código IBGE de sete dígitos combina o código da UF e os cinco dígitos
    # municipais. A população de toda MG compõe os denominadores dos rateios.
    populacao = pd.DataFrame({
        "codigo_ibge": mg["COD. UF"].str.strip() + mg["COD. MUNIC"].str.strip().str.zfill(5),
        "municipio": mg["NOME DO MUNICÍPIO"].str.strip(),
        "populacao": _numero_decimal(mg["POPULAÇÃO ESTIMADA"]),
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


def _ler_imrs(caminho, ano_imrs):
    """Lê o índice municipal da edição usada para definir o recorte."""
    # Filtra a aba Geral pelo ano da edição e conserva IBGE7 e o índice. A
    # seleção dos 50 menores valores é feita depois, em src/imrs.py.
    coluna_indice = "Índice Mineiro de Responsabilidade Social (imrs)"
    dados = carregar_excel(caminho, sheet_name="Geral", usecols=["Ano", "IBGE7", coluna_indice], dtype="string")
    anos = pd.to_numeric(dados["Ano"], errors="raise")
    edicao = dados.loc[anos.eq(ano_imrs), ["IBGE7", coluna_indice]].rename(
        columns={"IBGE7": "codigo_ibge", coluna_indice: "imrs"}
    )
    if edicao.empty:
        raise ValueError(f"A edição {ano_imrs} do IMRS não consta em {caminho.name}.")
    edicao["imrs"] = _numero_decimal(edicao["imrs"])
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
    populacao = _ler_populacao(
        externas / f"estimativa_dou_{ano_populacao}.xls", planejamento, monitoramento,
    )
    imrs = _ler_imrs(externas / "IMRS-consulta-indicadores.xlsx", ano_imrs)
    return planejamento, monitoramento, populacao, imrs
