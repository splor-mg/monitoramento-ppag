# monitoramento-ppag
Scripts e rotinas para tratamento, análise e geração de tabelas, gráficos e demonstrativos do monitoramento do PPAG de Minas Gerais.

## Organização do código

- `main.py` recebe o ano e o bimestre e coordena a geração do IMRS.
- `src/preparar.py` reúne leitura, padronização, checagem de período e gravação em Parquet.
- `src/preparar_mapas.py` lê a malha municipal de MG, reúne os municípios nas
  13 regiões intermediárias e associa indicadores pelo código territorial.
- `src/imrs/preparar_imrs.py` carrega as bases da seção e aplica o filtro de exclusão lógica ao
  planejamento do IMRS, o recorte dos 50 municípios, os pesos populacionais e o rateio.
- `src/imrs/` tem um arquivo por tabela e por mapa. `gerar.py` confere os totais e
  prepara os quadros, `texto.py` faz a análise e `cartografia.py` compartilha o desenho dos mapas.
- `src/exportacao/` reúne a formatação e a gravação do Excel e do Word.
- `src/execucao_global/`, `src/desempenho/` e `src/regionalizacao/` têm um script
  por componente e uma rotina de execução por seção.
- `src/pessoal/` reserva espaço para a seção de Pessoal e Auxílios.

## Tabelas do IMRS

Na raiz do repositório, instale as dependências e gere as tabelas 9, 10 e 11.

```powershell
poetry install
poetry run python main.py --ano 2026 --bimestre 2
```

O comando lê as quatro bases em `data/raw` e grava `outputs/IMRS_2026_2bim.xlsx`,
com uma aba por tabela e a memória de cálculo municipal. As bases incluídas
cobrem os três primeiros bimestres de 2026. Os padrões são IMRS de 2024 e
projeção populacional FJP de 2026, baseada no IBGE. Use `--ano-imrs` e `--ano-populacao` para escolher outras
edições disponíveis e `--saida` para definir o caminho do arquivo.

O Excel aplica o padrão azul do RIM e inclui subtotais e totais. A mesma
execução grava um Word de mesmo nome com as três tabelas editáveis e o texto
do bimestre. O texto recalcula os destaques e usa como média estadual a soma
dos valores elegíveis em Minas Gerais dividida pelos 853 municípios.

A mesma execução registra os DataFrames em Parquet em
`data/processed/imrs/<ano>/<bimestre>bim/imrs_<edição>_pop_<ano>/<execução>/`.
O caminho é exibido ao final. Cada pasta guarda as quatro bases preparadas,
o recorte do IMRS, a referência populacional, os pesos dos municípios do
recorte, as duas bases com `valor_imrs`, as três tabelas e a memória municipal.
Essas cópias servem para conferência. O comando lê `data/raw` a cada rodada.

## Mapas 6 e 7 do IMRS

Na primeira vez, baixe a [malha municipal de MG de 2025](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/UFs/MG/)
do IBGE e guarde o ZIP em `data/auxiliares/MG_Municipios_2025.zip`.
Para gerar Excel, Word e mapas em uma única execução:

```powershell
poetry run python main.py --ano 2026 --bimestre 2 --mapas
```

Os mapas usam os resultados da Tabela 11 em memória, cruzados com a malha
pelo código IBGE. O Mapa 6 usa o programado anual e o Mapa 7 usa o realizado
acumulado. Os dois PNGs saem junto dos outros arquivos, em `outputs/` por padrão.

Para gerar só os mapas a partir de um Excel já pronto:

```powershell
poetry run python -m src.imrs.mapas --ano 2026 --bimestre 2
```

Nesse comando, `--malha` aceita outra malha local com o campo `CD_MUN`,
`--tabela` indica outro Excel com a aba `Tabela 11` e `--saida` define a pasta
dos PNGs.

A preparação cartográfica aceita a relação entre código IBGE e região
intermediária para formar os limites dos Mapas 1 a 5 a partir da mesma
malha municipal. O desenho e os cálculos desses mapas estão em
`src/regionalizacao/`.

## Desempenho Consolidado

Gerar Tabelas 5 e 6 e Gráficos 1 e 2 a partir dos TXT de ações e localizadores
do bimestre em `data/raw/monitoramento/`.

```powershell
poetry run python -m src.desempenho.gerar --ano 2026 --bimestre 3
```

Cada componente possui um script comentado em `src/desempenho/`. A execução
grava um Excel com as duas tabelas e dois PNGs em
`outputs/Desempenho_<ano>_<bimestre>bim/`. O argumento `--saida` escolhe outra
pasta. As ações classificadas, tabelas e dados dos gráficos ficam registrados
em `data/processed/desempenho/<ano>/<bimestre>bim/<execução>/`.

O desempenho físico usa a programação inicial acumulada até o bimestre.
A validade orçamentária usa a previsão da LOA diferente de zero. A validade
física acrescenta as ações não orçamentárias. Os filtros são aplicados nas
contagens. Os gráficos recalculam percentuais excluindo Sem meta estabelecida.

## Execução Global

```powershell
poetry run python -m src.execucao_global.gerar --ano 2026 --bimestre 3
```

Os scripts comentados de cada Tabela 1 a 4 ficam em `src/execucao_global/`.
O Excel sai em `outputs/Global_<ano>_<bimestre>bim/`. A rotina confere os
totais anual, programado até o bimestre e realizado das quatro tabelas com
a base de ações. O argumento `--saida` escolhe outra pasta.

## Regionalização

```powershell
poetry run python -m src.regionalizacao.gerar --ano 2026 --bimestre 3
```

Gera as Tabelas 7 e 8 em Excel e um PNG por Mapa 1 a 5. Cada componente
possui um script comentado em `src/regionalizacao/`. As saídas ficam em
`outputs/Regionalizacao_<ano>_<bimestre>bim/`. Os argumentos `--saida`,
`--ano-populacao` e `--malha` permitem escolher a pasta, a edição da população
e a malha municipal, com os mesmos padrões usados no IMRS.

O programado desconsidera os registros marcados com exclusão lógica de ação.
O per capita estadual divide o executado total pela população de MG.
As conferências com as ações sinalizam divergências de origem, como a
diferença de R$ 10.714,63 do realizado de fevereiro de 2026.

As duas rotinas registram os DataFrames em `data/processed/global/` e
`data/processed/regionalizacao/`, identificados por ano, bimestre e execução.
