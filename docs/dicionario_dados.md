# Dicionário de Dados — Monitoramento do PPAG

Este documento descreve as bases de dados utilizadas nas rotinas de monitoramento do PPAG e as variáveis que compõem cada uma delas.

---

# 1. Bases de Planejamento

## 1.3. Localizadores

### Descrição
A base de Localizadores de Planejamento contém a programação do PPAG no nível dos localizadores das ações.
Cada registro representa a programação associada a determinada combinação de elementos do PPAG, incluindo programa, ação, unidade orçamentária e localizador.
A base é utilizada como principal referência para os valores planejados do exercício e para a identificação da localização territorial da programação.
Os localizadores podem representar municípios individualmente ou agregações territoriais, como Regiões Geográficas Intermediárias e o Estado de Minas Gerais como um todo.

### Fonte
Sistema de Informações Gerenciais e de Planejamento — SIGPlan. Futuramente do Portal de Planejamento e Orçamento - PPO.

### Periodicidade
Anual, considerando a programação vigente do exercício.

### Unidade de observação
Registro de planejamento associado a um localizador (valor vinculado a uma territorialização estadual, regional ou municipal) de uma ação do PPAG.

### Principais usos
- obtenção da programação orçamentária anual;
- consolidação por programa;
- consolidação por ação;
- consolidação por área temática;
- análise de regionalização;
- elaboração dos demonstrativos do IMRS;
- demais análises consolidadas do RIM.

### Variáveis
| Variável | Tipo | Descrição |
|---|---|---|
| codigo_programa | inteiro | Código identificador do programa no PPAG |
| programa | texto | Denominação do programa |
| codigo_acao | inteiro | Código identificador da ação |
| acao | texto | Denominação da ação |
| codigo_localizador | inteiro | Código identificador do localizador |
| localizador | texto | Denominação do localizador |
| previsao_orcamentaria | decimal | Valor orçamentário programado para o exercício |
| exclusao_logica_acao | lógico | Marca de exclusão lógica da ação no SIGPlan |
| codigo_ibge | texto | Código territorial do localizador |
| codigo_regiao_intermediaria | texto | Código da Região Geográfica Intermediária associada ao localizador |

## 1.4. QDD Fiscal — Pessoal e Auxílios

### Descrição e fonte

Quadro de Detalhamento da Despesa Fiscal do exercício, fornecido em `data/raw/planejamento/BASE_QDD_FISCAL.xlsx`, aba `BASE_QDD_FISCAL`. É a fonte do programado anual da Tabela 12.

### Unidade de observação

Linha de programação orçamentária detalhada por UO, ação e classificações da despesa. Uma UO e ação podem possuir várias linhas; seus valores elegíveis são somados antes da consolidação por setor.

### Variáveis utilizadas

| Campo de origem | Variável padronizada | Tipo | Descrição |
|---|---|---|---|
| ANO | ano | inteiro | Exercício da programação |
| COD_UO | codigo_uo | texto | Código da UO, usado no vínculo com o cadastro de ações |
| AÇÃO | codigo_acao | texto | Código completo da ação, como 4239 |
| GRUPO_DESPESA | grupo_despesa | texto | Código do grupo; 1 identifica Pessoal e Encargos Sociais |
| ELEMENTO_DESPESA | elemento_despesa | texto | Código do elemento; 34 identifica Outras Despesas Decorrentes de Contratos de Terceirização |
| IPU | ipu | texto | Identificador de Procedência e Uso; 7 identifica Auxílios e 9, Precatórios e Sentenças Judiciais |
| VALOR FINAL (R$) | programado_anual | decimal | Valor anual a somar após aplicar o recorte de despesas |

Selecionar o exercício e vincular ao setor por `ano + codigo_uo + codigo_acao`. O campo VALOR FINAL (R$) não deve ser somado a VALOR UO (R$) e VALOR SCPPO (R$), que são outros campos de valor da mesma base.

---

# 2. Bases de Monitoramento

