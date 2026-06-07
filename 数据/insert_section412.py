"""Insert revised Section 4.1.2 text + three OMML display formulas into 我的论文_v6.docx."""
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from copy import deepcopy
import re

doc = Document('d:/bishe/我的论文.docx')

# ── helpers ──────────────────────────────────────────────
def make_mr(text):
    r = OxmlElement('m:r')
    t = OxmlElement('m:t'); t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r

def make_math():
    return OxmlElement('m:oMath')

def make_math_para(math_elem):
    """Wrap an m:oMath in m:oMathPara, then in w:p."""
    omp = OxmlElement('m:oMathPara')
    omp.append(math_elem)
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    jc = OxmlElement('w:jc'); jc.set(qn('w:val'), 'center'); pPr.append(jc)
    sp = OxmlElement('w:spacing'); sp.set(qn('w:before'), '60'); sp.set(qn('w:after'), '60'); pPr.append(sp)
    p.append(pPr)
    p.append(omp)
    return p

def add_para_after(para_element):
    """Create empty w:p and insert after given element, return new element."""
    p = OxmlElement('w:p')
    para_element.addnext(p)
    return p

def insert_element_after(el, after_el):
    """Insert el sibling after after_el."""
    after_el.addnext(el)
    return el

# ── Build Formula 1:  T(n) = (1/L) · Σ_{i=n-L+1}^{n} E(i)  ──
m1 = make_math()
m1.extend([  # T(n) =
    make_mr('T'), make_mr('('), make_mr('n'), make_mr(')'), make_mr('='),
])

# Fraction (1/L)
f = OxmlElement('m:f')
num = OxmlElement('m:num'); num.append(make_mr('1')); f.append(num)
den = OxmlElement('m:den'); den.append(make_mr('L')); f.append(den)
m1.append(f)

m1.append(make_mr('·'))

# Summation Σ_{i=n-L+1}^{n} E(i)
nary = OxmlElement('m:nary')
naryPr = OxmlElement('m:naryPr')
chr_el = OxmlElement('m:chr'); chr_el.set(qn('m:val'), '∑'); naryPr.append(chr_el)
lim = OxmlElement('m:limLoc'); lim.set(qn('m:val'), 'subSup'); naryPr.append(lim)
nary.append(naryPr)

sub = OxmlElement('m:sub')
sub_e = OxmlElement('m:e'); sub_e.append(make_mr('i=n-L+1')); sub.append(sub_e)
nary.append(sub)

sup = OxmlElement('m:sup')
sup_e = OxmlElement('m:e'); sup_e.append(make_mr('n')); sup.append(sup_e)
nary.append(sup)

expr = OxmlElement('m:e'); expr.append(make_mr('E')); expr.append(make_mr('(')); expr.append(make_mr('i')); expr.append(make_mr(')'))
nary.append(expr)
m1.append(nary)

formula1_p = make_math_para(m1)

# ── Build Formula 2: S(n) = (1/L) · Σ_{i=n-L+1}^{n} |E(i)-T(i)| ──
m2 = make_math()
m2.extend([make_mr('S'), make_mr('('), make_mr('n'), make_mr(')'), make_mr('=')])

f2 = deepcopy(f)
m2.append(f2)
m2.append(make_mr('·'))

nary2 = deepcopy(nary)
# Replace expr in nary2
# Remove old expr, add new with absolute value
for child in list(nary2):
    if child.tag == qn('m:e'):
        nary2.remove(child)

abs_elem = OxmlElement('m:d')
dPr = OxmlElement('m:dPr')
beg = OxmlElement('m:begChr'); beg.set(qn('m:val'), '|'); dPr.append(beg)
endc = OxmlElement('m:endChr'); endc.set(qn('m:val'), '|'); dPr.append(endc)
abs_elem.append(dPr)
abs_inner = OxmlElement('m:e')
abs_inner.extend([make_mr('E'), make_mr('('), make_mr('i'), make_mr(')'), make_mr('-'), make_mr('T'), make_mr('('), make_mr('i'), make_mr(')')])
abs_elem.append(abs_inner)

