# Regras de Negócio — Despesa de Pessoal e Auxílios

## 1. Objetivo

Apresentar a programação anual e o realizado acumulado de pessoal e auxílios por Setor de Governo, conforme a seção 2.5 do RIM Geral.

## 2. Bases, valores e chaves

Usar a programação anual do PPAG e a despesa realizada de janeiro até o fim do bimestre. Os registros precisam permitir identificar a classificação da despesa e o setor.

| Variável | Tipo | Descrição |
|---|---|---|
| setor_governo | texto | Setor ao qual pertence a unidade orçamentária responsável pela despesa |
| grupo_despesa | texto | Grupo da natureza de despesa, usado para identificar Pessoal e Encargos Sociais |
| elemento_despesa | texto | Elemento da natureza de despesa, usado para identificar contratos de terceirização |
| ipu | texto | Código da classificação orçamentária usado no recorte de auxílios e precatórios |
| programado_anual | decimal | Valor elegível programado para o exercício (A) |
| realizado | decimal | Valor elegível realizado no período acumulado (B) |

### 2.1. Fontes identificadas na planilha de abril de 2026

A planilha `Despesa de Pessoal - Gabriel.xlsx`, na pasta corporativa `RIM/2° Bimestre/RIM GERAL/Dados`, contém as bases complementares usadas na Tabela 12.

| Parcela | Aba de origem | Campo de valor |
|---|---|---|
| Programado anual | BASE_QDD_FISCAL | VALOR FINAL (R$) |
| Realizado acumulado | Relatório BO 1 | Valor Despesa Realizada |

O planejamento contém Grupo de Despesa, Elemento de Despesa e IPU. A execução contém **Grupo Despesa - Código**, **Elemento Despesa - Código**, **Item Despesa - Código** e **Procedência - Código**, além de exercício e mês.

### 2.2. Chave e vínculo ao setor

No exercício e período selecionados, agrupar os registros elegíveis por **Unidade Orçamentária + Ação**. No QDD, esses campos são **COD_UO** e **AÇÃO**, que contém o código completo, como `4239`. Na execução, são **Unidade Orçamentária - Código** e **Projeto_Atividade - Código**.

Vincular os valores ao **Setor de Governo** da ação pela mesma combinação de códigos. Na planilha de abril, as abas **Planejamento 2026** e **acoes_monitoramento** fornecem os vínculos usados na consolidação. Conferir a unicidade da correspondência e identificar registros sem setor antes de agrupar a tabela final.

## 3. Recorte das despesas

Incluir o registro quando atender a pelo menos uma destas condições:

    (Grupo de Despesa = 1 e IPU diferente de 9)
    ou Elemento de Despesa = 34
    ou IPU = 7

O grupo 1 corresponde a **Pessoal e Encargos Sociais**, o elemento 34 a **Outras Despesas Decorrentes de Contratos de Terceirização**, o IPU 9 a **Precatórios e Sentenças Judiciais** e o IPU 7 a **Auxílios**. Somar cada registro elegível uma vez. A ação 2417 do programa 705 concentra parte da despesa. Aplicar o recorte também aos registros das demais ações.

## 4. Tabela 12 — Programação e execução por Setor de Governo

### 4.1. Unidade de observação do dataframe final

Uma linha por Setor de Governo e uma linha total chamada **Despesa de Pessoal e Auxílios**.

| Variável | Tipo | Descrição |
|---|---|---|
| setor_governo | texto | Denominação do setor |
| programado_anual | decimal | Programado PPAG anual elegível (A) |
| realizado | decimal | Realizado elegível acumulado até o bimestre (B) |
| analise_vertical | decimal | Participação do setor no realizado total (C) |
| execucao | decimal | Realizado do setor dividido pelo seu programado anual (B/A) |

### 4.2. Cálculo do Programado PPAG anual (A)

Aplicar o recorte do item 3 ao QDD do exercício. Somar **VALOR FINAL (R$)** dos registros elegíveis e atribuir os valores ao setor conforme o item 2.2.

### 4.3. Cálculo do Realizado (B)

Selecionar o exercício e os meses de janeiro até `2 × bimestre` no relatório de execução. Aplicar o recorte das despesas e somar **Valor Despesa Realizada** dos registros elegíveis por setor.

### 4.4. Cálculo da Análise Vertical (C)

    C = realizado do setor ÷ realizado de todos os setores

### 4.5. Cálculo de B/A

    B/A = realizado do setor ÷ programado anual do setor

### 4.6. Combinação e filtro

Combinar A e B pelo Setor de Governo após a agregação de cada base. Preservar setores que tenham somente programação ou somente execução. Cada registro elegível participa uma vez das somas, inclusive quando atende a mais de uma condição do item 3.

Calcular os indicadores depois da combinação e deixar a taxa em branco quando o denominador for zero.

### 4.7. Resultado esperado

Granularidade das linhas de detalhe.

    1 linha = 1 Setor de Governo

Exemplo estrutural com valores ilustrativos.

| setor_governo | programado_anual | realizado | analise_vertical | execucao |
|---|---:|---:|---:|---:|
| Setor A | 1000.00 | 200.00 | 0.80 | 0.20 |
| Setor B | 500.00 | 50.00 | 0.20 | 0.10 |
| **Despesa de Pessoal e Auxílios** | **1500.00** | **250.00** | **1.00** | **0.166667** |

Somar A e B dos setores para obter a linha total. Recalcular B/A sobre os totais e apresentar C como 100% quando houver realizado total diferente de zero.

## 5. Fechamento e pendências da referência

Conferir o total dos setores com as parcelas elegíveis de programação e execução, separadamente. As fontes de abril estão identificadas no item 2.1. A reprodução completa ainda exige conferir o tratamento do elemento 34 nas tabelas dinâmicas e a correspondência entre **Procedência - Código** na execução e **IPU** no planejamento.

“Total Prog. Inicial Desp. Pessoal e Auxílios” da exportação de ações é programação do período. “Despesa Realizada Pessoal e Auxílios 2026” da exportação de localizadores soma R$ 3,41 bilhões no 2º bimestre, diante de R$ 27,76 bilhões na Tabela 12.
