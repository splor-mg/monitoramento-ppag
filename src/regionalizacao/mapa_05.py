"""Mapa 5 — execução acumulada per capita da Tabela 8, em tons de verde."""

from .cartografia import CORES_PER_CAPITA, desenhar_indicador


def gerar_mapa_5(municipios, regioes, tabela_8, destino):
    # Divide a execução regional pela população na Tabela 8 e apenas desenha
    # o indicador pronto aqui. A barra mantém a unidade R$ por habitante.
    return desenhar_indicador(municipios, regioes, tabela_8, "executado_per_capita", CORES_PER_CAPITA,
                             "R$ por habitante", 1, destino)
