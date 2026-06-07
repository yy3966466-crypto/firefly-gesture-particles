#!/usr/bin/env python3
"""Generate defense PPT — 多生理参数监护系统及关键信号处理算法.
   Style: Blue-white light theme, 16:9 widescreen, carefully calculated layout."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ══════════════════════════════════════════════════════════════
# Color scheme — blue-white light theme
# ══════════════════════════════════════════════════════════════
BLUE_PRIMARY   = RGBColor(0x15, 0x5B, 0xC3)
BLUE_ACCENT    = RGBColor(0x34, 0x85, 0xF5)
BLUE_LIGHT     = RGBColor(0xE8, 0xF0, 0xFE)
BLUE_PALE      = RGBColor(0xF4, 0xF7, 0xFC)
WHITE          = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK      = RGBColor(0x1A, 0x1A, 0x2E)
TEXT_MEDIUM    = RGBColor(0x5A, 0x5F, 0x72)
TEXT_SUBTLE    = RGBColor(0xA0, 0xA5, 0xB5)
BORDER_LIGHT   = RGBColor(0xDE, 0xE2, 0xEC)
COVER_BG       = RGBColor(0xEA, 0xF2, 0xFB)
TABLE_HEADER   = RGBColor(0x1A, 0x56, 0xB8)
TABLE_STRIPE   = RGBColor(0xF0, 0xF4, 0xFB)

SLIDE_W = 13.333
SLIDE_H = 7.5
MARGIN  = 0.65          # left/right margin
CONTENT_W = SLIDE_W - 2 * MARGIN  # 12.033 inches usable width

prs = Presentation()
prs.slide_width  = Inches(SLIDE_W)
prs.slide_height = Inches(SLIDE_H)

# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════

def add_blank_slide():
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = WHITE
    return slide

def add_textbox(slide, left, top, width, height,
                text="", font_size=14, color=TEXT_DARK, bold=False,
                alignment=PP_ALIGN.LEFT, font_name='Microsoft YaHei',
                anchor=MSO_ANCHOR.TOP, line_spacing=1.15):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                     Inches(width), Inches(height))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.line_spacing = Pt(int(font_size * line_spacing))
    p.alignment = alignment
    return tf

def add_rich_textbox(slide, left, top, width, height):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                     Inches(width), Inches(height))
    txBox.word_wrap = True
    tf = txBox.text_frame
    tf.word_wrap = True
    return tf

def add_para(tf, text, font_size=14, color=TEXT_DARK, bold=False,
             alignment=PP_ALIGN.LEFT, font_name='Microsoft YaHei',
             first=False, space_after=4, space_before=0):
    if first:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    return p

def add_title_bar(slide, title_text, subtitle=""):
    """Top accent bar + title + bottom separator."""
    # Top thin accent line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        Inches(SLIDE_W), Inches(0.028)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = BLUE_ACCENT
    line.line.fill.background()

    # Title
    add_textbox(slide, MARGIN, 0.18, CONTENT_W, 0.48,
                text=title_text, font_size=24, color=BLUE_PRIMARY, bold=True)

    if subtitle:
        add_textbox(slide, MARGIN, 0.58, CONTENT_W, 0.26,
                    text=subtitle, font_size=11.5, color=TEXT_MEDIUM)
        sep_y = 0.92
    else:
        sep_y = 0.76

    # Separator
    sep = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(MARGIN), Inches(sep_y),
        Inches(CONTENT_W), Inches(0.006)
    )
    sep.fill.solid()
    sep.fill.fore_color.rgb = BORDER_LIGHT
    sep.line.fill.background()

def add_page_number(slide, num):
    add_textbox(slide, SLIDE_W - 1.1, SLIDE_H - 0.32, 0.8, 0.22,
                text=str(num), font_size=8.5, color=TEXT_SUBTLE,
                alignment=PP_ALIGN.RIGHT)

def add_card(slide, left, top, width, height, fill_color=BLUE_PALE):
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top),
        Inches(width), Inches(height)
    )
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.fill.background()
    return card

def add_bullet_block(slide, left, top, width, height, items,
                     font_size=13, color=TEXT_DARK, bullet='●', spacing=6):
    tf = add_rich_textbox(slide, left, top, width, height)
    for i, item in enumerate(items):
        add_para(tf, f"{bullet} {item}", font_size=font_size, color=color,
                 first=(i == 0), space_after=spacing)
    return tf

def add_kpi_card(slide, left, top, w, h, number, unit, label):
    add_card(slide, left, top, w, h)
    add_textbox(slide, left + 0.12, top + 0.1, w - 0.24, 0.45,
                text=number, font_size=26, color=BLUE_PRIMARY, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, left + 0.12, top + 0.48, w - 0.24, 0.2,
                text=unit, font_size=11, color=BLUE_ACCENT, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, left + 0.12, top + 0.7, w - 0.24, 0.28,
                text=label, font_size=10, color=TEXT_MEDIUM,
                alignment=PP_ALIGN.CENTER)

def add_rect_cell(slide, x, y, w, h, text, font_size=10.5,
                  color=TEXT_DARK, bg_color=WHITE, bold=False, align=PP_ALIGN.CENTER):
    cell = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    cell.fill.solid()
    cell.fill.fore_color.rgb = bg_color
    cell.line.color.rgb = BORDER_LIGHT
    cell.line.width = Pt(0.4)
    p = cell.text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = 'Microsoft YaHei'
    p.alignment = align
    return cell

# ══════════════════════════════════════════════════════════════
# SLIDE 1 — Cover
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()

# Top background block
top_block = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(0),
    Inches(SLIDE_W), Inches(4.6)
)
top_block.fill.solid()
top_block.fill.fore_color.rgb = COVER_BG
top_block.line.fill.background()

# Accent stripe
stripe = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(4.6),
    Inches(SLIDE_W), Inches(0.05)
)
stripe.fill.solid()
stripe.fill.fore_color.rgb = BLUE_PRIMARY
stripe.line.fill.background()

# Left vertical accent line
vline = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(1.3), Inches(1.4),
    Inches(0.055), Inches(2.2)
)
vline.fill.solid()
vline.fill.fore_color.rgb = BLUE_ACCENT
vline.line.fill.background()

# Main title
add_textbox(slide, 1.75, 1.4, 10.5, 1.2,
            text="多生理参数监护系统及\n关键信号处理算法",
            font_size=42, color=BLUE_PRIMARY, bold=True,
            alignment=PP_ALIGN.LEFT, line_spacing=1.2)

# English subtitle
add_textbox(slide, 1.75, 2.8, 10.5, 0.55,
            text="Multi-Physiological Parameter Monitoring System\n& Key Signal Processing Algorithms",
            font_size=14, color=TEXT_MEDIUM, alignment=PP_ALIGN.LEFT, line_spacing=1.35)

# Bottom info
add_textbox(slide, 1.75, 5.35, 10.5, 0.45,
            text="本科毕业设计答辩  |  河南工学院",
            font_size=22, color=BLUE_PRIMARY, bold=True, alignment=PP_ALIGN.LEFT)

add_textbox(slide, 1.75, 5.95, 5.0, 0.32,
            text="2026 年 5 月",
            font_size=14, color=TEXT_MEDIUM, alignment=PP_ALIGN.LEFT)

# Decorative circles
for cx, cy, cr in [(11.0, 5.2, 1.8), (11.6, 5.9, 0.9)]:
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        Inches(cx), Inches(cy), Inches(cr), Inches(cr))
    c.fill.solid()
    c.fill.fore_color.rgb = BLUE_PALE
    c.line.fill.background()

# ══════════════════════════════════════════════════════════════
# SLIDE 2 — Table of Contents
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "目  录")
add_page_number(slide, 2)

toc = [
    ("01", "研究背景与意义", "行业背景 · 现存问题 · 理论及实践意义"),
    ("02", "研究内容与方法", "技术路线总览 · 文献研究 · 实验验证 · 系统开发"),
    ("03", "核心算法工作", "ECG 频域带通+自适应差分阈值 · LMS ALE 呼吸增强 · 体温 FIR 校准"),
    ("04", "研究结果", "ECG 检测性能 · 呼吸/体温精度验证 · GUI 平台演示"),
    ("05", "结论与展望", "研究成果总结 · 研究局限性 · 未来改进方向"),
]

for i, (num, title, desc) in enumerate(toc):
    y = 1.35 + i * 1.1
    color = BLUE_PRIMARY if i % 2 == 0 else BLUE_ACCENT
    # Number circle
    ns = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        Inches(1.0), Inches(y + 0.04), Inches(0.5), Inches(0.5))
    ns.fill.solid()
    ns.fill.fore_color.rgb = color
    ns.line.fill.background()
    p = ns.text_frame.paragraphs[0]
    p.text = num; p.font.size = Pt(16); p.font.color.rgb = WHITE
    p.font.bold = True; p.font.name = 'Calibri'; p.alignment = PP_ALIGN.CENTER

    add_textbox(slide, 1.8, y, 10.0, 0.34,
                text=title, font_size=19, color=BLUE_PRIMARY, bold=True)
    add_textbox(slide, 1.8, y + 0.38, 10.0, 0.24,
                text=desc, font_size=11.5, color=TEXT_MEDIUM)

# ══════════════════════════════════════════════════════════════
# SLIDE 3 — Background 1: Industry & Clinical Needs
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究背景 — 行业现状与临床需求")
add_page_number(slide, 3)

# KPI cards
kpi_w = (CONTENT_W - 0.6) / 3
add_kpi_card(slide, MARGIN, 1.15, kpi_w, 1.3,
             "1,790 万", "/年", "全球心血管疾病年死亡人数 (WHO)")
add_kpi_card(slide, MARGIN + kpi_w + 0.3, 1.15, kpi_w, 1.3,
             "3 大核心", "体征参数", "ECG · 呼吸频率 · 体温")
add_kpi_card(slide, MARGIN + 2*(kpi_w + 0.3), 1.15, kpi_w, 1.3,
             "> 300 亿", "美元", "2027年全球监护设备市场规模")

# Policy & market driver banner
add_card(slide, MARGIN, 2.65, CONTENT_W, 0.48, BLUE_LIGHT)
add_textbox(slide, MARGIN + 0.2, 2.69, CONTENT_W - 0.4, 0.38,
            text="政策驱动：「健康中国2030」推动智慧医疗落地  |  中国 60 岁以上人口超 2.8 亿，慢性病管理需求激增  |  可穿戴医疗设备年复合增长率 > 20%",
            font_size=11.5, color=BLUE_PRIMARY, bold=True, anchor=MSO_ANCHOR.MIDDLE,
            alignment=PP_ALIGN.CENTER)

# Two-column layout below
cw = (CONTENT_W - 0.4) / 2

# Left: Core clinical needs
add_card(slide, MARGIN, 3.35, cw, 3.4, BLUE_PALE)
add_textbox(slide, MARGIN + 0.25, 3.48, cw - 0.5, 0.28,
            text="核心临床需求", font_size=16, color=BLUE_PRIMARY, bold=True)
items_left = [
    "ECG 是诊断心律失常、心肌缺血的「金标准」无创手段，12 导联心电图已纳入常规体检",
    "呼吸频率是危重患者早期预警最关键指标之一，连续监测可提前 6–12 h 发现病情恶化",
    "体温为感染、炎症的基础筛查参数，多参数融合（ECG+Resp+Temp）可显著提升诊断准确率",
    "传统监护仪价格昂贵（数万–数十万元），基层医疗机构与家庭场景难以普及",
]
add_bullet_block(slide, MARGIN + 0.25, 3.95, cw - 0.5, 2.6, items_left, font_size=12.5, spacing=12)

# Right: Technology trends
add_card(slide, MARGIN + cw + 0.4, 3.35, cw, 3.4, BLUE_PALE)
add_textbox(slide, MARGIN + cw + 0.65, 3.48, cw - 0.5, 0.28,
            text="技术发展趋势", font_size=16, color=BLUE_PRIMARY, bold=True)
items_right = [
    "便携化：从大型床边监护仪向可穿戴贴片/手表形态演进，MEMS 传感器加速小型化进程",
    "智能化：深度学习（CNN/LSTM）逐步应用于心电分类与异常检测，AI 辅助诊断成为热点",
    "远程化：5G + 物联网使能远程实时监护，院内–院外连续健康管理成为可能",
    "开源化：MIT-BIH / PhysioNet 等公开数据库推动算法验证标准化，促进学术与产业协同",
]
add_bullet_block(slide, MARGIN + cw + 0.65, 3.95, cw - 0.5, 2.6, items_right, font_size=12.5, spacing=12)

# ══════════════════════════════════════════════════════════════
# SLIDE 4 — Background 2: Existing Problems
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究背景 — 现存的技术挑战")
add_page_number(slide, 4)

problems = [
    ("ECG 信号", "基线漂移、肌电噪声、运动伪差严重干扰 R 波检测；传统固定阈值法在不同噪声下鲁棒性不足，易漏检/误检", BLUE_PRIMARY),
    ("呼吸信号", "阻抗式呼吸监测易受运动伪影影响；低信噪比下常规峰值检测失败率高，难以准确提取呼吸率", BLUE_ACCENT),
    ("体温信号", "低成本红外/NTC 传感器普遍存在精度偏差；缺乏系统化的数字滤波与校准流程，测量一致性差", RGBColor(0x4A, 0x90, 0xD9)),
    ("系统层面", "商用监护仪价格昂贵（数万至数十万元）、算法封闭不可定制；科研与教学中缺乏开源、可验证的多参数监护平台", RGBColor(0x6B, 0xA3, 0xE0)),
]

for i, (title, desc, color) in enumerate(problems):
    y = 1.25 + i * 1.4
    # Color stripe
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(MARGIN), Inches(y), Inches(0.055), Inches(1.1))
    s.fill.solid(); s.fill.fore_color.rgb = color; s.line.fill.background()

    add_textbox(slide, MARGIN + 0.35, y - 0.02, 2.8, 0.34,
                text=title, font_size=17, color=color, bold=True)
    add_textbox(slide, MARGIN + 0.35, y + 0.33, CONTENT_W - 0.35, 0.68,
                text=desc, font_size=13, color=TEXT_DARK, line_spacing=1.35)

# ══════════════════════════════════════════════════════════════
# SLIDE 5 — Background 3: Research Significance
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究意义")
add_page_number(slide, 5)

card_w = (CONTENT_W - 0.4) / 2

# Theory significance — shorter cards
add_card(slide, MARGIN, 1.2, card_w, 3.3)
add_textbox(slide, MARGIN + 0.35, 1.35, card_w - 0.7, 0.3,
            text="理论意义", font_size=17, color=BLUE_PRIMARY, bold=True)
theory_items = [
    "提出 FFT 频域带通 + 自适应差分阈值融合的 R 波检测方法，丰富了 ECG 特征提取理论框架",
    "将 LMS ALE 应用于呼吸信号运动伪差抑制，拓展了自适应滤波在生理信号处理中的应用",
    "设计完整的生理信号处理算法链（滤波→特征提取→参数估计），为同类研究提供可复现参考",
]
add_bullet_block(slide, MARGIN + 0.35, 1.8, card_w - 0.7, 2.5,
                 theory_items, font_size=13.5, spacing=12)

# Practice significance
add_card(slide, MARGIN + card_w + 0.4, 1.2, card_w, 3.3)
add_textbox(slide, MARGIN + card_w + 0.75, 1.35, card_w - 0.7, 0.3,
            text="实践意义", font_size=17, color=BLUE_PRIMARY, bold=True)
practice_items = [
    "构建基于 MATLAB 的完整多生理参数监护平台，覆盖 ECG/呼吸/体温三类信号",
    "所有算法纯 MATLAB 实现，不依赖第三方 WFDB 工具箱，便于教学演示与二次开发",
    "为低成本可穿戴设备算法选型提供参考——差分阈值法计算量小、可解释性强，适合嵌入式移植",
]
add_bullet_block(slide, MARGIN + card_w + 0.75, 1.8, card_w - 0.7, 2.5,
                 practice_items, font_size=13.5, spacing=12)

# Summary strip
add_card(slide, MARGIN, 4.85, CONTENT_W, 0.6, BLUE_LIGHT)
add_textbox(slide, MARGIN + 0.25, 4.92, CONTENT_W - 0.5, 0.44,
            text="核心目标：在噪声环境下实现高精度、鲁棒的多生理参数自动检测，构建可验证、可交互的综合监护平台。",
            font_size=14.5, color=BLUE_PRIMARY, bold=True, anchor=MSO_ANCHOR.MIDDLE,
            alignment=PP_ALIGN.CENTER)

# Keywords
keywords = ["ECG R 波检测", "LMS 自适应滤波", "呼吸率提取", "体温校准", "MIT-BIH 验证", "MATLAB GUI"]
kw_w = (CONTENT_W - 2.5) / 6
for j, kw in enumerate(keywords):
    x = MARGIN + j * (kw_w + 0.5)
    kw_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(5.85), Inches(kw_w), Inches(0.38))
    kw_box.fill.solid(); kw_box.fill.fore_color.rgb = WHITE
    kw_box.line.color.rgb = BLUE_ACCENT; kw_box.line.width = Pt(0.8)
    p = kw_box.text_frame.paragraphs[0]
    p.text = kw; p.font.size = Pt(10.5); p.font.color.rgb = BLUE_PRIMARY
    p.font.name = 'Microsoft YaHei'; p.alignment = PP_ALIGN.CENTER

# ══════════════════════════════════════════════════════════════
# SLIDE 6 — Research Content & Technical Roadmap
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究内容与技术路线", "整体研究框架总览")
add_page_number(slide, 6)

# 4-stage pipeline
stage_w = (CONTENT_W - 1.2) / 4  # ~2.71 each
stage_h = 2.65
colors_4 = [BLUE_PRIMARY, BLUE_ACCENT, RGBColor(0x4A, 0x90, 0xD9), RGBColor(0x6B, 0xA3, 0xE0)]
stages = [
    ("数据采集", "MIT-BIH 心律失常数据库\n(48条/360Hz/30min)\nBIDMC 呼吸数据集 (CSV)\nNTC 红外体温 (串口 9600)"),
    ("信号处理", "FFT 频域带通 (5-18 Hz)\n自适应差分阈值 R 波检测\nLMS ALE 呼吸自适应增强\nFIR 低通 + 最小二乘校准"),
    ("GUI 集成", "MATLAB App Designer\n4 层模块化架构设计\n3 层频分刷新 (0.5/1.0/2.0s)\n声光联动 + TTS 分级报警"),
    ("验证评估", "6 记录性能评估\n(Acc/Se/P+/F1/HR_MAE)\n3 类噪声鲁棒性测试\n(高斯/工频/脉冲, 0-30dB)"),
]

for i, (title, desc) in enumerate(stages):
    x = MARGIN + i * (stage_w + 0.4)
    color = colors_4[i]

    # Card
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.25), Inches(stage_w), Inches(stage_h))
    box.fill.solid(); box.fill.fore_color.rgb = WHITE
    box.line.color.rgb = color; box.line.width = Pt(1.4)

    # Color top bar
    tb = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(1.25), Inches(stage_w), Inches(0.05))
    tb.fill.solid(); tb.fill.fore_color.rgb = color; tb.line.fill.background()

    # Number circle
    nc = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        Inches(x + stage_w/2 - 0.22), Inches(1.48), Inches(0.44), Inches(0.44))
    nc.fill.solid(); nc.fill.fore_color.rgb = color; nc.line.fill.background()
    p = nc.text_frame.paragraphs[0]
    p.text = str(i+1); p.font.size = Pt(15); p.font.color.rgb = WHITE
    p.font.bold = True; p.font.name = 'Calibri'; p.alignment = PP_ALIGN.CENTER

    # Title
    add_textbox(slide, x + 0.1, 2.12, stage_w - 0.2, 0.3,
                text=title, font_size=15, color=color, bold=True,
                alignment=PP_ALIGN.CENTER)
    # Description
    add_textbox(slide, x + 0.15, 2.52, stage_w - 0.3, 1.25,
                text=desc, font_size=11, color=TEXT_DARK,
                alignment=PP_ALIGN.CENTER, line_spacing=1.35)

# Bottom — 3 processing chains
chain_w = (CONTENT_W - 0.6) / 3
chains = [
    ("ECG 处理链", BLUE_PRIMARY,
     "原始 ECG → 中值基线校正 → FFT带通(5-18Hz) → 一阶差分包络提取 → 自适应阈值(Trend+1.40×Spread, 1.50s窗) → 不应期(0.25s)选峰 → HR=60/RR"),
    ("呼吸处理链", BLUE_ACCENT,
     "原始 Resp → 去基线 → FFT带通(0.08-0.80Hz) → LMS ALE自适应增强(权值在线更新) → 自适应阈值峰值检测 → RespRate=60/RR"),
    ("体温处理链", RGBColor(0x4A, 0x90, 0xD9),
     "串口读取(9600-8N1, HEX 0xAB/0xAA) → 20阶Hamming窗FIR(0.05Hz) → 零相位filtfilt → 最小二乘线性校准(T=k·V+b, R²>0.99)"),
]
for j, (title, color, desc) in enumerate(chains):
    x = MARGIN + j * (chain_w + 0.3)
    add_card(slide, x, 4.2, chain_w, 2.1, BLUE_PALE)
    add_textbox(slide, x + 0.15, 4.28, chain_w - 0.3, 0.26,
                text=title, font_size=13, color=color, bold=True)
    add_textbox(slide, x + 0.15, 4.64, chain_w - 0.3, 1.6,
                text=desc, font_size=10.5, color=TEXT_DARK, line_spacing=1.45)

# Innovation highlight strip
add_card(slide, MARGIN, 6.42, CONTENT_W, 0.36, BLUE_LIGHT)
add_textbox(slide, MARGIN + 0.2, 6.44, CONTENT_W - 0.4, 0.3,
            text="创新亮点：FFT 频域+时域自适应阈值融合  |  LMS ALE 呼吸增强抗运动伪差  |  纯 MATLAB 实现不依赖 WFDB 工具箱  |  212 格式字节级解析",
            font_size=10.5, color=BLUE_PRIMARY, bold=True, anchor=MSO_ANCHOR.MIDDLE,
            alignment=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════
# SLIDE 7 — Method: Literature Research
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究方法 — 文献研究法", "对比分析国内外相关研究，确定技术路线")
add_page_number(slide, 7)

left_w = 8.6
right_x = MARGIN + left_w + 0.35
right_w = CONTENT_W - left_w - 0.35

# --- ECG ---
add_textbox(slide, MARGIN, 1.18, left_w, 0.26,
            text="ECG R 波检测方法对比", font_size=15, color=BLUE_PRIMARY, bold=True)
for j, (method, note, decision) in enumerate([
    ("时域法 (Pan-Tompkins)", "经典成熟，需调参较多", "参考"),
    ("小波变换法", "抗噪好，计算量大、实时性差", "未采用"),
    ("FFT 频域带通 + 自适应差分阈值 ✓", "计算量小、实时性好、可解释性强", "采用"),
]):
    y = 1.55 + j * 0.42
    tag_color = BLUE_ACCENT if "采用" in decision else TEXT_SUBTLE
    add_textbox(slide, MARGIN + 0.3, y, 3.8, 0.22,
                text=method, font_size=12, color=TEXT_DARK, bold=True)
    add_textbox(slide, MARGIN + 4.3, y, 2.8, 0.22,
                text=note, font_size=11, color=TEXT_MEDIUM)
    add_textbox(slide, MARGIN + 7.3, y, 1.0, 0.22,
                text=decision, font_size=12, color=tag_color, bold=True)

# --- Respiration ---
add_textbox(slide, MARGIN, 3.0, left_w, 0.26,
            text="呼吸信号处理方法对比", font_size=15, color=BLUE_PRIMARY, bold=True)
for j, (method, note, decision) in enumerate([
    ("简单带通 + 峰值检测", "实现简单，运动伪差干扰大，低SNR失效", "基础"),
    ("小波去噪 + 峰值检测", "去噪效果好，计算量大", "未采用"),
    ("LMS 自适应线谱增强 (ALE) ✓", "自适应抑制随机噪声、增强准周期呼吸波", "采用"),
]):
    y = 3.37 + j * 0.42
    tag_color = BLUE_ACCENT if "采用" in decision else TEXT_SUBTLE
    add_textbox(slide, MARGIN + 0.3, y, 3.8, 0.22,
                text=method, font_size=12, color=TEXT_DARK, bold=True)
    add_textbox(slide, MARGIN + 4.3, y, 2.8, 0.22,
                text=note, font_size=11, color=TEXT_MEDIUM)
    add_textbox(slide, MARGIN + 7.3, y, 1.0, 0.22,
                text=decision, font_size=12, color=tag_color, bold=True)

# --- Temp ---
add_textbox(slide, MARGIN, 4.82, left_w, 0.26,
            text="体温处理方法对比", font_size=15, color=BLUE_PRIMARY, bold=True)
for j, (method, note, decision) in enumerate([
    ("直接串口读取", "最简单，无滤波，传感器噪声大", "基础"),
    ("FIR 低通 + 最小二乘校准 ✓", "抑制高频噪声、无相位失真、校准精度高", "采用"),
]):
    y = 5.19 + j * 0.42
    tag_color = BLUE_ACCENT if "采用" in decision else TEXT_SUBTLE
    add_textbox(slide, MARGIN + 0.3, y, 3.8, 0.22,
                text=method, font_size=12, color=TEXT_DARK, bold=True)
    add_textbox(slide, MARGIN + 4.3, y, 2.8, 0.22,
                text=note, font_size=11, color=TEXT_MEDIUM)
    add_textbox(slide, MARGIN + 7.3, y, 1.0, 0.22,
                text=decision, font_size=12, color=tag_color, bold=True)

# Right — key references
add_card(slide, right_x, 1.18, right_w, 5.6, BLUE_PALE)
add_textbox(slide, right_x + 0.2, 1.3, right_w - 0.4, 0.24,
            text="关键参考文献", font_size=13, color=BLUE_PRIMARY, bold=True)
refs = [
    "Pan & Tompkins (1985)\nQRS 检测经典算法",
    "MIT-BIH Arrhythmia DB (1980)\n标准验证数据集",
    "BIDMC Respiration Dataset\n呼吸信号参考标准",
    "Widrow et al. (1975)\nLMS 自适应滤波理论",
    "Clifford et al. (2006)\n生理信号处理综述",
    "Zhang et al. (2020)\n深度学习 ECG 分类进展",
]
for j, ref in enumerate(refs):
    add_textbox(slide, right_x + 0.2, 1.68 + j * 0.82, right_w - 0.4, 0.72,
                text=ref, font_size=10.5, color=TEXT_DARK, line_spacing=1.3)

# ══════════════════════════════════════════════════════════════
# SLIDE 8 — Method: Experimental Validation
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究方法 — 实验验证法", "数据集构建与评估指标体系")
add_page_number(slide, 8)

card_w2 = (CONTENT_W - 0.4) / 2

# MIT-BIH
add_card(slide, MARGIN, 1.2, card_w2, 2.5)
add_textbox(slide, MARGIN + 0.3, 1.32, card_w2 - 0.6, 0.3,
            text="MIT-BIH 心律失常数据库", font_size=15, color=BLUE_PRIMARY, bold=True)
add_bullet_block(slide, MARGIN + 0.3, 1.72, card_w2 - 0.6, 1.8, [
    "48 条双通道动态心电图，每条 30 分钟",
    "采样率 360 Hz，12-bit ADC",
    "含 R 波专家标注，作为验证金标准",
    "覆盖正常窦性、室性早搏等多种心律类型",
], font_size=12, spacing=7)

# BIDMC
add_card(slide, MARGIN + card_w2 + 0.4, 1.2, card_w2, 2.5)
add_textbox(slide, MARGIN + card_w2 + 0.7, 1.32, card_w2 - 0.6, 0.3,
            text="BIDMC 呼吸数据集 & 体温实验", font_size=15, color=BLUE_PRIMARY, bold=True)
add_bullet_block(slide, MARGIN + card_w2 + 0.7, 1.72, card_w2 - 0.6, 1.8, [
    "53 条记录，含同步 ECG 与呼吸参考信号",
    "呼吸阻抗信号 + 专家标注呼吸峰位置",
    "体温：DS18B20 + NTC 热敏电阻双模采集",
    "自制校准台：恒温水浴 36–42°C，6 个校准点",
], font_size=12, spacing=7)

# Evaluation metrics — 6 cards across full width
add_textbox(slide, MARGIN, 4.05, CONTENT_W, 0.28,
            text="评估指标体系", font_size=15, color=BLUE_PRIMARY, bold=True)

metric_w = (CONTENT_W - 2.5) / 6  # ~1.59 each
metrics = [
    ("准确率\nAccuracy", "95.11%", "整体检测正确率"),
    ("灵敏度\nSensitivity", "97.75%", "真实R波检出率"),
    ("阳性预测值\nP+", "96.53%", "检出R波正确率"),
    ("F1 分数", "96.31%", "Se与P+调和均值"),
    ("心率 MAE", "0.55–1.99\nbpm", "6记录误差范围"),
    ("容差窗口", "±150 ms", "位置匹配窗口"),
]
for j, (name, value, desc) in enumerate(metrics):
    x = MARGIN + j * (metric_w + 0.5)
    add_card(slide, x, 4.45, metric_w, 1.85, BLUE_PALE)
    add_textbox(slide, x + 0.08, 4.52, metric_w - 0.16, 0.55,
                text=name, font_size=10.5, color=TEXT_MEDIUM,
                alignment=PP_ALIGN.CENTER, line_spacing=1.2)
    add_textbox(slide, x + 0.08, 5.05, metric_w - 0.16, 0.52,
                text=value, font_size=17, color=BLUE_PRIMARY, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, x + 0.08, 5.65, metric_w - 0.16, 0.3,
                text=desc, font_size=9, color=TEXT_SUBTLE,
                alignment=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════
# SLIDE 9 — Method: System Development (GUI)
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究方法 — 系统开发法", "MATLAB GUI 平台架构设计")
add_page_number(slide, 9)

# Section title — 4-layer architecture (full width)
add_textbox(slide, MARGIN, 1.15, CONTENT_W, 0.26,
            text="四层模块化架构", font_size=15, color=BLUE_PRIMARY, bold=True)

layers = [
    ("人机交互层", "App Designer GUI · 实时波形显示 · 数字参数面板 · 用户控制按钮",
     BLUE_PRIMARY),
    ("应用功能层", "数据存储(.mat) · 历史回放 · 声光报警 · TTS语音播报 · 可视化分析导出",
     BLUE_ACCENT),
    ("信号处理层", "ECG R波检测 · 呼吸 ALE 增强 · 体温 FIR 校准 · SNR 估计",
     RGBColor(0x4A, 0x90, 0xD9)),
    ("数据采集层", "PhysioNet 自动下载 · MIT-BIH 212 格式解析 · BIDMC CSV 加载 · 串口体温读取",
     RGBColor(0x6B, 0xA3, 0xE0)),
]
for j, (name, desc, color) in enumerate(layers):
    y = 1.55 + j * 0.82
    # Full-width card
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(MARGIN), Inches(y), Inches(CONTENT_W), Inches(0.65))
    box.fill.solid(); box.fill.fore_color.rgb = BLUE_PALE
    box.line.color.rgb = color; box.line.width = Pt(1.1)

    # Vertical color stripe on left edge
    stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(MARGIN), Inches(y), Inches(0.055), Inches(0.65))
    stripe.fill.solid(); stripe.fill.fore_color.rgb = color; stripe.line.fill.background()

    # Layer name
    add_textbox(slide, MARGIN + 0.3, y + 0.14, 2.4, 0.28,
                text=name, font_size=14, color=color, bold=True,
                anchor=MSO_ANCHOR.MIDDLE)
    # Description
    add_textbox(slide, MARGIN + 2.8, y + 0.14, CONTENT_W - 3.1, 0.28,
                text=desc, font_size=11.5, color=TEXT_MEDIUM,
                anchor=MSO_ANCHOR.MIDDLE)

# Bottom — two cards side by side: Refresh + Alarm
card_bottom_w = (CONTENT_W - 0.45) / 2
card_y = 5.05
card_height = 2.05

# Left: Refresh mechanism
add_card(slide, MARGIN, card_y, card_bottom_w, card_height)
add_textbox(slide, MARGIN + 0.3, card_y + 0.15, card_bottom_w - 0.6, 0.26,
            text="三层频分刷新机制", font_size=14, color=BLUE_PRIMARY, bold=True)
add_bullet_block(slide, MARGIN + 0.3, card_y + 0.55, card_bottom_w - 0.6, 1.3, [
    "主定时器周期 0.25 s，BusyMode='drop' 防队列堆积",
    "波形刷新 0.50 s（高频 — ECG/Resp 波形流畅滚动）",
    "参数刷新 1.00 s（中频 — 心率/呼吸率/体温数值更新）",
    "分析刷新 2.00 s（低频 — 报警判断/趋势分析/CV 计算）",
], font_size=11.5, spacing=7)

# Right: Alarm system
add_card(slide, MARGIN + card_bottom_w + 0.45, card_y, card_bottom_w, card_height)
add_textbox(slide, MARGIN + card_bottom_w + 0.75, card_y + 0.15, card_bottom_w - 0.6, 0.26,
            text="报警与数据管理", font_size=14, color=BLUE_PRIMARY, bold=True)
add_bullet_block(slide, MARGIN + card_bottom_w + 0.75, card_y + 0.55, card_bottom_w - 0.6, 1.3, [
    "两级阈值报警：黄色预警 + 红色报警，声光联动",
    "ECG：HR > 120 或 HR < 50 bpm → 红色报警",
    "呼吸：RR < 8 或 RR > 30 bpm → 黄色预警",
    "报警日志自动写入 output/alarms/，支持回溯",
], font_size=11.5, spacing=7)

# ══════════════════════════════════════════════════════════════
# SLIDE 10 — Result: ECG R-wave Detection
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究结果 — ECG R 波检测算法性能", "核心工作")
add_page_number(slide, 10)

# Algorithm flow — horizontal 6 steps across top
add_textbox(slide, MARGIN, 1.1, CONTENT_W, 0.24,
            text="算法流程", font_size=15, color=BLUE_PRIMARY, bold=True)

steps = [
    ("① 基线校正", "中值滤波"),
    ("② FFT 带通", "5–18 Hz"),
    ("③ 差分包络", "一阶差分+abs"),
    ("④ 自适应阈值", "Trend+1.40×Spread"),
    ("⑤ 不应期选峰", "0.25s窗口"),
    ("⑥ 心率计算", "HR=60/RR"),
]
step_w = (CONTENT_W - 2.5) / 6
for j, (name, detail) in enumerate(steps):
    x = MARGIN + j * (step_w + 0.5)
    sb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(1.42), Inches(step_w), Inches(0.72))
    sb.fill.solid(); sb.fill.fore_color.rgb = BLUE_PALE
    sb.line.color.rgb = BLUE_PRIMARY; sb.line.width = Pt(0.8)
    add_textbox(slide, x + 0.05, 1.44, step_w - 0.1, 0.26,
                text=name, font_size=11.5, color=BLUE_PRIMARY, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, x + 0.05, 1.72, step_w - 0.1, 0.22,
                text=detail, font_size=9.5, color=TEXT_MEDIUM,
                alignment=PP_ALIGN.CENTER)

# Performance table — full width
add_textbox(slide, MARGIN, 2.45, CONTENT_W, 0.24,
            text="6 记录性能验证表", font_size=14, color=BLUE_PRIMARY, bold=True)

table_data = [
    ["记录", "TP", "FP", "FN", "Acc(%)", "Se(%)", "P+(%)", "F1(%)"],
    ["100", "2273", "0", "0", "100", "100", "100", "100"],
    ["103", "2084", "0", "0", "100", "100", "100", "100"],
    ["105", "2572", "142", "206", "88.7", "92.6", "94.8", "93.7"],
    ["106", "2027", "118", "136", "88.9", "93.7", "94.5", "94.1"],
    ["109", "2492", "81", "103", "93.1", "96.0", "96.9", "96.4"],
    ["205", "2656", "43", "27", "97.4", "99.0", "98.4", "98.7"],
]
col_ws = [1.0, 1.15, 0.9, 0.9, 1.4, 1.4, 1.4, 1.4]
ROW_H = 0.42
tbl_y = 2.85

for j, row in enumerate(table_data):
    is_header = (j == 0)
    bg = TABLE_HEADER if is_header else (TABLE_STRIPE if j % 2 == 0 else WHITE)
    fc = WHITE if is_header else TEXT_DARK
    x_pos = MARGIN
    for k, cell_text in enumerate(row):
        w = col_ws[k]
        add_rect_cell(slide, x_pos, tbl_y + j * ROW_H, w, ROW_H - 0.04,
                      cell_text, font_size=10 if is_header else 11,
                      color=fc, bg_color=bg, bold=is_header)
        x_pos += w

# Summary bar
tbl_end_y = tbl_y + len(table_data) * ROW_H + 0.08
add_card(slide, MARGIN, tbl_end_y, CONTENT_W, 0.48, BLUE_LIGHT)
add_textbox(slide, MARGIN + 0.2, tbl_end_y + 0.04, CONTENT_W - 0.4, 0.38,
            text="加权平均：Acc 95.11%  |  Se 97.75%  |  P+ 96.53%  |  F1 96.31%  |  HR MAE 0.55–1.99 bpm",
            font_size=13.5, color=BLUE_PRIMARY, bold=True, anchor=MSO_ANCHOR.MIDDLE,
            alignment=PP_ALIGN.CENTER)

# Innovation
add_textbox(slide, MARGIN, tbl_end_y + 0.58, CONTENT_W, 0.22,
            text="创新点：频域带通 + 时域自适应阈值融合  |  自适应阈值追踪信号幅度变化  |  一阶微分增强 QRS 斜率特征",
            font_size=11, color=TEXT_MEDIUM, alignment=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════
# SLIDE 11 — Result: Respiration & Temperature
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究结果 — 呼吸率与体温检测性能")
add_page_number(slide, 11)

cw = (CONTENT_W - 0.4) / 2  # ~5.82

# Respiration
add_card(slide, MARGIN, 1.2, cw, 3.3)
add_textbox(slide, MARGIN + 0.3, 1.32, cw - 0.6, 0.28,
            text="呼吸信号 LMS ALE 自适应增强", font_size=15, color=BLUE_PRIMARY, bold=True)
resp_steps = [
    "① 去基线 + FFT 带通 (0.08–0.80 Hz)",
    "② LMS 自适应线谱增强（延迟×自相关，权值在线更新）",
    "③ 自适应阈值峰值检测（实时追踪呼吸波幅度）",
    "④ 呼吸率计算：60 / 呼吸峰间期均值",
]
for j, s in enumerate(resp_steps):
    y = 1.78 + j * 0.48
    add_textbox(slide, MARGIN + 0.3, y, cw - 0.6, 0.36,
                text=s, font_size=11.5, color=TEXT_DARK)
add_textbox(slide, MARGIN + 0.3, 3.82, cw - 0.6, 0.28,
            text="效果：自适应抑制运动伪差，低 SNR 下优于简单带通方法",
            font_size=11.5, color=BLUE_ACCENT, bold=True)

# Temperature
add_card(slide, MARGIN + cw + 0.4, 1.2, cw, 3.3)
add_textbox(slide, MARGIN + cw + 0.7, 1.32, cw - 0.6, 0.28,
            text="体温 FIR 滤波与最小二乘校准", font_size=15, color=BLUE_PRIMARY, bold=True)
temp_steps = [
    "① 20 阶 Hamming 窗 FIR 低通（截止 0.05 Hz）",
    "② 零相位 filtfilt 消除相位失真",
    "③ 最小二乘线性校准：T = k·V + b",
    "④ 校准精度：R² > 0.99，MAE < 0.1 °C",
]
for j, s in enumerate(temp_steps):
    y = 1.78 + j * 0.48
    add_textbox(slide, MARGIN + cw + 0.7, y, cw - 0.6, 0.36,
                text=s, font_size=11.5, color=TEXT_DARK)
add_textbox(slide, MARGIN + cw + 0.7, 3.82, cw - 0.6, 0.28,
            text="效果：高频噪声抑制 + 传感器精度校准，满足临床监护需求",
            font_size=11.5, color=RGBColor(0x4A, 0x90, 0xD9), bold=True)

# Anti-noise table — below the two cards
add_textbox(slide, MARGIN, 4.8, CONTENT_W, 0.26,
            text="抗噪声鲁棒性评估（ECG R 波检测灵敏度 Se，不同 SNR 水平）", font_size=14, color=BLUE_PRIMARY, bold=True)

noise_data = [
    ["噪声类型", "SNR = 0 dB", "SNR = 5 dB", "SNR = 10 dB", "SNR = 20 dB", "SNR = 30 dB"],
    ["高斯白噪声", "Se ≈ 82%", "Se ≈ 89%", "Se ≈ 94%", "Se ≈ 97%", "Se ≈ 98%"],
    ["50 Hz 工频干扰", "Se ≈ 78%", "Se ≈ 87%", "Se ≈ 93%", "Se ≈ 97%", "Se ≈ 98%"],
    ["脉冲伪差", "Se ≈ 70%", "Se ≈ 82%", "Se ≈ 90%", "Se ≈ 95%", "Se ≈ 97%"],
]

# 6 columns: type(2.0) + 5*data(1.8) = 2.0+9.0=11.0 < 12.033 ✓
noise_cols = [2.2, 1.96, 1.96, 1.96, 1.96, 1.96]
# Check: 2.2+5*1.96 = 2.2+9.8 = 12.0. Slightly over by 0. 12.0 < 12.033, OK.
# Actually 2.2 + 5*1.96 = 2.2 + 9.8 = 12.0. That's ≤ 12.033. Tight but OK.
# Let me adjust slightly: 2.0 + 5*2.0 = 12.0. Let me just do that.
noise_cols = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
# 6*2.0 = 12.0, starting from MARGIN (0.65). 0.65 + 12.0 = 12.65 < 13.333. Good.

for j, row in enumerate(noise_data):
    is_header = (j == 0)
    bg = TABLE_HEADER if is_header else (TABLE_STRIPE if j % 2 == 0 else WHITE)
    fc = WHITE if is_header else TEXT_DARK
    x_pos = MARGIN
    for k, cell_text in enumerate(row):
        w = noise_cols[k]
        add_rect_cell(slide, x_pos, 5.2 + j * 0.44, w, 0.38,
                      cell_text, font_size=10.5, color=fc, bg_color=bg,
                      bold=is_header)
        x_pos += w

# ══════════════════════════════════════════════════════════════
# SLIDE 12 — GUI Demo + Video
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "系统演示 — GUI 平台与实时监护", "MATLAB App Designer 综合监护平台")
add_page_number(slide, 12)

# Left — screenshot placeholder
add_card(slide, MARGIN, 1.2, cw, 3.2, BLUE_PALE)
add_textbox(slide, MARGIN + 0.2, 1.32, cw - 0.4, 0.26,
            text="GUI 主界面截图", font_size=14, color=BLUE_PRIMARY, bold=True,
            alignment=PP_ALIGN.CENTER)

frame = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(MARGIN + 0.5), Inches(1.72), Inches(cw - 1.0), Inches(2.5))
frame.fill.solid(); frame.fill.fore_color.rgb = WHITE
frame.line.color.rgb = BORDER_LIGHT; frame.line.width = Pt(0.8)
frame.line.dash_style = 2
p = frame.text_frame.paragraphs[0]
p.text = "请插入系统主界面截图"
p.font.size = Pt(13); p.font.color.rgb = TEXT_SUBTLE
p.font.name = 'Microsoft YaHei'; p.alignment = PP_ALIGN.CENTER

# Right — video placeholder
add_card(slide, MARGIN + cw + 0.4, 1.2, cw, 3.2, BLUE_PALE)
add_textbox(slide, MARGIN + cw + 0.6, 1.32, cw - 0.4, 0.26,
            text="系统操作演示视频", font_size=14, color=BLUE_PRIMARY, bold=True,
            alignment=PP_ALIGN.CENTER)

vf = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(MARGIN + cw + 0.9), Inches(1.72), Inches(cw - 1.0), Inches(2.5))
vf.fill.solid(); vf.fill.fore_color.rgb = WHITE
vf.line.color.rgb = BLUE_ACCENT; vf.line.width = Pt(1.5)

# Play button
play_x = MARGIN + cw + 0.4 + cw/2 - 0.55
play_c = slide.shapes.add_shape(MSO_SHAPE.OVAL,
    Inches(play_x), Inches(2.45), Inches(1.1), Inches(1.1))
play_c.fill.solid(); play_c.fill.fore_color.rgb = BLUE_ACCENT
play_c.line.fill.background()
p = play_c.text_frame.paragraphs[0]
p.text = "▶"; p.font.size = Pt(30); p.font.color.rgb = WHITE
p.font.name = 'Segoe UI Symbol'; p.alignment = PP_ALIGN.CENTER

add_textbox(slide, MARGIN + cw + 0.9, 4.35, cw - 1.0, 0.26,
            text="点击播放系统操作演示视频", font_size=12, color=BLUE_PRIMARY, bold=True,
            alignment=PP_ALIGN.CENTER)

# GUI features — bottom row
add_textbox(slide, MARGIN, 4.75, CONTENT_W, 0.24,
            text="GUI 核心特性", font_size=15, color=BLUE_PRIMARY, bold=True)

feat_w = (CONTENT_W - 2.0) / 5
features = [
    ("实时波形", "3路波形同步推进\nECG/Resp/Temp滚动"),
    ("智能报警", "两级声光报警\nTTS语音合成播报"),
    ("数据分析", "心率/呼吸率CV\n心呼相关性估计"),
    ("数据管理", "会话保存(.mat+CSV)\n可视化报告导出"),
    ("双模式", "Demo/实时采集\n无硬件也可验证"),
]
for j, (title, desc) in enumerate(features):
    x = MARGIN + j * (feat_w + 0.5)
    add_card(slide, x, 5.12, feat_w, 1.6, BLUE_PALE)
    add_textbox(slide, x + 0.08, 5.2, feat_w - 0.16, 0.26,
                text=title, font_size=12, color=BLUE_PRIMARY, bold=True,
                alignment=PP_ALIGN.CENTER)
    add_textbox(slide, x + 0.08, 5.52, feat_w - 0.16, 0.95,
                text=desc, font_size=10, color=TEXT_MEDIUM, line_spacing=1.45,
                alignment=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════
# SLIDE 13 — Research Limitations
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "研究局限性")
add_page_number(slide, 13)

limitations = [
    ("验证范围有限", "算法仅在 MIT-BIH / BIDMC 标准数据库验证，未经真实临床环境（多导联、多病人群体）的全面测试。数据库年代较早（1980s），患者群体和采集条件与当代临床存在差异。", BLUE_PRIMARY),
    ("运动状态下性能下降", "强运动伪差下 ECG 信号质量急剧恶化，R 波检测灵敏度从 97.75% 降至 70–80%（SNR < 5 dB），仍有较大提升空间。", BLUE_ACCENT),
    ("体温校准条件有限", "传感器校准仅在 36–42 °C 范围进行，未覆盖极端温度。实验在实验室恒温条件下完成，不同环境温度对传感器漂移的影响尚未量化。", RGBColor(0x4A, 0x90, 0xD9)),
    ("GUI 依赖 MATLAB 环境", "实时波形刷新在低性能机器上可能出现延迟/掉帧。当前方案依赖 MATLAB Runtime，未编译为独立可执行文件或移植至嵌入式平台。", RGBColor(0x6B, 0xA3, 0xE0)),
]

for i, (title, desc, color) in enumerate(limitations):
    y = 1.25 + i * 1.35
    # Color stripe
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(MARGIN), Inches(y), Inches(0.055), Inches(1.08))
    s.fill.solid(); s.fill.fore_color.rgb = color; s.line.fill.background()

    # Number circle
    nc = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        Inches(MARGIN + 0.35), Inches(y + 0.04), Inches(0.34), Inches(0.34))
    nc.fill.solid(); nc.fill.fore_color.rgb = color; nc.line.fill.background()
    p = nc.text_frame.paragraphs[0]
    p.text = str(i+1); p.font.size = Pt(12); p.font.color.rgb = WHITE
    p.font.bold = True; p.font.name = 'Calibri'; p.alignment = PP_ALIGN.CENTER

    add_textbox(slide, MARGIN + 0.9, y - 0.02, 4.0, 0.3,
                text=title, font_size=16, color=color, bold=True)
    add_textbox(slide, MARGIN + 0.9, y + 0.32, CONTENT_W - 0.9, 0.65,
                text=desc, font_size=12.5, color=TEXT_DARK, line_spacing=1.3)

# ══════════════════════════════════════════════════════════════
# SLIDE 14 — Conclusion & Outlook
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()
add_title_bar(slide, "结论与展望")
add_page_number(slide, 14)

# Conclusions
add_card(slide, MARGIN, 1.2, cw, 4.3)
add_textbox(slide, MARGIN + 0.3, 1.35, cw - 0.6, 0.28,
            text="研究结论", font_size=17, color=BLUE_PRIMARY, bold=True)
add_bullet_block(slide, MARGIN + 0.3, 1.78, cw - 0.6, 3.5, [
    "提出 FFT 频域带通 + 自适应差分阈值融合的 R 波检测方法，MIT-BIH 6 记录加权 Acc 95.11%、Se 97.75%、F1 96.31%",
    "将 LMS ALE 自适应线谱增强成功应用于呼吸信号运动伪差抑制，有效提升低 SNR 下的呼吸峰检测鲁棒性",
    "构建基于 MATLAB App Designer 的完整多生理参数监护平台，实现 ECG/呼吸/体温的实时监测、分级报警与数据管理",
    "所有信号处理算法以纯 MATLAB 实现，不依赖第三方 WFDB 工具箱，算法可复现、可验证、可移植",
], font_size=13.5, spacing=10)

# Outlook
add_card(slide, MARGIN + cw + 0.4, 1.2, cw, 4.3)
add_textbox(slide, MARGIN + cw + 0.7, 1.35, cw - 0.6, 0.28,
            text="未来展望", font_size=17, color=BLUE_PRIMARY, bold=True)
add_bullet_block(slide, MARGIN + cw + 0.7, 1.78, cw - 0.6, 3.5, [
    "引入深度学习（CNN / LSTM / Transformer），进一步提升复杂噪声场景下的 R 波检测与心律失常分类精度",
    "扩展更多生理参数（血压 PPG、血氧 SpO₂），构建覆盖更全面的多参数监护平台",
    "将核心算法移植至嵌入式平台（STM32 / DSP），推动从 MATLAB 原型到可穿戴设备的工程落地",
    "开展临床验证：与医院合作，在多导联、多病人群体条件下系统性验证算法性能与泛化能力",
], font_size=13.5, spacing=10)

# Bottom summary
add_card(slide, MARGIN, 5.85, CONTENT_W, 0.6, BLUE_LIGHT)
add_textbox(slide, MARGIN + 0.2, 5.92, CONTENT_W - 0.4, 0.44,
            text="从算法研究 → 系统集成 → 实验验证，完整实现了多生理参数监护系统的设计、开发与评估全流程。",
            font_size=15, color=BLUE_PRIMARY, bold=True, anchor=MSO_ANCHOR.MIDDLE,
            alignment=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════
# SLIDE 15 — Acknowledgments
# ══════════════════════════════════════════════════════════════
slide = add_blank_slide()

# Full background
bg_block = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(0), Inches(SLIDE_W), Inches(SLIDE_H))
bg_block.fill.solid(); bg_block.fill.fore_color.rgb = COVER_BG
bg_block.line.fill.background()

# Large title
add_textbox(slide, 1.0, 2.0, SLIDE_W - 2.0, 0.9,
            text="致  谢", font_size=44, color=BLUE_PRIMARY, bold=True,
            alignment=PP_ALIGN.CENTER)

# Elegant single-block text — font 16, tight but readable
tf = add_rich_textbox(slide, 2.5, 3.3, SLIDE_W - 5.0, 2.4)
add_para(tf,
    "感谢指导教师在本课题选题、算法设计与论文撰写各阶段给予的悉心指导。",
    font_size=16, color=TEXT_DARK, first=True, space_after=10, alignment=PP_ALIGN.CENTER)
add_para(tf,
    "感谢河南工学院提供的实验平台与学习环境，为本项目的顺利开展提供了坚实保障。",
    font_size=16, color=TEXT_DARK, space_after=10, alignment=PP_ALIGN.CENTER)
add_para(tf,
    "感谢 MIT-BIH / BIDMC / PhysioNet 等公开数据库为本研究提供宝贵的标准验证数据。",
    font_size=16, color=TEXT_DARK, space_after=10, alignment=PP_ALIGN.CENTER)
add_para(tf,
    "感谢所有同学和家人在论文撰写期间给予的支持与鼓励。",
    font_size=16, color=TEXT_DARK, space_after=10, alignment=PP_ALIGN.CENTER)

# Accent line
acc_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(SLIDE_W/2 - 1.2), Inches(5.9), Inches(2.4), Inches(0.045))
acc_line.fill.solid(); acc_line.fill.fore_color.rgb = BLUE_ACCENT
acc_line.line.fill.background()

add_textbox(slide, 1.0, 6.15, SLIDE_W - 2.0, 0.38,
            text="恳请各位老师批评指正", font_size=16, color=TEXT_MEDIUM,
            alignment=PP_ALIGN.CENTER)

add_page_number(slide, 15)

# ══════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════
output_path = r"d:\bishe\答辩PPT_多生理参数监护系统.pptx"
prs.save(output_path)
print(f"PPT saved to: {output_path}")
print(f"Total slides: {len(prs.slides)}")

# Quick dim check
print(f"Slide dimensions: {SLIDE_W}\" x {SLIDE_H}\"")
print(f"Content area: {MARGIN}\" margins, {CONTENT_W}\" usable width")
