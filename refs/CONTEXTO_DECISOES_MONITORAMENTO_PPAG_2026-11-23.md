# Monitoramento PPAG — contexto, decisões e continuidade

**Registro consolidado em:** 23/11/2026  
**Projeto:** `monitoramento-ppag`  
**Repositório local de referência (Windows):** `C:\dev\monitoramento-ppag`  
**Repositório remoto:** `https://github.com/splor-mg/monitoramento-ppag`  
**Finalidade:** fornecer contexto portátil para continuidade do projeto no Codex, Claude Code ou por outro desenvolvedor. Este arquivo pode ficar em qualquer pasta; os caminhos abaixo são relativos à raiz do repositório, salvo quando indicado.

> **Regra de interpretação:** este documento distingue **[DECIDIDO]** (diretriz aprovada pelo usuário), **[VERIFICADO]** (constatação nos arquivos, saídas ou histórico consultado), **[PROPOSTO]** (mudança ainda não confirmada como implementada) e **[PENDENTE]** (atividade em aberto). Não presumir que a arquitetura-alvo já esteja implementada. Código, testes e Git atuais devem ser conferidos antes de agir.

## 1. Propósito e escopo

Automatizar a elaboração de demonstrativos do **Relatório Institucional de Monitoramento (RIM)** do **Plano Plurianual de Ação Governamental (PPAG) de Minas Gerais**, especialmente a partir de dados do SIGPlan e bases auxiliares, com resultados rastreáveis e comparáveis às planilhas e ao relatório manual.

Componentes previstos:

| Bloco | Produtos |
|---|---|
| Execução Global | Tabelas 1 a 4 |
| Desempenho Consolidado | Tabelas 5 e 6; Gráficos 1 e 2 |
| Regionalização | Tabelas 7 e 8; Mapas 1 a 5 |
| Índice Mineiro de Responsabilidade Social (IMRS) | Tabelas 9, 10 e 11; Mapas 6 e 7; texto analítico associado |
| Pessoal e Auxílios | Tabela 12; implementação ainda pendente na última avaliação |

**Organização identificada** [VERIFICADO]: scripts em `src/` separados por bloco (`execucao_global/`, `desempenho/`, `regionalizacao/`, `imrs/`, `pessoal/`), utilitários em `src/preparar.py`, `src/config.py` e `src/exportacao/`, entrada `main.py`, bases em `data/raw/` e `data/auxiliares/`, DataFrames e memórias em `data/processed/`, resultados em `outputs/` e regras/documentação em `docs/`. Os caminhos e arquivos exatos devem ser confirmados no checkout atual.

## 2. Arquitetura-alvo: decisão principal de 23/11/2026

**[DECIDIDO] O fluxo desejado possui três etapas, com separação explícita de responsabilidades:**

```text
BASES BRUTAS E REFERÊNCIAS
          |
          v
(1) PREPARAÇÃO CENTRALIZADA
    - ler as bases necessárias uma vez, quando viável
    - padronizar códigos, tipos, números e identificadores
    - aplicar filtros e validar períodos, chaves e integridade
    - preparar população, classificação territorial e outras referências comuns
    - construir DataFrames reutilizáveis e rastreáveis
          |
          v
(2) CÁLCULOS DOS DEMONSTRATIVOS
    +------------------------+--------------------------+
    | Execução Global        | Desempenho Consolidado   |
    | Regionalização         | IMRS                     |
    | Pessoal e Auxílios     |                          |
    +------------------------+--------------------------+
    - executar independentemente / em paralelo QUANDO possível
    - retornar DataFrames e resultados estruturados
    - preservar memória de cálculo e conferências
          |
          v
(3) EXPORTAÇÃO INDEPENDENTE E OPCIONAL
    - DataFrames / Parquet de auditoria, quando requerido
    - Excel, Word, gráficos, mapas e textos
    - paralelismo somente quando houver independência e escrita segura
```

**[DECIDIDO]** Preparação cartográfica compartilhada (por exemplo, carregar/validar malhas) pode ocorrer antecipadamente **quando necessária**, mas a renderização dos mapas deve usar os resultados já calculados. Não carregar malhas nem produzir mapas quando o pedido for apenas calcular tabelas.

