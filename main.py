"""Execução principal das rotinas de monitoramento do PPAG."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from src.config import PASTA_DADOS, PASTA_SAIDAS
from src.exportacao.word import exportar_word
from src.imrs.gerar import exportar_tabelas_imrs, gerar_tabelas_imrs, montar_quadros
from src.imrs.preparar_imrs import carregar_bases_imrs
from src.imrs.texto import analisar
from src.preparar import salvar_bases_processadas


def main(ano, bimestre, ano_imrs=2024, ano_populacao=2026, saida=None, *, mapas=False):
    """Gera os produtos do IMRS e registra os DataFrames utilizados no cálculo."""
    # Recarrega as quatro bases brutas e prepara os valores de cada localizador
    # em memória. Reúne os DataFrames efetivamente usados nesta rodada.
    bases = carregar_bases_imrs(ano, bimestre, ano_imrs, ano_populacao)
    processadas = {}
    tabelas, memoria = gerar_tabelas_imrs(*bases, bases_processadas=processadas)
    quadros = montar_quadros(tabelas, ano, bimestre)
    texto = analisar(tabelas, processadas, ano, bimestre)

    # As três abas do RIM trazem os totais já conferidos. A memória registra
    # a origem de cada parcela municipal, regional e estadual da Tabela 11.
    caminho = Path(saida) if saida else PASTA_SAIDAS / f"IMRS_{ano}_{bimestre}bim.xlsx"
    if caminho.suffix.lower() != ".xlsx":
        raise ValueError("A saída do Excel deve ter extensão .xlsx.")
    word = caminho.with_suffix(".docx")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # Prepara os arquivos solicitados antes de gravá-los no destino final.
    with TemporaryDirectory(dir=caminho.parent) as pasta_temporaria:
        temporario = Path(pasta_temporaria) / caminho.name
        word_temporario = Path(pasta_temporaria) / word.name
        exportar_tabelas_imrs({**tabelas, "Memória Tabela 11": memoria}, temporario, quadros=quadros)
        exportar_word(quadros, texto, ano, bimestre, word_temporario)
        arquivos_mapa = []
        if mapas:
            from src.imrs.mapas import gerar_mapas_tabela

            # Reaproveita o resultado municipal, sem reler o Excel recém-gravado.
            arquivos_mapa = gerar_mapas_tabela(tabelas["Tabela 11"], ano, bimestre, Path(pasta_temporaria))
        temporario.replace(caminho)
        word_temporario.replace(word)
        for arquivo in arquivos_mapa:
            arquivo.replace(caminho.parent / arquivo.name)

    # Registra as etapas da mesma execução, identificadas pelas referências
    # usadas no relatório. As tabelas já foram calculadas em memória.
    pasta = PASTA_DADOS / "processed" / "imrs" / str(ano) / f"{bimestre}bim"
    registros = salvar_bases_processadas(processadas, pasta / f"imrs_{ano_imrs}_pop_{ano_populacao}")
    print(f"IMRS {ano_imrs} e população {ano_populacao} | RIM {ano}, {bimestre}º bimestre")
    print(f"Arquivo gerado: {caminho}")
    print(f"Relatório Word: {word}")
    for arquivo in arquivos_mapa:
        print(f"Mapa gerado: {caminho.parent / arquivo.name}")
    print(f"DataFrames registrados: {registros}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera as tabelas e, opcionalmente, os mapas do IMRS para o RIM.")
    parser.add_argument("--ano", type=int, required=True, help="Ano de referência do PPAG.")
    parser.add_argument(
        "--bimestre", type=int, choices=range(1, 7), required=True,
        help="Bimestre de referência (1 a 6).",
    )
    parser.add_argument(
        "--ano-imrs", type=int, default=2024, help="Edição de referência do IMRS (padrão 2024).",
    )
    parser.add_argument(
        "--ano-populacao", type=int, default=2026, help="População: FJP 2026 (padrão) ou IBGE 2025.",
    )
    parser.add_argument("--saida", type=Path, help="Caminho do arquivo Excel a gerar.")
    parser.add_argument("--mapas", action="store_true", help="Inclui os Mapas 6 e 7 na mesma execução.")
    args = parser.parse_args()
    try:
        main(**vars(args))
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
