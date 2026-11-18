# Regras de Negócio — Execução Global

## 1. Objetivo

Consolidar a programação e a execução orçamentária do PPAG nas Tabelas 1 a 4 do RIM Geral (§ 2.1).

## 2. Base e valores considerados

Usar a base de ações do monitoramento do SIGPlan do exercício e do bimestre selecionados. B e C abrangem janeiro até o último mês do bimestre. A corresponde ao exercício inteiro.

| Variável | Tipo | Descrição |
|---|---|---|
| previsao_orcamentaria | decimal | Previsão Orçamentária do exercício (LOA), origem de A |
| programacao_inicial_periodo | decimal | Orçamento Programado Inicial até o fim do bimestre, origem de B |
| despesa_realizada | decimal | Despesa Realizada acumulada até o fim do bimestre, origem de C |

## 3. Variáveis de agrupamento

| Variável | Tipo | Descrição |
|---|---|---|
| codigo_tipo_acao | texto | Código do Tipo de Ação, usado na classificação do orçamento |
| iag | texto | Identificador de Ação Governamental, usado para definir o tipo de acompanhamento |
| codigo_area_tematica | texto | Código usado para agrupar por Área Temática e associá-la ao seu grupo |
| codigo_funcao | texto | Código usado para agrupar as ações por função |

## 4. Regras comuns

### 4.1. Totais e taxas

Calcular as taxas sobre os valores já somados. Quando o denominador for zero, deixar a taxa em branco. Guardar as taxas como frações no DataFrame e exibir como percentuais no relatório.

### 4.2. Classificação por IAG

Usar o **Código do Identificador de Ação Governamental (IAG)**.

| Código | Tipo de acompanhamento |
|---|---|
| 0 | Demais Projetos e Atividades |
| 1 | Projetos Estratégicos |

Aplicar o mesmo vínculo na Tabela 2 e nos demonstrativos de Desempenho Consolidado. Identificar códigos ausentes ou diferentes dos previstos antes de agrupar.

### 4.3. Classificação das Áreas Temáticas

Na codificação do SIGPlan usada para o PPAG 2024–2027, associar cada área ao seu grupo.

| Código da Área Temática | Grupo |
|---|---|
| 02, 03, 04, 05, 06, 07, 09, 10, 11 | Áreas Temáticas Finalísticas |
| 01, 08, 12, 13, 14 | Áreas Temáticas de Apoio e Suporte |
| 15 | Outros Poderes, apresentado no grupo Outros na Tabela 3 |

Padronizar códigos como `06AT06` e `06` para `06` antes do vínculo. Usar uma denominação por código nas bases. No IMRS, a denominação do planejamento tem prioridade quando a diferença é de grafia.

Para registros de Outros Poderes com denominação de área vazia, preencher **Outros Poderes**. Identificar códigos sem grupo ou áreas ainda sem denominação antes das somas, preservando os registros para conferência.

## 5. Tabela 1 — Programação e execução por tipo de orçamento

### 5.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a um tipo de orçamento. A estrutura abaixo é a das linhas de detalhe.

| Variável | Tipo | Descrição |
|---|---|---|
| tipo_orcamento | texto | Denominação do tipo de orçamento |
| programado_anual | decimal | Programado PPAG do exercício (A) |
| programado_periodo | decimal | Programação inicial acumulada até o bimestre (B) |
| realizado | decimal | Despesa realizada acumulada até o bimestre (C) |
| analise_vertical | decimal | Participação no realizado geral (D) |
| execucao_anual | decimal | Realizado em relação ao programado anual (C/A) |
| execucao_periodo | decimal | Realizado em relação ao programado do período (C/B) |

### 5.2. Cálculo do Programado PPAG do exercício (A)

Somar a Previsão Orçamentária do exercício (LOA) das ações do tipo de orçamento.

### 5.3. Cálculo do Programado até o bimestre (B)

Somar o Orçamento Programado Inicial de janeiro até o fim do bimestre das ações do tipo de orçamento.

### 5.4. Cálculo do Realizado (C)

Somar a Despesa Realizada acumulada até o fim do bimestre das ações do tipo de orçamento.

### 5.5. Cálculo da Análise Vertical (D)

    D = C da linha ÷ C do Total Geral

### 5.6. Cálculo de C/A

    C/A = realizado da linha ÷ programado anual da mesma linha

### 5.7. Cálculo de C/B

    C/B = realizado da linha ÷ programado até o bimestre da mesma linha

### 5.8. Combinação e filtro

Classificar pelo **Código do Tipo de Ação**. Na exportação de 2026, os códigos 3, 6 e 8 compõem o Orçamento de Investimento das Empresas Controladas pelo Estado. Os demais registros da base de referência compõem o Orçamento Fiscal.

Combinar A, B e C pela categoria de orçamento usando o mesmo recorte de ações nas três somas.

### 5.9. Resultado esperado

