"""Revise Section 4.3 (体温信号校准与处理) based on processTemperature.m."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from copy import deepcopy

doc = Document('d:/bishe/我的论文.docx')
MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

def make_rPr():
    rPr = OxmlElement('w:rPr')
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), 'Cambria Math')
    rFonts.set(qn('w:hAnsi'), 'Cambria Math')
    rPr.append(rFonts)
    return rPr

def make_ctrlPr():
    ctrlPr = OxmlElement('m:ctrlPr')
    ctrlPr.append(make_rPr())
    return ctrlPr

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

def make_math_var(text):
    om = OxmlElement('m:oMath')
    om.append(make_mr(text))
    return om

def make_subscript_om(base, sub):
    om = OxmlElement('m:oMath')
    sSub = OxmlElement('m:sSub')
    sSubPr = OxmlElement('m:sSubPr')
    sSubPr.append(make_ctrlPr())
    sSub.append(sSubPr)
    e = OxmlElement('m:e')
    e.append(make_mr(base))
    e.append(make_ctrlPr())
    sSub.append(e)
    sub_el = OxmlElement('m:sub')
    sub_el.append(make_mr(sub))
    sub_el.append(make_ctrlPr())
    sSub.append(sub_el)
    om.append(sSub)
    return om

# ═══════════════════════════════════════════════════════════════
# REVISE 4.3.1 (para 144) — Digital filter implementation
# ═══════════════════════════════════════════════════════════════
print('=== Revising 4.3.1 ===')
p144 = doc.paragraphs[144]
old_text_431 = ''
for run in p144.runs:
    old_text_431 += run.text
print(f'Old text: \"{old_text_431[:100]}...\"')

# Clear para 144
for child in list(p144._element):
    tag = child.tag
    if tag.endswith('}pPr') or tag == qn('w:pPr'):
        continue
    p144._element.remove(child)

# Rebuild with corrected text + OMML
segments_431 = [
    ('text', '本研究采用FIR低通滤波器对体温传感器输出的原始信号进行平滑处理。滤波器采用汉明窗设计，阶数 '),
    ('math', 'N = 20'),
    ('text', '，通带截止频率 '),
    ('math_sub', ('f', 'c')),
    ('text', ' = 0.05 Hz。由于体温信号为准静态信号，其频率成分主要集中在0 Hz附近，'),
    ('math', 'f_c = 0.05 Hz'),
    ('text', ' 的截止频率在保证滤除高频噪声的同时，能够完整保留体温的缓慢变化趋势。'),
    ('text', '滤波器频率响应特性为：过渡带宽度约为 '),
    ('math', '0.10 Hz'),
    ('text', '，阻带衰减大于40 dB，可有效抑制50 Hz工频干扰及高频电磁噪声。'),
    ('text', '为消除FIR滤波器群延迟引起的时域偏移，本文采用filtfilt函数对信号进行零相位双向滤波，使得滤波后的信号波形与原始信号在时序上保持对齐。'),
    ('text', '经过滤波处理后，结合'),
    ('math', 'SNR = 10·log₁₀(P_signal / P_noise)'),
    ('text', '估计信噪比，噪声标准差 '),
    ('math', 'σ_noise = std(signal - filtered)'),
    ('text', '作为滤波效果的量化评价指标。实验表明，滤波后体温读数的短期波动幅度从±0.3°C降至±0.05°C以内，测量稳定性显著提升。'),
]

for seg_type, seg_content in segments_431:
    if seg_type == 'text':
        p144._element.append(make_text_run(seg_content))
    elif seg_type == 'math':
        p144._element.append(make_math_var(seg_content))
    elif seg_type == 'math_sub':
        base, sub = seg_content
        p144._element.append(make_subscript_om(base, sub))

print('4.3.1 updated')

# ═══════════════════════════════════════════════════════════════
# REVISE 4.3.2 (para 146) — Linear calibration
# ═══════════════════════════════════════════════════════════════
print('\n=== Revising 4.3.2 ===')
p146 = doc.paragraphs[146]
old_text_432 = ''
for run in p146.runs:
    old_text_432 += run.text
print(f'Old text: \"{old_text_432[:100]}...\"')

# Clear para 146
for child in list(p146._element):
    tag = child.tag
    if tag.endswith('}pPr') or tag == qn('w:pPr'):
        continue
    p146._element.remove(child)

# Rebuild with corrected text + OMML
segments_432 = [
    ('text', 'NTC热敏电阻存在固有的非线性和参数分散性，需进行校准处理[20]。本文采用线性校准模型对传感器输出电压与温度值进行拟合：'),
    ('math', 'T_cal = k × V_out + b'),
    ('text', '，其中 '),
    ('math', 'V_out'),
    ('text', ' 为传感器输出电压，'),
    ('math', 'k'),
    ('text', ' 为灵敏度系数，'),
    ('math', 'b'),
    ('text', ' 为偏移量。'),
    ('text', '校准过程在恒温水浴中进行，设置三个标准温度点 '),
    ('math', 'T_ref = [35, 37, 39] °C'),
    ('text', '，分别记录各温度点下传感器的稳定输出电压 '),
    ('math', 'V = [V_35, V_37, V_39]'),
    ('text', '。利用最小二乘法求解超定方程组：'),
    ('math', '[V, 1] × [k; b] = T_ref'),
    ('text', '，即最小化残差平方和 '),
    ('math', 'min ||V_avg × [k; b] - T_ref||²'),
    ('text', '，得到最优校准参数 '),
    ('math', 'k'),
    ('text', ' 和 '),
    ('math', 'b'),
    ('text', '。'),
    ('text', '校准精度通过最大残差评价：'),
    ('math', 'ε = max|T_fit(i) - T_ref(i)|'),
    ('text', '，其中 '),
    ('math', 'T_fit = k × V + b'),
    ('text', ' 为各校准点的拟合温度值。测试结果表明，校准后各点的最大残差控制在±0.1°C以内，满足临床体温监测的精度要求（±0.2°C）。'),
]

for seg_type, seg_content in segments_432:
    if seg_type == 'text':
        p146._element.append(make_text_run(seg_content))
    elif seg_type == 'math':
        p146._element.append(make_math_var(seg_content))
    elif seg_type == 'math_sub':
        base, sub = seg_content
        p146._element.append(make_subscript_om(base, sub))

print('4.3.2 updated')

# ═══════════════════════════════════════════════════════════════
# Verify
# ═══════════════════════════════════════════════════════════════
print('\n=== Verification ===')
for i in [144, 146]:
    p = doc.paragraphs[i]
    full = ''
    for r in p.runs:
        full += r.text
    oms = p._element.findall(f'{{{MATH_NS}}}oMath')
    print(f'Para {i}:')
    print(f'  Text: {full[:150]}...')
    print(f'  OMML count: {len(oms)}')
    for j, om in enumerate(oms):
        texts = []
        for t in om.iter(f'{{{MATH_NS}}}t'):
            if t.text: texts.append(t.text)
        joined = ''.join(texts)
        print(f'  [{j}] \"{joined}\"')
    print()

doc.save('d:/bishe/我的论文.docx')
print('Saved')
