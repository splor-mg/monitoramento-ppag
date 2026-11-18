"""Análise do bimestre para a seção do IMRS."""

from src.exportacao.estilo import percentual, reais


MESES_EXTENSO = ("fevereiro", "abril", "junho", "agosto", "outubro", "dezembro")


def analisar(tabelas, bases, ano, bimestre):
    """Gera comparações a partir do período selecionado, com denominadores explícitos."""
    programas, areas, municipios = (tabelas[f"Tabela {n}"] for n in (9, 10, 11))
    programado, realizado = areas[["programado", "realizado"]].sum()
    abertura = (
        f"No {bimestre}º bimestre de {ano}, os 50 municípios com menor Índice Mineiro de "
        f"Responsabilidade Social (IMRS) tiveram {reais(programado)} programados no PPAG "
        f"e {reais(realizado)} realizados de janeiro a {MESES_EXTENSO[bimestre - 1]}."
    )
    sem_programacao = programas.loc[programas["programado"].eq(0) & programas["realizado"].gt(0)]
    por_programa = []
    if len(sem_programacao):
        quantidade = len(sem_programacao)
        programas_sem_previsao = "programa" if quantidade == 1 else "programas"
        por_programa.append(
            f"A despesa de {quantidade} {programas_sem_previsao} com valor programado igual a zero "
            f"somou {reais(sem_programacao['realizado'].sum())} no recorte. "
            "Nesses casos, a taxa de execução fica indefinida."
        )

    por_area = []
    grupos = areas.groupby("grupo_area_tematica", sort=False)[["programado", "realizado"]].sum()
    for coluna, total, rotulo in (("programado", programado, "programado"), ("realizado", realizado, "realizado")):
        if total:
            partes = [
                f"{nome} ({reais(valor)} ou {percentual(valor / total)})"
                for nome, valor in grupos[coluna].items()
            ]
            por_area.append(f"Distribuição do valor {rotulo} entre os grupos. " + ", ".join(partes) + ".")
    maiores = areas.loc[areas["programado"].gt(0)].nlargest(4, "programado")
    if programado and len(maiores):
        destaques = [
            f"{r.area_tematica} ({reais(r.programado)} ou {percentual(r.programado / programado)})"
            for r in maiores.itertuples()
        ]
        por_area.append("As áreas com maior programação foram " + ", ".join(destaques) + ".")
    finalisticas = areas.loc[areas["grupo_area_tematica"].eq("Áreas Temáticas Finalísticas")]
    if len(finalisticas) and finalisticas["realizado"].sum() > 0:
        lider = finalisticas.loc[finalisticas["realizado"].idxmax()]
        por_area.append(
            f"Nas Áreas Temáticas Finalísticas, {lider['area_tematica']} concentrou "
            f"{percentual(lider['realizado'] / finalisticas['realizado'].sum())} do realizado do grupo."
        )
    taxas = areas.loc[areas["programado"].gt(0) & areas["execucao"].notna()]
    if len(taxas):
        lider = taxas.loc[taxas["execucao"].idxmax()]
        por_area.append(f"A maior taxa de execução (B/A) foi de {lider['area_tematica']}, "
                        f"com {percentual(lider['execucao'])}.")

    por_municipio = []
    # A média estadual usa toda a base elegível de MG, incluindo os valores
    # municipais, regionais e estaduais, dividida pelos 853 municípios.
    for coluna, base, rotulo in (("programado", bases["planejado"], "programação"),
                                  ("realizado", bases["monitorado"], "execução")):
        media = base["valor"].sum() / len(bases["referencia"])
        acima = municipios.loc[municipios[coluna].gt(media)]
        proximo = municipios.loc[municipios[coluna].sub(media).abs().idxmin()]
        por_municipio.append(
            f"Na {rotulo}, a média estadual foi de {reais(media)}. "
            f"Dos {len(municipios)} municípios do recorte, {len(acima)} superaram esse valor. "
            f"O valor mais próximo da média foi o de {proximo['municipio']} "
            f"({reais(proximo[coluna])})."
        )
    return abertura, (por_programa, por_area, por_municipio)
