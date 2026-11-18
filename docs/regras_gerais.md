# Regras Gerais do Monitoramento do PPAG

## 1. Parâmetros de execução
As rotinas devem receber o exercício e o bimestre como parâmetros.
O ano e o bimestre não devem ser fixados nas funções de processamento.
Na execução acumulada, usar janeiro até o último mês do bimestre.
Identificar em cada demonstrativo se a comparação usa a programação anual ou
a programação acumulada do período.

## 2. Identificadores
Sempre que houver identificador numérico ou código institucional disponível, ele deve ser utilizado como chave de relacionamento entre bases.
Nomes e descrições devem ser tratados como atributos, e não como chaves principais.

## 3. Integridade dos relacionamentos
Relacionamentos entre bases não devem produzir multiplicação inesperada de registros ou valores.
As chaves das tabelas de referência devem ser validadas quanto à unicidade antes dos relacionamentos.
Registros sem correspondência devem ser identificados explicitamente.

## 4. Valores ausentes
Valores financeiros ausentes que representem ausência de movimentação podem ser tratados como zero.
Ausência de chaves, classificações ou identificadores não deve ser silenciosamente convertida em zero ou ignorada.

## 5. Precisão numérica
Os cálculos devem preservar a precisão original dos valores durante o processamento.
Arredondamentos destinados à apresentação devem ocorrer somente na geração dos produtos finais.

## 6. Rastreabilidade
As bases brutas não devem ser sobrescritas.
As transformações devem ser reproduzíveis a partir das bases de entrada.

## 7. Validação
Cada módulo deve possuir verificações de consistência compatíveis com sua metodologia.
Resultados inconsistentes devem produzir erro ou alerta explícito.
Calcular taxas de subtotais e totais a partir dos valores agregados. Quando
o denominador for zero, apresentar a taxa como indisponível.
