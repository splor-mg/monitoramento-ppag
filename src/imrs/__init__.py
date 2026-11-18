"""Demonstrativos do Índice Mineiro de Responsabilidade Social."""

from src.config import N_MUNICIPIOS_MG
from src.imrs.gerar import exportar_tabelas_imrs, gerar_tabelas_imrs
from src.imrs.preparar_imrs import (
    N_MUNICIPIOS_IMRS,
    calcular_pesos_populacionais,
    calcular_valores_imrs,
    selecionar_menores_imrs,
)

__all__ = [
    "N_MUNICIPIOS_IMRS",
    "N_MUNICIPIOS_MG",
    "calcular_pesos_populacionais",
    "calcular_valores_imrs",
    "exportar_tabelas_imrs",
    "gerar_tabelas_imrs",
    "selecionar_menores_imrs",
]
