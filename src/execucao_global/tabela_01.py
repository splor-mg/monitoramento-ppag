"""Tabela 1 — Programado e Realizado por tipo de orçamento."""

from .calculos import acrescentar_total, agregar, calcular_indicadores


def gerar_tabela_1(acoes):
    # Reúne os valores das ações em Orçamento Fiscal e Investimento das Empresas.
    detalhes = agregar(acoes, ["tipo_orcamento"])
    # Inclui o total e calcula seus indicadores sobre a soma dos valores.
    tabela = acrescentar_total(detalhes, "tipo_orcamento")
    return calcular_indicadores(tabela, detalhes["realizado"].sum())
