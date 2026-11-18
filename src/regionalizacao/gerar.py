"""Executa Tabelas 7 e 8 e Mapas 1 a 5 da Regionalização do RIM."""

import argparse
import warnings
from pathlib import Path

import numpy as np

from src.config import PASTA_DADOS, PASTA_SAIDAS
from src.execucao_global.preparar_global import carregar_acoes_global
from src.exportacao.excel import exportar_excel
from src.preparar import salvar_bases_processadas
from src.preparar_mapas import MALHA_PADRAO
from .cartografia import preparar_geometrias
from .mapa_01 import gerar_mapa_1
from .mapa_02 import gerar_mapa_2
from .mapa_03 import gerar_mapa_3
from .mapa_04 import gerar_mapa_4
from .mapa_05 import gerar_mapa_5
from .preparar_regionalizacao import agregar_populacao, apropriar_regioes, carregar_bases_regionalizacao
from .tabela_07 import gerar_tabela_7
from .tabela_08 import gerar_tabela_8


def gerar_regionalizacao(ano, bimestre, ano_populacao=2025, saida=None, malha=MALHA_PADRAO):
    planejamento, monitoramento, populacao = carregar_bases_regionalizacao(ano, bimestre, ano_populacao)
    regioes = agregar_populacao(populacao)
    programado = apropriar_regioes(planejamento, "programado", populacao, regioes)
    executado = apropriar_regioes(monitoramento, "executado", populacao, regioes)
    tabela_7 = gerar_tabela_7(programado, executado)
    tabela_8 = gerar_tabela_8(tabela_7, regioes)
    # Confere o total anual e o realizado com a Execução Global do mesmo período.
    acoes = carregar_acoes_global(ano, bimestre)
    esperado = acoes[["programado_anual", "realizado"]].sum().to_numpy(dtype=float)
    obtido = tabela_7.iloc[-1][["programado", "executado"]].to_numpy(dtype=float)
    if not np.allclose(obtido, esperado, rtol=0, atol=0.005):
        # As exportações de ações e localizadores podem divergir na origem.
        # Sinaliza a diferença e conserva os valores da fonte territorial.
        warnings.warn(
            f"Diferença entre fontes em {ano}/{bimestre}bim. "
            f"Regionalização (programado, executado): {obtido.tolist()}; "
            f"ações da Execução Global: {esperado.tolist()}.",
            stacklevel=2,
        )
    pasta = Path(saida) if saida else PASTA_SAIDAS / f"Regionalizacao_{ano}_{bimestre}bim"
    municipios, geometrias = preparar_geometrias(populacao, Path(malha))
    gerar_mapa_1(municipios, geometrias, pasta / f"Mapa_1_{ano}_{bimestre}bim.png")
    for numero, funcao, tabela in [(2, gerar_mapa_2, tabela_7), (3, gerar_mapa_3, tabela_7),
                                    (4, gerar_mapa_4, tabela_8), (5, gerar_mapa_5, tabela_8)]:
        funcao(municipios, geometrias, tabela, pasta / f"Mapa_{numero}_{ano}_{bimestre}bim.png")
    tabelas = {"Tabela 7": tabela_7, "Tabela 8": tabela_8}
    formatos = dict.fromkeys(["programado", "executado", "programado_per_capita", "executado_per_capita"], "#,##0.00")
    formatos.update(dict.fromkeys(["execucao", "analise_vertical"], "0.00%"))
    exportar_excel(tabelas, pasta / f"Regionalizacao_{ano}_{bimestre}bim.xlsx", formatos=formatos)
    # Mantém a memória das três parcelas de cada valor, os pesos e os dados
    # finais. As tabelas e mapas foram calculados diretamente em memória.
    memoria = {"planejamento": planejamento, "monitoramento": monitoramento, "populacao": populacao,
               "regioes": regioes, "programado": programado, "executado": executado,
               "tabela_7": tabela_7, "tabela_8": tabela_8}
    salvar_bases_processadas(memoria, PASTA_DADOS / "processed" / "regionalizacao" / str(ano) / f"{bimestre}bim" / f"pop_{ano_populacao}")
    return tabelas


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera as Tabelas 7 e 8 e os Mapas 1 a 5 do RIM.")
    parser.add_argument("--ano", type=int, required=True)
    parser.add_argument("--bimestre", type=int, required=True, choices=range(1, 7))
    parser.add_argument("--ano-populacao", type=int, default=2025)
    parser.add_argument("--saida", type=Path, help="Pasta de saída do Excel e dos PNGs.")
    parser.add_argument("--malha", type=Path, default=MALHA_PADRAO)
    args = parser.parse_args()
    try:
        gerar_regionalizacao(**vars(args))
        print(f"Regionalização gerada para {args.ano}, bimestre {args.bimestre}.")
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
