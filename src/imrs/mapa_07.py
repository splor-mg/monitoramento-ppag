"""Mapa 7 do RIM, execução acumulada nos municípios do IMRS."""

from src.imrs.cartografia import desenhar_mapa


def gerar_mapa_07(malha, ano, bimestre, saida):
    """Gera o PNG a partir da malha já associada aos valores municipais."""
    destino = saida / f"Mapa_7_IMRS_{ano}_{bimestre}bim.png"
    desenhar_mapa(malha, "realizado", ('#b6e5e0', '#236a68'), destino)
    return destino