Granularidade das linhas de detalhe:

    1 linha = 1 tipo de orçamento

Exemplo estrutural com valores ilustrativos:

| tipo_orcamento | programado_anual | programado_periodo | realizado | analise_vertical | execucao_anual | execucao_periodo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Orçamento Fiscal | 900.00 | 360.00 | 270.00 | 0.90 | 0.30 | 0.75 |
| Orçamento de Investimento das Empresas Controladas pelo Estado | 100.00 | 40.00 | 30.00 | 0.10 | 0.30 | 0.75 |
| **Total Geral** | 1000.00 | 400.00 | 300.00 | 1.00 | 0.30 | 0.75 |

## 6. Tabela 2 — Programação e execução por tipo de acompanhamento

### 6.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a um tipo de acompanhamento da ação. A estrutura abaixo é a das linhas de detalhe.

| Variável | Tipo | Descrição |
|---|---|---|
| tipo_acompanhamento | texto | Grupo de acompanhamento identificado pelo IAG da ação |
| programado_anual | decimal | Programado PPAG do exercício (A) |
| programado_periodo | decimal | Programação inicial acumulada até o bimestre (B) |
| realizado | decimal | Despesa realizada acumulada até o bimestre (C) |
| analise_vertical | decimal | Participação no realizado geral (D) |
| execucao_anual | decimal | Realizado em relação ao programado anual (C/A) |
| execucao_periodo | decimal | Realizado em relação ao programado do período (C/B) |

### 6.2. Cálculo do Programado PPAG do exercício (A)

Somar a Previsão Orçamentária do exercício (LOA) das ações do tipo de acompanhamento.

### 6.3. Cálculo do Programado até o bimestre (B)

Somar o Orçamento Programado Inicial de janeiro até o fim do bimestre das ações do tipo de acompanhamento.

### 6.4. Cálculo do Realizado (C)

Somar a Despesa Realizada acumulada até o fim do bimestre das ações do tipo de acompanhamento.

### 6.5. Cálculo da Análise Vertical (D)

    D = C da linha ÷ C do Total Geral

### 6.6. Cálculo de C/A

    C/A = realizado da linha ÷ programado anual da mesma linha

### 6.7. Cálculo de C/B

    C/B = realizado da linha ÷ programado até o bimestre da mesma linha

### 6.8. Combinação e filtro

Usar o IAG para atribuir cada ação a **Demais Projetos e Atividades** ou **Projetos Estratégicos**. Combinar A, B e C pelo tipo de acompanhamento, com a mesma classificação nas três somas.

### 6.9. Resultado esperado

Granularidade das linhas de detalhe:

    1 linha = 1 tipo de acompanhamento

Exemplo estrutural com valores ilustrativos:

| tipo_acompanhamento | programado_anual | programado_periodo | realizado | analise_vertical | execucao_anual | execucao_periodo |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Demais Projetos e Atividades | 800.00 | 320.00 | 240.00 | 0.80 | 0.30 | 0.75 |
| Projetos Estratégicos | 200.00 | 80.00 | 60.00 | 0.20 | 0.30 | 0.75 |
| **Total Geral** | 1000.00 | 400.00 | 300.00 | 1.00 | 0.30 | 0.75 |

## 7. Tabela 3 — Programação e execução por Área Temática

### 7.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a uma Área Temática e ao grupo ao qual ela pertence. A estrutura abaixo é a das linhas de detalhe.

| Variável | Tipo | Descrição |
|---|---|---|
| codigo_area_tematica | texto | Código da Área Temática usado no agrupamento |
| area_tematica | texto | Denominação da Área Temática |
| grupo_area_tematica | texto | Áreas Temáticas de Apoio e Suporte, Áreas Temáticas Finalísticas ou Outros |
| programado_anual | decimal | Programado PPAG do exercício (A) |
| programado_periodo | decimal | Programação inicial acumulada até o bimestre (B) |
| realizado | decimal | Despesa realizada acumulada até o bimestre (C) |
| analise_vertical | decimal | Participação no realizado geral (D) |
| execucao_anual | decimal | Realizado em relação ao programado anual (C/A) |
| execucao_periodo | decimal | Realizado em relação ao programado do período (C/B) |

### 7.2. Cálculo do Programado PPAG do exercício (A)

Somar a Previsão Orçamentária do exercício (LOA) das ações da Área Temática.

### 7.3. Cálculo do Programado até o bimestre (B)

Somar o Orçamento Programado Inicial de janeiro até o fim do bimestre das ações da Área Temática.

### 7.4. Cálculo do Realizado (C)

Somar a Despesa Realizada acumulada até o fim do bimestre das ações da Área Temática.

### 7.5. Cálculo da Análise Vertical (D)

    D = C da linha ÷ C do Total Geral

### 7.6. Cálculo de C/A

    C/A = realizado da linha ÷ programado anual da mesma linha

