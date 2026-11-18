"""Mapa 4 — programação anual per capita da Tabela 8, em tons de verde."""

from .cartografia import CORES_PER_CAPITA, desenhar_indicador


def gerar_mapa_4(municipios, regioes, tabela_8, destino):
    # O indicador já está em reais por habitante. Sua média é a média simples
    # dos 13 per capita regionais, excluindo o Total Estadual da tabela.
    return desenhar_indicador(municipios, regioes, tabela_8, "programado_per_capita", CORES_PER_CAPITA,
                             "R$ por habitante", 1, destino)
