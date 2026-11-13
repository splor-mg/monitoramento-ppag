"""Tabela 11 do RIM — valores por município e memória de cálculo.

Na referência, a aba MUN_juncao_plan_exec guarda as seis parcelas usadas
para calcular Total planejado e Total executado. A aba MUN_final apresenta
Município, Programado PPAG 2026 (R$) e Realizado Jan-Fev. A saída do script
também inclui o Código do Município IBGE para conferência e geração dos mapas.
"""

import pandas as pd


def _calcular_parcelas(base, municipios, prefixo):
    """Calcula as três parcelas da MUN_juncao_plan_exec para uma das bases."""
    # valor contém a Previsão Orçamentária ou a Despesa Realizada Total do
    # localizador, antes do rateio. Esta função distribui esses valores a
    # cada município com os pesos individuais calculados em src/imrs.py.

    # Planejado ou Executado exclusivamente municipal. Filtra os localizadores
    # do tipo municipal e soma valor pelo Código do Município IBGE. Em seguida,
    # busca essa soma para cada um dos 50 municípios. Sem localizador direto,
    # a parcela municipal fica em zero.
    por_municipio = (
        base.loc[base["tipo_localizador"].eq("municipal")]
        .groupby("codigo_ibge")["valor"]
        .sum()
    )
    direto = municipios["codigo_ibge"].map(por_municipio).fillna(0)

    # Planejado ou Executado proporcional a região. Filtra os localizadores
    # do tipo regional e soma valor pelo Código da Região Geográfica Intermediária.
    # Busca o total da região de cada município do recorte. Se a região não
    # tem localizador nessa base, usa zero para o total regional.
    por_regiao = (
        base.loc[base["tipo_localizador"].eq("regional")]
        .groupby("codigo_regiao_intermediaria")["valor"]
        .sum()
    )
    valor_regional = municipios["codigo_regiao_intermediaria"].map(por_regiao).fillna(0)
    # Aplica % pop. Reginte da aba pop_2025_ibge. O peso é a população do
    # município dividida pela população de toda a sua região intermediária.
    # O peso é o mesmo em todos os registros da região para aquele município,
    # então multiplicar o total da região equivale a ratear linha a linha.
    regional = valor_regional.mul(municipios["peso_municipio_regiao"])

    # Planejado ou Executado proporcional ao estado. Soma valor dos registros
    # do tipo estadual, que correspondem a DIVERSOS MUNICÍPIOS - ESTADUAL.
    # Para cada município, multiplica esse total por % pop Estado da referência,
    # calculado como população do município dividida pela população de toda MG.
    valor_estadual = base.loc[base["tipo_localizador"].eq("estadual"), "valor"].sum()
    estadual = municipios["peso_municipio_mg"].mul(valor_estadual)

    # Guarda uma coluna por parcela. O prefixo indica se ela pertence ao
    # programado ou ao realizado. Cada linha segue o índice da lista do IMRS.
    return pd.DataFrame({
        f"{prefixo}_municipal": direto,
        f"{prefixo}_regional": regional,
        f"{prefixo}_estadual": estadual,
    })


def gerar_tabela_11(planejamento, monitoramento, municipios):
    """Monta a memória municipal e as linhas de detalhe da MUN_final."""
    # Parte da lista de 50 municípios, equivalente à imrs_2024_50 no arquivo
    # de referência. Mantém todos eles, inclusive os de valor total zero.
    municipios = municipios.reset_index(drop=True)

    # Calcula as três parcelas em cada base. Da Previsão Orçamentária do
    # exercício, a preparação já retirou as linhas com Exclusão Lógica da Ação
    # = True. A Despesa Realizada Total cobre janeiro até o fim do bimestre.
    programado = _calcular_parcelas(planejamento, municipios, "programado")
    realizado = _calcular_parcelas(monitoramento, municipios, "realizado")

    # Reúne, lado a lado, o Código do Município IBGE, o nome e as seis parcelas
    # de cada município, como na MUN_juncao_plan_exec.
    identificacao = ["codigo_ibge", "municipio"]
    memoria = pd.concat([municipios[identificacao], programado, realizado], axis=1)

    # Soma na horizontal para cada município. Total planejado soma as três
    # parcelas do programado. Total executado soma as três do realizado.
    # A MUN_final mostra esses totais e a memória permite conferir cada parcela.
    tabela = memoria[identificacao].assign(
        programado=programado.sum(axis=1),
        realizado=realizado.sum(axis=1),
    )

    # Ordena as duas saídas pelo Código do Município IBGE. Cada uma contém
    # 50 linhas de detalhe. A conferência do Total Geral roda em src/imrs.py.
    ordem = tabela.sort_values("codigo_ibge").index
    return tabela.loc[ordem].reset_index(drop=True), memoria.loc[ordem].reset_index(drop=True)
