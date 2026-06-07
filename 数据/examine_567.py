"""Examine current state of Chapters 5-7 and all tables."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn

doc = Document('d:/bishe/我的论文.docx')

MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

print('=' * 60)
print('PARAGRAPHS Ch5-7 (indices 160+)')
print('=' * 60)
for i in range(155, min(len(doc.paragraphs), 240)):
    p = doc.paragraphs[i]
    t = p.text.strip()
    has_img = False
    for child in p._element:
        if 'drawing' in child.tag: has_img = True; break
        for sub in child:
            if 'drawing' in sub.tag: has_img = True; break
    img_mark = ' [IMG]' if has_img else ''
    oms = len(p._element.findall(f'{{{MATH_NS}}}oMath'))
    if t or has_img:
        print(f'[{i}]{img_mark} OMML={oms} {t[:120]}')

print()
print('=' * 60)
print('TABLES IN DOCUMENT')
print('=' * 60)
for ti, table in enumerate(doc.tables):
    print(f'\n--- Table {ti} ({len(table.rows)} rows × {len(table.columns)} cols) ---')
    for ri, row in enumerate(table.rows):
        cells = [cell.text.strip()[:40] for cell in row.cells]
        print(f'  Row {ri}: {cells}')

print()
print('=' * 60)
print('FORMULAS IN Ch5-7 PARAS')
print('=' * 60)
for i in range(155, min(len(doc.paragraphs), 240)):
    p = doc.paragraphs[i]
    oms = p._element.findall(f'{{{MATH_NS}}}oMath')
    if oms:
        t = p.text.strip()[:80]
        print(f'[{i}] {t}')
        for j, om in enumerate(oms):
            texts = []
            for t_elem in om.iter(f'{{{MATH_NS}}}t'):
                if t_elem.text: texts.append(t_elem.text)
            print(f'  OMML[{j}]: {"".join(texts)}')
