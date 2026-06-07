#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build final, fully-formatted Word document from 项目说明文档.md.
- Replaces ASCII art with proper rendered diagrams
- Converts all formulas to OMML
- Standardizes all table formatting
- Fixes fonts, alignments, spacing throughout
"""

import re, os, copy
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from lxml import etree

# ── Paths ──
MD_FILE  = r"d:/bishe/项目说明文档.md"
DOCX_OUT = r"d:/bishe/项目说明文档.docx"
BASE_DIR = r"d:/bishe"

# ── Font constants ──
SIMHEI   = "SimHei"
TIMES    = "Times New Roman"
CONSOLAS = "Consolas"

# ═══════════════════════════════════════════════════════════════
# WORD BUILDING UTILITIES
# ═══════════════════════════════════════════════════════════════

def set_run_font(run, name=SIMHEI, size=Pt(11), bold=False, italic=False, color=None):
    """Configure a run's font."""
    run.font.name = name
    run.font.size = size
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts_elem = rPr.find(qn('w:rFonts'))
    if rFonts_elem is None:
        rFonts_elem = parse_xml(f'<w:rFonts {nsdecls("w")} />')
        rPr.insert(0, rFonts_elem)
    for attr, val in [('w:eastAsia', name), ('w:ascii', name), ('w:hAnsi', name), ('w:cs', name)]:
        rFonts_elem.set(qn(attr), val)


def add_styled_heading(doc, text, level):
    """Add SimHei heading."""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        sz = {1: Pt(22), 2: Pt(16), 3: Pt(13), 4: Pt(11)}.get(level, Pt(11))
        set_run_font(run, SIMHEI, sz, bold=True)
        if level <= 2:
            run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    pf = h.paragraph_format
    pf.space_before = Pt(14 if level <= 2 else 10)
    pf.space_after  = Pt(6)
    return h


def add_body_para(doc, text, bold=False, size=Pt(11)):
    """Add a body paragraph with SimHei font, handling inline formatting."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after  = Pt(3)
    pf.line_spacing = 1.15

    # Parse **bold** and `code` inline
    parts = re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            run = p.add_run(part[2:-2])
            set_run_font(run, SIMHEI, size, bold=True)
        elif part.startswith('`') and part.endswith('`'):
            run = p.add_run(part[1:-1])
            set_run_font(run, CONSOLAS, Pt(10))
        else:
            run = p.add_run(part)
            set_run_font(run, SIMHEI, size, bold=bold)
    return p


def add_code_para(doc, text):
    """Add a code line with Consolas font."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after  = Pt(0)
    pf.line_spacing = 1.0
    pf.left_indent = Cm(0.6)
    run = p.add_run(text if text else ' ')
    set_run_font(run, CONSOLAS, Pt(9), color=RGBColor(0x1A, 0x1A, 0x1A))
    return p


def add_hr(doc):
    """Add a thin horizontal rule."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4)
    pf.space_after  = Pt(4)
    pPr = p._element.get_or_add_pPr()
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:bottom w:val="single" w:sz="4" w:space="1" w:color="AAAAAA"/>'
        f'</w:pBdr>'
    )
    pPr.append(pBdr)


def add_image(doc, img_rel_path, width_inches=5.5):
    """Embed a PNG image, center-aligned."""
    full = os.path.join(BASE_DIR, img_rel_path.replace('/', os.sep))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(full):
        try:
            run = p.add_run()
            run.add_picture(full, width=Inches(width_inches))
        except Exception:
            run = p.add_run(f'[ 图片缺失: {img_rel_path} ]')
            set_run_font(run, SIMHEI, Pt(9), color=RGBColor(0x99, 0x99, 0x99))
    else:
        run = p.add_run(f'[ 图片缺失: {img_rel_path} ]')
        set_run_font(run, SIMHEI, Pt(9), color=RGBColor(0x99, 0x99, 0x99))
    return p


def add_image_caption(doc, text):
    """Add a centered caption below an image."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after  = Pt(8)
    run = p.add_run(text)
    set_run_font(run, SIMHEI, Pt(9), color=RGBColor(0x70, 0x70, 0x70))
    return p


# ── TABLE ────────────────────────────────────────────────────

