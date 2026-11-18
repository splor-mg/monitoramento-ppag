# Regras de Negócio — Desempenho Consolidado

## 1. Objetivo

Classificar as ações pelo desempenho físico e orçamentário até o bimestre nas Tabelas 5 e 6 e nos Gráficos 1 e 2 do RIM Geral (§ 2.2).

## 2. Bases, valores e chaves

Usar a base de ações do monitoramento do SIGPlan. Definir a validade pelos campos **Previsão Orçamentária do exercício (LOA)** e **Código do Tipo de Ação** dessa exportação. A unidade de contagem é a ação. Apurar os valores de janeiro ao último mês do bimestre nas duas dimensões.

| Variável | Tipo | Descrição |
|---|---|---|
| previsao_orcamentaria_loa | decimal | Previsão Orçamentária do exercício (LOA), usada no filtro de validade |
| codigo_tipo_acao | texto | Código do Tipo de Ação. O código 5 identifica Não Orçamentário |
| meta_fisica_periodo | decimal | Meta física inicialmente programada até o bimestre |
| realizado_fisico | decimal | Realização física acumulada até o bimestre |
| programado_orcamentario_periodo | decimal | Programação orçamentária inicial do período, ajustada quando aplicável |
| realizado_orcamentario | decimal | Despesa realizada acumulada no período, ajustada quando aplicável |
| iag | texto | Código 0 para Demais Projetos e Atividades e 1 para Projetos Estratégicos |
| valida_fisica | booleano | Ação orçamentária válida ou ação de tipo Não Orçamentário |
| valida_orcamentaria | booleano | Previsão Orçamentária do exercício (LOA) diferente de zero |
| intervalo_desempenho | texto | Intervalo de classificação da ação |

### 2.1. Unidade de observação e chave de relacionamento

Dentro do exercício e do período acumulado selecionados, identificar cada ação pela combinação **Código da Unidade Orçamentária Responsável pela Ação + Código da Ação**. Na planilha de junho de 2026, essa combinação identifica as 1.007 ações sem duplicatas.

Usar as duas colunas como chave. Para obter o realizado orçamentário de cada ação, somar primeiro os registros dos seus localizadores por essa chave e depois vincular o resultado à base de ações. Conferir a unicidade na base de ações e identificar localizadores sem ação correspondente.

O filtro de validade usa a Previsão Orçamentária do exercício (LOA) e o Tipo de Ação informados no próprio monitoramento.

### 2.2. Origem das variáveis orçamentárias

Na planilha de trabalho, o programado da taxa corresponde ao **Total Prog. Inicial Outras Desp.** até o bimestre. O realizado corresponde à soma de **Despesa Realizada Investimento** e **Despesa Realizada Outros** dos localizadores, agregada por UO e ação conforme o item 2.1. Essa soma retira a parcela de pessoal e auxílios do numerador.

## 3. Validade das ações e tratamento das despesas

### 3.1. Ações orçamentárias válidas

Contar a ação quando sua **Previsão Orçamentária do exercício (LOA)** for diferente de zero.

    valida_orcamentaria = previsao_orcamentaria_loa diferente de zero

Nas bases dos 2º e 3º bimestres de 2026, 14 ações possuem previsão da LOA igual a zero, entre elas as 5 não orçamentárias. O filtro resulta em **993 ações orçamentárias válidas** entre as 1.007 ações. O Tipo de Ação é usado no item 3.2 para acrescentar as não orçamentárias ao conjunto físico.

### 3.2. Ações físicas válidas

Contar as ações orçamentárias válidas do item 3.1 e acrescentar as ações de tipo **Não Orçamentário**, código `5`.

    valida_fisica = valida_orcamentaria ou codigo_tipo_acao igual a 5

Nas bases dos 2º e 3º bimestres de 2026, esse critério identifica **998 ações físicas válidas**, correspondentes às 993 orçamentárias válidas e às 5 não orçamentárias. A validade é determinada exclusivamente pela previsão orçamentária da LOA e pelo tipo de ação. A programação física do período é usada para classificar o desempenho.

