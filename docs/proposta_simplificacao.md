# Proposta de simplificação e referências dos cálculos

## 1. Referência populacional corrigida: IMRS e Regionalização

IMRS e Regionalização usam `data/raw/externas/estimativa_dou_2025.xls`, aba `Municípios`, filtrada para os 853 municípios de MG. A referência corresponde à aba `pop_2025_ibge` da planilha manual. A soma deve ser **21.393.441 habitantes**. Essa soma é uma conferência da edição; os pesos continuam sendo calculados com os valores municipais do arquivo.

A programação e a execução financeira continuam referentes a 2026. O índice que seleciona os 50 municípios é o IMRS 2024, da FJP. A referência populacional dos rateios é IBGE 2025 em ambos os blocos.

Foram corrigidos a leitura da população, os padrões dos geradores, as regras, o dicionário e o README. A leitura de projeções populacionais introduzida anteriormente foi retirada. Os Excel e PNG anteriores não foram regenerados.

## 2. Alterações propostas, ainda não implementadas

### 2.1. Reunir a preparação compartilhada

**Hoje:** o leitor de localizadores, a população e a classificação de áreas ficam no IMRS. A Regionalização importa esse leitor e trata campos de programa e área que não utiliza; depois relê o planejamento para obter os nomes das regiões. Global e Desempenho repetem parte da leitura e padronização das ações.

**Proposta:** criar um módulo comum `src/bases.py` para ler e preparar ações, localizadores e população. Cada bloco pede os campos necessários. Manter `src/preparar.py` com leitura básica, conversão numérica, validação de período e gravação das memórias. Os preparadores dos blocos ficam responsáveis por seus recortes e cálculos específicos.

**Resultado:** o planejamento traz código e nome da região na mesma leitura; a Regionalização não prepara áreas temáticas. Espaços, zeros de preenchimento e números são normalizados uma vez na entrada. As validações de período, chaves e totais continuam.

**Arquivos envolvidos:** `src/preparar.py`, `src/imrs/preparar_imrs.py`, `src/regionalizacao/preparar_regionalizacao.py`, `src/execucao_global/preparar_global.py` e `src/desempenho/preparar_desempenho.py`.

### 2.2. Explicitar a referência populacional

**Hoje:** a seleção identifica a estimativa municipal local do IBGE pelo ano. O padrão é 2025, usando o arquivo fornecido para o projeto.

**Proposta:** registrar em uma configuração simples de população os campos `fonte`, `ano`, `arquivo`, `aba` e `total_mg_esperado`. Reutilizar a mesma referência IBGE 2025 na Regionalização e no IMRS. O leitor usa a referência declarada.

**Resultado:** fica explícito qual população gerou cada peso. A mudança de referência ocorre nessa configuração e aparece na memória da execução. Nenhum coeficiente populacional é digitado manualmente.

### 2.3. Retirar a conversão genérica paralela

**Hoje:** `converter_bases_raw` e `converter_para_parquet` convertem arquivos brutos para Parquet, mas os geradores não consomem essas cópias. A leitura genérica usa a primeira aba dos Excel, sem selecionar a aba e os cabeçalhos próprios de cada base.

**Proposta:** retirar esse caminho de conversão da rotina de produção e sua entrada duplicada `src/preparar_dados.py`. Preservar `salvar_bases_processadas`, que registra os DataFrames efetivamente usados no cálculo.

**Resultado:** manter um fluxo: arquivos brutos → preparação → cálculo → produtos e memória. As 13 cópias solicitadas para o IMRS continuam disponíveis; não haverá uma segunda preparação criada só para gravar arquivos.

### 2.4. Escolher os produtos a gerar

**Hoje:** `main.py` gera texto e Word mesmo quando o interesse é o Excel. Na Regionalização, gerar as tabelas exige carregar a malha e produzir cinco mapas.

**Proposta:** deixar Excel como saída básica e permitir ativar Word e mapas separadamente. Calcular as tabelas uma vez e entregar os mesmos resultados em memória aos produtos selecionados. Carregar geometrias somente quando houver mapas solicitados.

**Resultado:** o cálculo de uma tabela não depende da geração do Word ou da disponibilidade da malha. O comando específico de mapas a partir de um Excel continua útil para refazer só a imagem.

**Arquivos envolvidos:** `main.py`, os `gerar.py` dos blocos e a coordenação dos mapas. A matemática das tabelas não muda por essa separação.

### 2.5. Reaproveitar a formatação azul

**Hoje:** `src/exportacao/excel.py` identifica colunas monetárias e percentuais pelo número da tabela, com regras específicas para 9, 10 e 11. Os demais blocos usam a exportação simples.

**Proposta:** cada componente informa cabeçalhos, colunas monetárias, colunas percentuais, larguras e linhas de grupo/total. O formatador aplica o estilo existente usando essas informações.

**Resultado:** reaproveitar cabeçalho azul, faixas e destaques nas Tabelas 1 a 12 sem copiar um formatador para cada bloco. Preservar os scripts individuais por componente e os comentários explicativos.

### 2.6. Enxugar repetições da documentação

**Proposta:** preservar em cada bloco objetivo, bases, variáveis, filtros e cálculos explícitos por componente, esquema final e exemplo com total. Resumir explicações repetidas sobre percentuais e operações iguais. Reunir o histórico detalhado das divergências de planilhas em um único registro de conferências, com links a partir das regras.

**Resultado:** a regra vigente fica fácil de localizar e os registros de auditoria permanecem disponíveis. As regras de cálculo de cada tabela não serão substituídas por referências genéricas.

### 2.7. Conferir a simplificação

