"""Clean up 4.2.3 area: remove orphan labels, fix image positioning, and ensure RR formula is correct."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document('d:/bishe/我的论文.docx')
body = doc.element.body
MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

print('=== Current structure ===')
for i in range(130, 150):
    if i < len(doc.paragraphs):
        t = doc.paragraphs[i].text.strip()[:90]
        has_img = False
        for child in doc.paragraphs[i]._element:
            if 'drawing' in child.tag: has_img = True; break
            for sub in child:
                if 'drawing' in sub.tag: has_img = True; break
        print(f'[{i}] img={has_img} \"{t}\"')

# ── STEP 1: Remove orphan (4-7) label at para 137 ──
p137 = doc.paragraphs[137]
if p137.text.strip() == '(4-7)':
    # Check if it has no OMML content (just a label)
    oms = p137._element.findall(f'{{{MATH_NS}}}oMath')
    if len(oms) == 0:
        body.remove(p137._element)
        print('\nRemoved orphan (4-7) label at para 137')
    else:
        print(f'\n(4-7) has {len(oms)} OMML elements - keeping it')
else:
    print(f'\nPara 137 is not (4-7), it is: \"{p137.text.strip()[:50]}\"')

# ── STEP 2: After removal, re-index to find current positions ──
print('\n=== Structure after cleanup ===')
for i in range(130, 150):
    if i < len(doc.paragraphs):
        t = doc.paragraphs[i].text.strip()[:90]
        has_img = False
        for child in doc.paragraphs[i]._element:
            if 'drawing' in child.tag: has_img = True; break
            for sub in child:
                if 'drawing' in sub.tag: has_img = True; break
        print(f'[{i}] img={has_img} \"{t}\"')

doc.save('d:/bishe/我的论文.docx')
print('\nSaved')
