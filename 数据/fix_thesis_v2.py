import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
import re

MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
etree.register_namespace('m', MATH_NS)


def m(tag):
    return OxmlElement(f'm:{tag}')


def mr(text):
    r = m('r')
    t = m('t')
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r


def set_equation(paragraph, text, num_text=None):
    """Replace paragraph with OMML equation containing plain text."""
    p = paragraph._p
    pPr = p.find(qn('w:pPr'))
    for child in list(p):
        if child.tag != qn('w:pPr'):
            p.remove(child)

    omath = m('oMath')
    omath.append(mr(text))
    omathPara = m('oMathPara')
    omathPara.append(omath)

    if pPr is not None:
        p.insert(p.index(pPr) + 1, omathPara)
    else:
        p.append(omathPara)

    if num_text:
        tab_run = OxmlElement('w:r')
        tab = OxmlElement('w:tab')
        tab_run.append(tab)
        p.append(tab_run)
        num_run = OxmlElement('w:r')
        num_t_w = OxmlElement('w:t')
        num_t_w.text = f'({num_text})'
        num_t_w.set(qn('xml:space'), 'preserve')
        num_run.append(num_t_w)
        p.append(num_run)


# ---- Inline math conversion helpers ----

# Chinese character range (CJK Unified Ideographs)
CHINESE_RE = re.compile(r'[一-鿿]')
# Patterns for non-Chinese segments that are MATH expressions
MATH_OPERATORS_RE = re.compile(r'[=^_×∑±μαβσεθΔπωφλητλ]')
# Pattern to split Chinese text vs non-Chinese runs
SPLIT_RE = re.compile(
    r'[一-鿿　-〿＀-￯，。、；：（）【】""''《》！？…·—]+'
    r'|[^一-鿿　-〿＀-￯，。、；：（）【】""''《》！？…·—]+'
)


def is_math_segment(segment):
    """Determine if a non-Chinese text segment is a math expression."""
    s = segment.strip()
    if not s:
        return False
    # Citation references like [18-19], [16] — NOT math
    if re.match(r'^\[\d+[\-\d,\.]*\]$', s):
        return False
    # Pure numbers (with optional % or unit) — NOT math
    if re.match(r'^[\d.]+%?$', s):
        return False
    # Enumerations (1), (2), a), b) etc. — NOT math
    if re.match(r'^[\(（]?\d+[\)）]\.?$', s):
        return False
    if re.match(r'^[a-zA-Z][\)）]\.?$', s):
        return False
    # Standalone brackets/arrows — NOT math
    if re.match(r'^[\[\](){}<>→↓↑←]+$', s):
        return False
    # Check for math operators or Greek letters — IS math
    if MATH_OPERATORS_RE.search(s):
        return True
    # Variable(parentheses) pattern like x(n), HR_i — IS math
    if re.match(r'[a-zA-Z_][a-zA-Z0-9_]*(?:\([^)]*\)|_[a-zA-Z0-9]+)+', s):
        return True
    # Short standalone variable (single letter or letter+digit) — IS math
    # only if in a math context (surrounded by math operators or variables)
    if re.match(r'^[a-zA-Z][a-zA-Z0-9]?$', s):
        return False  # conservative — avoid over-matching
    return False


def split_math_segments(text):
    """Split text into list of (is_math, segment_string) pairs."""
    segments = []
    for match in SPLIT_RE.finditer(text):
        segment = match.group()
        if not segment.strip():
            continue
        if CHINESE_RE.search(segment):
            segments.append((False, segment))
        else:
            segments.append((is_math_segment(segment), segment))
    return segments


def create_text_run(text, rPr_source=None):
    """Create a w:r element with text content and optional formatting."""
    r = OxmlElement('w:r')
    if rPr_source is not None:
        src_rPr = rPr_source.find(qn('w:rPr'))
        if src_rPr is not None:
            r.append(etree.__deepcopy(src_rPr, {}) if hasattr(etree, '__deepcopy')
                     else src_rPr.__deepcopy__({}))
    t = OxmlElement('w:t')
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r


