"""Cores, créditos e formatação numérica dos relatórios do RIM."""

AZUL = "1F4E78"
AZUL_CLARO = "DDEBF7"
FONTE = "Fonte: Sistema de Informações Gerenciais e de Planejamento (SIGPlan)."
ELABORACAO = "Elaboração: Superintendência Central de Planejamento e Orçamento (SCPO)."
NOTA_PODERES = "Outros Poderes reúne os programas sem vinculação às áreas temáticas do Executivo."


def numero_br(valor, casas=2):
    return f"{valor:,.{casas}f}".translate(str.maketrans(",.", ".,"))


def reais(valor):
    return f"R$ {numero_br(valor)}"


def percentual(valor):
    return f"{numero_br(valor * 100)}%"
