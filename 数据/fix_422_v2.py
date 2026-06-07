"""Fix 4.2.2: apply corrected text to correct paragraph, remove duplicate."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from copy import deepcopy

doc = Document('d:/bishe/我的论文.docx')
MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

# ── Helper functions ──
def make_rPr():
    rPr = OxmlElement('w:rPr')
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), 'Cambria Math')
    rFonts.set(qn('w:hAnsi'), 'Cambria Math')
    rPr.append(rFonts)
    return rPr

def make_mr(text):
    r = OxmlElement('m:r')
    t = OxmlElement('m:t'); t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r

def make_text_run(text):
    r = OxmlElement('w:r')
    t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r

def make_math_subscript(base, sub_text):
    """Build m:oMath with m:sSub for f_s etc"""
    om = OxmlElement('m:oMath')
    sSub = OxmlElement('m:sSub')
    sSubPr = OxmlElement('m:sSubPr')
    ctrlPr = OxmlElement('m:ctrlPr')
    ctrlPr.append(make_rPr())
    sSubPr.append(ctrlPr)
    sSub.append(sSubPr)

    e = OxmlElement('m:e')
    mr_e = make_mr(base)
    e.append(mr_e)
    ctrlPr_copy = OxmlElement('m:ctrlPr')
    ctrlPr_copy.append(make_rPr())
    e.append(ctrlPr_copy)
    sSub.append(e)

    sub_el = OxmlElement('m:sub')
    mr_sub = make_mr(sub_text)
    sub_el.append(mr_sub)
    ctrlPr_copy2 = OxmlElement('m:ctrlPr')
    ctrlPr_copy2.append(make_rPr())
    sub_el.append(ctrlPr_copy2)
    sSub.append(sub_el)

    om.append(sSub)
    return om

def make_math_var(name):
    """Simple variable like trend, spread"""
    om = OxmlElement('m:oMath')
    om.append(make_rPr())
    om.append(make_mr(name))
    return om

def make_rr_formula():
    """Build RR = 60 / T_resp as OMML fraction"""
    om = OxmlElement('m:oMath')
    om.append(make_mr('RR='))

    f = OxmlElement('m:f')
    fPr = OxmlElement('m:fPr')
    ctrlPr = OxmlElement('m:ctrlPr')
    ctrlPr.append(make_rPr())
    fPr.append(ctrlPr)
    f.append(fPr)

    num = OxmlElement('m:num')
    num.append(make_mr('60'))
    sSub = OxmlElement('m:sSub')
    sSubPr = OxmlElement('m:sSubPr')
    ctrlPr2 = OxmlElement('m:ctrlPr')
    ctrlPr2.append(make_rPr())
    sSubPr.append(ctrlPr2)
    sSub.append(sSubPr)

    den_e = OxmlElement('m:e')
    den_e.append(make_mr('T'))
    ctrlPr3 = OxmlElement('m:ctrlPr')
    ctrlPr3.append(make_rPr())
    den_e.append(ctrlPr3)
    sSub.append(den_e)

    den_sub = OxmlElement('m:sub')
    den_sub.append(make_mr('respiratory'))
    ctrlPr4 = OxmlElement('m:ctrlPr')
    ctrlPr4.append(make_rPr())
    den_sub.append(ctrlPr4)
    sSub.append(den_sub)

    f.append(sSub)
    om.append(f)
    return om

# ── Current state ──
# [135]: 4.2.2 header ✓
# [136]: 4.2.2 body (OLD text, needs replacement)
# [137]: 4.2.3 header
# [138]: NEW corrected text (WRONG POSITION, needs removal)

print('Current state:')
for i in range(134, 140):
    t = doc.paragraphs[i].text.strip()[:100]
    print(f'  [{i}] {t}')

# ── STEP 1: Replace para 136 with corrected content ──
p136 = doc.paragraphs[136]

# Remove all children except w:pPr
for child in list(p136._element):
    tag = child.tag
    if tag.endswith('}pPr') or tag == qn('w:pPr'):
        continue
    p136._element.remove(child)

# Define segments
segments = [
    ('text', '经过LMS自适应线增强器（ALE）对呼吸信号进行增强和移动平均平滑（窗口约0.95 × '),
    ('math_sub', ('f', 's')),
    ('text', '）后，信号的波形质量得到显著提升。对增强后的信号采用基于移动平均趋势的自适应阈值法检测呼吸波峰，而非心电信号中的差分阈值法。具体步骤为：首先计算增强信号的移动平均趋势 '),
    ('math', 'trend'),
    ('text', ' 和平均偏差 '),
    ('math', 'spread'),
    ('text', '：趋势 '),
    ('math', 'trend'),
    ('text', ' 采用窗口为采样率 '),
    ('math_sub', ('f', 's')),
    ('text', ' 的4.00倍进行移动平均计算，平均偏差 '),
    ('math', 'spread'),
    ('text', ' 为信号与趋势之差的绝对值在同一窗口上的移动平均。在此基础上构造自适应检测阈值：'),
    ('math', 'threshold = trend + 0.20 × spread'),
    ('text', '。'),
    ('text', '定位信号的局部极大值点，取增强信号超过自适应阈值的点作为候选呼吸波峰。为提高检测鲁棒性，当候选波峰少于3个时，自动启用备用阈值策略（信号均值 + 0.10 × 标准差），确保低信噪比条件下仍能检出有效波峰。最后通过不应期（'),
    ('math_sub', ('f', 's')),
    ('text', ' 的1.40倍，约1.4秒）筛选最终波峰位置，剔除间距过近的伪峰。'),
    ('text', '相邻波峰的时间间隔即为呼吸周期 '),
    ('math', 'T_resp'),
    ('text', '（单位为秒），呼吸率 '),
    ('math', 'RR'),
    ('text', ' 按以下公式计算，单位为次/分钟。'),
]

for seg_type, seg_content in segments:
    if seg_type == 'text':
        p136._element.append(make_text_run(seg_content))
    elif seg_type == 'math':
        p136._element.append(make_math_var(seg_content))
    elif seg_type == 'math_sub':
        base, sub = seg_content
        p136._element.append(make_math_subscript(base, sub))

# Append RR formula at the end
p136._element.append(make_rr_formula())

print('\nPara 136 updated with corrected content')

# ── STEP 2: Remove para 138 (duplicate corrected text in wrong position) ──
p138 = doc.paragraphs[138]
p138_text = p138.text.strip()
print(f'\nPara 138 to remove: "{p138_text[:80]}..."')

body = doc.element.body
body.remove(p138._element)
print('Para 138 removed')

# ── Verify ──
print('\nAfter fix:')
for i in range(134, 140):
    if i < len(doc.paragraphs):
        t = doc.paragraphs[i].text.strip()[:100]
        print(f'  [{i}] {t}')
    else:
        print(f'  [{i}] <end of paragraphs>')

# Check OMML in para 136
omml_count = len(doc.paragraphs[135]._element.findall(f'{{{MATH_NS}}}oMath'))
print(f'\nOMML in para 136: {omml_count}')

doc.save('d:/bishe/我的论文.docx')
print('\nSaved successfully')
