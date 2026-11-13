# monitoramento-ppag
Scripts e rotinas para tratamento, análise e geração de tabelas, gráficos e demonstrativos do monitoramento do PPAG de Minas Gerais.

## Tabelas do IMRS

Na raiz do repositório, instale as dependências e gere as tabelas 9, 10 e 11.

```powershell
poetry install
poetry run python main.py --ano 2026 --bimestre 2
```

O comando lê as quatro bases em `data/raw` e grava `outputs/IMRS_2026_2bim.xlsx`,
com uma aba por tabela e a memória de cálculo municipal. As bases incluídas
cobrem os três primeiros bimestres de 2026. Os padrões são IMRS de 2024 e
população de 2025. Use `--ano-imrs` e `--ano-populacao` para escolher outras
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
Depois de gerar o Excel do bimestre, rode:

```powershell
poetry run python -m src.mapas_imrs --ano 2026 --bimestre 2
```

O script lê a aba `Tabela 11`, cruza os 50 municípios pelo código IBGE e
grava os dois PNGs em `outputs/`. O Mapa 6 usa o programado anual e o Mapa 7
usa o realizado acumulado do bimestre. Cada mapa tem sua escala em R$ milhões.

Use `--malha` para indicar outra malha local com o campo `CD_MUN`, `--tabela`
para escolher outro Excel com a aba `Tabela 11` ou `--saida` para gravar os PNGs
em outra pasta.
