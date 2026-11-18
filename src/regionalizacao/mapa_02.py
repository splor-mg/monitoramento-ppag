"""Mapa 2 — programação anual global da Tabela 7, em tons de vermelho."""

from .cartografia import CORES_GLOBAIS, desenhar_indicador


def gerar_mapa_2(municipios, regioes, tabela_7, destino):
    # A conversão para R$ bilhões muda a unidade da legenda, preservando os
    # valores em reais na tabela. A escala toma a média das 13 regiões.
    return desenhar_indicador(municipios, regioes, tabela_7, "programado", CORES_GLOBAIS,
                             "R$ bilhões", 1_000_000_000, destino)
