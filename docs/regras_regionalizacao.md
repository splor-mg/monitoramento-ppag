# Regras de Negócio — Regionalização

## 1. Objetivo

Apresentar a programação e a execução orçamentária do PPAG nas 13 Regiões Geográficas Intermediárias de Minas Gerais nas Tabelas 7 e 8 e nos Mapas 1 a 5 do RIM Geral (§ 2.3).

## 2. Bases, valores e variáveis consideradas

Usar a programação anual dos localizadores de planejamento e a **Despesa Realizada Total** dos localizadores do monitoramento de janeiro até o fim do bimestre. Usar a população de referência e a malha territorial do IBGE.

| Variável | Tipo | Descrição |
|---|---|---|
| previsao_orcamentaria | decimal | Programação anual do localizador de planejamento |
| despesa_realizada_total | decimal | Execução acumulada do localizador de monitoramento |
| codigo_ibge | texto | Código usado para vincular cada município à sua região |
| codigo_regiao_intermediaria | texto | Código da Região Geográfica Intermediária usado no cruzamento com a malha |
| regiao_intermediaria | texto | Nome da Região Geográfica Intermediária |
| tipo_localizador | texto | Abrangência municipal, regional ou estadual |
| populacao_regiao | inteiro | Soma da população dos municípios da região |
| populacao_mg | inteiro | Soma da população das 13 regiões |
| peso_regiao | decimal | Participação da região na população de Minas Gerais |

### 2.1. População de referência

Na rotina atual, usar a estimativa municipal do IBGE de **2025**, em `data/raw/externas/estimativa_dou_2025.xls`, selecionada pelo parâmetro `ano_populacao`. Manter a mesma edição nos denominadores municipais, regionais e estadual e registrar a edição utilizada.

A matriz manual de 2026 identifica a aba como projeção para 2026 e a coluna como população de 2025. Registrar essa diferença de identificação ao conferir a referência. A população regional é a soma dos municípios da região e a estadual é a soma dos 853 municípios de MG.

### 2.2. Identificação e chaves dos localizadores

Reconhecer o alcance pelo **Código do Município IBGE** da exportação do SIGPlan.

| Tipo de localizador | Identificação |
|---|---|
| Municipal | Código IBGE de sete dígitos presente na referência municipal de MG |
| Regional | Códigos `3199901` a `3199913`, que representam as 13 regiões na exportação |
| Estadual | Código `3199999`, correspondente a Diversos Municípios – Estadual |

Nos registros regionais, conferir se o sufixo de `01` a `13` corresponde ao **Código da Região Geográfica Intermediária** informado no SIGPlan. Padronizar os zeros à esquerda antes da comparação.

Vincular os registros municipais à população pelo código IBGE. Cada município deve possuir um único vínculo regional. No cruzamento com a malha, usar a correspondência entre a codificação regional do SIGPlan e a da malha escolhida. Identificar códigos sem correspondência antes da apropriação.

## 3. Apropriação dos localizadores

Aplicar separadamente à programação anual e ao realizado acumulado.

No programado, desconsiderar os localizadores com **Exclusão Lógica da Ação = True** antes das somas e dos rateios. A base bruta permanece disponível para conferência. O realizado usa os localizadores do monitoramento do bimestre.

### 3.1. Localizador municipal

Atribuir o valor integral à Região Geográfica Intermediária do município identificado pelo código IBGE.

### 3.2. Localizador regional

Atribuir o valor integral à Região Geográfica Intermediária informada no próprio localizador.

### 3.3. Localizador estadual

Distribuir o valor de **Diversos Municípios – Estadual** pelo peso populacional de cada região:

    peso_regiao = populacao_regiao ÷ populacao_mg
    parcela_estadual_da_regiao = valor_estadual × peso_regiao

### 3.4. Apresentação dos mapas

No Mapa 1, usar cores categóricas e uma legenda numerada em ordem alfabética dos nomes. Nos Mapas 2 e 3, usar tons de rosa a vermelho escuro. Nos Mapas 4 e 5, usar tons de verde claro a verde escuro, seguindo as famílias de cores da referência.

Nos quatro mapas de valores, usar escala contínua com a média das 13 regiões no ponto intermediário da paleta. Interpolar entre mínimo e média e entre média e máximo de cada indicador. O Total Geral ou Estadual fica fora do cruzamento e da escala. Exibir a média e a barra de cores, com valores globais em R$ bilhões e per capita em R$ por habitante.

