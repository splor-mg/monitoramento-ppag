# Produto final esperado — Relatório Institucional de Monitoramento (RIM)

## Fonte de referência

O documento Word original anexado é a **referência visual e de composição dos produtos**, não uma garantia de que todos os números, períodos e redações estejam corretos. As versões PDF/HTML/Markdown são derivadas desse original e não representam nova auditoria.

**RIM:** Plano Plurianual de Ação Governamental (PPAG) 2024–2027, exercício 2026. Documento rotulado como **3º bimestre de 2026**.

## Inventário de produtos observados

| Demonstrativo | Tabelas | Gráficos | Mapas | Conteúdo esperado |
|---|---|---|---|---|
| Execução Global | 1–4 | — | — | Orçamento, acompanhamento da ação, área temática e função |
| Desempenho Consolidado | 5–6 | 1–2 | — | Status físico/orçamentário, IAG e comparações por intervalo |
| Regionalização | 7–8 | — | 1–5 | Programação/execução por região intermediária, per capita, distribuição espacial |
| IMRS | 9–11 | — | 6–7 | Programas, áreas temáticas e municípios selecionados; rateios e mapas |
| Pessoal e Auxílios | 12 | — | — | Programação e execução por setor de governo |

O relatório também contém capa, sumário, listas de tabelas/gráficos/mapas, introdução, metodologia, comentários analíticos, fontes, notas e um demonstrativo posterior indicado no sumário.

## Arquitetura-alvo do software (decidida pelo usuário)

1. **Preparação de dados:** leitura centralizada, padronização e validação das bases; referências comuns (população, territórios, malhas quando necessário) processadas apenas uma vez quando tecnicamente viável.
2. **Cálculos dos cinco demonstrativos:** independentes e paralelizáveis somente quando as dependências reais, memória e integridade permitirem. Retornar DataFrames e métricas; não exigir exportação para executar cálculos.
3. **Exportação:** produtos opcionais e desacoplados — tabelas, DataFrames, Excel, Word, gráficos, mapas e texto, com paralelismo seguro quando fizer sentido.

Para detalhes, consultar `CONTEXTO_DECISOES_MONITORAMENTO_PPAG_2026-11-23.md` neste diretório.

## Cuidados documentais — reproduzir estrutura, não possíveis erros

- O **sumário e a capa** referem o 3º bimestre, mas o início da seção 2.1 e diversas tabelas/textos de Execução Global e Regionalização ainda mencionam o **2º bimestre de 2026**. É indispensável recalcular/substituir esses trechos antes de publicar o produto final.
- A referência contém tabelas como **imagens** e não apenas tabelas nativas do Word. Para gerar o produto final, priorizar tabelas acessíveis/editáveis com dados reconciliados, se essa for a escolha do usuário.
- Na Tabela 5 aparecem totais físicos e notas de rodapé que precisam de conferência cruzada; **este pacote não valida consistência numérica ou metodológica**.
- Os gráficos e mapas representam o estilo visual e tipo de produto esperado, mas suas escalas, períodos, títulos e números devem ser regenerados a partir de DataFrames validados.
- Não corrigir silenciosamente dados ou nomenclaturas do original ao usá-lo como referência; registrar ajustes e obter os cálculos da fonte aprovada.

## Como usar como referência para agentes

1. Leia primeiro `LEIA-ME.md` e este arquivo.
2. Para captar apresentação, tipografia e paginação: consulte `01_visual/RIM_GERAL_3B_2026_REFERENCIA_VISUAL.pdf`.
3. Para regras e redação: consulte apenas a seção necessária em `02_texto/secoes/`; não carregue todo o documento se a tarefa for localizada.
4. Para imagens e detalhes de figuras: consulte `02_texto/media/`, ou as páginas originais no PDF.
5. Compare a saída gerada com a referência **estruturalmente**, mas valide valores, janelas temporais, agregações e denominadores contra as bases de referência, nunca apenas contra o Word.