A ação **4059 — GESTÃO DE UNIDADES E CONSERVAÇÃO**, da UO **02101 — INSTITUTO ESTADUAL DE FLORESTAS**, possui previsão orçamentária da LOA de **R$ 57.356.871,00** e tipo orçamentário. Ela é válida nas duas dimensões. Sua programação física do período é zero, portanto integra **Sem meta estabelecida** no físico.

### 3.3. Pessoal e auxílios na taxa orçamentária

Em ações com pessoal e auxílios e outras despesas, retirar a parcela de pessoal e auxílios do programado e do realizado usados na taxa orçamentária, conforme o item 2.2. Essa operação é feita após a identificação das ações válidas.

### 3.4. Aplicação dos filtros nas contagens

Manter os indicadores de validade na base de ações e aplicar o filtro da dimensão ao contar cada intervalo nas Tabelas 5 e 6. A classificação dos intervalos pode ser calculada na base completa.

No físico, contar somente registros com `valida_fisica = verdadeiro`. No orçamentário, contar somente registros com `valida_orcamentaria = verdadeiro`. Na Tabela 6, acrescentar o agrupamento por IAG. Uma ação física válida com programação do período igual a zero participa de **Sem meta estabelecida**.

## 4. Taxas e intervalos de desempenho

Calcular os intervalos por dimensão e aplicar a validade na contagem conforme o item 3.4. Em cada dimensão, quando a programação inicial acumulada até o bimestre for zero, classificar a ação como **Sem meta estabelecida**. Na análise física, esse critério usa `meta_fisica_periodo`.

Para contar **Sem meta estabelecida**, combinar o filtro de validade da dimensão com a programação inicial do período igual a zero. Identificar valores ausentes para conferência antes da classificação.

Quando houver programação do período diferente de zero, calcular a taxa:

    taxa física = realizado_fisico ÷ meta_fisica_periodo
    taxa orçamentária = realizado_orcamentario ÷ programado_orcamentario_periodo

Classificar antes de arredondar. Guardar as taxas como frações no DataFrame.

| Intervalo | Condição |
|---|---|
| Sem meta estabelecida | Ação válida na dimensão com programação inicial acumulada até o bimestre igual a zero |
| Sem execução | Com programação e execução igual a 0% |
| Crítico | Acima de 0% e abaixo de 70% |
| Satisfatório | De 70% a 130%, inclusive |
| Subestimado | Acima de 130% |

## 5. Tabela 5 — Ações válidas por intervalo de desempenho

### 5.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a um intervalo. A estrutura é:

| Variável | Tipo | Descrição |
|---|---|---|
| intervalo_desempenho | texto | Intervalo de classificação da ação |
| qtd_acoes_validas_fisico | inteiro | Quantidade de ações válidas no intervalo físico |
| percentual_acoes_validas_fisico | decimal | Participação do intervalo no total de válidas no físico |
| qtd_acoes_validas_orcamentario | inteiro | Quantidade de ações válidas no intervalo orçamentário |
| percentual_acoes_validas_orcamentario | decimal | Participação do intervalo no total de válidas no orçamentário |

### 5.2. Contagem do Desempenho Físico

#### 5.2.1. Contagem da quantidade de ações válidas

Contar as ações por intervalo de desempenho físico aplicando `valida_fisica = verdadeiro`.

#### 5.2.2. Cálculo do percentual de ações válidas no intervalo

    percentual = quantidade no intervalo físico ÷ total de ações válidas no físico

O denominador inclui **Sem meta estabelecida**.

### 5.3. Contagem do Desempenho Orçamentário

#### 5.3.1. Contagem da quantidade de ações válidas

Contar as ações por intervalo de desempenho orçamentário aplicando `valida_orcamentaria = verdadeiro`.

#### 5.3.2. Cálculo do percentual de ações válidas no intervalo

    percentual = quantidade no intervalo orçamentário ÷ total de ações válidas no orçamentário

O denominador inclui **Sem meta estabelecida**.

### 5.4. Combinação e filtro