## 4. Mapa 1 — Regiões Geográficas Intermediárias de Minas Gerais

### 4.1. Malha territorial

Usar a malha das Regiões Geográficas Intermediárias do IBGE ou a malha municipal com identificação da região.

### 4.2. Identificação das regiões

Usar o código e o nome da Região Geográfica Intermediária. A cor é categórica e identifica a região.

### 4.3. Combinação e filtro

Selecionar as 13 regiões de Minas Gerais. Se partir da malha municipal, vincular o município à região por código IBGE e usar o vínculo para formar as áreas regionais.

### 4.4. Resultado esperado

Mapa com as 13 regiões diferenciadas por cor e identificadas na legenda. A malha regional serve de referência aos Mapas 2 a 5.

## 5. Tabela 7 — Valor global programado e executado por região

### 5.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a uma Região Geográfica Intermediária.

| Variável | Tipo | Descrição |
|---|---|---|
| codigo_regiao_intermediaria | texto | Código da Região Geográfica Intermediária usado no cruzamento com a malha |
| regiao_intermediaria | texto | Nome da Região Geográfica Intermediária |
| programado | decimal | Valor global programado no exercício (A) |
| executado | decimal | Valor global executado até o bimestre (B) |
| execucao | decimal | Executado em relação ao programado anual (B/A) |
| analise_vertical | decimal | Participação no total executado de Minas Gerais (C) |

### 5.2. Cálculo do Programado PPAG do exercício (A)

Na base de planejamento, aplicar a apropriação do item 3 e somar os valores por região:

    A da região = programado municipal + programado regional + parcela estadual do programado

### 5.3. Cálculo do Executado até o bimestre (B)

Na base de monitoramento, aplicar o mesmo tratamento à execução acumulada:

    B da região = executado municipal + executado regional + parcela estadual do executado

### 5.4. Cálculo de B/A

    B/A = executado da região ÷ programado anual da mesma região

### 5.5. Cálculo da Análise Vertical (C)

    C = executado da região ÷ soma do executado das 13 regiões

### 5.6. Combinação e filtro

Combinar A e B pelo código da região após agregar cada base. Preservar as 13 regiões e calcular os indicadores após a combinação. Deixar a taxa em branco se o denominador for zero.

### 5.7. Resultado esperado

Granularidade das linhas de detalhe:

    1 linha = 1 Região Geográfica Intermediária

Exemplo estrutural com valores ilustrativos (trecho do demonstrativo):

| codigo_regiao_intermediaria | regiao_intermediaria | programado | executado | execucao | analise_vertical |
| --- | --- | ---: | ---: | ---: | ---: |
| … | Barbacena | 200.00 | 60.00 | 0.30 | 0.20 |
| … | Belo Horizonte | 300.00 | 120.00 | 0.40 | 0.40 |
| … | … | … | … | … | … |
|  | **Total Geral** | Soma de A das 13 regiões | Soma de B das 13 regiões | B total ÷ A total | 1.00 |

Conferir os totais de A e B com o programado anual e o realizado da Execução Global para o mesmo período.

## 6. Mapa 2 — Gasto Global Programado por Região Geográfica Intermediária

### 6.1. Malha e chave de identificação

Usar as 13 Regiões Geográficas Intermediárias do Mapa 1, identificadas por `codigo_regiao_intermediaria`.

### 6.2. Indicador e unidade

Usar **Programado PPAG do exercício (A) da Tabela 7**, em reais.

### 6.3. Referência para a escala de cor

    média regional = soma dos 13 valores de programado anual ÷ 13

Aplicar a escala contínua do item 3.4, com tons mais claros até a média e mais escuros acima dela.

### 6.4. Combinação e filtro

Vincular o indicador à malha pelo código da região. Usar apenas as 13 linhas de detalhe da tabela, excluindo a linha de total do cruzamento e da média.

### 6.5. Resultado esperado

Mapa das 13 regiões de Minas Gerais coloridas segundo a programação anual, com identificação das regiões e legenda do indicador.

## 7. Mapa 3 — Gasto Global Executado por Região Geográfica Intermediária

### 7.1. Malha e chave de identificação

Usar as 13 Regiões Geográficas Intermediárias do Mapa 1, identificadas por `codigo_regiao_intermediaria`.

### 7.2. Indicador e unidade

