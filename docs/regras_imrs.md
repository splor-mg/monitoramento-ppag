# Regras de Negócio — Demonstrativos do IMRS

## 1. Objetivo
Produzir os três demonstrativos do RIM referentes aos municípios classificados nas 50 últimas posições do IMRS:
- por programa;
- por área temática;
- por município.

## 2. Recorte de municípios
Selecionar os 50 municípios com menor valor de IMRS na edição utilizada como referência para o exercício.
A seleção deve ser feita ordenando o índice em ordem crescente e mantendo os 50 primeiros municípios.

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

## 9. Tabela 9 — Programas
Agrupar os valores apropriados por:

    código do programa
    programa

Calcular:

    programado
    realizado

Programas com programado igual a zero e realizado superior a zero devem permanecer no demonstrativo.

Registros em que programado e realizado sejam ambos zero não precisam ser apresentados.

## 10. Tabela 10 — Áreas Temáticas
Agrupar por área temática.

Calcular:

    programado
    realizado

Além disso:

    execução = realizado / programado

    participação global =
        realizado da área / realizado total

    participação no grupo =
        realizado da área / realizado do respectivo grupo

As áreas devem ser organizadas nos grupos:

- Áreas Temáticas Finalísticas;
- Áreas Temáticas de Apoio e Suporte;
- Outros Poderes.

Programas dos demais Poderes sem área temática do PMDI devem ser
consolidados como "Outros Poderes".

## 11. Tabela 11 — Municípios
Apresentar exclusivamente os 50 municípios selecionados.

Para cada município:

    programado =
        municipal direto
        + regional rateado
        + estadual rateado

    realizado =
        municipal direto
        + regional rateado
        + estadual rateado

## 12. Fechamento
Os totais das três tabelas devem coincidir:

    total por programa
    =
    total por área temática
    =
    total por município

A igualdade deve ser verificada separadamente para:

- programado;
- realizado.

## 13. Particularidades

### Programas sociais
Atualmente é um filtro não utilizado pois não são demonstrativos presentes no RIM Social, mas é uma base válida de ser considerada.

### Exclusão lógica
Os campos de exclusão lógica existentes na base de planejamento não são
utilizados.

### Execução sem programação
Programas com execução e sem valor inicialmente programado devem permanecer Essa ocorrência não deve ser tratada como erro.