Combinar as contagens física e orçamentária pelo intervalo. Usar apenas as ações válidas na respectiva dimensão. Para um intervalo sem ocorrências, exibir quantidade zero. Se a dimensão não tiver ações válidas, deixar seus percentuais em branco.

### 5.5. Resultado esperado

Granularidade das linhas de detalhe:

    1 linha = 1 intervalo de desempenho

Exemplo com os resultados dos TXT do 3º bimestre de 2026, usando a programação física inicial acumulada até junho.

| intervalo_desempenho | qtd_acoes_validas_fisico | percentual_acoes_validas_fisico | qtd_acoes_validas_orcamentario | percentual_acoes_validas_orcamentario |
| --- | ---: | ---: | ---: | ---: |
| Sem meta estabelecida | 207 | 0.2074 | 230 | 0.2316 |
| Sem execução | 36 | 0.0361 | 42 | 0.0423 |
| Crítico | 63 | 0.0631 | 194 | 0.1954 |
| Satisfatório | 584 | 0.5852 | 446 | 0.4491 |
| Subestimado | 108 | 0.1082 | 81 | 0.0816 |
| Total | 998 |  | 993 |  |

A linha de total soma as quantidades de ações válidas. As células de percentual dessa linha ficam em branco, como na tabela de referência.

## 6. Gráfico 1 — Porcentagem de ações com programação por intervalo de desempenho

### 6.1. Dados de entrada

Usar as quantidades física e orçamentária da Tabela 5 por intervalo.

### 6.2. Categorias e séries

No eixo horizontal, usar **Sem execução**, **Crítico**, **Satisfatório** e **Subestimado**. Em cada categoria, exibir duas séries em colunas, **Físico** e **Orçamentário**. O eixo vertical mostra o percentual.

### 6.3. Cálculo dos percentuais

    percentual = quantidade no intervalo ÷ soma das quantidades dos quatro intervalos na mesma dimensão

### 6.4. Combinação e filtro

Excluir **Sem meta estabelecida** e a linha Total da Tabela 5. Alinhar as duas séries pelo intervalo. Uma série sem ações com programação fica sem percentual calculado.

### 6.5. Resultado esperado

Quatro grupos de colunas com os percentuais do desempenho das ações válidas com programação no período. Cada série com ações programadas soma 100% antes do arredondamento.

## 7. Tabela 6 — Ações válidas por intervalo de desempenho e IAG

### 7.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a um intervalo. As colunas ficam em dois blocos, **Demais Projetos e Atividades** e **Projetos Estratégicos**.

| Variável | Tipo | Descrição |
|---|---|---|
| intervalo_desempenho | texto | Intervalo de classificação da ação |
| qtd_acoes_validas_fisico_demais | inteiro | Quantidade no intervalo físico de Demais Projetos e Atividades |
| percentual_acoes_validas_fisico_demais | decimal | Percentual no total de válidas no físico de Demais Projetos e Atividades |
| qtd_acoes_validas_orcamentario_demais | inteiro | Quantidade no intervalo orçamentário de Demais Projetos e Atividades |
| percentual_acoes_validas_orcamentario_demais | decimal | Percentual no total de válidas no orçamentário de Demais Projetos e Atividades |
| qtd_acoes_validas_fisico_estrategicos | inteiro | Quantidade no intervalo físico de Projetos Estratégicos |
| percentual_acoes_validas_fisico_estrategicos | decimal | Percentual no total de válidas no físico de Projetos Estratégicos |
| qtd_acoes_validas_orcamentario_estrategicos | inteiro | Quantidade no intervalo orçamentário de Projetos Estratégicos |
| percentual_acoes_validas_orcamentario_estrategicos | decimal | Percentual no total de válidas no orçamentário de Projetos Estratégicos |

### 7.2. Contagem do Desempenho Físico

#### 7.2.1. Contagem da quantidade de ações válidas

Contar as ações por intervalo de desempenho físico e grupo de IAG, aplicando `valida_fisica = verdadeiro`.

#### 7.2.2. Cálculo do percentual de ações válidas no intervalo

    percentual = quantidade no intervalo físico do IAG ÷ total de ações válidas no físico do mesmo IAG

