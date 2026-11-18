# Regras de Negócio — Demonstrativos do IMRS

## 1. Objetivo
Produzir os três demonstrativos do RIM referentes aos municípios classificados nas 50 últimas posições do IMRS:
- por programa;
- por área temática;
- por município.

Produzir também os Mapas 6 e 7 a partir dos valores municipais da Tabela 11.

## 2. Bases, chaves e regras comuns

### 2.1. Bases e referências

Usar os localizadores de planejamento para o programado anual e os localizadores de monitoramento do bimestre para o realizado acumulado. Vincular municípios, população, índice e malha pelo código IBGE de sete dígitos.

Os parâmetros atuais usam a edição **2024 do IMRS** e a estimativa populacional **2025 do IBGE**. A edição do índice e o ano da população são parâmetros da execução. A identificação dos localizadores e a referência populacional seguem os itens 2.1 e 2.2 de [Regionalização](regras_regionalizacao.md).

### 2.2. Recorte de municípios e desempate

Selecionar os 50 municípios com menor valor de IMRS na edição utilizada como referência para o exercício. Ordenar o índice em ordem crescente e manter os 50 primeiros.

Na edição de 2024, o código atual prioriza **Presidente Olegário**, código IBGE `3153400`, entre os municípios empatados em **0,225** no corte da 50ª posição, para reproduzir a lista da referência manual. Após essa prioridade, desempatar pelo código IBGE crescente. Nas demais edições, o desempate implementado usa o código IBGE crescente. Essa é a convenção de reprodução adotada no projeto.

### 2.3. Classificação das Áreas Temáticas

Usar a correspondência entre código de área e grupo do item 4.3 de [Execução Global](regras_execucao_global.md). No DataFrame do IMRS, a área 15 compõe o grupo **Outros Poderes**. Normalizar os códigos e conferir áreas sem denominação antes das agregações.

### 2.4. Exclusão lógica

Antes de calcular o programado das Tabelas 9, 10 e 11, excluir da base de planejamento todos os registros de localizadores com `Exclusão Lógica da Ação = True`. Aplicar o filtro antes da apropriação territorial e das agregações financeiras.

O campo é o da ação na base de planejamento. O realizado é calculado a partir da base de monitoramento do bimestre.

## 3. Valores considerados
Para cada exercício devem ser considerados:
- o valor programado anual do PPAG;
- o valor realizado acumulado até o bimestre monitorado.

## 4. Tipos de localizador
Cada registro deve ser tratado conforme o alcance territorial de seu localizador:
- municipal;
- regional;
- estadual.

## 5. Localizador municipal

### 5.1 Município pertencente ao recorte
O valor é apropriado integralmente:

    valor_imrs = valor_original

### 5.2 Município fora do recorte
O valor não é apropriado:

    valor_imrs = 0

## 6. Localizador regional
Os valores registrados em uma Região Geográfica Intermediária devem ser apropriados aos municípios do recorte proporcionalmente à população.

Para cada região:

    peso_imrs_regiao =
        soma da população dos municípios dentro da região que estão entre os 50 IMRSs mais baixos
        /
        população total da região

Então:

    valor_imrs_regiao =
        valor_regional
        * peso_imrs_regiao

## 7. Localizador estadual
Calcular:

    peso_imrs_mg =
        soma da população dos municípios que estão entre os 50 IMRSs mais baixos 
        /
        população total de Minas Gerais

Então:

    valor_imrs_estadual =
        valor_estadual
        * peso_imrs_mg

## 8. Rateio individual por município
Para a municipalização dos valores, os valores regionais e estaduais devem ser distribuídos a cada município individualmente.

### Regional

    peso_municipio_regiao =
        população do município
        /
        população total da região

    valor_regional_municipio =
        valor regional
        * peso_municipio_regiao

### Estadual

    peso_municipio_mg =
        população do município
        /
        população total de Minas Gerais

    valor_estadual_municipio =
        valor estadual
        * peso_municipio_mg

O valor total do município corresponde a:

    valor municipal direto
    + valor regional rateado
    + valor estadual rateado

A regra é aplicada separadamente ao programado e ao realizado.

## 9. Tabela 9 — Valores programados e realizados por programa

### 9.1. Unidade de observação do dataframe final

Cada linha do dataframe final corresponde a um programa do PPAG que possua
valor programado e/ou realizado apropriado ao recorte dos 50 municípios do IMRS.

O dataframe utilizado para geração do demonstrativo deve possuir a seguinte
estrutura:

