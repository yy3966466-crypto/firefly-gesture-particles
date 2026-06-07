"""Examine OMML structure in para 183 (CV formula) and para 201-202."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

doc = Document('d:/bishe/我的论文.docx')

MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

# Para 183 - CV formula
print('=== Para 183 OMML structure ===')
p = doc.paragraphs[183]
oms = p._element.findall(f'{{{MATH_NS}}}oMath')
for j, om in enumerate(oms):
    print(f'\nOMML[{j}]:')
    print(etree.tostring(om, pretty_print=True).decode())

# Para 201 - concatenated formulas
print('\n\n=== Para 201 OMML structure ===')
p = doc.paragraphs[201]
oms = p._element.findall(f'{{{MATH_NS}}}oMath')
for j, om in enumerate(oms):
    print(f'\nOMML[{j}]:')
    texts = []
    for t_elem in om.iter(f'{{{MATH_NS}}}t'):
        if t_elem.text: texts.append(t_elem.text)
    print(f'Texts: {"".join(texts)}')
    # Check for fraction elements
    fracs = om.findall(f'{{{MATH_NS}}}f')
    print(f'  Fractions: {len(fracs)}')
    for k, f in enumerate(fracs):
        print(f'  Fraction[{k}]:')
        nums = f.findall(f'{{{MATH_NS}}}num/{{{MATH_NS}}}r/{{{MATH_NS}}}t')
        dens = f.findall(f'{{{MATH_NS}}}den/{{{MATH_NS}}}r/{{{MATH_NS}}}t')
        num_text = ''.join([n.text or '' for n in nums])
        den_text = ''.join([d.text or '' for d in dens])
        print(f'    num: "{num_text}", den: "{den_text}"')

# Para 202
print('\n\n=== Para 202 OMML structure ===')
p = doc.paragraphs[202]
oms = p._element.findall(f'{{{MATH_NS}}}oMath')
for j, om in enumerate(oms):
    print(f'\nOMML[{j}]:')
    texts = []
    for t_elem in om.iter(f'{{{MATH_NS}}}t'):
        if t_elem.text: texts.append(t_elem.text)
    print(f'Texts: {"".join(texts)}')

# Check Table 3 structure
print('\n\n=== Table 3 Detailed ===')
table = doc.tables[3]
for ri, row in enumerate(table.rows):
    cells_text = []
    for ci, cell in enumerate(row.cells):
        cells_text.append(f'[{ci}]"{cell.text}"')
    print(f'Row {ri}: {", ".join(cells_text)}')

# Check Table 6 Detailed
print('\n\n=== Table 6 Detailed ===')
table = doc.tables[5]
for ri, row in enumerate(table.rows):
    cells_text = []
    for ci, cell in enumerate(row.cells):
        cells_text.append(f'[{ci}]"{cell.text}"')
    print(f'Row {ri}: {", ".join(cells_text)}')