### 7.7. Cálculo de C/B

    C/B = realizado da linha ÷ programado até o bimestre da mesma linha

### 7.8. Combinação e filtro

Combinar A, B e C pelo código da Área Temática. Usar a classificação do PPAG para reunir as áreas nos grupos de Apoio e Suporte e Finalísticas e apresentar **Outros Poderes** no grupo **Outros**. Somar as linhas de detalhe para formar cada subtotal. Contar cada detalhe uma vez no Total Geral e recalcular os três indicadores para subtotais e total.

### 7.9. Resultado esperado

Granularidade das linhas de detalhe:

    1 linha = 1 Área Temática dentro de um grupo

Exemplo estrutural com valores ilustrativos (trecho do demonstrativo):

| codigo_area_tematica | area_tematica | grupo_area_tematica | programado_anual | programado_periodo | realizado | analise_vertical | execucao_anual | execucao_periodo |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 03 | Educação | Finalísticas | 300.00 | 120.00 | 90.00 | 0.30 | 0.30 | 0.75 |
| 04 | Saúde | Finalísticas | 200.00 | 80.00 | 60.00 | 0.20 | 0.30 | 0.75 |
| … | … | Finalísticas | … | … | … | … | … | … |
|  | **Subtotal** | Finalísticas | Soma de A do grupo | Soma de B do grupo | Soma de C do grupo | C do grupo ÷ C geral | C do grupo ÷ A do grupo | C do grupo ÷ B do grupo |
| … | … | … | … | … | … | … | … | … |
|  | **Total Geral** |  | Soma de A | Soma de B | Soma de C | 1.00 | C total ÷ A total | C total ÷ B total |

## 8. Tabela 4 — Programação e execução por função

### 8.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a uma função orçamentária. A estrutura abaixo é a das linhas de detalhe.

| Variável | Tipo | Descrição |
|---|---|---|
| codigo_funcao | texto | Código da função orçamentária |
| funcao | texto | Denominação da função orçamentária |
| programado_anual | decimal | Programado PPAG do exercício (A) |
| programado_periodo | decimal | Programação inicial acumulada até o bimestre (B) |
| realizado | decimal | Despesa realizada acumulada até o bimestre (C) |
| analise_vertical | decimal | Participação no realizado geral (D) |
| execucao_anual | decimal | Realizado em relação ao programado anual (C/A) |
| execucao_periodo | decimal | Realizado em relação ao programado do período (C/B) |

### 8.2. Cálculo do Programado PPAG do exercício (A)

Somar a Previsão Orçamentária do exercício (LOA) das ações da função.

### 8.3. Cálculo do Programado até o bimestre (B)

Somar o Orçamento Programado Inicial de janeiro até o fim do bimestre das ações da função.

### 8.4. Cálculo do Realizado (C)

Somar a Despesa Realizada acumulada até o fim do bimestre das ações da função.

### 8.5. Cálculo da Análise Vertical (D)

    D = C da linha ÷ C do Total Geral

### 8.6. Cálculo de C/A

    C/A = realizado da linha ÷ programado anual da mesma linha

### 8.7. Cálculo de C/B

    C/B = realizado da linha ÷ programado até o bimestre da mesma linha

### 8.8. Combinação e filtro

Combinar A, B e C pelo código da função. Usar a denominação para exibição e manter a Reserva de Contingência quando constar da base.

### 8.9. Resultado esperado

Granularidade das linhas de detalhe:

    1 linha = 1 função

Exemplo estrutural com valores ilustrativos (trecho do demonstrativo):

| codigo_funcao | funcao | programado_anual | programado_periodo | realizado | analise_vertical | execucao_anual | execucao_periodo |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | Saúde | 300.00 | 120.00 | 90.00 | 0.30 | 0.30 | 0.75 |
| 12 | Educação | 200.00 | 80.00 | 60.00 | 0.20 | 0.30 | 0.75 |
| … | … | … | … | … | … | … | … |
|  | **Total Geral** | Soma de A | Soma de B | Soma de C | 1.00 | C total ÷ A total | C total ÷ B total |

## 9. Fechamento

Conferir separadamente, para o mesmo exercício, período e recorte de ações.

| Valor | Conferência entre os demonstrativos |
|---|---|
| A — Programado PPAG anual | Total Geral da Tabela 1 = Tabela 2 = Tabela 3 = Tabela 4 |
| B — Programado até o bimestre | Total Geral da Tabela 1 = Tabela 2 = Tabela 3 = Tabela 4 |
| C — Realizado acumulado | Total Geral da Tabela 1 = Tabela 2 = Tabela 3 = Tabela 4 |

Na Tabela 3, obter o total a partir das linhas de detalhe, contando cada valor uma vez. Recalcular os indicadores dos totais a partir de A, B e C agregados.

As imagens da cópia do RIM do 3º bimestre repetem as do 2º. Para conferir abril de 2026, o realizado de R$ 40.228.138.480,84 coincide com a base de ações.