| Variável | Tipo | Descrição |
|---|---|---|
| codigo_programa | texto | Código identificador do programa no PPAG |
| programa | texto | Denominação do programa |
| programado | decimal | Valor programado apropriado ao recorte do IMRS |
| realizado | decimal | Valor realizado apropriado ao recorte do IMRS |

O código do programa tem de um a três dígitos. Antes de agrupar e cruzar as
bases, remova os zeros de preenchimento do SIGPlan. Mantenha o código como
texto e ordene pelo seu valor numérico na tabela final.

### 9.2. Cálculo do valor programado

Partir da base de planejamento após a aplicação das regras de apropriação
territorial definidas nos itens 5, 6 e 7.

Cada registro da base deverá possuir um valor programado apropriado ao IMRS:

    valor_programado_imrs

Para cada programa, calcular:

    programado =
        soma de valor_programado_imrs
        para todos os registros pertencentes ao programa

O agrupamento deve ser realizado por:

    codigo_programa
    programa

### 9.3. Cálculo do valor realizado

Partir da base de monitoramento após a aplicação das mesmas regras de
apropriação territorial.

Cada registro deverá possuir um valor realizado apropriado ao IMRS:

    valor_realizado_imrs

Para cada programa, calcular:

    realizado =
        soma de valor_realizado_imrs
        para todos os registros pertencentes ao programa

O agrupamento deve ser realizado por:

    codigo_programa
    programa

### 9.4. Combinação entre planejamento e monitoramento

Os valores programados e realizados devem ser calculados separadamente antes
da combinação das duas bases.

Após as agregações, combinar os resultados utilizando todos os programas
existentes em qualquer uma das duas bases.

Portanto, a combinação não deve eliminar programas existentes somente no
planejamento ou somente no monitoramento.

Conceitualmente:

    programas =
        união dos programas existentes no planejamento
        e dos programas existentes no monitoramento

Quando um programa não possuir valor em uma das bases:

    valor ausente de programado → 0
    valor ausente de realizado → 0

Essa regra garante a permanência de programas com execução mesmo quando não
houver valor programado correspondente.

### 9.5. Filtro das linhas

Após a combinação:

    se programado = 0 e realizado = 0
        excluir a linha

    caso contrário
        manter a linha

Programas com:

    programado = 0
    realizado > 0

devem permanecer no demonstrativo.

### 9.6. Ordenação

O dataframe final deve ser ordenado pelo código do programa em ordem
crescente, salvo quando o padrão de apresentação do RIM determinar outra
ordenação.

### 9.7. Resultado esperado

A granularidade final será:

    1 linha = 1 programa

Exemplo estrutural:

| codigo_programa | programa | programado | realizado |
|---|---|---:|---:|
| 1 | Programa A | 1000000.00 | 250000.00 |
| 2 | Programa B | 0.00 | 50000.00 |
| 3 | Programa C | 800000.00 | 0.00 |
| n | Programa n | … | … |
| | **Total Geral** | Soma do programado | Soma do realizado |

A linha Total Geral é acrescentada na apresentação e inclui todos os programas da tabela.

---

## 10. Tabela 10 — Valores por Área Temática

### 10.1. Unidade de observação do dataframe final

Cada linha do dataframe final corresponde a uma área temática utilizada na
classificação do PPAG.

O dataframe deve possuir a seguinte estrutura:

| Variável | Tipo | Descrição |
|---|---|---|
| grupo_area_tematica | texto | Grupo ao qual pertence a área temática |
| area_tematica | texto | Denominação da área temática |
| programado | decimal | Valor programado apropriado ao recorte do IMRS |
| realizado | decimal | Valor realizado apropriado ao recorte do IMRS |
| participacao_grupo | decimal | Participação do realizado da área no realizado total de seu grupo |
| participacao_global | decimal | Participação do realizado da área no realizado total de todas as áreas |
| execucao | decimal | Relação entre realizado e programado |

Os grupos possíveis são:

- Áreas Temáticas Finalísticas;
- Áreas Temáticas de Apoio e Suporte;
- Outros Poderes.

### 10.2. Classificação das áreas

Cada registro utilizado no cálculo deve estar associado à respectiva área
temática.

Também deve possuir a identificação do grupo da área temática:

    grupo_area_tematica

Programas pertencentes aos demais Poderes que não possuam vinculação a uma
área temática do PMDI devem ser classificados como:

    area_tematica = "Outros Poderes"
    grupo_area_tematica = "Outros Poderes"