**[DECIDIDO]** A ordem de execução deve ser determinada pelas **dependências reais e pelo custo computacional**, não por uma ordem fixa arbitrária entre os cinco demonstrativos. Priorizar eliminar leituras e transformações redundantes **antes** de introduzir paralelismo.

**[DECIDIDO]** As exportações devem ser selecionáveis: por exemplo, calcular IMRS sem obrigatoriamente gerar Word; calcular Regionalização sem obrigatoriamente gerar os cinco mapas. Os cálculos não devem depender de gravação em Excel ou Word.

**[PROPOSTO]** Uma camada comum poderia carregar as fontes uma vez e fornecer DataFrames com contratos explícitos (colunas, tipos, chaves e período). Os blocos específicos operariam sobre esses resultados e devolveriam objetos estruturados; um orquestrador central coordenaria cálculo, validação e exportação. Nenhuma dessas mudanças deve ser considerada pronta sem inspeção do código.

## 3. Diagnóstico de arquitetura que motivou a decisão

**[VERIFICADO]** O grafo local apontou acoplamentos entre preparação de dados e cálculos. Em particular:

- `src/regionalizacao/preparar_regionalizacao.py` reutiliza funções definidas em `src/imrs/preparar_imrs.py`, incluindo leitura de localizadores e população. **Preparação comum não deveria pertencer conceitualmente ao IMRS.**
- O histórico de auditoria indicou leituras e padronizações repetidas (códigos, textos, valores numéricos) em etapas distintas do IMRS e da Regionalização.
- O fluxo genérico de conversão de bases brutas para Parquet não alimentava diretamente todos os geradores e podia realizar processamento redundante. A intenção é manter Parquets úteis de **DataFrames efetivamente calculados**, e não conversões paralelas sem consumidor.
- Havia acoplamento entre geração de resultados e exportações: no IMRS, gerar os produtos também desencadeava texto/Word; na Regionalização, tabelas e mapas eram gerados de forma fortemente vinculada.
- Os estilos Excel não estavam generalizados para os vários demonstrativos; a formatação mais especializada atendia principalmente às Tabelas 9–11.
- O `main.py` mostrado na análise anterior estava especialmente concentrado na geração do IMRS, em vez de atuar como orquestrador completo dos cinco blocos.

**[PROPOSTO]** Simplificar preparação compartilhada, separar leitura/cálculo/exportação, consolidar estilos de saída, manter scripts por componente e testes de regressão. A existência de `docs/proposta_simplificacao.md` é um **registro de proposta**, não prova de execução da refatoração.

**[DECIDIDO]** Preservar comentários úteis, documentação das fórmulas, filtros, exceções, chaves e denominadores, memórias de cálculo e auditoria. Reduzir duplicação documental sem apagar decisões metodológicas ou evidências de conciliação.

### Sobre o aparente “inchaço” do IMRS

**[VERIFICADO]** O IMRS possui mais funções e etapas especializadas (população, seleção municipal, rateio, classificação, três tabelas, mapas, texto e exportação). Uma parte da densidade representada no Graphify se deve a nós de documentação e conceitos — **contagem de nós não equivale a linhas executáveis nem prova baixa qualidade**. O problema prioritário é a mistura de responsabilidades e a reutilização de funções comuns a partir de um pacote específico.

## 4. Regras e referências de dados já verificadas

### População e seleção municipal

- **[DECIDIDO E VERIFICADO]** Utilizar a **estimativa municipal IBGE 2025** como referência populacional **tanto do IMRS quanto da Regionalização**. População total de MG: **21.393.441 habitantes**, distribuídos pelos **853 municípios** e vinculados às **13 regiões intermediárias** utilizadas no processamento.
- **[DECIDIDO]** A **FJP permanece como fonte do índice IMRS da edição de 2024**, utilizado na seleção dos **50 municípios com menores pontuações**. Não confundir a fonte do índice com a fonte da população.
- **[VERIFICADO]** Houve uma alteração equivocada temporária para população FJP 2026; foi identificada, revertida e a documentação corrigida no histórico. **Não reintroduzir essa fonte sem decisão expressa e nova validação metodológica.**
- **[VERIFICADO]** Foi confrontada a população com a aba manual `pop_2025_ibge` e a base `estimativa_dou_2025.xls`; as 853 populações municipais, vínculos regionais e 50 municípios selecionados foram conciliados.
- **[RECOMENDAÇÃO]** Declarar sempre nos produtos a fonte, o ano, a edição do índice, o período monitorado e, quando aplicável, a aba e o arquivo utilizados; validar o total estadual de população e o número de municípios.