new_expr = OxmlElement('m:e'); new_expr.append(abs_elem)
nary2.append(new_expr)
m2.append(nary2)

formula2_p = make_math_para(m2)

# ── Build Formula 3: Th(n) = T(n) + 1.40 × S(n) ──
m3 = make_math()
m3.extend([
    make_mr('Th'), make_mr('('), make_mr('n'), make_mr(')'), make_mr('='),
    make_mr('T'), make_mr('('), make_mr('n'), make_mr(')'), make_mr('+'),
    make_mr('1.40'), make_mr('×'), make_mr('S'), make_mr('('), make_mr('n'), make_mr(')'),
])
formula3_p = make_math_para(m3)

# ── Insert into document ────────────────────────────────

# Find section header "4.1.2"
insertion_point = None
for i, p in enumerate(doc.paragraphs):
    if '4.1.2' in p.text and '差分阈值' in p.text:
        insertion_point = p
        print(f'Found insertion point: para {i}: {p.text[:60]}...')
        break

if insertion_point is None:
    raise RuntimeError('Could not find section 4.1.2')

# Remove all existing paragraphs between this header and the next section header
# First, collect paragraphs to remove
body = doc.element.body
all_p_elems = list(body.iterchildren(qn('w:p')))

# Find the element of the header
header_elem = insertion_point._element
header_idx = None
for idx, pe in enumerate(all_p_elems):
    if pe is header_elem:
        header_idx = idx
        break

if header_idx is None:
    raise RuntimeError('Could not find header element in body')

# Find next section header (next paragraph starting with a number like 4.1.3 or 4.2)
next_header_idx = None
for idx in range(header_idx + 1, len(all_p_elems)):
    pe = all_p_elems[idx]
    # Get text content
    texts = []
    for r in pe.iterchildren(qn('w:r')):
        t = r.find(qn('w:t'))
        if t is not None and t.text:
            texts.append(t.text)
    text = ''.join(texts)
    if re.match(r'^\d+\.\d+', text.strip()):
        next_header_idx = idx
        break

# Remove paragraphs between header (exclusive) and next_header (exclusive)
if next_header_idx is not None:
    to_remove = all_p_elems[header_idx + 1:next_header_idx]
    print(f'Removing {len(to_remove)} existing paragraphs between header and next section')
    for pe in to_remove:
        body.remove(pe)

# Now insert new content after the header
current_el = header_elem

# Paragraph A: method description
paraA_text = (
    '本研究在传统的差分阈值算法基础上进行了改进，'
    '主要步骤包括差分运算、自适应阈值设定和候选峰筛选。'
    '首先计算一阶差分来增强R波的斜率特征，'
    '对差分信号取绝对值并进行移动平均平滑，得到差分包络信号。'
    '自适应阈值采用基于滑动窗口的动态阈值策略：'
)
# Insert description paragraph
pA = OxmlElement('w:p')
pA_pr = OxmlElement('w:pPr')
pA_sp = OxmlElement('w:spacing'); pA_sp.set(qn('w:after'), '120'); pA_pr.append(pA_sp)
pA.append(pA_pr)
rA = OxmlElement('w:r')
tA = OxmlElement('w:t'); tA.text = paraA_text; tA.set(qn('xml:space'), 'preserve')
rA.append(tA); pA.append(rA)
current_el = insert_element_after(pA, current_el)

# Formula 1
current_el = insert_element_after(formula1_p, current_el)

# Formula 2
current_el = insert_element_after(formula2_p, current_el)

# Formula 3
current_el = insert_element_after(formula3_p, current_el)

