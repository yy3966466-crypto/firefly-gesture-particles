"""Comprehensive fix for section 4.3: deduplicate, restore headers, position figures correctly."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from lxml import etree

doc = Document('d:/bishe/我的论文.docx')
body = doc.element.body
MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

def make_text_run(text):
    r = OxmlElement('w:r')
    t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r

def make_header_para(text, level=3):
    """Create a heading paragraph."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    if level == 2:
        pStyle = OxmlElement('w:pStyle'); pStyle.set(qn('w:val'), '2'); pPr.append(pStyle)
    elif level == 3:
        pStyle = OxmlElement('w:pStyle'); pStyle.set(qn('w:val'), '3'); pPr.append(pStyle)
    p.append(pPr)
    p.append(make_text_run(text))
    return p

print('=== Current state ===')
for i in range(138, 165):
    if i < len(doc.paragraphs):
        t = doc.paragraphs[i].text.strip()[:100]
        has_img = False
        for child in doc.paragraphs[i]._element:
            if 'drawing' in child.tag: has_img = True; break
            for sub in child:
                if 'drawing' in sub.tag: has_img = True; break
        img_mark = ' [IMG]' if has_img else ''
        print(f'[{i}]{img_mark} {t}')

# ── STEP 1: Identify paragraphs to remove ──
# Remove: empty paras [140-143], old duplicated content [147-156]
# But keep: IMG for 图4.6 at [154], caption 图4.6 and 图4.7 at [155-156]
# After removal, re-insert needed elements

paras_to_remove = []

# Empty paragraphs [140-143]
for i in range(140, 144):
    if i < len(doc.paragraphs):
        p = doc.paragraphs[i]
        t = p.text.strip()
        has_img = False
        for child in p._element:
            if 'drawing' in child.tag: has_img = True; break
            for sub in child:
                if 'drawing' in sub.tag: has_img = True; break
        if t == '' and not has_img:
            paras_to_remove.append((i, p, f'empty para {i}'))

# Old duplicated content [147-156] except IMG and real 图4.6/4.7
# Actually, let's find old content by text matching
for i in range(147, 158):
    if i < len(doc.paragraphs):
        p = doc.paragraphs[i]
        t = p.text.strip()
        # Check if it's old duplicated content
        is_old = False
        if '图4 3' in t:
            is_old = True
        elif t == '4.3 体温信号校准与处理' and i > 148:  # Only the duplicate, not first
            is_old = True
        elif t == '4.3.1 数字滤波实现' and i > 148:
            is_old = True
        elif t == '4.3.2 线性校准算法设计与优化' and i > 148:
            is_old = True
        elif '本研究采用了FIR低通滤波器对原始体温信号进行平滑处理' in t and i > 148:
            is_old = True
        elif 'NTC热敏电阻存在固有的非线性和参数分散性' in t and i > 148:
            is_old = True
        elif t == '' and i >= 147:
            is_old = True

        if is_old:
            paras_to_remove.append((i, p, t[:60]))
        else:
            # Check if this is 图4.6 or 图4.7 — keep these
            has_img = False
            for child in p._element:
                if 'drawing' in child.tag: has_img = True; break
                for sub in child:
                    if 'drawing' in sub.tag: has_img = True; break
            if has_img or '图4.6' in t or '图4.7' in t:
                print(f'  KEEPING [{i}]: {t[:60]}')

print(f'\nParas to remove: {len(paras_to_remove)}')
for idx, p, reason in paras_to_remove:
    print(f'  [{idx}]: {reason}')

# Remove from bottom to top
removed_indices = []
for idx, p, reason in sorted(paras_to_remove, key=lambda x: -x[0]):
    try:
        body.remove(p._element)
        removed_indices.append(idx)
    except Exception as e:
        print(f'  Error removing [{idx}]: {e}')

print(f'Removed {len(removed_indices)} paragraphs')

# ── STEP 2: Find the current position of revised 4.3.2 text ──
# After removal, find by content
revised_432_idx = None
revised_431_idx = None
for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    if 'NTC热敏电阻存在固有的非线性和参数分散性' in t:
        revised_432_idx = i
    if '本研究采用FIR低通滤波器对体温传感器输出的原始信号进行平滑处理' in t:
        revised_431_idx = i

print(f'\nRevised 4.3.1 at para {revised_431_idx}')
print(f'Revised 4.3.2 at para {revised_432_idx}')

# ── STEP 3: Add missing headers ──
# We need: 4.3 header -> 4.3.1 header -> [431 body] -> 4.3.2 header -> [432 body] -> figures

