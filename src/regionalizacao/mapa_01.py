"""Mapa 1 — localização e identificação das 13 regiões intermediárias."""

from .cartografia import desenhar_mapa


def gerar_mapa_1(municipios, regioes, destino):
    # Cada região recebe uma cor própria, seu número e o nome na legenda.
    return desenhar_mapa(municipios, regioes, destino)
