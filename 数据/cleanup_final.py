"""Final cleanup: fix para 136 text/duplicate RR, remove empty paras, keep (4-7) formula."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = Document('d:/bishe/我的论文.docx')
body = doc.element.body
MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

print('=== Before ===')
for i in range(135, 145):
    if i < len(doc.paragraphs):
        t = doc.paragraphs[i].text.strip()[:90]
        has_img = False
        for child in doc.paragraphs[i]._element:
            if 'drawing' in child.tag: has_img = True; break
            for sub in child:
                if 'drawing' in sub.tag: has_img = True; break
        print(f'[{i}] img={has_img} \"{t}\"')

# ── Fix 1: Para 136 - remove duplicate "RR" OMML at end, fix text to reference (4-7) ──
p136 = doc.paragraphs[136]

# Find all OMML elements
omaths = p136._element.findall(f'{{{MATH_NS}}}oMath')
print(f'\nPara 136 has {len(omaths)} OMML elements')

# Check last OMML
last_om = omaths[-1]
last_texts = []
for t_el in last_om.iter(f'{{{MATH_NS}}}t'):
    if t_el.text:
        last_texts.append(t_el.text)
print(f'Last OMML: \"{"".join(last_texts)}\"')

# If last OMML is just "RR" (variable only, not formula), remove it
# and update the ending text to reference (4-7)
if ''.join(last_texts).strip() == 'RR':
    last_om.getparent().remove(last_om)
    print('Removed duplicate "RR" OMML from para 136')

    # Fix the ending text run that says "单位为次/分钟。"
    # Find the last text run and modify it to reference (4-7)
    text_runs = []
    for child in p136._element:
        if child.tag == qn('w:r'):
            t_el = child.find(qn('w:t'))
            if t_el is not None and t_el.text:
                text_runs.append((child, t_el))

    if text_runs:
        last_run, last_t = text_runs[-1]
        old_text = last_t.text
        if '单位为次/分钟' in old_text:
            new_text = old_text.replace('按以下公式计算，单位为次/分钟', '按公式(4-7)计算，单位为次/分钟')
            if new_text == old_text:
                new_text = old_text.replace('单位为次/分钟', '。单位为次/分钟')
            last_t.text = new_text
            print(f'Updated ending text: \"{new_text}\"')
elif 'RR=' in ''.join(last_texts):
    print('Last OMML is already the full RR formula - OK')
else:
    print(f'Unexpected last OMML: \"{"".join(last_texts)}\"')

# ── Fix 2: Remove empty paragraphs ──
# Find and remove para 138 (empty) and para 139 (empty image)
paras_to_remove = []
for i in range(137, 145):
    if i < len(doc.paragraphs):
        p = doc.paragraphs[i]
        t = p.text.strip()
        has_img = False
        for child in p._element:
            if 'drawing' in child.tag:
                has_img = True
                break
            for sub in child:
                if 'drawing' in sub.tag:
                    has_img = True
                    break

        # Remove if empty OR empty with image (leftover from failed insert)
        if (t == '' and not has_img) or (t == '' and has_img and i > 137):
            paras_to_remove.append((i, p))
            print(f'Will remove para [{i}] (empty, img={has_img})')

# Remove from bottom to top to preserve indices
for idx, p in reversed(paras_to_remove):
    body.remove(p._element)
    print(f'Removed para [{idx}]')

# ── Verify after ──
print('\n=== After ===')
for i in range(135, 150):
    if i < len(doc.paragraphs):
        t = doc.paragraphs[i].text.strip()[:90]
        has_img = False
        for child in doc.paragraphs[i]._element:
            if 'drawing' in child.tag: has_img = True; break
            for sub in child:
                if 'drawing' in sub.tag: has_img = True; break
        print(f'[{i}] img={has_img} \"{t}\"')

doc.save('d:/bishe/我的论文.docx')
print('\nDone')
