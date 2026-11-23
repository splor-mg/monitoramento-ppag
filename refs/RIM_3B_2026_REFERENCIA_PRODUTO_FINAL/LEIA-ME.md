# Pacote de referência — produto final do RIM

Este ZIP contém **o RIM original anexado pelo usuário e representações complementares** para apoiar a construção do produto final no projeto `monitoramento-ppag`.

## Por onde começar

- **Precisão visual e paginação:** `01_visual/RIM_GERAL_3B_2026_REFERENCIA_VISUAL.pdf` (35 páginas).
- **Conteúdo em texto e figuras:** `02_texto/RIM_COMPLETO.md`.
- **Consulta rápida e econômica por seção:** `02_texto/secoes/` (comece pelo arquivo específico do demonstrativo).
- **Leitura no navegador:** `02_texto/RIM_NAVEGAVEL.html` (abrir o arquivo HTML com a pasta `media/` ao lado).
- **Especificação do resultado desejado:** `04_especificacao/PRODUTO_FINAL_ESPERADO.md`.
- **Inventário estruturado:** `04_especificacao/MANIFESTO_PRODUTOS.json`.
- **Decisões sobre arquitetura do projeto:** `04_especificacao/CONTEXTO_DECISOES_MONITORAMENTO_PPAG_2026-11-23.md`.
- **Documento editável intacto:** `00_original/RIM_GERAL_3B_2026_original.docx`.

## Por que vários formatos?

- **PDF:** preserva a aparência, paginação, mapas e tabelas como vistos no relatório.
- **Markdown em arquivos separados:** reduz o volume de contexto para Claude/Codex e permite ler somente a parte em análise.
- **HTML:** consulta visual pesquisável no navegador.
- **PNG/JPG:** permite consultar cada figura separadamente sem renderizar o Word; arquivos EMF do Word foram convertidos para PNG.
- **DOCX:** original para comparar estilo e manter elementos editáveis existentes.
- **JSON:** inventário inequívoco dos produtos esperados.

## Escopo e fidelidade

O conteúdo não foi reescrito nem validado. Um relatório com rótulo de 3º bimestre pode conter **trechos ainda referentes ao 2º bimestre**. A formatação exportada para PDF pode ter pequenas diferenças de fontes/paginação dependendo do aplicativo. O Word original permanece a fonte primária da aparência pretendida.

**Não tratar o documento como fonte validada de números**, mas como referência de quais produtos e seções o software deverá gerar. Os dados e fórmulas precisam de conciliação independente.

Não é necessário enviar todo o ZIP ao contexto do modelo: extraia-o localmente e selecione somente os arquivos pertinentes.