### Exclusão lógica

- **[DECIDIDO]** Desconsiderar nos cálculos pertinentes os registros do SIGPlan com **`Exclusão Lógica da Ação = True`** para reproduzir as regras da referência manual.
- **[VERIFICADO]** Essas linhas geraram divergências substanciais entre somas brutas e valores válidos. Em análise do primeiro bimestre, foram identificadas 989 linhas excluídas; em uma matriz cartográfica, a presença de registros excluídos inflava o programado. Revalidar filtros por base e bimestre.

### Valores de referência já conciliados — IMRS, 3º bimestre de 2026

**[VERIFICADO NO HISTÓRICO, NÃO REVALIDADO NESTA DATA NO REPOSITÓRIO LOCAL]**

| Referência | Valor |
|---|---:|
| Programado total do recorte IMRS (Tabelas 9–11) | R$ 2.585.968.212,15 |
| Realizado total do recorte IMRS (Tabelas 9–11) | R$ 1.186.478.063,54 |
| População IBGE 2025 de MG | 21.393.441 |
| Municípios selecionados pelo IMRS 2024 | 50 |
| Média estadual de execução por município usada na análise do Mapa 7 | R$ 79.425.189,42 |
| Município do recorte acima dessa média | Espinosa, R$ 85.750.538,23 |

A média do Mapa 7 foi calculada a partir de **R$ 67.749.686.578,83 / 853 municípios**, isto é, um indicador estadual por município, **não** uma média apenas dos 50 municípios do IMRS.

### Erros concretos identificados em planilhas manuais

Estes exemplos justificam preservar rastreabilidade e não assumir que a planilha manual esteja sempre correta:

- **1º bimestre:** em `MUN_final!D53`, uma soma começava em `D8` e não em `D3`, omitindo cinco municípios.
- **3º bimestre:** fórmulas da planilha manual ficaram desalinhadas em **1.558 linhas** após ampliação da base, fazendo chaves e valores apontarem para registros diferentes.
- **3º bimestre:** na aba `pop_2025_ibge`, o município de **Wenceslau Braz (2.377 habitantes)** estava classificado incorretamente na linha 854 e fora de intervalos de soma, produzindo denominador de 21.391.064 em vez de 21.393.441. O ajuste das referências e a atualização da tabela dinâmica foram necessários para reconciliar os demonstrativos.

**[DECIDIDO]** Quando houver divergências, separar: erro do algoritmo, erro da referência manual, diferença de regra, problema de atualização de tabela dinâmica e mera diferença de apresentação.

## 5. Situação das entregas e pendências

- **[VERIFICADO NO HISTÓRICO]** Execução Global, Desempenho Consolidado, Regionalização e IMRS já tiveram geradores e saídas em Excel/mapas/gráficos desenvolvidos em alguma medida. Isso não significa que todos estejam prontos, completos ou testados no checkout atual.
- **[PENDENTE]** Pessoal e Auxílios / Tabela 12: base e regras já começaram a ser documentadas; o módulo tinha somente estrutura inicial na última inspeção. QDD Fiscal e dados SIAFI foram apontados como fontes relevantes a validar.
- **[PENDENTE]** Auditoria do arquivo institucional `RIM GERAL - 3º Bimestre 2026.docx` contra saídas de 2026/3bim. Achado preliminar: **Tabelas 1–4, 7 e 8 aparentemente continham números de janeiro–abril**, embora o 3º bimestre exija janeiro–junho. Revisão do Desempenho e IMRS ainda não havia sido concluída quando a sessão anterior foi interrompida por limite de uso. Não tratar o achado como relatório conclusivo sem conferência.
- **[PENDENTE]** Auditoria sistemática da arquitetura e matriz de dependências antes de implementar a refatoração centralizada.

