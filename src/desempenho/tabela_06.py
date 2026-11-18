"""Tabela 6 — contagens física e orçamentária em cada grupo de IAG."""

from src.desempenho.preparar_desempenho import GRUPOS_IAG
from src.desempenho.tabela_05 import gerar_tabela_5


def gerar_tabela_6(acoes):
    """Retorna os intervalos em dois blocos, Demais e Estratégicos."""
    blocos = []
    for codigo, grupo in GRUPOS_IAG.items():
        # Reaplica as mesmas contagens e os mesmos denominadores da Tabela 5
        # dentro do IAG. Isso mantém os critérios iguais nos dois demonstrativos.
        bloco = gerar_tabela_5(acoes.loc[acoes["iag"].eq(codigo)])
        bloco["intervalo_desempenho"] = bloco["intervalo_desempenho"].replace("Total", "Total Geral")
        bloco = bloco.rename(columns={c: f"{c}_{grupo}" for c in bloco if c != "intervalo_desempenho"})
        blocos.append(bloco)
    return blocos[0].merge(blocos[1], on="intervalo_desempenho", validate="one_to_one")
