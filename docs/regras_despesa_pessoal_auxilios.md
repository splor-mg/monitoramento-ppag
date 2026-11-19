# Regras de Negócio — Despesa de Pessoal e Auxílios

## 1. Objetivo

Apresentar a programação anual e o realizado acumulado de pessoal e auxílios por Setor de Governo, conforme a seção 2.5 do RIM Geral.

## 2. Bases, valores e chaves

### 2.1. Bases e valores considerados

Usar o QDD Fiscal para a programação anual e a execução do SIAFI para o realizado acumulado. Reutilizar o cadastro de ações do SIGPlan para identificar o Setor de Governo.

| Base | Variáveis de origem | Uso |
|---|---|---|
| `data/raw/planejamento/BASE_QDD_FISCAL.xlsx`, aba `BASE_QDD_FISCAL` | `ANO`, `COD_UO`, `AÇÃO`, `GRUPO_DESPESA`, `ELEMENTO_DESPESA`, `IPU`, `VALOR FINAL (R$)` | Programado anual, classificação das despesas e chaves de vínculo ao setor |
| CSV de execução do SIAFI | `ano`, `mes_cod`, `uo_cod`, `acao_cod`, `grupo_cod`, `elemento_item_cod`, `ipu_cod`, `vlr_liquidado` | Realizado mensal, classificação das despesas e chaves de vínculo ao setor |
| Cadastro de ações do SIGPlan já disponível | `Ano Monitoramento`, `Código da Unidade Orçamentária Responsável pela Ação`, `Código da Ação`, `Setor de Governo` | Correspondência entre exercício, UO, ação e setor |

O CSV conferido está em `dados-siafi-2026-main/data/execucao.csv/execucao.csv`. Seu campo `vlr_liquidado` corresponde a **Valor Despesa Realizada** no BO analisado. O **Relatório BO 1** da planilha manual permanece como referência de conferência, sem ser somado novamente ao SIAFI.

O valor programado é anual. O realizado acumula os valores mensais de janeiro até `2 × bimestre`, no mesmo exercício. **Total Prog. Inicial Desp. Pessoal e Auxílios** do SIGPlan é programação do período, portanto não substitui o programado anual do QDD.

### 2.2. Significado das principais variáveis

| Variável | Tipo | Descrição |
|---|---|---|
| ano | inteiro | Exercício selecionado nas três bases |
| mes | inteiro | Mês de execução, de 1 até o último mês do bimestre |
| codigo_uo | texto | Código da UO responsável pela ação, usado no vínculo ao setor |
| codigo_acao | texto | Código completo da ação, como `4239` |
| setor_governo | texto | Denominação do setor obtida no cadastro de ações |
| grupo_despesa | texto | Grupo da natureza de despesa; o código `1` identifica Pessoal e Encargos Sociais |
| elemento_despesa | texto | Elemento da natureza de despesa; o código `34` identifica Outras Despesas Decorrentes de Contratos de Terceirização |
| ipu | texto | Identificador de Procedência e Uso; códigos `7` para Auxílios e `9` para Precatórios e Sentenças Judiciais |
| programado_anual | decimal | Soma elegível de VALOR FINAL (R$) do QDD, correspondente a A |
| realizado | decimal | Soma elegível de vlr_liquidado do SIAFI até o bimestre, correspondente a B |

As correspondências entre os nomes originais e os nomes padronizados estão no [dicionário de dados](dicionario_dados.md).

### 2.3. Chave e vínculo ao Setor de Governo

Identificar a ação pela combinação **exercício + UO responsável pela ação + código completo da ação**. Usar `ANO + COD_UO + AÇÃO` no QDD e `ano + uo_cod + acao_cod` no SIAFI. Padronizar os códigos nas bases antes do cruzamento.

No repositório atual, obter o setor em `data/raw/monitoramento/<bimestre>bim/acoes_monitoramento.txt`. Usar **Ano Monitoramento**, **Código da Unidade Orçamentária Responsável pela Ação** e **Código da Ação** para formar a correspondência com **Setor de Governo**. Validar uma única correspondência por chave e identificar despesas sem setor antes da consolidação.

Várias linhas financeiras podem pertencer à mesma ação. Somar seus valores; a unicidade exigida é a do cadastro usado no vínculo, para que o cruzamento não multiplique despesas.

## 3. Regras comuns

### 3.1. Recorte de pessoal e auxílios

Aplicar o mesmo recorte ao programado e ao realizado. Incluir o registro quando atender a pelo menos uma destas condições:

    (Grupo de Despesa = 1 e IPU diferente de 9)
    ou Elemento de Despesa = 34
    ou IPU = 7

O teste `IPU diferente de 9` pertence à primeira condição. As condições de elemento 34 e IPU 7 são alternativas, conforme a expressão acima. Somar cada registro elegível uma única vez, mesmo quando atende a mais de uma condição. Aplicar o recorte às despesas de todas as ações, sem restringir à ação 2417 do programa 705.

### 3.2. Elemento e item da despesa na execução

