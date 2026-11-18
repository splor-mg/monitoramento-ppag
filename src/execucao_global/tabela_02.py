"""Tabela 2 — Programado e Realizado por tipo de acompanhamento (IAG)."""

from .calculos import acrescentar_total, agregar, calcular_indicadores


def gerar_tabela_2(acoes):
    # O IAG já foi associado a Demais Projetos e Atividades ou Projetos
    # Estratégicos na preparação. Somam-se os três valores dentro de cada grupo.
    detalhes = agregar(acoes, ["tipo_acompanhamento"])
    tabela = acrescentar_total(detalhes, "tipo_acompanhamento")
    return calcular_indicadores(tabela, detalhes["realizado"].sum())