## 6. Graphify: instalação, resultados e interpretação

**[VERIFICADO EM 23/11/2026]**

- Windows Enterprise; ferramentas locais instaladas no escopo do usuário.
- `uv` **0.13.9** instalado via WinGet.
- Graphify CLI **0.9.118** instalado em ambiente isolado com `uv` (`graphifyy`).
- Comandos `graphify install` e `graphify install --platform codex` executados com sucesso; skills globais instaladas respectivamente em `.claude/skills/graphify` e `.codex/skills/graphify` **na pasta do usuário**, não necessariamente dentro do repositório.
- Para fazer consultas `graphify query`, foi necessário instalar as dependências opcionais: `uv tool install --reinstall "graphifyy[mcp]==0.9.118"`. A extração local já havia funcionado antes disso.
- Grafo do projeto: **262 nós, 615 arestas, 13 comunidades** na versão compartilhada, associado no relatório ao commit `adcd124`.
- Consulta de exemplo: `graphify query "IMRS população regionalização" --budget 1000`; `god-nodes` destacou funções como `codigo_texto()`, `gerar_regionalizacao()`, `gerar_tabelas_imrs()` e `carregar_txt()`.
- Visualizações geradas em `graphify-out/`: `graph.html` (rede de nós), `GRAPH_TREE.html` (árvore de diretórios/funções) e `CALLFLOW.html` (diagramas de chamadas e arquitetura).

**[DECIDIDO]** Preferir **CALLFLOW.html** para compreensão visual da arquitetura, por ser mais legível que o diagrama de rede completo. Usar a árvore para localização de elementos e as consultas do grafo para relações específicas.

**[ATENÇÃO]** Nomes automáticos das comunidades no CALLFLOW, como `Security & Global Graph` e `CLI & Skill Installers`, **não correspondem às áreas funcionais reais do RIM**. Não basear decisões arquiteturais nesses rótulos. O grafo mostra relações `calls` e `imports`, mas não estabelece sozinho ordem de processamento, redundância em tempo de execução, custos ou possibilidade de paralelismo.

Comandos úteis, executados **na raiz do projeto**:

```powershell
graphify extract . --code-only
graphify update .
graphify god-nodes --top 10
graphify query "carregar_populacao" --depth 1 --budget 500
graphify affected "carregar_populacao()" --depth 2
graphify export html --graph .\graphify-out\graph.json
graphify tree --graph .\graphify-out\graph.json --output .\graphify-out\GRAPH_TREE.html
graphify export callflow-html .\graphify-out\graph.json --output .\graphify-out\CALLFLOW.html --max-sections 10
```

O modo `--code-only` constrói o grafo estrutural local sem chave de API de modelo. **Graphify local e Graphify Cloud são índices separados**: o primeiro lê alterações ainda sem `git push`; o segundo não as conhece automaticamente. O diretório `graphify-out/` é produto gerado — decidir sua política de versionamento antes de adicionar ao Git.

## 7. Claude Code, Codex e contexto compartilhado

**[DECIDIDO]** Usar **uma fonte única de instruções**, evitando duplicação entre agentes:

```text
AGENTS.md                 # documento principal de instruções do projeto
CLAUDE.md                 # somente @AGENTS.md, quando criado/configurado no projeto
docs/CONTINUIDADE.md      # estado de execução mutável, separado das regras permanentes
docs/HANDOFFS/            # opcional: registros curtos entre agentes
```

- `AGENTS.md` é lido nativamente pelo Codex; o Claude Code pode importar `@AGENTS.md` no `CLAUDE.md`.
- **Não há necessidade de `CODEX.md` duplicado.** Só considerar arquivo separado se surgir configuração específica que não pertença às instruções compartilhadas.
- **[STATUS]** Estrutura **proposta/decidida**, mas não há confirmação nesta conversa de que esses arquivos já tenham sido criados no repositório. O Graphify criou ou alterou um `CLAUDE.md` **global do usuário** durante sua própria instalação, o que não substitui automaticamente um `CLAUDE.md` do projeto.
- **[DECIDIDO]** Para economizar contexto, manter instruções estáveis concisas; registrar mudanças e pendências em documento de continuidade; iniciar novas sessões com leitura localizada do arquivo e consulta do Git, sem colar transcrições extensas.
- **[DECIDIDO]** Graphify para dependências e impactos; Serena para localizar/editar símbolos e funções; Context7 **somente quando necessário** para documentação atualizada de APIs. Não invocar todas as ferramentas em cada tarefa.
- **[STATUS]** Instalação local do Graphify nos dois agentes confirmada. A instalação/ativação do Serena no Codex e a autenticação do Context7 em cada agente **não estão confirmadas** aqui. Para Context7, foi preferida a integração oficial do catálogo Anthropic (servidor `https://mcp.context7.com/mcp`).