## 2.2. Ações — Monitoramento

Exportação bimestral do SIGPlan em `monitoramento/<bimestre>bim/acoes_monitoramento.txt`.
Cada linha corresponde a uma ação na exportação do período. A chave de relacionamento é a combinação de **Código da Unidade Orçamentária Responsável pela Ação + Código da Ação**, dentro do exercício e período selecionados. É a base da
Execução Global e o ponto de partida para o Desempenho Consolidado.

| Campo ou grupo de campos do SIGPlan | Uso |
|---|---|
| Ano Monitoramento, Mês Inicial e Mês Final | Identificar o período acumulado |
| Código do Programa, Código da Ação e Código da Unidade Orçamentária Responsável pela Ação | Identificar os registros no cruzamento com outras bases |
| Código do Tipo de Ação e Tipo de Ação | Classificar o orçamento e identificar ações não orçamentárias |
| Código do Identificador de Ação Governamental (IAG) | 0 para Demais Projetos e Atividades e 1 para Projetos Estratégicos |
| Código da Área Temática, Área Temática, Código da Função, Função e Setor de Governo | Agrupar os demonstrativos |
| Previsão Orçamentária (LOA), Orç. Programado Inicial e Despesa Realizada do exercício | Programado anual, programado até o bimestre e realizado acumulado |
| Previsão Física do exercício | Meta física anual, distinta da programação até o bimestre |
| Fis Programado Inicial de janeiro até o fim do bimestre | Meta física inicial acumulada do período |
| Realização Física do exercício | Realizado físico acumulado até o fim do bimestre |
| Total Prog. Inicial Outras Desp. e Total Prog. Inicial Desp. Pessoal e Auxílios | Parcelas da programação inicial acumulada no período |
| Ação Transposta Durante Exercício | Campo disponível para a conferência de validade |

Para a Tabela 12, reutilizar **Ano Monitoramento**, **Código da Unidade Orçamentária Responsável pela Ação**, **Código da Ação** e **Setor de Governo** como `ano`, `codigo_uo`, `codigo_acao` e `setor_governo`. Exigir uma única correspondência de setor por chave no período selecionado.

### Variáveis para a validade das ações

| Variável | Tipo | Descrição |
|---|---|---|
| previsao_orcamentaria_loa | decimal | Previsão Orçamentária do exercício (LOA) na exportação de ações, usada no filtro de validade |
| codigo_tipo_acao | texto | Código do Tipo de Ação. O código 5 identifica Não Orçamentário na exportação de 2026 |
| valida_orcamentaria | booleano | Previsão Orçamentária do exercício (LOA) diferente de zero |
| valida_fisica | booleano | Ação orçamentária válida ou ação de tipo Não Orçamentário |

A validade usa a previsão orçamentária da LOA e o Tipo de Ação do próprio monitoramento. Aplicar o filtro da dimensão ao contar os intervalos. As regras de contagem e a classificação por desempenho estão em [Desempenho Consolidado](regras_desempenho_consolidado.md).

## 2.3. Localizadores — Monitoramento

### Descrição
A base de Localizadores de Monitoramento contém as informações de execução das ações do PPAG no nível de seus localizadores.
Ela registra a execução física e orçamentária observada durante o exercício e permite acompanhar os valores realizados até determinado período de monitoramento.
Ao contrário da base de planejamento, que representa a programação anual, esta base possui referência temporal vinculada ao período monitorado e é atualizada ao longo do exercício.

### Fonte
Sistema de Informações Gerenciais e de Planejamento — SIGPlan. Futuramente do Portal de Planejamento e Orçamento - PPO.

### Periodicidade
Bimestral.

### Unidade de observação
Registro de monitoramento associado a um localizador (valor vinculado a uma territorialização estadual, regional ou municipal) de uma ação do PPAG.

### Principais usos
- obtenção da execução orçamentária;
- acompanhamento da execução física;
- cálculo dos indicadores de desempenho;
- consolidação por programa e ação;
- regionalização;
- elaboração dos demonstrativos do IMRS.

