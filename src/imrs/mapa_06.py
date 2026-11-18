"""Mapa 6 do RIM, programação anual nos municípios do IMRS."""

from src.imrs.cartografia import desenhar_mapa


def gerar_mapa_06(malha, ano, bimestre, saida):
    """Gera o PNG a partir da malha já associada aos valores municipais."""
    destino = saida / f"Mapa_6_IMRS_{ano}_{bimestre}bim.png"
    desenhar_mapa(malha, "programado", ('#f5d4d0', '#a44b44'), destino)
    return destino
