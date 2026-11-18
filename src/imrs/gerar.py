"""Executa as tabelas do IMRS, confere os totais e prepara o relatório."""

from math import isclose

from src.exportacao.excel import exportar_excel
from src.imrs.preparar_imrs import (
    calcular_pesos_populacionais,
    calcular_valores_imrs,
    classificar_areas,
    selecionar_menores_imrs,
)
from src.imrs.tabela_09 import gerar_tabela_9
from src.imrs.tabela_10 import PERCENTUAIS, gerar_tabela_10
from src.imrs.tabela_11 import gerar_tabela_11


COLUNAS_VALORES = ["programado", "realizado"]
MESES = ("Fev", "Abr", "Jun", "Ago", "Out", "Dez")


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