A classificação deve ocorrer antes das agregações financeiras.

### 10.3. Cálculo do programado por área temática

Partir dos valores programados já apropriados ao recorte do IMRS.

Para cada combinação de:

    grupo_area_tematica
    area_tematica

calcular:

    programado =
        soma de valor_programado_imrs

### 10.4. Cálculo do realizado por área temática

Partir dos valores realizados já apropriados ao recorte do IMRS.

Para cada combinação de:

    grupo_area_tematica
    area_tematica

calcular:

    realizado =
        soma de valor_realizado_imrs

### 10.5. Combinação entre planejamento e monitoramento

As agregações de planejamento e monitoramento devem ser calculadas
separadamente.

Em seguida, os dois resultados devem ser combinados pela união das áreas
existentes nas duas bases.

Quando uma área temática existir somente em uma das bases:

    programado ausente → 0
    realizado ausente → 0

Não deve ser utilizada uma combinação que elimine áreas existentes apenas no
planejamento ou apenas no monitoramento.

### 10.6. Total realizado global

Calcular:

    realizado_total =
        soma de realizado de todas as áreas temáticas

Esse valor será utilizado como denominador da participação global.

### 10.7. Total realizado de cada grupo

Para cada grupo:

    realizado_grupo =
        soma de realizado das áreas pertencentes ao grupo

Esse valor será utilizado como denominador da participação dentro do grupo.

### 10.8. Participação no grupo

Para cada área:

    participacao_grupo =
        realizado da área
        /
        realizado total do grupo

Exemplo:

    realizado da área = 20
    realizado do grupo = 100

    participacao_grupo = 0,20

Na apresentação do demonstrativo:

    0,20 → 20,00%

Se o realizado total do grupo for igual a zero, a participação não deve ser
calculada e deve permanecer nula.

### 10.9. Participação global

Para cada área:

    participacao_global =
        realizado da área
        /
        realizado_total

Exemplo:

    realizado da área = 20
    realizado total = 400

    participacao_global = 0,05

Na apresentação:

    0,05 → 5,00%

Se o realizado total for igual a zero, a participação global deve permanecer
nula.

### 10.10. Execução

Para cada área:

    execucao =
        realizado
        /
        programado

Exemplo:

    programado = 100
    realizado = 70

    execucao = 0,70

Na apresentação:

    0,70 → 70,00%

Quando:

    programado = 0

a execução não deve ser calculada.

Nesse caso, o valor deve permanecer nulo no dataframe, evitando a geração de
infinito ou a atribuição artificial de execução igual a zero.

A forma de apresentação desse valor no demonstrativo, como campo vazio,
traço ou outro símbolo, pertence à etapa de formatação.

### 10.11. Ordem das operações

A geração da tabela deve seguir a seguinte sequência:

    1. classificar cada registro por área temática e grupo;
    2. aplicar as regras de apropriação territorial ao programado;
    3. aplicar as regras de apropriação territorial ao realizado;
    4. agregar o programado por grupo e área temática;
    5. agregar o realizado por grupo e área temática;
    6. combinar planejamento e monitoramento;
    7. substituir valores monetários ausentes por zero;
    8. calcular o realizado total;
    9. calcular o realizado total de cada grupo;
    10. calcular participação no grupo;
    11. calcular participação global;
    12. calcular execução;
    13. ordenar as áreas conforme os grupos do demonstrativo.

### 10.12. Resultado esperado

A granularidade final será:

    1 linha = 1 área temática

Exemplo estrutural com valores ilustrativos:

| grupo_area_tematica | area_tematica | programado | realizado | participacao_grupo | participacao_global | execucao |
|---|---|---:|---:|---:|---:|---:|
| Finalísticas | Educação | 1000.00 | 800.00 | 0.80 | 0.40 | 0.80 |
| Finalísticas | Saúde | 500.00 | 200.00 | 0.20 | 0.10 | 0.40 |
| Finalísticas | **Subtotal** | 1500.00 | 1000.00 | 1.00 | 0.50 | 0.6667 |
| Apoio e Suporte | Planejamento e Gestão | 2000.00 | 1000.00 | 1.00 | 0.50 | 0.50 |
| Apoio e Suporte | **Subtotal** | 2000.00 | 1000.00 | 1.00 | 0.50 | 0.50 |
| | **Total Geral** | 3500.00 | 2000.00 | 1.00 | 1.00 | 0.5714 |

Na apresentação, calcular o Total Geral somando as linhas de detalhe de cada
área uma vez. Recalcular a execução como realizado total ÷ programado total.

