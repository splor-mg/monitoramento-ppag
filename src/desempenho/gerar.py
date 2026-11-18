"""Executa os quatro componentes de Desempenho Consolidado do RIM."""

import argparse
from pathlib import Path

from src.config import PASTA_DADOS, PASTA_SAIDAS
from src.desempenho.grafico_01 import gerar_grafico_1
from src.desempenho.grafico_02 import gerar_grafico_2
from src.desempenho.preparar_desempenho import carregar_acoes_desempenho
from src.desempenho.tabela_05 import gerar_tabela_5
from src.desempenho.tabela_06 import gerar_tabela_6
from src.exportacao.excel import exportar_excel
from src.preparar import salvar_bases_processadas


def gerar_desempenho(ano, bimestre, saida=None):
    """Lê os TXT, calcula as tabelas, confere e exporta Excel, PNG e memória."""
    acoes = carregar_acoes_desempenho(ano, bimestre)
    tabela_5 = gerar_tabela_5(acoes)
    tabela_6 = gerar_tabela_6(acoes)
    # Cada contagem dos dois IAGs precisa recompor a mesma linha da Tabela 5,
    # incluindo o total. Esta conferência precede a exportação dos produtos.
    for dimensao in ("fisico", "orcamentario"):
        coluna = f"qtd_acoes_validas_{dimensao}"
        soma = tabela_6[f"{coluna}_demais"] + tabela_6[f"{coluna}_estrategicos"]
        if not soma.equals(tabela_5[coluna]):
            raise ValueError(f"Tabela 6 diverge da Tabela 5 no {dimensao}.")
    pasta = Path(saida) if saida else PASTA_SAIDAS / f"Desempenho_{ano}_{bimestre}bim"
    pasta.mkdir(parents=True, exist_ok=True)
    grafico_1 = gerar_grafico_1(tabela_5, pasta / f"Grafico_1_{ano}_{bimestre}bim.png")
    grafico_2 = gerar_grafico_2(tabela_6, pasta / f"Grafico_2_{ano}_{bimestre}bim.png")
    tabelas = {"Tabela 5": tabela_5, "Tabela 6": tabela_6}
    formatos = {c: "0.00%" for t in tabelas.values() for c in t if c.startswith("percentual_")}
    exportar_excel(tabelas, pasta / f"Desempenho_{ano}_{bimestre}bim.xlsx", formatos=formatos)
    # Registra os DataFrames usados na execução, seguindo o fluxo do IMRS.
    # Os gráficos são calculados em memória a partir das tabelas, sem reler Excel.
    processadas = {"acoes": acoes, "tabela_5": tabela_5, "tabela_6": tabela_6,
                   "grafico_1": grafico_1.reset_index(), "grafico_2": grafico_2.reset_index()}
    salvar_bases_processadas(processadas, PASTA_DADOS / "processed" / "desempenho" / str(ano) / f"{bimestre}bim")
    return tabelas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera Tabelas 5 e 6 e Gráficos 1 e 2 do RIM.")
    parser.add_argument("--ano", type=int, required=True)
    parser.add_argument("--bimestre", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--saida", type=Path, help="Pasta de destino dos componentes.")
    args = parser.parse_args()
    try:
        gerar_desempenho(**vars(args))
        print(f"Componentes gerados para {args.ano}, {args.bimestre}º bimestre.")
        print(f"Saída: {args.saida or PASTA_SAIDAS / f'Desempenho_{args.ano}_{args.bimestre}bim'}")
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