Usar **Executado acumulado até o bimestre (B) da Tabela 7**, em reais.

### 7.3. Referência para a escala de cor

    média regional = soma dos 13 valores de realizado acumulado ÷ 13

Aplicar a escala contínua do item 3.4, com tons mais claros até a média e mais escuros acima dela.

### 7.4. Combinação e filtro

Vincular o indicador à malha pelo código da região. Usar apenas as 13 linhas de detalhe da tabela, excluindo a linha de total do cruzamento e da média.

### 7.5. Resultado esperado

Mapa das 13 regiões de Minas Gerais coloridas segundo a execução acumulada do bimestre, com identificação das regiões e legenda do indicador.

## 8. Tabela 8 — Gasto per capita programado e executado por região

### 8.1. Unidade de observação do dataframe final

Cada linha de detalhe corresponde a uma Região Geográfica Intermediária. Os valores per capita são expressos em reais por habitante.

| Variável | Tipo | Descrição |
|---|---|---|
| codigo_regiao_intermediaria | texto | Código da Região Geográfica Intermediária usado no cruzamento com a malha |
| regiao_intermediaria | texto | Nome da Região Geográfica Intermediária |
| programado_per_capita | decimal | Programado PPAG por habitante (A) |
| executado_per_capita | decimal | Executado acumulado por habitante (B) |
| execucao | decimal | Executado per capita em relação ao programado per capita (B/A) |
| analise_vertical | decimal | Executado per capita da região em relação ao executado per capita estadual (C) |

### 8.2. Cálculo do Programado per capita (A)

    A per capita = programado anual da região na Tabela 7 ÷ populacao_regiao

### 8.3. Cálculo do Executado per capita (B)

    B per capita = executado acumulado da região na Tabela 7 ÷ populacao_regiao

### 8.4. Cálculo de B/A

    B/A = executado per capita ÷ programado per capita da mesma região

### 8.5. Cálculo da Análise Vertical (C)

    executado per capita estadual = executado do Total Geral da Tabela 7 ÷ populacao_mg
    C = executado per capita da região ÷ executado per capita estadual

O executado per capita estadual serve de base para 100%. A regra adotada divide o executado total da Tabela 7 pela população de MG. Ver a conferência da referência no item 11.

### 8.6. Combinação e filtro

Juntar as linhas regionais da Tabela 7 à população pelo código da região. Manter as 13 regiões. Sinalizar ausência de população e deixar em branco o cálculo que depender de denominador ausente ou zero.

### 8.7. Resultado esperado

Granularidade das linhas de detalhe:

    1 linha = 1 Região Geográfica Intermediária

Exemplo estrutural com valores ilustrativos (trecho do demonstrativo):

| codigo_regiao_intermediaria | regiao_intermediaria | programado_per_capita | executado_per_capita | execucao | analise_vertical |
| --- | --- | ---: | ---: | ---: | ---: |
| … | Barbacena | 20.00 | 6.00 | 0.30 | 2.00 |
| … | Belo Horizonte | 15.00 | 6.00 | 0.40 | 2.00 |
| … | … | … | … | … | … |
|  | **Total Estadual** | A total da Tabela 7 ÷ população de MG | B total da Tabela 7 ÷ população de MG | B per capita estadual ÷ A per capita estadual | 1.00 |

## 9. Mapa 4 — Gasto Global Programado Per Capita por Região Geográfica Intermediária

### 9.1. Malha e chave de identificação

Usar as 13 Regiões Geográficas Intermediárias do Mapa 1, identificadas por `codigo_regiao_intermediaria`.

### 9.2. Indicador e unidade

Usar **Programado per capita (A) da Tabela 8**, em reais por habitante.

### 9.3. Referência para a escala de cor

    média regional = soma dos 13 valores de programado per capita ÷ 13

Aplicar a escala contínua do item 3.4, com tons mais claros até a média e mais escuros acima dela.

### 9.4. Combinação e filtro

Vincular o indicador à malha pelo código da região. Usar apenas as 13 linhas de detalhe da tabela, excluindo a linha de total do cruzamento e da média.

### 9.5. Resultado esperado

Mapa das 13 regiões de Minas Gerais coloridas segundo a programação anual por habitante, com identificação das regiões e legenda do indicador.

## 10. Mapa 5 — Gasto Global Executado Per Capita por Região Geográfica Intermediária

### 10.1. Malha e chave de identificação