Derivar o elemento a partir de `elemento_item_cod` antes de aplicar o recorte:

    código com até dois dígitos: elemento = código; item = 0
    código com mais de dois dígitos: item = dois últimos dígitos;
                                    elemento = dígitos anteriores

Assim, `3611` representa elemento 36 e item 11; `11` representa elemento 11 e item zero. O elemento participa do filtro. O item serve à conferência com o BO e não é um agrupamento da tabela final.

## 4. Tabela 12 — Programação e execução por Setor de Governo

### 4.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a um Setor de Governo, com a seguinte estrutura:

| Variável | Tipo | Descrição |
|---|---|---|
| setor_governo | texto | Denominação do setor |
| programado_anual | decimal | Programado PPAG anual elegível (A) |
| realizado | decimal | Realizado elegível acumulado até o bimestre (B) |
| analise_vertical | decimal | Participação do setor no realizado total (C) |
| execucao | decimal | Realizado do setor dividido pelo seu programado anual (B/A) |

### 4.2. Cálculo do Programado PPAG anual (A)

Selecionar `ANO` igual ao exercício no QDD, aplicar o recorte do item 3.1 e vincular as despesas ao setor conforme o item 2.3. Agrupar por `setor_governo` e calcular:

    programado_anual do setor (A) = soma de VALOR FINAL (R$) elegível do setor

Usar o valor anual integral, sem dividir pelo número de bimestres e sem somar VALOR UO (R$) ou VALOR SCPPO (R$) ao VALOR FINAL (R$).

### 4.3. Cálculo do Realizado (B)

Selecionar `ano` igual ao exercício e `mes_cod` de 1 até `2 × bimestre`, inclusive. Derivar o elemento, aplicar o recorte do item 3.1 e vincular ao setor. Agrupar por `setor_governo` e calcular:

    realizado do setor (B) = soma de vlr_liquidado elegível do setor no período

Somar os valores mensais uma vez. Usar `vlr_liquidado`, sem acrescentar `vlr_liquidado_retido` ou os campos de empenhado e pago.

### 4.4. Cálculo da Análise Vertical (C)

    realizado_total = soma de realizado de todos os setores
    analise_vertical (C) = realizado do setor ÷ realizado_total

Calcular após a agregação. Se o realizado total for zero, manter C nulo.

### 4.5. Cálculo de B/A

    execucao (B/A) = realizado do setor ÷ programado anual do setor

Se A for zero, manter a taxa nula. Guardar as duas taxas como frações; por exemplo, `0.20` corresponde a `20,00%` na apresentação.

### 4.6. Combinação e filtro

Calcular A e B separadamente e combinar pela união dos setores presentes nas duas agregações. Preservar setores que tenham somente programação ou somente execução e preencher com zero a parcela financeira ausente nessa combinação. Ausência de setor no cadastro deve ser identificada antes, conforme o item 2.3.

Calcular C e B/A depois da combinação. Ordenar os setores pelo nome e acrescentar a linha total ao final, somando as linhas de detalhe uma única vez. Recalcular a taxa do total como B total dividido por A total.

### 4.7. Resultado esperado

Granularidade das linhas de detalhe.

    1 linha = 1 Setor de Governo

Exemplo estrutural com valores ilustrativos.

| setor_governo | programado_anual | realizado | analise_vertical | execucao |
|---|---:|---:|---:|---:|
| Setor A | 1000.00 | 200.00 | 0.80 | 0.20 |
| Setor B | 0.00 | 50.00 | 0.20 | — |
| Setor C | 500.00 | 0.00 | 0.00 | 0.00 |
| **Despesa de Pessoal e Auxílios** | **1500.00** | **250.00** | **1.00** | **0.166667** |

O traço do exemplo representa taxa nula, pois A é zero. A linha **Despesa de Pessoal e Auxílios** apresenta a soma de A, a soma de B e a taxa calculada sobre esses totais. Sua análise vertical é 100% quando houver realizado total diferente de zero; caso contrário, é nula. O arredondamento dos valores e percentuais pertence à apresentação.

## 5. Fechamento

Conferir A total com a soma elegível do QDD e B total com a soma elegível do SIAFI no período, separadamente. O vínculo ao setor deve preservar essas duas somas. A soma das análises verticais deve ser 100% quando o realizado total for diferente de zero.

Na conferência das bases de 2026, todas as despesas elegíveis do QDD e do SIAFI de janeiro–junho encontraram setor no cadastro das 1.007 ações do 3º bimestre. O recorte produziu os mesmos totais no SIAFI e no BO:

| Período | Realizado de pessoal e auxílios |
|---|---:|
| Janeiro–abril de 2026 | R$ 27.768.088.568,47 |
| Janeiro–junho de 2026 | R$ 42.134.016.740,27 |

## 6. Pendência da referência manual

A correspondência de `ipu_cod` com **Procedência - Código** foi conferida nas bases analisadas. A regra de cálculo inclui o elemento 34 conforme o item 3.1; ainda falta conferir como esse elemento foi tratado nas tabelas dinâmicas da referência manual.
