"""Insert three OMML math formulas into the thesis after para 114."""
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from copy import deepcopy

doc = Document('d:/bishe/我的论文_v6.docx')

def make_math_para():
    return OxmlElement('m:oMathPara')

def make_math():
    return OxmlElement('m:oMath')

def make_run(text):
    r = OxmlElement('m:r')
    t = OxmlElement('m:t')
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    r.append(t)
    return r

def make_subscript(base, sub):
    ssub = OxmlElement('m:sSub')
    e = OxmlElement('m:e')
    e.append(make_run(base))
    ssub.append(e)
    sub_e = OxmlElement('m:sub')
    sub_e.append(make_run(sub))
    ssub.append(sub_e)
    return ssub

def add_eq_paragraph(doc, elements, insert_after_element):
    """Add OMML equation paragraph after the given element (CT_P)."""
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')
    pPr.append(jc)
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), '60')
    spacing.set(qn('w:after'), '60')
    pPr.append(spacing)
    p.append(pPr)

    oMathPara = make_math_para()
    oMath = make_math()
    for elem in elements:
        oMath.append(elem)
    oMathPara.append(oMath)
    p.append(oMathPara)
    insert_after_element.addnext(p)
    return p

# Update para 114 text
p114 = doc.paragraphs[114]
# Remove all existing runs except first
first_run = p114.runs[0]
for run in p114.runs[1:]:
    run.text = ''
first_run.text = (
    '本研究在传统的差分阈值算法基础上进行了改进，'
    '主要步骤包括差分运算、自适应阈值设定和候选峰筛选。'
    '首先计算一阶差分来增强R波的斜率特征，再对差分信号取绝对值并进行移动平均平滑，得到差分包络信号。'
    '自适应阈值采用基于滑动窗口的动态阈值策略，如下列公式所示：'
)

# Insert formulas after para 114
current_element = p114._element

# Formula 1: trend(n) = movmean(envelope(n), 1.50 × f_s)
p1 = add_eq_paragraph(doc, [
    make_run('trend'),
    make_run('('), make_run('n'), make_run(')'),
    make_run('='),
    make_run('movmean'),
    make_run('('),
    make_run('envelope'), make_run('('), make_run('n'), make_run(')'),
    make_run(','),
    make_run('1.50'), make_run('×'), make_subscript('f', 's'),
    make_run(')'),
], current_element)
current_element = p1

# Formula 2: spread(n) = movmean(|envelope(n) - trend(n)|, 1.50 × f_s)
p2 = add_eq_paragraph(doc, [
    make_run('spread'),
    make_run('('), make_run('n'), make_run(')'),
    make_run('='),
    make_run('movmean'),
    make_run('('),
    make_run('|'), make_run('envelope'), make_run('('), make_run('n'), make_run(')'),
    make_run('-'),
    make_run('trend'), make_run('('), make_run('n'), make_run(')'),
    make_run('|'),
    make_run(','),
    make_run('1.50'), make_run('×'), make_subscript('f', 's'),
    make_run(')'),
], current_element)
current_element = p2

# Formula 3: threshold(n) = trend(n) + 1.40 × spread(n)
p3 = add_eq_paragraph(doc, [
    make_run('threshold'),
    make_run('('), make_run('n'), make_run(')'),
    make_run('='),
    make_run('trend'), make_run('('), make_run('n'), make_run(')'),
    make_run('+'),
    make_run('1.40'), make_run('×'),
    make_run('spread'), make_run('('), make_run('n'), make_run(')'),
], current_element)

doc.save('d:/bishe/我的论文_v6.docx')
print('Done — 3 formulas inserted after para 114')