# Paragraph B: explanation and peak selection
paraB_text = (
    '其中 为差分包络信号， 和 分别为包络的趋势估计和偏差估计，'
    ' 为滑动窗口长度（ 为采样率）， 为自适应检测阈值。'
    '在候选峰筛选中，首先定位信号的局部极大值点，'
    '取差分包络超过自适应阈值的峰值作为候选点。'
    '当候选点不足5个时，降阈值启动备用策略以保证检测的鲁棒性。'
    '随后通过不应期（250 ms）剔除间距过近的候选峰，'
    '并利用幅值下限（中位数减去1.20倍标准差）过滤幅值过低的误检点。'
)
pB = OxmlElement('w:p')
pB_pr = OxmlElement('w:pPr')
pB_sp = OxmlElement('w:spacing'); pB_sp.set(qn('w:before'), '120'); pB_pr.append(pB_sp)
pB.append(pB_pr)

# Para B will have mixed: text + inline math variables
# Split into segments
segments = [
    ('text', '其中 '),
    ('math', 'E(n)'),
    ('text', ' 为差分包络信号，'),
    ('math', 'T(n)'),
    ('text', ' 和 '),
    ('math', 'S(n)'),
    ('text', ' 分别为包络的趋势估计和偏差估计，'),
    ('math', 'L = 1.50 × f_s'),
    ('text', ' 为滑动窗口长度（'),
    ('math', 'f_s'),
    ('text', ' 为采样率），'),
    ('math', 'Th(n)'),
    ('text', ' 为自适应检测阈值。在候选峰筛选中，首先定位信号的局部极大值点，'
             '取差分包络超过自适应阈值的峰值作为候选点。'
             '当候选点不足5个时，降阈值启动备用策略以保证检测的鲁棒性。'
             '随后通过不应期（250 ms）剔除间距过近的候选峰，'
             '并利用幅值下限（中位数减去1.20倍标准差）过滤幅值过低的误检点。'),
]

for seg_type, seg_text in segments:
    if seg_type == 'text':
        r = OxmlElement('w:r')
        t = OxmlElement('w:t'); t.text = seg_text; t.set(qn('xml:space'), 'preserve')
        r.append(t); pB.append(r)
    else:  # inline math
        # Create w:r containing m:oMath
        r = OxmlElement('w:r')
        # Font properties for the math run
        rPr = OxmlElement('w:rPr')
        rFonts = OxmlElement('w:rFonts'); rFonts.set(qn('w:ascii'), 'Cambria Math'); rPr.append(rFonts)
        r.append(rPr)
        om = make_math()
        # Parse the math text
        # Simple tokenizer: split variables, operators, parentheses
        tokens = []
        i = 0
        while i < len(seg_text):
            c = seg_text[i]
            if c.isalpha() or c == '_':
                # Variable name
                j = i
                while j < len(seg_text) and (seg_text[j].isalpha() or seg_text[j] == '_'):
                    j += 1
                tokens.append(('var', seg_text[i:j]))
                i = j
            elif c.isdigit() or c == '.':
                j = i
                while j < len(seg_text) and (seg_text[j].isdigit() or seg_text[j] == '.'):
                    j += 1
                tokens.append(('num', seg_text[i:j]))
                i = j
            elif c in '()[]':
                tokens.append(('paren', c))
                i += 1
            elif c in '=+×·-':
                tokens.append(('op', c))
                i += 1
            else:
                tokens.append(('char', c))
                i += 1

        for ttype, tval in tokens:
            if ttype == 'var':
                om.append(make_mr(tval))
            elif ttype == 'num':
                om.append(make_mr(tval))
            elif ttype == 'paren':
                om.append(make_mr(tval))
            elif ttype == 'op':
                om.append(make_mr(tval))
            else:
                om.append(make_mr(tval))

        r.append(om)
        pB.append(r)

current_el = insert_element_after(pB, current_el)

doc.save('d:/bishe/我的论文.docx')
print('Done — section 4.1.2 updated')
