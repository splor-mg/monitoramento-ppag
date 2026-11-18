"""Tabela 10 do RIM — valores e percentuais por área temática.

A aba A.TEM_final da planilha de referência usa Programado PPAG 2026 (A),
Realizado Jan - Fev (B), Análise Vertical - Subtotal (C), Análise Vertical -
Global (D) e B/A. No script, os nomes são programado, realizado,
participacao_grupo, participacao_global e execucao, respectivamente.
"""

import pandas as pd

from src.imrs.preparar_imrs import CHAVES_AREA, GRUPOS


PERCENTUAIS = ["participacao_grupo", "participacao_global", "execucao"]


def _agrupar_areas(base, valor):
    """Reproduz a Soma de Proporcional Reginte IMRS por área das abas de apoio."""
    # Agrupa pelo par grupo e Área Temática. Em cada par, soma valor_imrs,
    # a parcela de cada localizador que cabe aos 50 municípios. O argumento
    # valor define o nome dessa soma no resultado, programado ou realizado.
    return (
        base.groupby(CHAVES_AREA, as_index=False)["valor_imrs"]
        .sum()
        .rename(columns={"valor_imrs": valor})
    )


def gerar_tabela_10(planejamento, monitoramento):
    """Monta as linhas de detalhe da A.TEM_final com valores e percentuais."""
    # Programado PPAG (A) vem da Previsão Orçamentária do exercício, com os
    # registros marcados como Exclusão Lógica da Ação = True já retirados.
    # Realizado (B) vem da Despesa Realizada Total de janeiro ao fim do bimestre.
    # Nos dois casos, valor_imrs já incorpora o rateio territorial. As somas
    # correspondem às abas A.TEM_plan_2026 e A.TEM_exec_bim da referência.
    programado = _agrupar_areas(planejamento, "programado")
    realizado = _agrupar_areas(monitoramento, "realizado")

    # Junta as somas por grupo e Área Temática. A junção externa mantém as
    # áreas presentes só no planejamento ou só no monitoramento. Preenche com
    # zero o total ausente de um dos lados e preserva as áreas com dois zeros.
    tabela = programado.merge(realizado, on=CHAVES_AREA, how="outer", validate="one_to_one")
    valores = ["programado", "realizado"]
    tabela[valores] = tabela[valores].fillna(0)

    # Soma o Realizado (B) de todas as áreas para obter o Total Geral. Soma
    # também por grupo para obter o Realizado do Subtotal. O transform repete
    # o subtotal em cada linha do próprio grupo para servir de denominador.
    realizado_global = tabela["realizado"].sum()
    realizado_grupo = tabela.groupby("grupo_area_tematica")["realizado"].transform("sum")

    # Análise Vertical - Subtotal (C) divide o realizado da área pelo
    # realizado do grupo. O where deixa nulo o denominador quando ele é zero.
    tabela["participacao_grupo"] = tabela["realizado"].div(
        realizado_grupo.where(realizado_grupo.ne(0))
    )
    # Análise Vertical - Global (D) divide o realizado da área pelo realizado
    # do Total Geral. Se o Total Geral for zero, a coluna fica nula.
    if realizado_global == 0:
        tabela["participacao_global"] = float("nan")
    else:
        tabela["participacao_global"] = tabela["realizado"].div(realizado_global)

    # B/A divide Realizado (B) por Programado PPAG (A) da própria área. Se A
    # for zero, a taxa fica nula. A exportação apresenta frações como 0,20 em
    # formato percentual (20,00%) e deixa taxas nulas em branco no Excel.
    programado = tabela["programado"]
    tabela["execucao"] = tabela["realizado"].div(programado.where(programado.ne(0)))

    # Ordena os grupos como na A.TEM_final e, dentro de cada grupo, ordena as
    # áreas pelo nome. A saída traz uma linha de detalhe por área. Os subtotais
    # são usados nas divisões e ficam fora das linhas de detalhe exportadas.
    tabela["ordem_grupo"] = pd.Categorical(tabela["grupo_area_tematica"], GRUPOS, ordered=True)
    return (
        tabela.sort_values(["ordem_grupo", "area_tematica"])
        .loc[:, [*CHAVES_AREA, *valores, *PERCENTUAIS]]
        .reset_index(drop=True)
    )