### Variáveis
| Variável | Tipo | Descrição |
|---|---|---|
| codigo_programa | inteiro | Código identificador do programa no PPAG |
| programa | texto | Denominação do programa |
| codigo_acao | inteiro | Código identificador da ação |
| acao | texto | Denominação da ação |
| codigo_localizador | inteiro | Código identificador do localizador |
| localizador | texto | Denominação do localizador |
| mes_inicial | inteiro | Primeiro mês considerado no período de monitoramento |
| mes_final | inteiro | Último mês considerado no período de monitoramento |
| despesa_realizada_total | decimal | Valor da despesa realizada acumulada no período |
| codigo_ibge | texto | Código territorial do localizador, inclusive códigos especiais do SIGPlan |
| codigo_regiao_intermediaria | texto | Região usada na consolidação territorial |
| despesa_realizada_pessoal_auxilios | decimal | Coluna de pessoal e auxílios da exportação, acumulada até o bimestre. A cobertura para a Tabela 12 deve ser conferida. |

## 2.4. Execução SIAFI — Pessoal e Auxílios

### Descrição e fonte

CSV de execução do SIAFI, disponível em `dados-siafi-2026-main/data/execucao.csv/execucao.csv`. Fornece o realizado mensal usado na Tabela 12, acumulado de janeiro até o fim do bimestre selecionado.

### Unidade de observação

Linha de execução com exercício e mês, detalhada por classificações orçamentárias e atributos do empenho. Várias linhas podem pertencer à mesma UO e ação; somá-las após o recorte, sem exigir unicidade dessa combinação na execução.

### Variáveis utilizadas

| Campo de origem | Variável padronizada | Tipo | Descrição |
|---|---|---|---|
| ano | ano | inteiro | Exercício da execução |
| mes_cod | mes | inteiro | Mês de execução; selecionar de 1 até 2 × bimestre |
| uo_cod | codigo_uo | texto | Código da UO, usado no vínculo com o cadastro de ações |
| acao_cod | codigo_acao | texto | Código completo da ação |
| grupo_cod | grupo_despesa | texto | Código do grupo usado no recorte de pessoal e auxílios |
| elemento_item_cod | codigo_elemento_item | texto | Código usado para derivar elemento e item da despesa |
| ipu_cod | ipu | texto | Código correspondente a Procedência - Código no BO conferido |
| vlr_liquidado | realizado | decimal | Valor liquidado mensal a somar; corresponde a Valor Despesa Realizada no BO conferido |

### Variáveis derivadas e relacionamentos

| Variável | Tipo | Origem e uso |
|---|---|---|
| elemento_despesa | texto | Se o código elemento/item possui até dois dígitos, usar o código; nos demais casos, retirar os dois últimos dígitos. Usado para identificar o elemento 34 |
| item_despesa | texto | Zero nos códigos com até dois dígitos; nos demais, os dois últimos dígitos. Usado na conferência com o BO |
| setor_governo | texto | Setor obtido no cadastro de ações pela chave ano + codigo_uo + codigo_acao |
| analise_vertical | decimal | Indicador da Tabela 12: realizado do setor dividido pelo realizado de todos os setores |
| execucao | decimal | Indicador da Tabela 12: realizado do setor dividido pelo programado anual do setor |

As taxas são frações e permanecem nulas quando o denominador é zero. Exemplos de elemento/item: `3611` corresponde ao elemento 36 e item 11; `11`, ao elemento 11 e item zero. A **Despesa Realizada** corresponde a `vlr_liquidado`, sem somar `vlr_liquidado_retido`, empenhado ou pago. O **Relatório BO 1** da planilha manual é referência de conferência, sem ser acrescentado à execução do CSV. Ver o recorte, os cálculos e a estrutura final nas [regras da Tabela 12](regras_despesa_pessoal_auxilios.md).

---

# 3. Bases Externas

## 3.1. População dos Municípios — IBGE