O denominador inclui **Sem meta estabelecida**.

### 7.3. Contagem do Desempenho Orçamentário

#### 7.3.1. Contagem da quantidade de ações válidas

Contar as ações por intervalo de desempenho orçamentário e grupo de IAG, aplicando `valida_orcamentaria = verdadeiro`.

#### 7.3.2. Cálculo do percentual de ações válidas no intervalo

    percentual = quantidade no intervalo orçamentário do IAG ÷ total de ações válidas no orçamentário do mesmo IAG

O denominador inclui **Sem meta estabelecida**.

### 7.4. Combinação e filtro

Separar as ações válidas por IAG e dimensão antes de contar. Alinhar os dois blocos de IAG pelo intervalo. Aplicar o tratamento de contagens zero e percentuais sem denominador da Tabela 5 a cada combinação de IAG e dimensão.

### 7.5. Resultado esperado

Granularidade das linhas de detalhe:

    1 linha = 1 intervalo de desempenho

Exemplo com os resultados dos TXT do 3º bimestre de 2026, usando a programação física inicial acumulada até junho.

| intervalo_desempenho | qtd_acoes_validas_fisico_demais | percentual_acoes_validas_fisico_demais | qtd_acoes_validas_orcamentario_demais | percentual_acoes_validas_orcamentario_demais | qtd_acoes_validas_fisico_estrategicos | percentual_acoes_validas_fisico_estrategicos | qtd_acoes_validas_orcamentario_estrategicos | percentual_acoes_validas_orcamentario_estrategicos |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sem meta estabelecida | 195 | 0.2046 | 215 | 0.2268 | 12 | 0.2667 | 15 | 0.3333 |
| Sem execução | 32 | 0.0336 | 42 | 0.0443 | 4 | 0.0889 | 0 | 0.0000 |
| Crítico | 55 | 0.0577 | 183 | 0.1930 | 8 | 0.1778 | 11 | 0.2444 |
| Satisfatório | 570 | 0.5981 | 432 | 0.4557 | 14 | 0.3111 | 14 | 0.3111 |
| Subestimado | 101 | 0.1060 | 76 | 0.0802 | 7 | 0.1556 | 5 | 0.1111 |
| Total Geral | 953 |  | 948 |  | 45 |  | 45 |  |

A linha de total soma as quantidades de ações válidas. As células de percentual dessa linha ficam em branco, como na tabela de referência.

## 8. Gráfico 2 — Percentual de ações com programação por intervalo de desempenho e IAG

### 8.1. Dados de entrada

Usar as quantidades da Tabela 6 por intervalo, IAG e dimensão.

### 8.2. Categorias e séries

No eixo horizontal, identificar **Físico** e **Orçamentário** em cada bloco de IAG. As séries são **Sem execução**, **Crítico**, **Satisfatório** e **Subestimado**. O eixo vertical mostra o percentual.

### 8.3. Cálculo dos percentuais

    percentual = quantidade no intervalo do IAG e dimensão ÷ soma das quantidades dos quatro intervalos do mesmo IAG e dimensão

### 8.4. Combinação e filtro

Excluir **Sem meta estabelecida** e a linha Total Geral. Reunir as séries mantendo cada combinação de IAG e dimensão. Uma combinação sem ações com programação fica sem percentual calculado.

### 8.5. Resultado esperado

Quatro grupos de colunas, um por combinação de IAG e dimensão. Os percentuais dos intervalos em cada grupo com ações programadas somam 100% antes do arredondamento.

## 9. Fechamento

Somar as contagens dos grupos da Tabela 6 e conferir com a Tabela 5 para cada intervalo e dimensão.

## 10. Particularidades e pendências da referência

### 10.1. Denominador do desempenho físico

A planilha de abril usa **Realização Física 2026 ÷ Fis Programado Inicial de Jan a Abr**. A de junho usa **Realização Física 2026 ÷ Previsão Física 2026**, embora também possua a programação inicial até junho. A regra consolidada para os scripts usa a programação inicial acumulada até o bimestre em todos os períodos. Os resultados físicos de junho foram recalculados com esse denominador nas Tabelas 5 e 6 acima.