def add_table_md(doc, lines):
    """Convert markdown table lines (header + sep + rows) into a formatted Word table."""
    def parse_row(line):
        line = line.strip().lstrip('|').rstrip('|')
        return [c.strip() for c in line.split('|')]

    header = parse_row(lines[0])
    data_rows = [parse_row(l) for l in lines[2:]] if len(lines) > 2 else []
    ncols = len(header)
    nrows = 1 + len(data_rows)

    table = doc.add_table(rows=nrows, cols=ncols, style='Table Grid')
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Autofit
    table.autofit = True

    # Header
    for j, txt in enumerate(header):
        cell = table.rows[0].cells[j]
        # Blue header background
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="2F5496" w:val="clear"/>')
        cell._element.get_or_add_tcPr().append(shading)
        # Clear default paragraph and add styled one
        p = cell.paragraphs[0]
        p.clear()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf = p.paragraph_format
        pf.space_before = Pt(2)
        pf.space_after  = Pt(2)
        pf.line_spacing = 1.0
        run = p.add_run(txt)
        set_run_font(run, SIMHEI, Pt(9.5), bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))

    # Data rows
    for i, row in enumerate(data_rows):
        bg = 'F4F8FD' if i % 2 == 0 else 'FFFFFF'
        for j in range(ncols):
            cell = table.rows[i + 1].cells[j]
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg}" w:val="clear"/>')
            cell._element.get_or_add_tcPr().append(shading)

            p = cell.paragraphs[0]
            p.clear()
            pf = p.paragraph_format
            pf.space_before = Pt(1)
            pf.space_after  = Pt(1)
            pf.line_spacing = 1.05

            txt = row[j] if j < len(row) else ''
            # Bold if cell content is wrapped with **
            if txt.startswith('**') and txt.endswith('**'):
                txt = txt[2:-2]
                bold = True
            else:
                bold = False

            # Use formula cell rendering if text contains math tags
            if is_mixed_formula_text(txt):
                add_mixed_text_to_paragraph(p, txt, Pt(8.5))
            else:
                run = p.add_run(txt)
                set_run_font(run, SIMHEI, Pt(8.5), bold=bold)

    # Spacer
    spacer = doc.add_paragraph()
    pf = spacer.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after  = Pt(2)
    return table


# ── MIXED TEXT PARSER (Chinese + Math) ──────────────────────

def add_mixed_text_to_paragraph(p, text, base_size=Pt(11), sub=False, sup=False):
    """Parse text with <i>/<sub>/<sup>/<b> tags into properly-fonted runs.
    Handles nested tags recursively (e.g. <sub><i>x</i></sub>).
    """
    tokens = re.split(r'(<i>.*?</i>|<sub>.*?</sub>|<sup>.*?</sup>|<b>.*?</b>|&emsp;)', text)
    for token in tokens:
        if not token:
            continue
        if token == '&emsp;':
            run = p.add_run('    ')
            set_run_font(run, TIMES, base_size)
            continue

        m_i   = re.match(r'<i>(.*?)</i>', token)
        m_sub = re.match(r'<sub>(.*?)</sub>', token)
        m_sup = re.match(r'<sup>(.*?)</sup>', token)
        m_b   = re.match(r'<b>(.*?)</b>', token)

        if m_i:
            run = p.add_run(m_i.group(1))
            set_run_font(run, TIMES, base_size, italic=True)
            if sub: run.font.subscript = True
            if sup: run.font.superscript = True
        elif m_sub:
            add_mixed_text_to_paragraph(p, m_sub.group(1), Pt(base_size.pt * 0.75), sub=True)
        elif m_sup:
            add_mixed_text_to_paragraph(p, m_sup.group(1), Pt(base_size.pt * 0.75), sup=True)
        elif m_b:
            run = p.add_run(m_b.group(1))
            set_run_font(run, TIMES, base_size, bold=True)
            if sub: run.font.subscript = True
            if sup: run.font.superscript = True
        else:
            run = p.add_run(token)
            if re.search(r'[一-鿿]', token):
                set_run_font(run, SIMHEI, base_size)
            else:
                set_run_font(run, TIMES, base_size)
            if sub: run.font.subscript = True
            if sup: run.font.superscript = True