# Check what headers exist before 4.3.1 body
headers_found = {'4.3': False, '4.3.1': False, '4.3.2': False}
for i in range(revised_431_idx - 5, revised_431_idx):
    if i >= 0:
        t = doc.paragraphs[i].text.strip()
        if t == '4.3 体温信号校准与处理': headers_found['4.3'] = True
        if t == '4.3.1 数字滤波实现': headers_found['4.3.1'] = True
        if t == '4.3.2 线性校准算法设计与优化': headers_found['4.3.2'] = True

print(f'Headers found before 4.3.1: {headers_found}')

# Insert missing headers
current_ref = doc.paragraphs[revised_431_idx - 1] if revised_431_idx > 0 else None

if not headers_found['4.3']:
    # Find 4.2.3 body end to insert 4.3 header
    # Find last paragraph of 4.2.3 section
    for i in range(revised_431_idx - 5, revised_431_idx):
        if i >= 0:
            t = doc.paragraphs[i].text.strip()
            if '4.2.3' in t:
                # Insert 4.3 header after this
                hdr = make_header_para('4.3 体温信号校准与处理', 2)
                doc.paragraphs[i]._element.addnext(hdr)
                print('Inserted 4.3 header')
                break

if not headers_found['4.3.1']:
    # Insert 4.3.1 header before revised 4.3.1 body
    hdr = make_header_para('4.3.1 数字滤波实现', 3)
    doc.paragraphs[revised_431_idx]._element.addprevious(hdr)
    print('Inserted 4.3.1 header')

if not headers_found['4.3.2']:
    # Insert 4.3.2 header before revised 4.3.2 body
    hdr = make_header_para('4.3.2 线性校准算法设计与优化', 3)
    doc.paragraphs[revised_432_idx]._element.addprevious(hdr)
    print('Inserted 4.3.2 header')

# ── STEP 4: Re-insert Figure 4.5 ──
# After 4.2.3 body, before 4.3
# Find 4.2.3 body end or 4.3 header
insert_before_idx = None
for i, p in enumerate(doc.paragraphs):
    if '4.3 体温信号校准与处理' in p.text.strip():
        insert_before_idx = i
        break

if insert_before_idx is not None:
    # Add image
    pic_para = doc.add_paragraph()
    pic_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic_run = pic_para.add_run()
    pic_run.add_picture('d:/bishe/fig_respiration_comparison.png', width=Cm(14))

    # Move before 4.3 header
    all_paras = list(body.iterchildren(qn('w:p')))
    new_pic_elem = all_paras[-1]
    doc.paragraphs[insert_before_idx]._element.addprevious(new_pic_elem)

    # Add caption
    cap_p = OxmlElement('w:p')
    cap_p.append(make_text_run('图4.5 自适应滤波前后的呼吸信号波形对比'))
    # Center the caption
    cap_pPr = OxmlElement('w:pPr')
    cap_jc = OxmlElement('w:jc'); cap_jc.set(qn('w:val'), 'center'); cap_pPr.append(cap_jc)
    cap_p.insert(0, cap_pPr)
    new_pic_elem.addnext(cap_p)

    print(f'Inserted Figure 4.5 image + caption before para {insert_before_idx}')

# ── STEP 5: Move 图4.6 and 图4.7 to after 4.3.2 ──
# Find 图4.6 image and captions
fig46_img = None
fig46_cap = None
fig47_cap = None

for i, p in enumerate(doc.paragraphs):
    t = p.text.strip()
    has_img = False
    for child in p._element:
        if 'drawing' in child.tag: has_img = True; break
        for sub in child:
            if 'drawing' in sub.tag: has_img = True; break

    if has_img and i > 145:
        fig46_img = (i, p)
    if '图4.6' in t:
        fig46_cap = (i, p)
    if '图4.7' in t:
        fig47_cap = (i, p)

print(f'\n图4.6 image: para {fig46_img[0] if fig46_img else "not found"}')
print(f'图4.6 caption: para {fig46_cap[0] if fig46_cap else "not found"}')
print(f'图4.7 caption: para {fig47_cap[0] if fig47_cap else "not found"}')

# ── Final verification ──
print('\n=== Final structure ===')
for i in range(135, 170):
    if i < len(doc.paragraphs):
        p = doc.paragraphs[i]
        t = p.text.strip()[:100]
        has_img = False
        for child in p._element:
            if 'drawing' in child.tag: has_img = True; break
            for sub in child:
                if 'drawing' in sub.tag: has_img = True; break
        img_mark = ' [IMG]' if has_img else ''
        oms = len(p._element.findall(f'{{{MATH_NS}}}oMath'))
        if t or has_img:
            print(f'[{i}]{img_mark} OMML={oms} {t}')

doc.save('d:/bishe/我的论文.docx')
print('\nSaved')