### 10.2. Acréscimo de uma ação em abril

Na planilha `Desempenho GERAL - Gabriel.xlsx` do 2º bimestre, a célula C4 de **Desempenho das ações** contém uma contagem condicional seguida de `+1`. A contagem encontra **238** ações físicas sem meta no período e a fórmula apresenta **239**. A célula C5 de **Por tipo de ação** repete o acréscimo no grupo **Demais Projetos e Atividades**, passando de **225** para **226**.

As duas células representam o mesmo acréscimo nos demonstrativos geral e por IAG. O total físico apresentado passa de **997** para **998** ações. O filtro por previsão orçamentária da LOA e tipo de ação inclui a **4059 da UO 02101**, pertencente a **Demais Projetos e Atividades**, mesmo com previsão física anual zero. Sua inclusão pela regra do item 3.2 reproduz o acréscimo de uma unidade nessas contagens. A fórmula manual registra esse acréscimo como `+1`, sem vínculo explícito à chave da ação.

### 10.3. Célula vazia no 1º bimestre

Na planilha do 1º bimestre, a previsão física anual da ação **4111 da UO 01631** está vazia em **AU16**. O critério `<>0` do CONT.SES conta essa célula vazia. A ação **4059 da UO 02101**, com zero numérico em **AU115**, fica fora. A regra dos itens 3.1 e 3.2 inclui a 4059 pela previsão orçamentária da LOA e exclui a 4111, de tipo orçamentário com previsão da LOA zero. As duas diferenças se compensam nas quantidades de **309 ações sem meta** e **998 ações físicas** apresentadas em fevereiro.

No 2º bimestre, a previsão física da 4111 passa a zero numérico em **BA16**. A fórmula passa a excluir as duas ações e encontra **238** ações sem meta antes do `+1`. Distinguir campo ausente de zero ao interpretar a referência e usar os critérios de validade do item 3 para definir quais ações contar.

### 10.4. Deslocamento na soma do realizado orçamentário de junho

Na planilha do 3º bimestre, a fórmula de **Outras despesas realizadas total (base loc)** usa as chaves de `A2:A66096` dos localizadores e a soma em `CC:CC`. Como os intervalos começam em linhas diferentes, a soma associa a chave ao valor da linha anterior. Esse deslocamento reproduz os 1.007 valores gravados na coluna AJ da planilha.

Os scripts somam **Despesa Realizada Investimento + Despesa Realizada Outros** pela combinação UO e ação, com os registros alinhados. As contagens orçamentárias de junho acima usam essa agregação corrigida.

No grupo estratégico, sete ações mudam de intervalo por essa diferença no realizado. São as ações 1002/UO 1191, 4412/UO 1481, 4360/UO 4491, 4363/UO 1231, 4398/UO 1231, 1088/UO 2071 e 4380/UO 1501. As 45 ações e os valores programados coincidem entre script e referência manual.

### 10.5. Referências à chave de outra ação em abril

Na planilha do 2º bimestre, cinco ações estratégicas mudam de intervalo porque o SOMASE da coluna AJ consulta a chave de outra linha da aba de ações. A soma dos localizadores pela chave correta coincide com os TXT nos cinco casos.

| Célula da fórmula | Referência usada na planilha | Chave da própria linha | UO / Ação |
|---|---|---|---|
| AJ668 | A129 | A668 | 1191 / 1002 |
| AJ536 | A199 | A536 | 1401 / 1098 |
| AJ361 | A355 | A361 | 1481 / 4412 |
| AJ379 | A431 | A379 | 1271 / 4328 |
| AJ895 | A450 | A895 | 4491 / 4360 |

A contagem estratégica orçamentária de abril no script é 17 sem meta, 3 sem execução, 7 críticas, 14 satisfatórias e 4 subestimadas. Na referência manual, as quantidades são 17, 8, 5, 11 e 4, respectivamente. O Gráfico 2 recalcula os percentuais sobre as 28 ações com programação.
