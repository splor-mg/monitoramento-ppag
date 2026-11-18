"""Gera Tabelas 1 a 4 do RIM a partir das ações do monitoramento."""

import argparse
from pathlib import Path

import numpy as np

from src.config import PASTA_DADOS, PASTA_SAIDAS
from src.exportacao.excel import exportar_excel
from src.preparar import salvar_bases_processadas
from .preparar_global import VALORES, carregar_acoes_global
from .tabela_01 import gerar_tabela_1
from .tabela_02 import gerar_tabela_2
from .tabela_03 import gerar_tabela_3
from .tabela_04 import gerar_tabela_4


def gerar_tabelas_global(acoes):
    """Calcula os quatro agrupamentos e compara seus totais com a base."""
    tabelas = {"Tabela 1": gerar_tabela_1(acoes), "Tabela 2": gerar_tabela_2(acoes),
               "Tabela 3": gerar_tabela_3(acoes), "Tabela 4": gerar_tabela_4(acoes)}
    esperado = acoes[VALORES].sum().to_numpy(dtype=float)
    for nome, tabela in tabelas.items():
        # A última linha é sempre o Total Geral, incluindo a Tabela 3,
        # cujos detalhes e subtotais não podem ser somados conjuntamente.
        total = tabela.iloc[-1][VALORES].to_numpy(dtype=float)
        if not np.allclose(total, esperado, rtol=0, atol=0.005):
            raise ValueError(f"{nome}: A, B ou C diverge da base de ações.")
    return tabelas


def gerar_global(ano, bimestre, saida=None):
    acoes = carregar_acoes_global(ano, bimestre)
    tabelas = gerar_tabelas_global(acoes)
    pasta = Path(saida) if saida else PASTA_SAIDAS / f"Global_{ano}_{bimestre}bim"
    pasta.mkdir(parents=True, exist_ok=True)
    formatos = dict.fromkeys(VALORES, "#,##0.00")
    formatos.update(dict.fromkeys(["analise_vertical", "execucao_anual", "execucao_periodo"], "0.00%"))
    exportar_excel(tabelas, pasta / f"Global_{ano}_{bimestre}bim.xlsx", formatos=formatos)
    memoria = {"acoes": acoes, **{f"tabela_{n}": t for n, t in enumerate(tabelas.values(), 1)}}
    salvar_bases_processadas(memoria, PASTA_DADOS / "processed" / "global" / str(ano) / f"{bimestre}bim")
    return tabelas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera as Tabelas 1 a 4 da Execução Global.")
    parser.add_argument("--ano", type=int, required=True)
    parser.add_argument("--bimestre", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--saida", type=Path, help="Pasta de saída do Excel.")
    args = parser.parse_args()
    try:
        gerar_global(**vars(args))
        print(f"Execução Global gerada para {args.ano}, bimestre {args.bimestre}.")
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
