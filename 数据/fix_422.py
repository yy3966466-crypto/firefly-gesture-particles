"""Fix Section 4.2.2: correct inaccuracies vs processRespiration.m, add OMML formulas."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

doc = Document('d:/bishe/我的论文.docx')
MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

def make_mr(text):
    r = OxmlElement('m:r')
    t = OxmlElement('m:t'); t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r

def make_rPr():
    rPr = OxmlElement('w:rPr')
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), 'Cambria Math')
    rFonts.set(qn('w:hAnsi'), 'Cambria Math')
    rPr.append(rFonts)
    return rPr

def make_text_run(text):
    r = OxmlElement('w:r')
    t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r

def make_math_variable(name):
    """Simple variable like f_s, T_resp"""
    om = OxmlElement('m:oMath')
    rPr = make_rPr()
    om.append(rPr)
    om.append(make_mr(name))
    return om

def make_subscript(base, sub):
    """m:sSub for subscript like f_s"""
    om = OxmlElement('m:oMath')
    sSub = OxmlElement('m:sSub')
    sSubPr = OxmlElement('m:sSubPr')
    ctrlPr = OxmlElement('m:ctrlPr')
    ctrlPr.append(make_rPr())
    sSubPr.append(ctrlPr)
    sSub.append(sSubPr)
    e = OxmlElement('m:e')
    mr = make_mr(base)
    e.append(mr)
    e.append(deepcopy(ctrlPr) if hasattr(ctrlPr, 'append') else OxmlElement('m:ctrlPr'))
    sSub.append(e)
    sub_el = OxmlElement('m:sub')
    sub_mr = make_mr(sub)
    sub_el.append(sub_mr)
    sub_el.append(deepcopy(ctrlPr) if hasattr(ctrlPr, 'append') else OxmlElement('m:ctrlPr'))
    sSub.append(sub_el)
    om.append(sSub)
    return om

# Need deepcopy
from copy import deepcopy

def make_inline_math():
    """Create an empty inline math element with proper properties"""
    om = OxmlElement('m:oMath')
    return om

def add_text_to_om(om, text):
    om.append(make_mr(text))

def add_math_variable(om, name):
    om.append(make_mr(name))

# ── Find para 138 ──
p = doc.paragraphs[138]
print(f'Para 138 text: "{p.text.strip()[:80]}..."')

# ── Build new paragraph content ──
# We'll clear the paragraph and rebuild with new content

# First, remove all children
for child in list(p._element):
    tag = child.tag
    # Keep w:pPr
    if tag.endswith('}pPr') or tag == qn('w:pPr'):
        continue
    p._element.remove(child)

# Build the paragraph structure
# The paragraph already has w:pPr from the original

# Segment 1: text before first variable
segments = [
    ('text', '经过LMS自适应线增强器（ALE）对呼吸信号进行增强和移动平均平滑（窗口约0.95 × '),
    ('math_sub', ('f', 's')),  # f_s
    ('text', '）后，信号的波形质量得到显著提升。对增强后的信号采用基于移动平均趋势的自适应阈值法检测呼吸波峰，而非心电信号中的差分阈值法。具体步骤为：首先计算增强信号的移动平均趋势 '),
    ('math', 'trend'),
    ('text', ' 和平均偏差 '),
    ('math', 'spread'),
    ('text', '：'),
]

# Sub-segments with formulas
segments2 = [
    ('text', '趋势 '),
    ('math', 'trend'),
    ('text', ' 采用窗口 '),
    ('math_sub', ('f', 's')),
    ('text', ' 的4.00倍进行移动平均计算，平均偏差 '),
    ('math', 'spread'),
    ('text', ' 为信号与趋势之差的绝对值在同一窗口上的移动平均。在此基础上构造自适应检测阈值：'),
    ('math', 'threshold = trend + 0.20 × spread'),
    ('text', '。'),
]

segments3 = [
    ('text', '定位信号的局部极大值点，取增强信号超过自适应阈值的点作为候选呼吸波峰。为了提高检测的鲁棒性，当候选波峰少于3个时，自动启用备用阈值策略（信号均值 + 0.10 × 标准差），确保低信噪比条件下仍能检出有效波峰。最后通过不应期（'),
    ('math_sub', ('f', 's')),
    ('text', ' 的1.40倍，约1.4秒）筛选最终波峰位置，剔除间距过近的伪峰。'),
]

segments4 = [
    ('text', '相邻波峰的时间间隔即为呼吸周期 '),
    ('math', 'T_resp'),
    ('text', '（单位为秒），呼吸率 '),
    ('math', 'RR'),
    ('text', ' 按以下公式计算，单位为次/分钟。'),
    ('math_display', 'RR = 60 / T_resp'),  # Special: the fraction formula
]

all_segments = segments + segments2 + segments3 + segments4

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
    e.append(deepcopy(ctrlPr))
    sSub.append(e)

    sub_el = OxmlElement('m:sub')
    mr_sub = make_mr(sub_text)
    sub_el.append(mr_sub)
    sub_el.append(deepcopy(ctrlPr))
    sSub.append(sub_el)

    om.append(sSub)
    return om

def make_math_variable_simple(name):
    om = OxmlElement('m:oMath')
    om.append(make_rPr())
    om.append(make_mr(name))
    return om

def make_rr_formula():
    """Build RR = 60 / T_resp as OMML fraction with subscript"""
    om = OxmlElement('m:oMath')

    # RR=
    om.append(make_mr('RR='))

    # Fraction: 60 / T_resp
    f = OxmlElement('m:f')
    fPr = OxmlElement('m:fPr')
    ctrlPr = OxmlElement('m:ctrlPr')
    ctrlPr.append(make_rPr())
    fPr.append(ctrlPr)
    f.append(fPr)

    # Numerator: 60
    num = OxmlElement('m:num')
    num.append(make_mr('60'))
    num.append(deepcopy(ctrlPr))
    f.append(num)

    # Denominator: T_resp (with subscript)
    den = OxmlElement('m:den')
    sSub = OxmlElement('m:sSub')
    sSubPr = OxmlElement('m:sSubPr')
    sSubPr.append(deepcopy(ctrlPr))
    sSub.append(sSubPr)

    den_e = OxmlElement('m:e')
    den_e.append(make_mr('T'))
    den_e.append(deepcopy(ctrlPr))
    sSub.append(den_e)

    den_sub = OxmlElement('m:sub')
    den_sub.append(make_mr('respiratory'))
    den_sub.append(deepcopy(ctrlPr))
    sSub.append(den_sub)

    den.append(sSub)
    den.append(deepcopy(ctrlPr))
    f.append(den)

    om.append(f)
    return om

# Now build the paragraph
current_el = None
# pPr already exists

for seg_type, seg_content in all_segments:
    if seg_type == 'text':
        el = make_text_run(seg_content)
        p._element.append(el)
    elif seg_type == 'math':
        el = make_math_variable_simple(seg_content)
        p._element.append(el)
    elif seg_type == 'math_sub':
        base, sub = seg_content
        el = make_math_subscript(base, sub)
        p._element.append(el)
    elif seg_type == 'math_display':
        # Build RR formula
        el = make_rr_formula()
        p._element.append(el)

print('Para 138 updated successfully')

# Verify
verify_text = ''
for child in p._element:
    tag = child.tag
    if tag == qn('w:r') or tag.endswith('}r'):
        t_el = child.find(qn('w:t'))
        if t_el is not None and t_el.text:
            verify_text += t_el.text
    elif MATH_NS in tag:
        # OMML element, just mark it
        pass

print(f'New text length: {len(verify_text)}')
print(f'New text starts: "{verify_text[:80]}..."')
print(f'New text ends: "...{verify_text[-80:]}"')

# Check for OMML count
omml_count = len(p._element.findall(f'{{{MATH_NS}}}oMath'))
print(f'OMML elements: {omml_count}')

doc.save('d:/bishe/我的论文.docx')
print('Saved')
