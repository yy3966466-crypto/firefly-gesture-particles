"""Fix remaining issues: formula fonts, figure/table numbering, and position issues."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
import re

doc = Document('d:/bishe/我的论文.docx')
print('Document loaded')

# ── 1. Fix table/figure caption format: "表4 1" -> "表4.1", "图4 1" -> "图4.1" ──
print('\n=== 1. Fix caption formats ===')
fixed_captions = 0
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    # Fix "表4 1" -> "表4.1" etc
    new_t = re.sub(r'(表|图)(\d+)\s+(\d+)', r'\1\2.\3', t)
    if new_t != t:
        for run in p.runs:
            run.text = ''
        if p.runs:
            p.runs[0].text = new_t
            print(f'  [{i}] "{t[:50]}" -> "{new_t[:50]}"')
            fixed_captions += 1

if fixed_captions == 0:
    print('  No caption format fixes needed')

# ── 2. Fix "图3.3" in Chapter 5 -> "图5.4" ──
print('\n=== 2. Fix Figure 3.3 in Chapter 5 ===')
for i, p in enumerate(doc.paragraphs):
    if '图3.3' in p.text and i > 150:  # Chapter 5 starts around para 155
        for run in p.runs:
            run.text = ''
        if p.runs:
            p.runs[0].text = '图5.4  系统数据流全景图'
            print(f'  [{i}] 图3.3 -> 图5.4')
        break
else:
    # Try finding without dot
    for i, p in enumerate(doc.paragraphs):
        if '图3' in p.text and '3' in p.text and '系统' in p.text and i > 150:
            print(f'  Found at [{i}]: "{p.text.strip()}"')
            break

# ── 3. Fix OMML formula fonts: Times New Roman, 12pt ──
print('\n=== 3. Fix OMML formula fonts ===')
MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
count = 0
for p in doc.paragraphs:
    p_elem = p._element
    # Find ALL m:oMath elements
    oms = p_elem.findall(f'{{{MATH_NS}}}oMath')
    for om in oms:
        for r in om.findall(f'{{{MATH_NS}}}r'):
            rPr = r.find(f'{{{MATH_NS}}}rPr')
            if rPr is None:
                rPr = OxmlElement('m:rPr')
                r.insert(0, rPr)

            # Remove existing font/size elements to avoid duplicates
            old_fonts = rPr.find(f'{{{MATH_NS}}}rFonts')
            if old_fonts is not None:
                rPr.remove(old_fonts)
            old_sz = rPr.find(f'{{{MATH_NS}}}sz')
            if old_sz is not None:
                rPr.remove(old_sz)
            old_szCs = rPr.find(f'{{{MATH_NS}}}szCs')
            if old_szCs is not None:
                rPr.remove(old_szCs)

            # Set font name
            rFonts = OxmlElement('m:rFonts')
            rFonts.set(qn('m:ascii'), 'Times New Roman')
            rFonts.set(qn('m:hAnsi'), 'Times New Roman')
            rFonts.set(qn('m:cs'), 'Times New Roman')
            rPr.append(rFonts)

            # Set size 12pt (sz=24 in half-points)
            sz = OxmlElement('m:sz')
            sz.set(qn('m:val'), '24')
            rPr.append(sz)

            szCs = OxmlElement('m:szCs')
            szCs.set(qn('m:val'), '24')
            rPr.append(szCs)

            count += 1
print(f'  Fixed {count} OMML runs')

# ── 4. Verify font changes immediately ──
print('\n=== Verifying font changes ===')
verified = 0
for p in doc.paragraphs:
    for r in p._element.findall(f'{{{MATH_NS}}}oMath/{{{MATH_NS}}}r'):
        rPr = r.find(f'{{{MATH_NS}}}rPr')
        if rPr is not None:
            rFonts = rPr.find(f'{{{MATH_NS}}}rFonts')
            sz = rPr.find(f'{{{MATH_NS}}}sz')
            if rFonts is not None and sz is not None:
                font = rFonts.get(qn('m:ascii'))
                sz_val = sz.get(qn('m:val'))
                if font == 'Times New Roman' and sz_val == '24':
                    verified += 1
print(f'  Verified {verified} OMML runs have correct font settings')

# ── 5. Save with explicit path verification ──
print('\n=== Saving ===')
doc.save('d:/bishe/我的论文.docx')
print('Saved to d:/bishe/我的论文.docx')

# ── 6. Post-verification ──
doc2 = Document('d:/bishe/我的论文.docx')
print('\n=== Post-save verification ===')

# Check caption fixes
print('\n-- Captions --')
for i, p in enumerate(doc2.paragraphs):
    t = p.text.strip()
    if t and (t.startswith('表') or t.startswith('图')):
        if i < 200:  # Only main text
            print(f'  [{i}] {t[:70]}')

# Check font on first formula
print('\n-- Font check on (4-4) --')
for i, p in enumerate(doc2.paragraphs):
    if '(4-4)' in p.text.strip():
        for r in p._element.findall(f'{{{MATH_NS}}}oMath/{{{MATH_NS}}}r'):
            rPr = r.find(f'{{{MATH_NS}}}rPr')
            if rPr is not None:
                rFonts = rPr.find(f'{{{MATH_NS}}}rFonts')
                sz = rPr.find(f'{{{MATH_NS}}}sz')
                if rFonts is not None and sz is not None:
                    fam = rFonts.get(qn('m:ascii'))
                    sv = sz.get(qn('m:val'))
                    print(f'  Font: {fam}, Size: {sv}')
                    break
        break

print('\n=== DONE ===')
