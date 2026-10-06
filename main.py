"""Execução principal das rotinas de monitoramento do PPAG."""

import argparse


def main(ano, bimestre):
    """Executa o processamento do RIM para o período informado."""

    print(f"Monitoramento do PPAG - {ano} - {bimestre}º bimestre")

    # As rotinas serão adicionadas aqui conforme forem desenvolvidas.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gera os produtos de monitoramento do PPAG."
    )

    parser.add_argument(
        "--ano",
        type=int,
        required=True,
        help="Ano de referência do PPAG.",
    )

    parser.add_argument(
        "--bimestre",
        type=int,
        choices=range(1, 7),
        required=True,
        help="Bimestre de referência (1 a 6).",
    )

    args = parser.parse_args()

    main(
        ano=args.ano,
        bimestre=args.bimestre,
    )