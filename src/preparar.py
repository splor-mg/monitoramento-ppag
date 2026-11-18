"""Leitura, padronização de dados do PPAG e gravação em Parquet."""

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.config import PASTA_DADOS


PASTA_RAW = PASTA_DADOS / "raw"
PASTA_PROCESSED = PASTA_DADOS / "processed"
COLUNAS_PERIODO = ("Ano Monitoramento", "Mês Inicial", "Mês Final")


def carregar_excel(caminho, **kwargs):
    """Lê o Excel com as opções de aba, cabeçalho e tipos do chamador."""
    return pd.read_excel(caminho, **kwargs)


def carregar_csv(caminho, **kwargs):
    """Carrega uma base CSV ou TXT."""
    return pd.read_csv(caminho, **kwargs)


def padronizar_colunas(df):
    """Padroniza nomes de colunas para uso nas rotinas do projeto."""
    df = df.copy()

    # Remove espaços nas pontas e converte nomes como Código IBGE em código_ibge.
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


def carregar_txt(caminho, **kwargs):
    """
    Carrega arquivos TXT delimitados por |.

    Tenta primeiro UTF-8 e, se a decodificação falhar, usa Windows-1252.
    O chamador pode pedir só as colunas que usa e manter códigos como texto.
    """
    try:
        return pd.read_csv(
            caminho,
            sep="|",
            encoding="utf-8",
            low_memory=False,
            **kwargs,
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            caminho,
            sep="|",
            encoding="windows-1252",
            low_memory=False,
            **kwargs,
        )


def codigo_texto(serie):
    """Uniformiza identificadores de junção e sinaliza códigos em branco."""
    return serie.astype("string").str.strip().replace("", pd.NA)


def numero_decimal(serie):
    """Converte valores numéricos e textos decimais no formato brasileiro."""
    # Em valores como 1.234,56, o ponto separa milhares e a vírgula é decimal.
    # Células vazias ficam ausentes. Um texto financeiro inválido gera erro.
    texto = serie.astype("string").str.strip().replace("", pd.NA)
    com_virgula = texto.str.contains(",", na=False)
    texto.loc[com_virgula] = (
        texto.loc[com_virgula].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(texto, errors="raise")


def validar_periodo_monitoramento(dados, caminho, ano, bimestre):
    """Confere se o arquivo cobre janeiro até o último mês do bimestre."""
    esperado = zip(COLUNAS_PERIODO, (ano, 1, 2 * bimestre), strict=True)
    for campo, valor in esperado:
        iguais = pd.to_numeric(dados[campo], errors="raise").eq(valor).fillna(False)
        if dados.empty or not iguais.all():
            raise ValueError(f"{caminho.name} não corresponde a {ano}, {bimestre}º bimestre ({campo}).")


def gravar_parquet(df, caminho, *, index=False):
    """Grava as colunas com seus tipos e usa compressão Zstandard."""
    df.to_parquet(caminho, index=index, engine="pyarrow", compression="zstd")


def salvar_bases_processadas(bases, pasta):
    """Guarda os DataFrames do processamento juntos em uma pasta por execução."""
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")

    # Escreve todos os Parquets antes de disponibilizar a pasta. Cada rodada
    # ganha uma cópia própria e mantém os índices originais quando existirem.
    with TemporaryDirectory(dir=pasta) as temporario:
        registros = Path(temporario) / "registros"
        registros.mkdir()
        for nome, df in bases.items():
            gravar_parquet(df, registros / f"{nome}.parquet", index=None)
        registros.rename(destino)
    return destino


def converter_para_parquet(caminho_origem):
    """Converte uma base bruta para Parquet preservando a estrutura de pastas."""

    caminho_origem = Path(caminho_origem)

    # Replica a posição do arquivo em data/raw, trocando a extensão por .parquet.
    caminho_relativo = caminho_origem.relative_to(PASTA_RAW)

    caminho_destino = (
        PASTA_PROCESSED
        / caminho_relativo
    ).with_suffix(".parquet")

    caminho_destino.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    extensao = caminho_origem.suffix.lower()

    if extensao in {".txt", ".csv"}:
        df = carregar_txt(caminho_origem)

    elif extensao in {".xlsx", ".xls"}:
        df = carregar_excel(caminho_origem)

    else:
        print(f"Ignorado: {caminho_origem}")
        return

    gravar_parquet(df, caminho_destino)

    print(
        f"Convertido: {caminho_origem} "
        f"-> {caminho_destino}"
    )


def converter_bases_raw():
    """Converte os arquivos brutos de forma independente do cálculo do IMRS."""

    extensoes = {
        ".txt",
        ".csv",
        ".xlsx",
        ".xls",
    }

    arquivos = [
        caminho
        for caminho in PASTA_RAW.rglob("*")
        if caminho.is_file()
        and caminho.suffix.lower() in extensoes
    ]

    for caminho in arquivos:
        converter_para_parquet(caminho)

    print(f"\n{len(arquivos)} arquivo(s) processado(s).")


if __name__ == "__main__":
    converter_bases_raw()