## 8. Procedimento de trabalho aprovado

1. **Verificar o estado atual:** `git status --short`, branch, último commit, arquivos de instruções e diretórios de dados. Em 23/11/2026, `git status --short` mostrou a pasta **`dados-siafi-2026-main/` não rastreada**. Não apagar, mover nem incluir essa pasta automaticamente.
2. **Analisar antes de alterar:** usar Graphify para dependências, Serena para símbolos, ler apenas os arquivos relevantes e comparar com regras em `docs/`.
3. **Entregar diagnóstico e plano da refatoração antes de implementá-la.** Registrar fluxo real de execução, matriz de dependências, redundâncias e riscos.
4. **Refatorar incrementalmente:** primeiro preparação centralizada, depois interface de cálculos por bloco, exportação independente e por último paralelismo mensurado.
5. **Validar antes/depois:** chaves, totais, período, população, classificação regional, recorte IMRS, indicadores per capita, fórmulas e arquivos finais. Conferir também as referências manuais, pois já continham erros.
6. **Preservar trabalho existente:** não reescrever sem necessidade, não sobrescrever alterações de outro agente e **não fazer commit/push sem autorização específica**.
7. **Segurança institucional:** distinguir ferramentas locais de MCPs remotos. Não enviar código, dados ou documentos corporativos confidenciais a serviços externos sem autorização adequada.

## 9. Próximo trabalho recomendado

**[PENDENTE — prioridade arquitetural]** Solicitar ao Codex ou Claude uma auditoria **somente leitura** da implementação atual, incluindo:

- fluxo real desde os arquivos brutos até cada um dos cinco demonstrativos e respectivos produtos;
- quais funções abrem novamente os mesmos arquivos ou repetem normalização, classificação e cálculo;
- dependências diretas entre IMRS e Regionalização; quais devem migrar para preparação comum;
- funções que simultaneamente calculam, exportam e desenham mapas/gráficos;
- contratos esperados para DataFrames intermediários e produtos finais;
- dependências que bloqueiam ou permitem execução paralela, custo de memória e riscos de escrita;
- testes de equivalência numérica e critérios objetivos de aceitação.

**[PENDENTE — prioridade de entrega]** Retomar a auditoria do Word institucional do 3º bimestre de 2026 e concluir a comparação por tabela, gráfico e mapa, indicando erros numéricos, períodos desatualizados, diferenças de regras e diferenças apenas estéticas.

### Mensagem curta para iniciar outra sessão

> Trabalhe no repositório `C:\dev\monitoramento-ppag`. Leia o documento “Monitoramento PPAG — contexto, decisões e continuidade”, confira `git status` e o código atual. **Não presuma que propostas foram implementadas.** A arquitetura-alvo é: (1) preparação centralizada de dados, (2) cálculos independentes dos cinco demonstrativos com paralelismo quando justificável, (3) exportações opcionais e independentes. Preserve IBGE 2025 (21.393.441 habitantes) no IMRS e na Regionalização; FJP IMRS 2024 define o recorte dos 50 municípios. Use Graphify/Serena para investigar e não altere, commite ou envie arquivos sem autorização. Primeiramente apresente um diagnóstico do fluxo real e um plano incremental, preservando os resultados numéricos.

---

**Limite deste registro:** consolidação do histórico de conversas e arquivos de visualização fornecidos até 23/11/2026; não equivale a uma auditoria atualizada do código local. Após novas alterações, atualizar as seções de status e retirar pendências concluídas. Evitar guardar neste documento dados pessoais, credenciais ou segredos de acesso.