### Descrição
A base contém a estimativa municipal do IBGE de 2025, correspondente à aba `pop_2025_ibge` da planilha manual.
No monitoramento do PPAG, a população é utilizada principalmente nas análises territoriais que exigem proporcionalização dos valores associados a localizadores regionais ou estaduais.
Também permite a produção de indicadores per capita e a consolidação das populações das Regiões Geográficas Intermediárias.

### Fonte
Instituto Brasileiro de Geografia e Estatística — IBGE. Usar o arquivo fornecido em `data/raw/externas/estimativa_dou_2025.xls`, aba `Municípios`.

### Periodicidade
Anual.

### Edição utilizada em cada bloco

| Bloco | Arquivo e aba | Referência | Total de MG |
|---|---|---|---:|
| Regionalização | `data/raw/externas/estimativa_dou_2025.xls`, aba `Municípios` | Estimativa IBGE 2025 | 21.393.441 |
| IMRS | `data/raw/externas/estimativa_dou_2025.xls`, aba `Municípios` | Estimativa IBGE 2025 | 21.393.441 |

Usar a mesma edição em todos os pesos e denominadores de um bloco. O total esperado valida a leitura; os pesos são derivados dos valores municipais efetivamente lidos. Registrar a referência utilizada em cada execução.

### Unidade de observação
Município.

### Abrangência e capilaridade
O arquivo contém municípios do Brasil; filtrar os 853 de Minas Gerais. A estimativa populacional IBGE 2025 é independente do índice IMRS 2024 produzido pela FJP.

### Principais usos
- cálculo da população das Regiões Geográficas Intermediárias;
- rateio populacional de valores regionais;
- rateio populacional de valores estaduais;
- cálculo de indicadores per capita;
- elaboração dos demonstrativos do IMRS.

## Variáveis
| Variável | Tipo | Descrição |
|---|---|---|
| codigo_ibge | texto | Código IBGE do município |
| municipio | texto | Nome do município |
| populacao | inteiro | População estimada do município |
| ano_populacao | inteiro | Ano de referência da estimativa populacional |
| codigo_regiao_intermediaria | texto | Código da Região Geográfica Intermediária |
| regiao_intermediaria | texto | Nome da Região Geográfica Intermediária |



## 3.2. Índice Mineiro de Responsabilidade Social — IMRS

### Descrição
A base do Índice Mineiro de Responsabilidade Social contém os resultados municipais do IMRS produzidos pela Fundação João Pinheiro.
No projeto de monitoramento do PPAG, essa base é utilizada para identificar os municípios classificados nas cinquenta últimas posições do índice, que compõem o recorte territorial específico dos demonstrativos do IMRS apresentados no RIM. 
No projeto de monitoramento do PPAG, essa base fornece o índice utilizado na definição do recorte dos cinquenta municípios contemplados pelos demonstrativos específicos do IMRS.

### Fonte
Fundação João Pinheiro — FJP.

### Periodicidade
Anual. Conforme as edições publicadas pela Fundação João Pinheiro.

### Unidade de observação
Município.

### Abrangência e capilaridade
853 municípios de Minas Gerais.

### Principais usos
- classificação dos municípios pelo IMRS;
- identificação dos cinquenta municípios de menor índice;
- composição do recorte dos demonstrativos específicos do RIM.

### Variáveis
| Variável | Tipo | Descrição |
|---|---|---|
| codigo_ibge | texto | Código IBGE do município |
| municipio | texto | Nome do município |
| imrs | decimal | Valor do Índice Mineiro de Responsabilidade Social |
| ano_imrs | inteiro | Ano de referência da edição do IMRS |

## 3.3. Malha territorial — IBGE

Geometrias municipais com código IBGE e respectivo vínculo à Região Geográfica
Intermediária, ou malha das próprias regiões. Usadas para os Mapas 1 a 7. Nos Mapas 6 e 7, a malha municipal recebe os valores da Tabela 11 pelo código IBGE.