def convert_para_inline_math(paragraph, para_idx=None):
    """Convert a paragraph's inline math expressions to OMML elements.

    Scans the paragraph text, identifies math segments vs text segments,
    and rebuilds the paragraph XML with w:r for text and m:oMath for math.
    """
    text = paragraph.text
    if not text.strip():
        return

    segments = split_math_segments(text)
    has_math = any(is_math for is_math, _ in segments)
    if not has_math:
        return

    p = paragraph._p
    pPr = p.find(qn('w:pPr'))
    # get first run for formatting reference
    first_run = p.find(qn('w:r'))
    rPr_ref = first_run if first_run is not None else None

    # remove all children except pPr
    for child in list(p):
        if child.tag != qn('w:pPr'):
            p.remove(child)

    insert_after = pPr if pPr is not None else None

    for is_math, seg in segments:
        if not seg.strip():
            continue
        if is_math:
            elem = m('oMath')
            elem.append(mr(seg))
        else:
            elem = create_text_run(seg, rPr_ref)

        if insert_after is not None:
            # insert right after the previous element (pPr or last inserted)
            p.insert(p.index(insert_after) + 1, elem)
        else:
            p.append(elem)
        insert_after = elem  # next one goes after this

    tag = f'[Para {para_idx}] ' if para_idx is not None else ''
    print(f'  {tag}inline math → OMML')


# ---- Three-line table ----
def make_three_line(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)

    old_borders = tblPr.find(qn('w:tblBorders'))
    if old_borders is not None:
        tblPr.remove(old_borders)

    borders = OxmlElement('w:tblBorders')
    for side, val, sz in [('top', 'single', 12), ('bottom', 'single', 6),
                           ('left', 'none', 0), ('right', 'none', 0),
                           ('insideH', 'none', 0), ('insideV', 'none', 0)]:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), val)
        el.set(qn('w:sz'), str(sz))
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), '000000')
        borders.append(el)
    tblPr.append(borders)

    for row in table.rows:
        for cell in row.cells:
            tcPr = cell._tc.tcPr
            if tcPr is not None:
                tc_borders = tcPr.find(qn('w:tcBorders'))
                if tc_borders is not None:
                    tcPr.remove(tc_borders)

    for cell in table.rows[0].cells:
        tcPr = cell._tc.tcPr
        if tcPr is None:
            tcPr = OxmlElement('w:tcPr')
            cell._tc.insert(0, tcPr)
        tc_borders = OxmlElement('w:tcBorders')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '0')
        bottom.set(qn('w:color'), '000000')
        tc_borders.append(bottom)
        tcPr.append(tc_borders)


# ================================================================
# MAIN
# ================================================================
doc = Document('我的论文_v6_updated.docx')

# 0) Quick sanity — skip para 26-31 (intro re-written, no inline math)
#    Actually these may have English terms like MATLAB that would be
#    incorrectly classified as math, so skip them.
skip_paras = set(range(26, 32))

# 1) Figure renumbering (Chapter 3)
fig_fixes = {
    79: ('图3.2', '图3.1'),
    88: ('图3.3', '图3.2'),
    98: ('图3.4', '图3.3'),
    101: ('图3.1', '图3.4'),
}
for idx, (old, new) in fig_fixes.items():
    for run in doc.paragraphs[idx].runs:
        if old in run.text:
            run.text = run.text.replace(old, new)
    print(f'[Para {idx}] {old} → {new}')

for run in doc.paragraphs[99].runs:
    if '图3.1' in run.text:
        run.text = run.text.replace('图3.1', '图3.4')
        print(f'[Para 99] 图3.1 → 图3.4')
        break

# 2) Standalone OMML equations
eq_defs = [
    (49, "x'(n) = (1/N) ∑_{k=0}^{N-1} X(k)·M(k)·e^{j2πkn/N}", '2-1'),
    (50, 'X(k) = ∑_{n=0}^{N-1} x(n)·e^{−j2πkn/N}', '2-2'),
    (111, 'threshold(n) = mean(envelope(n)) + 1.40 × std(envelope(n))', '4-1'),
    (127, 'y(n) = w^{T}(n)·x(n−d)', '4-2'),
    (126, 'e(n) = d(n) − y(n)', '4-3'),
    (125, 'w(n+1) = w(n) + 2μ·e(n)·x(n−d)', '4-4'),
    (167, 'CV = σ / μ', '5-1'),
    (197, 'SNR(dB) = 10 × log₁₀(var(x_filtered) / var(x_raw − x_filtered))', '6-1'),
]
for idx, text, num in eq_defs:
    set_equation(doc.paragraphs[idx], text, num)
    print(f'[Para {idx}] Equation ({num})')

# 3) Inline math conversion in running text paragraphs
#    Auto-detect math expressions within Chinese text
inline_paras = [64, 95, 110, 117, 124, 133, 135, 139, 141, 196]
for idx in inline_paras:
    if idx < len(doc.paragraphs) and idx not in skip_paras:
        convert_para_inline_math(doc.paragraphs[idx], para_idx=idx)

# 4) Three-line tables
for i, table in enumerate(doc.tables):
    make_three_line(table)
    print(f'[Table {i}] three-line')

# 5) Save
output_path = '我的论文_v6_final_formatted.docx'
doc.save(output_path)
print(f'\nDone → {output_path}')