Comparar as saídas anteriores e posteriores usando as mesmas bases e referências: valores financeiros, contagens, taxas, recorte de 50 municípios e cobertura de 13 regiões. O efeito da mudança de população da Regionalização deve ser conferido separadamente da reorganização do código. Preservar os fechamentos entre tabelas e os alertas de divergência entre fontes.

## 3. Referências locais e dados definidos no código

### 3.1. Arquivos de origem externa já presentes no projeto

| Referência | Caminho | Uso atual |
|---|---|---|
| Estimativa IBGE 2025 | `data/raw/externas/estimativa_dou_2025.xls` | População da Regionalização e do IMRS |
| Índice IMRS | `data/raw/externas/IMRS-consulta-indicadores.xlsx`, aba `Geral`, edição 2024 | Selecionar os 50 menores índices |
| Malha municipal IBGE 2025 | `data/auxiliares/MG_Municipios_2025.zip` | Limites geográficos; não fornece pesos financeiros |
| SIGPlan | TXT de ações e localizadores em `data/raw` | Programação, execução, metas, classificações e vínculos territoriais |
| QDD Fiscal | `data/raw/planejamento/BASE_QDD_FISCAL.xlsx` | Entrada prevista para o programado de Pessoal e Auxílios |
| Execução SIAFI | `dados-siafi-2026-main/data/execucao.csv/execucao.csv` | Entrada prevista para o realizado de Pessoal e Auxílios; já conferida com o BO |

Os geradores atuais leem arquivos locais, sem consultar IBGE, FJP ou ALMG pela internet durante a execução. A rotina de Pessoal ainda não foi implementada; suas entradas estão descritas nas regras. As planilhas manuais e PDFs corporativos foram referências de conferência, não entradas automáticas dos geradores.

No estado local conferido, as bases externas de população e índice estão versionadas. A malha está presente, mas é ignorada pelo Git. O QDD e a pasta SIAFI estão presentes, mas ainda não estão versionados; uma execução em outra máquina precisa receber esses arquivos.

### 3.2. Regras e parâmetros definidos no código

| Definição | Valor | Onde participa |
|---|---|---|
| Quantidades de referência | 853 municípios, 13 regiões e recorte de 50 municípios | Validação territorial e seleção do IMRS |
| Desempate do IMRS 2024 | Prioridade para Presidente Olegário, IBGE 3153400 | Seleção no empate da 50ª posição; convenção da referência manual |
| Grupos de Área Temática | Códigos 02, 03, 04, 05, 06, 07, 09, 10 e 11 finalísticos; 01, 08, 12, 13 e 14 apoio; 15 Outros Poderes | Correspondência fixa em `GRUPO_POR_AREA`; a origem citada no código é o PPAG 2024–2027/parecer da ALMG |
| Tipo de orçamento | Tipos de ação 3, 6 e 8 identificam investimento das empresas | Tabela 1 |
| IAG | 0 demais; 1 estratégicos | Tabela 2 e Desempenho |
| Não orçamentárias | Tipo de ação 5 | Validade física no Desempenho |
| Faixas de desempenho | 0%; acima de 0% e abaixo de 70%; 70% a 130%; acima de 130%; programação zero sem meta | Tabelas 5 e 6 e Gráficos 1 e 2 |
| Localizadores especiais | 3199901 a 3199913 regionais; 3199999 estadual | Reconhecimento do alcance e rateio |
| Validação populacional regional | Total esperado de 21.393.441 | Rejeitar uma referência populacional diferente; não impõe os pesos |
| Apresentação dos mapas | Cores, escala de valores, conversão para milhões/bilhões e projeção EPSG 5880 | Desenho e legenda, sem alterar os valores financeiros das tabelas |

Nas regras de Pessoal, o recorte `(grupo = 1 e IPU diferente de 9) ou elemento = 34 ou IPU = 7` está documentado, mas ainda não está implementado em um gerador. A correspondência de grupos e outros códigos é uma regra de classificação; não é uma base financeira adicional.

## 4. Como os pesos populacionais são calculados

### 4.1. Regionalização

    população da região = soma das populações dos seus municípios
    peso da região = população da região / soma das populações de MG
    valor da região = valores municipais diretos + valores regionais diretos
                      + valor estadual × peso da região

O vínculo entre município e região vem dos localizadores do SIGPlan. Na configuração atual, usar os habitantes da estimativa IBGE 2025 e conferir o total de 21.393.441. Os per capita dividem os valores financeiros pelas populações correspondentes.

Com a referência IBGE 2025, o peso da região de Belo Horizonte é `6329241 / 21393441`, aproximadamente **29,58496018%**. Esses números são lidos e somados do arquivo fornecido, não estimados pelo script.

Nas bases atuais, o programado estadual a ratear é R$ 64.082.642.771,00. Sua parcela destinada à região de Belo Horizonte é R$ 18.958.824.343,15 com IBGE 2025.

### 4.2. IMRS

    peso do município na região = população municipal / população regional
    peso do município em MG = população municipal / população de MG
    peso do recorte na região = população dos selecionados na região / população regional
    peso do recorte em MG = população dos 50 selecionados / população de MG

No IMRS, os habitantes vêm da mesma estimativa IBGE 2025, correspondente à aba manual `pop_2025_ibge`. A seleção dos 50 vem do índice IMRS 2024, com o desempate documentado. Aplicar os pesos regionais e estaduais somente às parcelas com essas abrangências; os registros municipais dos selecionados entram integralmente. As mesmas regras são aplicadas separadamente ao programado e ao realizado.

O total estadual esperado é conferido contra a soma do arquivo. Não há uma tabela escondida de percentuais: todos os pesos são recalculados em memória a partir das populações e dos vínculos locais.
