"""Tabela 5 — ações válidas por intervalo de desempenho físico e orçamentário."""

import pandas as pd

from src.desempenho.preparar_desempenho import INTERVALOS


def gerar_tabela_5(acoes):
    """Retorna cinco intervalos e o Total, com percentuais como frações."""
    tabela = pd.DataFrame({"intervalo_desempenho": INTERVALOS})
    for dimensao, validade in [("fisico", "valida_fisica"), ("orcamentario", "valida_orcamentaria")]:
        # O filtro é aplicado na contagem. A base de ações completa permanece
        # disponível para conferir tanto os registros incluídos como os excluídos.
        validas = acoes.loc[acoes[validade], f"intervalo_{dimensao}"]
        quantidades = validas.value_counts().reindex(INTERVALOS, fill_value=0)
        coluna_qtd = f"qtd_acoes_validas_{dimensao}"
        coluna_pct = f"percentual_acoes_validas_{dimensao}"
        tabela[coluna_qtd] = quantidades.to_numpy(dtype=int)
        # O denominador da tabela inclui Sem meta estabelecida. Um conjunto
        # vazio mantém quantidades zero e percentuais indisponíveis.
        tabela[coluna_pct] = tabela[coluna_qtd] / len(validas) if len(validas) else float("nan")
        if quantidades.sum() != len(validas):
            raise ValueError(f"Há ação válida sem intervalo reconhecido no {dimensao}.")
    # Soma apenas as quantidades. A referência deixa o percentual do total vazio.
    total = {"intervalo_desempenho": "Total"}
    total.update({c: tabela[c].sum() for c in tabela if c.startswith("qtd_")})
    return pd.concat([tabela, pd.DataFrame([total])], ignore_index=True)
