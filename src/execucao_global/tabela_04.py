"""Tabela 4 — Programado e Realizado por função orçamentária."""

from .calculos import acrescentar_total, agregar, calcular_indicadores


def gerar_tabela_4(acoes):
    # Agrupa por código e nome da função. Preserva a Reserva de Contingência
    # quando existir e mantém funções com execução e programação zero.
    detalhes = agregar(acoes, ["codigo_funcao", "funcao"])
    detalhes = detalhes.sort_values("codigo_funcao", key=lambda c: c.astype(int))
    tabela = acrescentar_total(detalhes, "funcao")
    return calcular_indicadores(tabela, detalhes["realizado"].sum())
