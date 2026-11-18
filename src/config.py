"""Configurações gerais do projeto."""

from pathlib import Path


PASTA_RAIZ = Path(__file__).resolve().parents[1]

PASTA_DADOS = PASTA_RAIZ / "data"
PASTA_SAIDAS = PASTA_RAIZ / "outputs"
N_MUNICIPIOS_MG = 853
