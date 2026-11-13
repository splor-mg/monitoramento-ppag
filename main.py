"""Execução principal das rotinas de monitoramento do PPAG."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from src.config import PASTA_DADOS, PASTA_SAIDAS
from src.exportar_word import exportar_word
from src.imrs import exportar_tabelas_imrs, gerar_tabelas_imrs
from src.preparar_dados import salvar_bases_processadas
from src.preparar_imrs import carregar_bases_imrs
from src.relatorio_imrs import analisar, montar_quadros


def main(ano, bimestre, ano_imrs=2024, ano_populacao=2025, saida=None):
    """Gera o Excel do período e registra os DataFrames utilizados no cálculo."""
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
    # Publica o arquivo de saída depois que todas as abas forem gravadas.
    with TemporaryDirectory(dir=caminho.parent) as pasta_temporaria:
        temporario = Path(pasta_temporaria) / caminho.name
        word_temporario = Path(pasta_temporaria) / word.name
        exportar_tabelas_imrs({**tabelas, "Memória Tabela 11": memoria}, temporario, quadros=quadros)
        exportar_word(quadros, texto, ano, bimestre, word_temporario)
        temporario.replace(caminho)
        word_temporario.replace(word)

    # Registra as etapas da mesma execução, identificadas pelas referências
    # usadas no relatório. As tabelas já foram calculadas em memória.
    pasta = PASTA_DADOS / "processed" / "imrs" / str(ano) / f"{bimestre}bim"
    registros = salvar_bases_processadas(processadas, pasta / f"imrs_{ano_imrs}_pop_{ano_populacao}")
    print(f"IMRS {ano_imrs} e população {ano_populacao} | RIM {ano}, {bimestre}º bimestre")
    print(f"Arquivo gerado: {caminho}")
    print(f"Relatório Word: {word}")
    print(f"DataFrames registrados: {registros}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera as tabelas 9, 10 e 11 do IMRS para o RIM.")
    parser.add_argument("--ano", type=int, required=True, help="Ano de referência do PPAG.")
    parser.add_argument(
        "--bimestre", type=int, choices=range(1, 7), required=True,
        help="Bimestre de referência (1 a 6).",
    )
    parser.add_argument(
        "--ano-imrs", type=int, default=2024, help="Edição de referência do IMRS (padrão 2024).",
    )
    parser.add_argument(
        "--ano-populacao", type=int, default=2025, help="Ano da estimativa do IBGE (padrão 2025).",
    )
    parser.add_argument("--saida", type=Path, help="Caminho do arquivo Excel a gerar.")
    args = parser.parse_args()
    try:
        main(**vars(args))
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro: {erro}\n")
