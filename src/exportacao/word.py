"""Exporta as tabelas editáveis e o texto da seção do IMRS para Word."""

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from src.exportacao.estilo import AZUL, AZUL_CLARO, ELABORACAO, FONTE, NOTA_PODERES, numero_br, percentual


def _tabela(doc, cabecalho, larguras, linhas, numericas, percentuais):
    tabela = doc.add_table(rows=1, cols=len(cabecalho))
    tabela.autofit = False
    largura = doc.sections[0].page_width - doc.sections[0].left_margin - doc.sections[0].right_margin
    for coluna, proporcao in zip(tabela.columns, larguras, strict=True):
        coluna.width = int(largura * proporcao / sum(larguras))
    tabela.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    faixa = 0
    for tipo, dados in [("cabecalho", cabecalho), *linhas]:
        linha = tabela.rows[0] if tipo == "cabecalho" else tabela.add_row()
        linha._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        for celula, coluna in zip(linha.cells, tabela.columns, strict=True):
            celula.width = coluna.width
        if tipo == "grupo":
            linha.cells[0].merge(linha.cells[-1])
            dados = dados[:1]
        escura = tipo in ("cabecalho", "grupo")
        fundo = AZUL if escura else AZUL_CLARO if tipo == "total" or faixa % 2 == 0 else "FFFFFF"
        for i, (celula, valor) in enumerate(zip(linha.cells, dados)):
            par = celula.paragraphs[0]
            espaco = Pt(0.5 if len(cabecalho) == 3 else 1)
            par.paragraph_format.space_after = espaco
            par.paragraph_format.space_before = espaco
            par.paragraph_format.line_spacing = 1
            par.paragraph_format.keep_with_next = tipo in ("cabecalho", "grupo")
            par.alignment = (WD_ALIGN_PARAGRAPH.CENTER if escura else
                             WD_ALIGN_PARAGRAPH.RIGHT if i in numericas else WD_ALIGN_PARAGRAPH.LEFT)
            texto = "" if pd.isna(valor) else str(valor)
            if texto and i in numericas and not escura:
                if i in percentuais:
                    texto = percentual(valor)
                else:
                    texto = numero_br(valor) if valor else "–"
            run = par.add_run(texto)
            run.bold = escura or tipo == "total"
            run.font.size = Pt(9)
            if escura:
                run.font.color.rgb = RGBColor.from_string("FFFFFF")
            preenchimento = OxmlElement("w:shd")
            preenchimento.set(qn("w:fill"), fundo)
            celula._tc.get_or_add_tcPr().append(preenchimento)
        if tipo == "dado":
            faixa += 1


def exportar_word(quadros, texto, ano, bimestre, caminho):
    doc = Document()
    secao = doc.sections[0]
    secao.page_width, secao.page_height = Cm(21), Cm(29.7)
    secao.left_margin = secao.right_margin = Cm(1.6)
    secao.top_margin = secao.bottom_margin = Cm(1.6)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.paragraph_format.space_after = Pt(6)
    for nome in ("Title", "Heading 1"):
        estilo = doc.styles[nome]
        estilo.font.name = "Arial"
        estilo.font.color.rgb = RGBColor.from_string("000000")
        propriedades = estilo.element.get_or_add_pPr()
        borda = propriedades.find(qn("w:pBdr"))
        if borda is not None:
            propriedades.remove(borda)
    doc.add_heading("Execução orçamentária nos municípios com menor IMRS", level=0)
    doc.add_paragraph(f"{bimestre}º bimestre de {ano}")
    abertura, analises = texto
    doc.add_paragraph(abertura)
    titulos = ("Recursos por programa", "Recursos por área temática", "Recursos por município")
    for n, (titulo, analise) in enumerate(zip(titulos, analises, strict=True), start=9):
        if n > 9:
            doc.add_page_break()
        doc.add_heading(f"Tabela {n}  {titulo}", level=1)
        for paragrafo in analise:
            doc.add_paragraph(paragrafo)
        cabecalho, larguras, linhas = quadros[f"Tabela {n}"]
        if n == 11:
            cabecalho, larguras = cabecalho[1:], larguras[1:]
            linhas = [(tipo, valores[1:]) for tipo, valores in linhas]
        numericas = {9: {2, 3}, 10: {1, 2, 3, 4, 5}, 11: {1, 2}}[n]
        _tabela(doc, cabecalho, larguras, linhas, numericas, {3, 4, 5} if n == 10 else set())
        notas = (FONTE, ELABORACAO, *((NOTA_PODERES,) if n == 10 else ()))
        par = doc.add_paragraph()
        par.paragraph_format.space_after = Pt(2)
        par.paragraph_format.keep_together = True
        par.add_run("\n".join(notas)).font.size = Pt(8)
    doc.save(caminho)
