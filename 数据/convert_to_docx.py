#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert 项目说明文档.md to a professionally formatted Word document.
- 黑体 (SimHei) for all headings and body text
- Times New Roman for formulas, numbers, code
- White background, black text
- Proper tables, code blocks, and image placeholders
"""

import re
import os
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import copy

# ── Configuration ──────────────────────────────────────────────
MD_FILE = r"d:/bishe/项目说明文档.md"
DOCX_FILE = r"d:/bishe/项目说明文档.docx"
BASE_DIR = r"d:/bishe"

# Font names
SIMHEI = "SimHei"
TIMES = "Times New Roman"
CONSOLAS = "Consolas"

# ── Helper functions ───────────────────────────────────────────

def set_font(run, name=SIMHEI, size=Pt(11), bold=False, color=None, east_asian=None):
    """Set font properties for a run."""
    run.font.name = name
    run.font.size = size
    run.bold = bold
    if color:
        run.font.color.rgb = color
    # Set East-Asian font
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} />')
        rPr.insert(0, rFonts)
    ea = east_asian if east_asian else name
    rFonts.set(qn('w:eastAsia'), ea)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)

def set_cell_font(cell, name=SIMHEI, size=Pt(10), bold=False):
    """Set font for all runs in a table cell."""
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            set_font(run, name=name, size=size, bold=bold)

def set_paragraph_spacing(paragraph, before=0, after=0, line_spacing=1.15):
    """Set paragraph spacing."""
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line_spacing

def add_heading_styled(doc, text, level=1):
    """Add a heading with SimHei font."""
    h = doc.add_heading(text, level=level)
    set_paragraph_spacing(h, before=12, after=6, line_spacing=1.2)
    for run in h.runs:
        size_map = {1: Pt(22), 2: Pt(16), 3: Pt(13), 4: Pt(11)}
        set_font(run, name=SIMHEI, size=size_map.get(level, Pt(11)), bold=True)
    return h

def add_paragraph_styled(doc, text, size=Pt(11), bold=False, alignment=None):
    """Add a normal paragraph with SimHei font."""
    p = doc.add_paragraph()
    set_paragraph_spacing(p, before=0, after=4, line_spacing=1.15)
    if alignment is not None:
        p.alignment = alignment
    run = p.add_run(text)
    set_font(run, name=SIMHEI, size=size, bold=bold)
    return p

def add_code_block(doc, code_text):
    """Add a code block with Consolas font."""
    lines = code_text.strip().split('\n')
    for line in lines:
        p = doc.add_paragraph()
        set_paragraph_spacing(p, before=0, after=0, line_spacing=1.0)
        # Left indent for code
        pf = p.paragraph_format
        pf.left_indent = Cm(0.5)
        run = p.add_run(line if line else ' ')
        set_font(run, name=CONSOLAS, size=Pt(9), color=RGBColor(0x1A, 0x1A, 0x1A))
    # Add a small spacer after code block
    sp = doc.add_paragraph()
    set_paragraph_spacing(sp, before=0, after=2, line_spacing=1.0)

def parse_inline_formatting(paragraph, text):
    """
    Parse inline markdown and add formatted runs to the paragraph.
    Handles: **bold**, `code`, <i>italic</i>, <sub>subscript</sub>, <sup>superscript</sup>
    """
    # Pattern for all inline formats
    patterns = [
        (r'\*\*(.+?)\*\*', 'bold'),
        (r'`([^`]+)`', 'code'),
        (r'<i>(.+?)</i>', 'italic'),
        (r'<sub>(.+?)</sub>', 'subscript'),
        (r'<sup>(.+?)</sup>', 'superscript'),
        (r'<b>(.+?)</b>', 'bold_math'),
    ]

    # Combine all patterns
    combined = '|'.join(f'({p})' for p, _ in patterns)
    tokens = re.split(combined, text)

    for token in tokens:
        if token is None or token == '':
            continue

        # Check which pattern matched
        matched = False
        for pattern, style in patterns:
            m = re.fullmatch(pattern, token)
            if m:
                content = m.group(1)
                run = paragraph.add_run(content)
                if style == 'bold' or style == 'bold_math':
                    set_font(run, name=SIMHEI, size=Pt(11), bold=True)
                elif style == 'code':
                    set_font(run, name=CONSOLAS, size=Pt(10))
                elif style == 'italic':
                    set_font(run, name=SIMHEI, size=Pt(11))
                    run.italic = True
                elif style == 'subscript':
                    set_font(run, name=SIMHEI, size=Pt(9))
                    run.font.subscript = True
                elif style == 'superscript':
                    set_font(run, name=SIMHEI, size=Pt(9))
                    run.font.superscript = True
                matched = True
                break

        if not matched:
            # Plain text - detect numbers and variables for Times New Roman
            run = paragraph.add_run(token)
            set_font(run, name=SIMHEI, size=Pt(11))

    return paragraph

def is_table_separator(line):
    """Check if line is a markdown table separator like |---|---|"""
    return bool(re.match(r'^\|[\s\-:|]+\|$', line.strip()))

def parse_table_row(line):
    """Parse a markdown table row into cells."""
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [cell.strip() for cell in line.split('|')]

def add_table_from_lines(doc, lines):
    """Create a Word table from markdown table lines."""
    # lines[0] is header, lines[1] is separator, lines[2:] are data
    header_cells = parse_table_row(lines[0])
    data_lines = lines[2:] if len(lines) > 2 else []

    num_cols = len(header_cells)
    num_rows = 1 + len(data_lines)

    table = doc.add_table(rows=num_rows, cols=num_cols, style='Table Grid')
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for j, cell_text in enumerate(header_cells):
        cell = table.rows[0].cells[j]
        # Header background
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="2F5496" w:val="clear"/>')
        cell._element.get_or_add_tcPr().append(shading)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_spacing(p, before=2, after=2, line_spacing=1.0)
        p.clear()
        run = p.add_run(cell_text)
        set_font(run, name=SIMHEI, size=Pt(10), bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))

    # Data rows
    for i, row_line in enumerate(data_lines):
        cells = parse_table_row(row_line)
        for j, cell_text in enumerate(cells):
            if j < num_cols:
                cell = table.rows[i + 1].cells[j]
                # Alternating row color
                if i % 2 == 0:
                    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F2F7FB" w:val="clear"/>')
                    cell._element.get_or_add_tcPr().append(shading)
                p = cell.paragraphs[0]
                set_paragraph_spacing(p, before=1, after=1, line_spacing=1.0)
                p.clear()
                run = p.add_run(cell_text)
                set_font(run, name=SIMHEI, size=Pt(9))

    # Add spacer after table
    doc.add_paragraph()
    return table

def add_image_placeholder(doc, img_path, caption=""):
    """Add an image or placeholder caption."""
    full_path = img_path if os.path.isabs(img_path) else os.path.join(BASE_DIR, img_path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_spacing(p, before=6, after=2, line_spacing=1.0)

    if os.path.exists(full_path):
        try:
            run = p.add_run()
            run.add_picture(full_path, width=Inches(5.5))
        except Exception:
            run = p.add_run(f'[图片: {img_path}]')
            set_font(run, name=SIMHEI, size=Pt(9), color=RGBColor(0x80, 0x80, 0x80))
    else:
        run = p.add_run(f'[图片: {img_path}]')
        set_font(run, name=SIMHEI, size=Pt(9), color=RGBColor(0x80, 0x80, 0x80))

    if caption:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_spacing(cap, before=0, after=8, line_spacing=1.0)
        run = cap.add_run(caption)
        set_font(run, name=SIMHEI, size=Pt(9), color=RGBColor(0x50, 0x50, 0x50))

def add_horizontal_rule(doc):
    """Add a horizontal rule (border line)."""
    p = doc.add_paragraph()
    set_paragraph_spacing(p, before=6, after=6, line_spacing=1.0)
    # Add bottom border to paragraph
    pPr = p._element.get_or_add_pPr()
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:bottom w:val="single" w:sz="6" w:space="1" w:color="999999"/>'
        f'</w:pBdr>'
    )
    pPr.append(pBdr)

# ── Page setup ─────────────────────────────────────────────────

def setup_styles(doc):
    """Configure document styles."""
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = SIMHEI
    font.size = Pt(11)
    rPr = style.element.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{SIMHEI}" w:ascii="{SIMHEI}" w:hAnsi="{SIMHEI}"/>')
    rPr.insert(0, rFonts)
    pf = style.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(4)
    pf.line_spacing = 1.15

    # Page margins
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.5)

# ── Main Conversion ────────────────────────────────────────────

def convert_markdown_to_docx():
    """Main conversion function."""

    with open(MD_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = Document()
    setup_styles(doc)

    i = 0
    in_code_block = False
    code_buffer = []
    in_table = False
    table_buffer = []

    while i < len(lines):
        line = lines[i].rstrip()

        # ── Code block (```...```) ──
        if line.strip().startswith('```'):
            if in_code_block:
                add_code_block(doc, '\n'.join(code_buffer))
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # ── Table handling ──
        # Detect table: starts with | header |, followed by |---|---|
        if line.strip().startswith('|') and not in_table:
            if i + 1 < len(lines) and is_table_separator(lines[i + 1].strip()):
                in_table = True
                table_buffer = [line]
                i += 1
                continue

        if in_table:
            table_buffer.append(line)
            # Check if next line continues the table
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('|'):
                i += 1
                continue
            else:
                # End of table
                add_table_from_lines(doc, table_buffer)
                table_buffer = []
                in_table = False
                i += 1
                continue

        # ── Heading detection ──
        heading_match = re.match(r'^(#{1,4})\s+(.+?)(?:\s*\{.*\})?$', line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            add_heading_styled(doc, title, level=level)
            i += 1
            continue

        # ── Horizontal rule ──
        if line.strip() in ('---', '___', '***'):
            add_horizontal_rule(doc)
            i += 1
            continue

        # ── Image ──
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
        if img_match:
            alt_text = img_match.group(1)
            img_path = img_match.group(2)
            add_image_placeholder(doc, img_path, alt_text)
            i += 1
            continue

        # ── Blockquote (>) — used for image captions ──
        if line.strip().startswith('>'):
            text = line.strip()[1:].strip()
            p = doc.add_paragraph()
            set_paragraph_spacing(p, before=0, after=4, line_spacing=1.0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = p.paragraph_format
            pf.left_indent = Cm(1)
            run = p.add_run(text)
            set_font(run, name=SIMHEI, size=Pt(9), color=RGBColor(0x60, 0x60, 0x60))
            i += 1
            continue

        # ── Empty line ──
        if line.strip() == '':
            # Add small space only if not after table/code
            i += 1
            continue

        # ── Center-aligned formula paragraph ──
        center_match = re.match(r'^<p align="center">(.+)</p>$', line.strip())
        if center_match:
            text = center_match.group(1)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_paragraph_spacing(p, before=1, after=1, line_spacing=1.15)
            parse_inline_formatting(p, text)
            i += 1
            continue

        # ── Regular paragraph ──
        p = doc.add_paragraph()
        set_paragraph_spacing(p, before=0, after=3, line_spacing=1.15)
        parse_inline_formatting(p, line.strip())
        i += 1

    # ── Save ──
    doc.save(DOCX_FILE)
    print(f"Word document saved to: {DOCX_FILE}")

if __name__ == '__main__':
    convert_markdown_to_docx()