Usar as 13 Regiões Geográficas Intermediárias do Mapa 1, identificadas por `codigo_regiao_intermediaria`.

### 10.2. Indicador e unidade

Usar **Executado per capita (B) da Tabela 8**, em reais por habitante.

### 10.3. Referência para a escala de cor

    média regional = soma dos 13 valores de realizado per capita ÷ 13

Aplicar a escala contínua do item 3.4, com tons mais claros até a média e mais escuros acima dela.

### 10.4. Combinação e filtro

Vincular o indicador à malha pelo código da região. Usar apenas as 13 linhas de detalhe da tabela, excluindo a linha de total do cruzamento e da média.

### 10.5. Resultado esperado

Mapa das 13 regiões de Minas Gerais coloridas segundo a execução acumulada por habitante, com identificação das regiões e legenda do indicador.

## 11. Particularidades da referência

- O per capita estadual calculado com os localizadores é R$ 844,76 em fevereiro, R$ 1.880,40 em abril e R$ 3.166,84 em junho de 2026. A Tabela 8 publicada de fevereiro e a matriz manual de junho coincidem com seus respectivos valores. A matriz de abril conserva R$ 844,76 no total, apesar de os detalhes regionais somarem R$ 40.228.138.480,84. Os scripts usam o total executado do próprio período dividido pela população estadual.
- As Tabelas 7 e 8 e os Mapas 2 a 5 da cópia do 3º bimestre repetem as imagens do 2º e servem como referência de abril.
- Em fevereiro, a base de ações informa R$ 10.714,63 para a ação 4491 — Apreensão e Liberação de Veículos, UO 2481 — DETRAN-MG. Seu único localizador é Belo Horizonte, IBGE 3106200, com realizado zero no extrato do 1º bimestre. O relatório financeiro confirma o gasto em fevereiro, Grupo 1, Elemento 11, Item 17, Procedência 1, na célula L9733 da aba Relatório BO 1 de `Despesa de Pessoal - Gabriel.xlsx`, pasta corporativa do 1º bimestre. Nos extratos de localizadores dos 2º e 3º bimestres, o mesmo valor já aparece no campo Desp. Realizada Pessoal e Auxílios Fev desse município. Isso evidencia uma atualização posterior da informação territorial de fevereiro. O histórico disponível não identifica a causa operacional dessa atualização. A rotina sinaliza a divergência e preserva os valores de cada fonte.
- O realizado das 13 regiões coincide com as matrizes manuais de abril e junho. A distribuição regional do programado difere dos valores preenchidos na referência, apesar de o total anual coincidir. Os scripts usam a base atual de localizadores elegíveis e registram as três parcelas territoriais para rastreamento.
- Na matriz de junho, o realizado municipal foi conferido para os 853 municípios e coincide com a base territorial. O programado em ` Global!C3:C15` contém valores fixos, sem fórmula que identifique a base original. As diferenças regionais devem ser tratadas como divergências da referência até que essa origem seja identificada.
- Em `Per capita GLOBAL!C16`, a matriz de junho guarda o valor arredondado 7396,11. O cálculo integral é 158228308922 ÷ 21393441 = 7396,113085407813. Usar a divisão por fórmula preserva a precisão de B/A em E16. O arredondamento para duas casas pertence à apresentação.
- Na pasta corporativa `1º Bimestre/RIM GERAL/Dados/Mapas`, o arquivo `Matriz Mapa - Programado-  Geral - 2026  - Daniel.xlsx` contém em `Planilha3!B15:D15` população de 21.460.311, programado de R$ 160.176.559.171,00 e per capita de R$ 7.463,85. O programado coincide com a soma bruta dos localizadores. A diferença para o total elegível de R$ 158.228.308.922,00 é R$ 1.948.250.249,00, igual à soma dos registros com exclusão lógica de ação. A população também difere da estimativa de 2025 adotada nos scripts.
- Nessa mesma pasta, `Matriz Mapa GERAL _Daniel.xlsx` conserva o executado de fevereiro de R$ 18.072.337.482,14 e usa população de 21.460.311, resultando em R$ 842,13 por habitante. As duas matrizes de mapas recebem os valores regionais fixos em Planilha3. Mesmo reproduzindo o total bruto e os pesos populacionais dessa referência, permanece diferença na distribuição regional do programado. A memória anterior à agregação regional é necessária para identificar os registros que a originaram.
