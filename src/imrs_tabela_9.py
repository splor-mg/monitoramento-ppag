"""Tabela 9 do RIM — valores programados e realizados por programa.

Na planilha de referência, a aba PROG_final apresenta Código do Programa,
Programa, Programado PPAG 2026 (R$) e Realizado Jan - Fev (R$). No script, as
colunas são codigo_programa, programa, programado e realizado. O exercício
e o mês final da execução vêm das bases selecionadas para cada bimestre.
"""

def _agrupar_programas(base, valor):
    """Transforma os valores por localizador em um total por programa."""
    # valor_imrs é a coluna que corresponde a Proporcional Reginte IMRS nas
    # abas de localizadores da referência. Cada linha já traz a parcela que
    # cabe ao recorte dos 50 municípios, calculada em src/imrs.py.
    # Um localizador municipal entra por inteiro se estiver no recorte e vale
    # zero fora dele. Nos localizadores regionais e estaduais, entra a fração
    # da população que os municípios do recorte representam no território.
    dados = base[["codigo_programa", "programa", "valor_imrs"]].copy()

    # Remove espaços e zeros de preenchimento do SIGPlan. Assim, 0001 e 1
    # representam o mesmo programa no agrupamento e na junção das duas bases.
    dados["codigo_programa"] = (
        dados["codigo_programa"].astype("string").str.strip().str.replace(r"^0+(?=[0-9])", "", regex=True)
    )
    dados["programa"] = dados["programa"].astype("string").str.strip()
    if not dados["codigo_programa"].str.fullmatch(r"[0-9]{1,3}", na=False).all():
        raise ValueError("A base contém código de programa ausente ou inválido.")
    if (dados["programa"].isna() | dados["programa"].eq("")).any():
        raise ValueError("A base contém programa sem denominação.")

    # Um código pode aparecer em vários localizadores da mesma base. Confere
    # se essas linhas usam o mesmo nome para que o agrupamento gere um só total.
    nomes = dados[["codigo_programa", "programa"]].drop_duplicates()
    if nomes["codigo_programa"].duplicated().any():
        raise ValueError("Há mais de uma denominação para o mesmo programa na base.")

    # Equivale à Soma de Proporcional Reginte IMRS das abas PROG_plan_2026 e
    # PROG_exec_bim. Soma pelo par código e nome e dá ao total o nome da coluna
    # de saída, programado ou realizado, conforme a base processada.
    return (
        dados.groupby(["codigo_programa", "programa"], as_index=False)["valor_imrs"]
        .sum()
        .rename(columns={"valor_imrs": valor})
    )


def gerar_tabela_9(planejamento, monitoramento):
    """Monta a junção de planejamento e execução usada na PROG_final."""
    # Programado PPAG usa a Previsão Orçamentária do exercício. Na preparação,
    # os registros com Exclusão Lógica da Ação = True já foram retirados.
    # Realizado usa a Despesa Realizada Total acumulada de janeiro até o fim
    # do bimestre. O rateio do IMRS já foi aplicado aos dois valores de origem.
    # A soma de cada base vem antes da junção para evitar multiplicar valores
    # quando um programa tem vários localizadores dos dois lados.
    programado = _agrupar_programas(planejamento, "programado")
    realizado = _agrupar_programas(monitoramento, "realizado")

    # Como na PROG_juncao_plan_exec, aproxima os dois totais pelo Código do
    # Programa. A junção externa mantém programas que aparecem em qualquer
    # base. A validação exige uma linha por código em cada lado da junção.
    tabela = programado.merge(
        realizado,
        on="codigo_programa",
        how="outer",
        suffixes=("_plan", "_mon"),
        validate="one_to_one",
    )

    # Exibe o nome do planejamento quando ele existe. Usa o do monitoramento
    # para programas que aparecem só na execução. Preenche com zero o valor
    # do lado sem registro para o programa.
    tabela["programa"] = tabela["programa_plan"].fillna(tabela["programa_mon"])
    valores = ["programado", "realizado"]
    tabela[valores] = tabela[valores].fillna(0)

    # Mantém a linha quando Programado PPAG ou Realizado é diferente de zero.
    # Assim, um programa com execução e sem programação aparece na tabela.
    tabela = tabela.loc[tabela[valores].ne(0).any(axis=1)]

    # Ordena pelo valor numérico do código para que 9 venha antes de 10.
    # Os valores seguem numéricos. O formato com duas casas decimais é aplicado
    # na exportação para Excel.
    return (
        tabela[["codigo_programa", "programa", *valores]]
        .sort_values("codigo_programa", key=lambda codigos: codigos.astype(int))
        .reset_index(drop=True)
    )