---

## 11. Tabela 11 — Valores por Município

### 11.1. Unidade de observação do dataframe final

Cada linha do dataframe final corresponde a um dos 50 municípios selecionados
pelo IMRS.

O dataframe deve possuir a seguinte estrutura:

| Variável | Tipo | Descrição |
|---|---|---|
| codigo_ibge | texto | Código IBGE do município |
| municipio | texto | Nome do município |
| programado | decimal | Valor programado total apropriado ao município |
| realizado | decimal | Valor realizado total apropriado ao município |

O dataframe deverá possuir exatamente os 50 municípios pertencentes ao recorte,
inclusive quando determinado município possuir valor programado e realizado
iguais a zero.

### 11.2. Estrutura do cálculo

Diferentemente das tabelas por programa e área temática, a tabela municipal
exige a distribuição individual dos valores regionais e estaduais.

Para cada município devem ser calculados separadamente três componentes:

    valor municipal direto
    valor regional rateado
    valor estadual rateado

O procedimento deve ser executado separadamente para:

    programado
    realizado

### 11.3. Parcela municipal direta

Para cada município do recorte:

    programado_municipal =
        soma dos valores programados
        cujo localizador corresponde diretamente ao município

    realizado_municipal =
        soma dos valores realizados
        cujo localizador corresponde diretamente ao município

Somente registros de localizadores municipais correspondentes ao próprio
município entram nessa parcela.

### 11.4. Parcela proveniente de localizadores regionais

Primeiro, identificar a Região Geográfica Intermediária à qual pertence cada
município.

Para cada município:

    peso_municipio_regiao =
        população do município
        /
        população total da região

Para cada registro associado àquela região:

    programado_regional_municipio =
        valor_programado_regional
        * peso_municipio_regiao

    realizado_regional_municipio =
        valor_realizado_regional
        * peso_municipio_regiao

Quando houver mais de um registro regional, calcular a parcela de cada registro
e posteriormente somá-las.

Assim:

    programado_regional =
        soma de programado_regional_municipio

    realizado_regional =
        soma de realizado_regional_municipio

O cálculo deve ser realizado exclusivamente para os municípios pertencentes ao
recorte dos 50 menores IMRS.

### 11.5. Parcela proveniente do localizador estadual

Para cada município:

    peso_municipio_mg =
        população do município
        /
        população total de Minas Gerais

Para cada registro de abrangência estadual:

    programado_estadual_municipio =
        valor_programado_estadual
        * peso_municipio_mg

    realizado_estadual_municipio =
        valor_realizado_estadual
        * peso_municipio_mg

Quando houver mais de um registro estadual, calcular a parcela correspondente
a cada registro e posteriormente somá-las.

Assim:

    programado_estadual =
        soma de programado_estadual_municipio

    realizado_estadual =
        soma de realizado_estadual_municipio

### 11.6. Valor programado total do município

Após calcular os três componentes:

    programado =
        programado_municipal
        + programado_regional
        + programado_estadual

### 11.7. Valor realizado total do município

Da mesma forma:

    realizado =
        realizado_municipal
        + realizado_regional
        + realizado_estadual

### 11.8. Construção do dataframe

A construção deve partir da relação completa dos 50 municípios selecionados
pelo IMRS.

Essa relação funciona como base principal do dataframe.

A ela devem ser associados:

    programado_municipal
    programado_regional
    programado_estadual

    realizado_municipal
    realizado_regional
    realizado_estadual

Quando determinado componente não existir para um município, seu valor deve
ser considerado igual a zero.

Somente depois dessa substituição devem ser calculados os totais:

    programado
    realizado

Esse procedimento garante que um município permaneça no demonstrativo mesmo
quando não houver registros diretamente associados a ele.

### 11.9. Dataframe intermediário de conferência

Durante o processamento, recomenda-se manter um dataframe intermediário com
os componentes separados:

| codigo_ibge | municipio | programado_municipal | programado_regional | programado_estadual | realizado_municipal | realizado_regional | realizado_estadual |
|---|---|---:|---:|---:|---:|---:|---:|

Esse dataframe permite verificar a origem dos valores antes da geração do
demonstrativo.

Após a conferência, o dataframe destinado à apresentação pode ser reduzido
para:

| codigo_ibge | municipio | programado | realizado |
|---|---|---:|---:|

Caso o código IBGE não seja exibido no RIM, ele pode permanecer como coluna
técnica e ser removido somente na etapa de formatação do demonstrativo.

