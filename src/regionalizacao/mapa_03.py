"""Mapa 3 — execução acumulada global da Tabela 7, em tons de vermelho."""

from .cartografia import CORES_GLOBAIS, desenhar_indicador


def gerar_mapa_3(municipios, regioes, tabela_7, destino):
    # Usa o Executado até o bimestre, incluindo as parcelas territoriais
    # apropriadas. Os limites da escala são calculados para este indicador.
    return desenhar_indicador(municipios, regioes, tabela_7, "executado", CORES_GLOBAIS,
                             "R$ bilhões", 1_000_000_000, destino)
