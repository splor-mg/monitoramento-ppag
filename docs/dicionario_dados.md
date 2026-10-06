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

---

# 2. Bases de Monitoramento

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