### 11.10. Ordem das operações

A geração da tabela municipal deve seguir a seguinte sequência:

    1. criar a relação dos 50 municípios selecionados pelo IMRS;
    2. associar cada município à sua Região Geográfica Intermediária;
    3. associar a população de cada município;
    4. calcular a população total de cada região;
    5. obter a população total de Minas Gerais;
    6. calcular os valores municipais diretos;
    7. calcular os pesos município/região;
    8. distribuir os valores regionais;
    9. calcular os pesos município/Minas Gerais;
    10. distribuir os valores estaduais;
    11. repetir o procedimento para programado e realizado;
    12. substituir componentes ausentes por zero;
    13. somar os três componentes do programado;
    14. somar os três componentes do realizado;
    15. manter exclusivamente os 50 municípios selecionados;
    16. ordenar os municípios conforme o padrão definido para o demonstrativo.

### 11.11. Resultado esperado

A granularidade final será:

    1 linha = 1 município do recorte

O DataFrame possui exatamente 50 linhas de detalhe. A apresentação
acrescenta o Total Geral, calculado sobre os 50 municípios.

Exemplo estrutural:

| codigo_ibge | municipio | programado | realizado |
|---|---|---:|---:|
| 3100203 | Município A | 145100951.07 | 32328644.50 |
| 3100302 | Município B | 25000000.00 | 8000000.00 |
| 3100401 | Município C | 0.00 | 0.00 |
| … | … | … | … |
| | **Total Geral** | Soma do programado | Soma do realizado |

## 12. Mapa 6 — Valor global programado nos municípios do recorte IMRS

### 12.1. Dados, malha e chave

Usar `codigo_ibge` e `programado` das 50 linhas municipais da Tabela 11. Vincular os dados à malha municipal de MG pelo código IBGE e retirar a linha Total Geral do cruzamento.

### 12.2. Indicador e escala de cores

Na implementação atual, converter o programado para **R$ milhões** e usar escala contínua do rosa claro ao vermelho escuro. O limite inferior é o menor valor entre zero e o mínimo observado no recorte. O superior é o maior entre zero e o máximo observado no recorte.

Municípios fora do recorte aparecem em cinza. Zero dentro do recorte recebe a cor correspondente da escala. Se todos os valores forem zero, exibir essa condição na legenda.

### 12.3. Combinação e filtro

Manter os municípios de MG como fundo e colorir os 50 municípios selecionados, preservando valores zero. Cada código da Tabela 11 deve ter correspondência na malha.

### 12.4. Resultado esperado

PNG contendo o mapa, as divisas municipais, a escala em R$ milhões e a legenda do recorte. O título, o subtítulo e a fonte são inseridos no relatório.

## 13. Mapa 7 — Valor global realizado nos municípios do recorte IMRS

### 13.1. Dados, malha e chave

Usar `codigo_ibge` e `realizado` das 50 linhas municipais da Tabela 11, com a mesma malha e os mesmos vínculos do Mapa 6.

### 13.2. Indicador e escala de cores

Converter o realizado acumulado para **R$ milhões**. Usar escala contínua do verde claro ao verde escuro, com limites calculados sobre o realizado pelo mesmo procedimento do Mapa 6. Os dois mapas possuem escalas próprias.

### 13.3. Combinação e filtro

Aplicar o recorte, a conferência dos códigos e o tratamento de zero e de municípios fora do recorte definidos para o Mapa 6.

### 13.4. Resultado esperado

PNG com o realizado acumulado até o bimestre, divisas, escala em R$ milhões e legenda do recorte. O título, o subtítulo e a fonte são inseridos no relatório.

## 14. Fechamento
Os totais das três tabelas devem coincidir:

    total por programa
    =
    total por área temática
    =
    total por município

A igualdade deve ser verificada separadamente para:

- programado;
- realizado.

Conferir também se os valores vinculados aos Mapas 6 e 7 são os da Tabela 11 para os mesmos códigos municipais.

## 15. Particularidades e pendências da referência

### Programas sociais
Atualmente é um filtro não utilizado pois não são demonstrativos presentes no RIM Social, mas é uma base válida de ser considerada.

### Execução sem programação
Preservar programas com execução e sem valor inicialmente programado.

### Referência das cores dos mapas

O texto do RIM descreve a intensidade das cores em relação à média estadual. Os itens 12 e 13 registram a escala atualmente implementada no projeto, baseada nos valores do recorte e em zero. A adoção da média estadual como referência das cores permanece como decisão a confirmar.
