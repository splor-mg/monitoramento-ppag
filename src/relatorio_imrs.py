"""Monta as linhas de apresentação do RIM a partir dos resultados conferidos."""

AZUL = "1F4E78"
AZUL_CLARO = "DDEBF7"
MESES = ("Fev", "Abr", "Jun", "Ago", "Out", "Dez")
MESES_EXTENSO = ("fevereiro", "abril", "junho", "agosto", "outubro", "dezembro")
FONTE = "Fonte: Sistema de Informações Gerenciais e de Planejamento (SIGPlan)."
ELABORACAO = "Elaboração: Superintendência Central de Planejamento e Orçamento (SCPO)."
NOTA_PODERES = "Outros Poderes reúne os programas sem vinculação às áreas temáticas do Executivo."


def _dividir(valor, total):
    return valor / total if total else None


def montar_quadros(tabelas, ano, bimestre):
    """Devolve cabeçalhos, larguras relativas e linhas para Excel e Word."""
    periodo = f"Jan–{MESES[bimestre - 1]}"
    moeda = (f"Programado PPAG {ano} (R$)", f"Realizado {periodo} (R$)")
    programas, areas, municipios = (tabelas[f"Tabela {n}"] for n in (9, 10, 11))
    programado, realizado = areas[["programado", "realizado"]].sum()
    linhas_9 = [("dado", (codigo, nome, a, b)) for codigo, nome, a, b in programas.itertuples(index=False, name=None)]
    linhas_9.append(("total", ("", "Total Geral", programado, realizado)))

    linhas_10 = []
    for grupo, bloco in areas.groupby("grupo_area_tematica", sort=False):
        linhas_10.append(("grupo", (grupo, None, None, None, None, None)))
        for linha in bloco.drop(columns="grupo_area_tematica").itertuples(index=False, name=None):
            linhas_10.append(("dado", linha))
        if grupo != "Outros Poderes":
            a, b = bloco[["programado", "realizado"]].sum()
            linhas_10.append(("total", ("Subtotal", a, b, _dividir(b, b), _dividir(b, realizado), _dividir(b, a))))
    linhas_10.append(("total", ("Total Geral", programado, realizado, _dividir(realizado, realizado),
                                _dividir(realizado, realizado), _dividir(realizado, programado))))

    # Mantém o IBGE no Excel para o cruzamento dos mapas. O Word mostra só
    # Município, Programado e Realizado, como no relatório de referência.
    ordenados = municipios.sort_values("municipio", key=lambda s: s.str.normalize("NFKD").str.casefold())
    linhas_11 = [("dado", linha) for linha in ordenados.itertuples(index=False, name=None)]
    linhas_11.append(("total", ("", "Total Geral", programado, realizado)))

    return {
        "Tabela 9": (("Código do Programa", "Programa", *moeda), (11, 53, 18, 18), linhas_9),
        "Tabela 10": (("Áreas Temáticas", f"Programado PPAG {ano} (A)", f"Realizado {periodo} (B)",
                       "Análise Vertical – Subtotal (C)", "Análise Vertical – Global (D)", "B/A"),
                      (34, 17, 17, 12, 12, 8), linhas_10),
        "Tabela 11": (("codigo_ibge", "Município", *moeda), (13, 47, 20, 20), linhas_11),
    }


def numero_br(valor, casas=2):
    return f"{valor:,.{casas}f}".translate(str.maketrans(",.", ".,"))


def reais(valor):
    return f"R$ {numero_br(valor)}"


def percentual(valor):
    return f"{numero_br(valor * 100)}%"


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
