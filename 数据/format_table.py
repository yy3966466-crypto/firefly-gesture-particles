"""Reformat Table 3 as a proper 三线表 and fix data errors."""
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

doc = Document('d:/bishe/我的论文.docx')

# Find Table 3 (R-wave detection results, 8x9)
t = doc.tables[3]

# ── Fix data ──
# Row 5 (index 5) = record 233, TP cell (index 4) has 2799, should be 2779
tp_cell = t.rows[5].cells[4]
if tp_cell.text.strip() == '2799':
    for p in tp_cell.paragraphs:
        for r in p.runs:
            r.text = '2779'

# Fix "bmp" to "bpm" in header
last_header_cell = t.rows[0].cells[8]
if 'bmp' in last_header_cell.text.lower():
    for p in last_header_cell.paragraphs:
        for r in p.runs:
            r.text = r.text.replace('bmp', 'bpm')

# ── Apply 三线表 borders ──
tbl = t._tbl
tblPr = tbl.find(qn('w:tblPr'))
if tblPr is None:
    tblPr = OxmlElement('w:tblPr')
    tbl.insert(0, tblPr)

# Remove existing table borders
existing = tblPr.find(qn('w:tblBorders'))
if existing is not None:
    tblPr.remove(existing)

# Create proper borders
borders = OxmlElement('w:tblBorders')

# Top: thick (1.5pt = sz=18)
top = OxmlElement('w:top')
top.set(qn('w:val'), 'single')
top.set(qn('w:sz'), '18')
top.set(qn('w:space'), '0')
top.set(qn('w:color'), '000000')
borders.append(top)

# Left: none
left = OxmlElement('w:left')
left.set(qn('w:val'), 'none')
left.set(qn('w:sz'), '0')
left.set(qn('w:space'), '0')
left.set(qn('w:color'), '000000')
borders.append(left)

# Bottom: thick (1.5pt = sz=18)
bottom = OxmlElement('w:bottom')
bottom.set(qn('w:val'), 'single')
bottom.set(qn('w:sz'), '18')
bottom.set(qn('w:space'), '0')
bottom.set(qn('w:color'), '000000')
borders.append(bottom)

# Right: none
right = OxmlElement('w:right')
right.set(qn('w:val'), 'none')
right.set(qn('w:sz'), '0')
right.set(qn('w:space'), '0')
right.set(qn('w:color'), '000000')
borders.append(right)

# InsideH: none
ih = OxmlElement('w:insideH')
ih.set(qn('w:val'), 'none')
ih.set(qn('w:sz'), '0')
ih.set(qn('w:space'), '0')
ih.set(qn('w:color'), '000000')
borders.append(ih)

# InsideV: none
iv = OxmlElement('w:insideV')
iv.set(qn('w:val'), 'none')
iv.set(qn('w:sz'), '0')
iv.set(qn('w:space'), '0')
iv.set(qn('w:color'), '000000')
borders.append(iv)

tblPr.append(borders)

# ── Add thin bottom border to header row (row 0) ──
for cell in t.rows[0].cells:
    tc = cell._tc
    tcPr = tc.find(qn('w:tcPr'))
    if tcPr is None:
        tcPr = OxmlElement('w:tcPr')
        tc.insert(0, tcPr)

    # Remove existing cell borders
    existing_cell_borders = tcPr.find(qn('w:tcBorders'))
    if existing_cell_borders is not None:
        tcPr.remove(existing_cell_borders)

    # Add thin bottom border
    cell_borders = OxmlElement('w:tcBorders')
    cb = OxmlElement('w:bottom')
    cb.set(qn('w:val'), 'single')
    cb.set(qn('w:sz'), '6')
    cb.set(qn('w:space'), '0')
    cb.set(qn('w:color'), '000000')
    cell_borders.append(cb)
    tcPr.append(cell_borders)

# ── Center align all cells ──
for row in t.rows:
    for cell in row.cells:
        tc = cell._tc
        tcPr = tc.find(qn('w:tcPr'))
        if tcPr is None:
            tcPr = OxmlElement('w:tcPr')
            tc.insert(0, tcPr)

        # Remove old alignment if exists
        old_jc = tcPr.find(qn('w:jc'))
        if old_jc is not None:
            tcPr.remove(old_jc)

        # Add center alignment
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'center')
        tcPr.append(jc)

        # Also center paragraph alignment
        for p in cell.paragraphs:
            p_elem = p._element
            pPr = p_elem.find(qn('w:pPr'))
            if pPr is None:
                pPr = OxmlElement('w:pPr')
                p_elem.insert(0, pPr)
            p_jc = pPr.find(qn('w:jc'))
            if p_jc is not None:
                pPr.remove(p_jc)
            p_jc_new = OxmlElement('w:jc')
            p_jc_new.set(qn('w:val'), 'center')
            pPr.append(p_jc_new)

doc.save('d:/bishe/我的论文.docx')
print('Done — Table 3 reformatted as 三线表')
