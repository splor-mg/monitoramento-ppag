"""Coordena a geração dos dois mapas e a execução a partir de um Excel."""

import argparse
from pathlib import Path

from src.config import PASTA_SAIDAS
from src.imrs.cartografia import ler_tabela_11, preparar_mapa
from src.imrs.mapa_06 import gerar_mapa_06
from src.imrs.mapa_07 import gerar_mapa_07
from src.preparar_mapas import MALHA_PADRAO


def gerar_mapas_tabela(tabela, ano, bimestre, saida, malha=None):
    """Gera ambos os mapas com um único cruzamento municipal."""
    municipios = preparar_mapa(tabela, malha or MALHA_PADRAO)
    saida.mkdir(parents=True, exist_ok=True)
    return [
        gerar_mapa_06(municipios, ano, bimestre, saida),
        gerar_mapa_07(municipios, ano, bimestre, saida),
    ]


def gerar_mapas(tabela, ano, bimestre, saida, malha=None):
    """Lê a Tabela 11 de um Excel do RIM já gerado."""
    return gerar_mapas_tabela(ler_tabela_11(tabela), ano, bimestre, saida, malha)


def main():
    parser = argparse.ArgumentParser(description="Gera os mapas 6 e 7 do IMRS a partir da Tabela 11.")
    parser.add_argument("--ano", type=int, required=True, help="Ano do RIM.")
    parser.add_argument("--bimestre", type=int, choices=range(1, 7), required=True)
    parser.add_argument("--tabela", type=Path, help="Excel gerado pelo main.py com a aba Tabela 11.")
    parser.add_argument("--malha", type=Path, help="Malha do IBGE em ZIP, SHP, GeoJSON ou GPKG.")
    parser.add_argument("--saida", type=Path, default=PASTA_SAIDAS, help="Pasta dos dois PNGs.")
    args = parser.parse_args()
    tabela = args.tabela or PASTA_SAIDAS / f"IMRS_{args.ano}_{args.bimestre}bim.xlsx"
    try:
        for caminho in gerar_mapas(tabela, args.ano, args.bimestre, args.saida, args.malha):
            print(f"Mapa gerado: {caminho}")
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")


if __name__ == "__main__":
    main()
