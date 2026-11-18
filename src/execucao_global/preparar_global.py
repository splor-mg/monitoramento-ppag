"""Lê as ações e identifica os quatro agrupamentos da Execução Global."""

import numpy as np

from src.config import PASTA_DADOS
from src.imrs.preparar_imrs import GRUPO_POR_AREA
from src.preparar import COLUNAS_PERIODO, carregar_txt, codigo_texto, numero_decimal, validar_periodo_monitoramento


MESES = ("Fev", "Abr", "Jun", "Ago", "Out", "Dez")
VALORES = ["programado_anual", "programado_periodo", "realizado"]


def carregar_acoes_global(ano, bimestre):
    """Retorna uma linha por UO e ação do período, incluindo execução sem LOA."""
    if bimestre not in range(1, 7):
        raise ValueError("O bimestre deve estar entre 1 e 6.")
    caminho = PASTA_DADOS / "raw" / "monitoramento" / f"{bimestre}bim" / "acoes_monitoramento.txt"
    campos = {
        "Código da Unidade Orçamentária Responsável pela Ação": "codigo_uo",
        "Código da Ação": "codigo_acao",
        "Código do Tipo de Ação": "codigo_tipo_acao",
        "Código do Identificador de Ação Governamental (IAG)": "iag",
        "Código da Área Temática": "codigo_area_tematica",
        "Área Temática": "area_tematica",
        "Código da Função": "codigo_funcao",
        "Função": "funcao",
        f"Previsão Orçamentária {ano} (LOA)": "programado_anual",
        f"Orç. Programado Inicial de Jan a {MESES[bimestre - 1]}": "programado_periodo",
        f"Despesa Realizada {ano}": "realizado",
    }
    dados = carregar_txt(caminho, usecols=[*campos, *COLUNAS_PERIODO], dtype="string")
    validar_periodo_monitoramento(dados, caminho, ano, bimestre)
    dados = dados.rename(columns=campos)[list(campos.values())]
    # Preserva os códigos como texto e retira preenchimentos como 02101/2101.
    for coluna in ["codigo_uo", "codigo_acao", "codigo_tipo_acao", "iag", "codigo_funcao"]:
        dados[coluna] = codigo_texto(dados[coluna]).str.replace(r"^0+(?=\d)", "", regex=True)
    if dados[["codigo_uo", "codigo_acao"]].isna().any().any() or dados.duplicated(["codigo_uo", "codigo_acao"]).any():
        raise ValueError("Há chave UO + ação ausente ou repetida na Execução Global.")
    for coluna in VALORES:
        dados[coluna] = numero_decimal(dados[coluna])
    if not np.isfinite(dados[VALORES].to_numpy(dtype=float, na_value=np.nan)).all():
        raise ValueError("Há valores financeiros ausentes ou inválidos nas ações.")

    # A Tabela 1 separa investimento das empresas pelos tipos 3, 6 e 8.
    # As quatro tabelas usam todas as ações do período e os mesmos três valores.
    dados["tipo_orcamento"] = "Orçamento Fiscal"
    dados.loc[dados["codigo_tipo_acao"].isin(["3", "6", "8"]), "tipo_orcamento"] = (
        "Orçamento de Investimento das Empresas Controladas pelo Estado"
    )
    dados["tipo_acompanhamento"] = dados["iag"].map({"0": "Demais Projetos e Atividades", "1": "Projetos Estratégicos"})
    # O código padronizado permite agrupar grafias 06 e 06AT06 na mesma área.
    dados["codigo_area_tematica"] = codigo_texto(dados["codigo_area_tematica"]).str.extract(r"^(\d{2})(?:AT\1)?$", expand=False)
    dados["grupo_area_tematica"] = dados["codigo_area_tematica"].map(GRUPO_POR_AREA).replace("Outros Poderes", "Outros")
    dados["area_tematica"] = codigo_texto(dados["area_tematica"])
    outros = dados["codigo_area_tematica"].eq("15") & dados["area_tematica"].isna()
    dados.loc[outros, "area_tematica"] = "Outros Poderes"
    dados["funcao"] = codigo_texto(dados["funcao"])
    classificacoes = ["codigo_tipo_acao", "tipo_acompanhamento", "codigo_area_tematica",
                      "grupo_area_tematica", "area_tematica", "codigo_funcao", "funcao"]
    if dados[classificacoes].isna().any().any():
        raise ValueError("Há ação sem classificação para a Execução Global.")
    for codigo, nome in [("codigo_area_tematica", "area_tematica"), ("codigo_funcao", "funcao")]:
        if dados[[codigo, nome]].drop_duplicates()[codigo].duplicated().any():
            raise ValueError(f"Há mais de uma denominação para {codigo}.")
    return dados