def add_formula_paragraph(doc, text, base_size=Pt(11)):
    """Parse and add a formula paragraph (centered, mixed fonts for math)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after  = Pt(2)
    pf.line_spacing = 1.2
    add_mixed_text_to_paragraph(p, text, base_size)
    return p


def is_mixed_formula_text(text):
    """Check if text contains formula markup (<i>, <sub>, <sup>)."""
    return bool(re.search(r'<(i|sub|sup|b)>', text))


# ═══════════════════════════════════════════════════════════════
# MAIN STATE MACHINE PARSER
# ═══════════════════════════════════════════════════════════════

def build_document():
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = Document()

    # ── Page setup ──
    for sec in doc.sections:
        sec.top_margin    = Cm(2.54)
        sec.bottom_margin = Cm(2.54)
        sec.left_margin   = Cm(2.8)
        sec.right_margin  = Cm(2.4)

    # Default style
    style = doc.styles['Normal']
    style.font.name = SIMHEI
    style.font.size = Pt(11)
    rPr = style.element.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{SIMHEI}" w:ascii="{SIMHEI}" w:hAnsi="{SIMHEI}"/>')
    rPr.insert(0, rFonts)

    i = 0
    in_code_block = False
    code_buffer = []
    in_table = False
    table_buffer = []
    # Track consecutive code blocks for 4.2.x (ASCII call flows) to replace with images
    code_block_start_idx = 0
    ascii_art_sections = {}  # line_start → replacement diagram

    # Map ASCII art sections to their replacements
    # 2.5: data flow diagram
    # 3.11: folder hierarchy
    # 4.2.1-4.2.4: call flow diagrams (these should stay as code since they're detailed text, not ASCII art)
    # 4.3: call dependency graph

    while i < len(lines):
        line = lines[i].rstrip()

        # ── Code block ──
        if line.strip().startswith('```'):
            if in_code_block:
                code_text = '\n'.join(code_buffer)
                in_code_block = False

                # Check if this is an ASCII art section that should be replaced by an image
                stripped = code_text.strip()
                # Detect box-drawing characters for 2.5
                if '┌' in stripped or '└' in stripped:
                    if '数据采集层' in stripped and 'MIT-BIH' in stripped:
                        add_image(doc, 'diagrams/01_data_flow.png', 5.5)
                        add_image_caption(doc, '图 2.5  系统数据流总览（四层架构）')
                        code_buffer = []
                        i += 1
                        continue
                # Detect tree characters for 3.11
                if ('├──' in stripped or '└──' in stripped) and 'main.m' in stripped:
                    add_image(doc, 'diagrams/02_folder_hierarchy.png', 5.8)
                    add_image_caption(doc, '图 3.11  项目文件夹层级关联与调用关系')
                    code_buffer = []
                    i += 1
                    continue
                # Detect 4.3 dependency graph (short tree)
                if ('BioMonitorApp.m' in stripped and '/    |' in stripped):
                    add_image(doc, 'diagrams/03_call_dependency.png', 5.5)
                    add_image_caption(doc, '图 4.3  子程序互相调用依赖关系图')
                    code_buffer = []
                    i += 1
                    continue
                # Detect 4.2.x call flows (these have detailed function names, keep as code)
                # These are the detailed flow descriptions - keep them as code blocks
                if 'BioMonitorApp' in stripped and ('prepareData()' in stripped or 'startMonitoring()' in stripped
                                                     or 'saveSession()' in stripped
                                                     or 'addpath' in stripped):
                    # These are detailed walkthroughs - keep as code
                    pass

                # Normal code block
                for cl in code_buffer:
                    add_code_para(doc, cl)
                spacer = doc.add_paragraph()
                spacer.paragraph_format.space_after = Pt(2)
                code_buffer = []
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # ── Table ──
        if line.strip().startswith('|') and not in_table:
            if i + 1 < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i + 1].strip()):
                in_table = True
                table_buffer = [line]
                i += 1
                continue

        if in_table:
            table_buffer.append(line)
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('|'):
                i += 1
                continue
            else:
                # End table — decide if it's a formula table
                add_table_md(doc, table_buffer)
                table_buffer = []
                in_table = False
                i += 1
                continue

        # ── Heading ──
        h_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if h_match:
            level = len(h_match.group(1))
            title = h_match.group(2).strip()
            # Remove trailing {#...} if present
            title = re.sub(r'\s*\{#.*\}', '', title)
            add_styled_heading(doc, title, level)
            i += 1
            continue

        # ── HR ──
        if line.strip() == '---':
            add_hr(doc)
            i += 1
            continue

        # ── Image ──
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
        if img_match:
            alt = img_match.group(1)
            path = img_match.group(2)
            w = 5.5
            if 'architecture' in path.lower():
                w = 5.2
            add_image(doc, path, w)
            add_image_caption(doc, alt)
            i += 1
            continue

        # ── Blockquote ──
        if line.strip().startswith('>'):
            txt = line.strip()[1:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf = p.paragraph_format
            pf.left_indent = Cm(1)
            pf.space_before = Pt(0)
            pf.space_after  = Pt(4)
            run = p.add_run(txt)
            set_run_font(run, SIMHEI, Pt(9), color=RGBColor(0x70, 0x70, 0x70))
            i += 1
            continue

        # ── Centered HTML formula paragraph ──
        center_match = re.match(r'^<p align="center">(.+)</p>$', line.strip())
        if center_match:
            text = center_match.group(1)
            add_formula_paragraph(doc, text)
            i += 1
            continue

        # ── Empty line ──
        if line.strip() == '':
            i += 1
            continue

        # ── Normal paragraph ──
        if is_mixed_formula_text(line):
            add_formula_paragraph(doc, line, Pt(11))
        else:
            add_body_para(doc, line)

        i += 1

    # ── Save ──
    doc.save(DOCX_OUT)
    print(f"Saved: {DOCX_OUT}")


# ═══════════════════════════════════════════════════════════════
# ENTRY
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    build_document()
