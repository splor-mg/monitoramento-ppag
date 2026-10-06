"""Leitura e preparação das bases utilizadas no monitoramento do PPAG."""

from pathlib import Path

import pandas as pd


PASTA_RAW = Path("data/raw")
PASTA_PROCESSED = Path("data/processed")


def carregar_excel(caminho, **kwargs):
    """Carrega uma base Excel."""
    return pd.read_excel(caminho, **kwargs)


def carregar_csv(caminho, **kwargs):
    """Carrega uma base CSV ou TXT."""
    return pd.read_csv(caminho, **kwargs)


def padronizar_colunas(df):
    """Padroniza nomes de colunas para uso nas rotinas do projeto."""
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


def carregar_txt(caminho):
    """
    Carrega arquivos TXT delimitados por |.

    Tenta primeiro UTF-8 e, caso não seja compatível,
    utiliza Windows-1252.
    """
    try:
        return pd.read_csv(
            caminho,
            sep="|",
            encoding="utf-8",
            low_memory=False,
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            caminho,
            sep="|",
            encoding="windows-1252",
            low_memory=False,
        )


def converter_para_parquet(caminho_origem):
    """Converte uma base bruta para Parquet preservando a estrutura de pastas."""

    caminho_origem = Path(caminho_origem)

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

    df.to_parquet(
        caminho_destino,
        index=False,
        engine="pyarrow",
        compression="zstd",
    )

    print(
        f"Convertido: {caminho_origem} "
        f"-> {caminho_destino}"
    )


def converter_bases_raw():
    """Converte todas as bases de data/raw para data/processed."""

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