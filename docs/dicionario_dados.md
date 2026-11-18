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

## 2.4. Detalhamento de Pessoal e Auxílios

Na planilha corporativa `RIM/2° Bimestre/RIM GERAL/Dados/Despesa de Pessoal - Gabriel.xlsx`, foram identificadas as fontes da Tabela 12.

| Aba | Campos principais e uso |
|---|---|
| BASE_QDD_FISCAL | ANO, COD_UO, AÇÃO, GRUPO_DESPESA, ELEMENTO_DESPESA, IPU e VALOR FINAL (R$), para o programado anual |
| Relatório BO 1 | Ano de Exercício, Mês - Numérico, Unidade Orçamentária - Código, Projeto_Atividade - Código, Grupo Despesa - Código, Elemento Despesa - Código, Item Despesa - Código, Procedência - Código e Valor Despesa Realizada, para o realizado |
| acoes_monitoramento e Planejamento 2026 | Vínculo entre UO, ação e Setor de Governo |

Vincular os registros pela UO e pelo código completo da ação. Conferir a correspondência entre Procedência e IPU e o tratamento do elemento 34 conforme as [regras da Tabela 12](regras_despesa_pessoal_auxilios.md).

---

# 3. Bases Externas

## 3.1. População dos Municípios — IBGE

### Descrição
A base contém as estimativas populacionais dos municípios de Minas Gerais produzidas pelo IBGE.
No monitoramento do PPAG, a população é utilizada principalmente nas análises territoriais que exigem proporcionalização dos valores associados a localizadores regionais ou estaduais.
Também permite a produção de indicadores per capita e a consolidação das populações das Regiões Geográficas Intermediárias.

### Fonte
Instituto Brasileiro de Geografia e Estatística — IBGE.

### Periodicidade
Anual.

### Edição utilizada na rotina
O parâmetro `ano_populacao` usa **2026** como padrão: projeção municipal da FJP baseada no IBGE, aba `2026` de `data/raw/externas/projecoes_populacionais_fjp_2025_2047.xlsx`. A edição IBGE 2025 permanece disponível para reproduzir cálculos anteriores. Registrar a edição efetivamente utilizada em cada execução.

### Unidade de observação
Município.

### Abrangência e capilaridade
Todos os municípios do Brasil.
Para as rotinas de monitoramento do PPAG, são filtrados os 853 municípios de Minas Gerais.

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
